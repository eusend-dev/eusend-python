# eusend

Official Python SDK for the [Eusend](https://eusend.dev) API — the EU-native transactional email platform.

Its shape mirrors [`resend-python`](https://github.com/resend/resend-python), so migrating from Resend is largely a `resend` → `eusend` rename.

- **Module-level config** — `eusend.api_key = "..."`, then call `eusend.Emails.send(...)`.
- **Zero HTTP dependencies** — the transport is built on the standard library.
- **Typed** — `TypedDict` params and responses; ships `py.typed`.

```bash
pip install eusend
```

Requires Python 3.8+.

---

## Getting started

```python
import eusend

eusend.api_key = "eu_live_..."

params: eusend.Emails.SendParams = {
    # `from` accepts a bare email or a display-name form: "Acme <you@yourdomain.com>"
    "from": "Acme <you@yourdomain.com>",
    "to": ["user@example.com"],
    "subject": "Hello",
    "html": "<p>Hello world</p>",
}

email = eusend.Emails.send(params)
print(email["id"])  # 9a8b7c6d-... (UUID)
```

The key can also come from the `EUSEND_API_KEY` environment variable, in which
case you can skip setting `eusend.api_key`.

Responses are dicts with **snake_case** keys — access fields with `email["id"]`.
On failure, methods raise `eusend.EusendError` (see [Error handling](#error-handling)).

---

## Emails

### Send

`from` and `to` are required; provide at least one of `html`, `text`, or `template_id`.

| Key                            | Type               | Notes                                                                        |
| ------------------------------ | ------------------ | ---------------------------------------------------------------------------- |
| `from`                         | `str`              | Verified domain; bare or display-name form.                                  |
| `to` `cc` `bcc` `reply_to`     | `str \| list[str]` | Max 50 each.                                                                 |
| `subject`                      | `str`              |                                                                              |
| `html` / `text`                | `str`              |                                                                              |
| `template_id`                  | `str`              | Saved template.                                                              |
| `variables`                    | `dict`             | Template substitutions (HTML-escaped).                                       |
| `headers`                      | `dict[str, str]`   | No line breaks in names or values.                                           |
| `track_opens` / `track_clicks` | `bool`             | Omit to use your organization default (Settings → General → Email tracking), off unless changed. |
| `attachments`                  | `list[Attachment]` | See below. Up to 20, 10 MB combined.                                         |
| `scheduled_at`                 | `str`              | Future send, ≤ 30 days.                                                      |

### Attachments

Each attachment is a dict. `content` accepts raw `bytes` (base64-encoded for you)
or an already-base64 `str`; alternatively pass `path` (a public URL fetched at
send time). Set `content_id` for an inline `<img src="cid:...">`.

```python
with open("invoice.pdf", "rb") as f:
    eusend.Emails.send({
        "from": "you@yourdomain.com",
        "to": "user@example.com",
        "subject": "Your invoice",
        "html": "<p>Attached.</p>",
        "attachments": [
            {"filename": "invoice.pdf", "content": f.read(), "content_type": "application/pdf"},
        ],
    })
```

### Idempotent sends

Pass an `options` dict with an `idempotency_key` to safely retry without duplicating:

```python
eusend.Emails.send(
    {"from": "you@yourdomain.com", "to": "user@example.com",
     "subject": "Your receipt", "html": "<p>Thanks!</p>"},
    options={"idempotency_key": f"receipt-{order_id}"},
)
```

### Scheduled sends

`scheduled_at` accepts an ISO 8601 string or natural language (`"in 1 hour"`,
`"tomorrow at 9am"`), parsed server-side in UTC.

```python
sent = eusend.Emails.send({
    "from": "you@yourdomain.com", "to": "user@example.com",
    "subject": "Reminder", "html": "<p>Soon.</p>",
    "scheduled_at": "in 1 hour",
})

eusend.Emails.update({"id": sent["id"], "scheduled_at": "in 2 hours"})  # reschedule
eusend.Emails.cancel(sent["id"])                                        # cancel before it sends
```

### Batch

Up to 100 emails in one request. Attachments and scheduling are stripped (not
supported on the batch endpoint). The result maps positionally to the input:
queued items carry `id`, rejected items carry `error` and `code`.

```python
res = eusend.Batch.send([
    {"from": "you@yourdomain.com", "to": "alice@example.com", "subject": "Hi", "html": "<p>Hi</p>"},
    {"from": "you@yourdomain.com", "to": "bob@example.com",   "subject": "Hi", "html": "<p>Hi</p>"},
])
for item in res["data"]:
    print(item.get("id") or f"{item['code']}: {item['error']}")
```

Pass `options={"idempotency_key": ...}` as the second argument to retry a batch
safely. The key is applied per item by position, so a retry must send the items in
the same order.

```python
eusend.Batch.send(emails, options={"idempotency_key": f"digest-{run_id}"})
```

### Retrieve & list

```python
email = eusend.Emails.get("9a8b7c6d-...")
print(email["status"], email["events"][0]["type"])

page = eusend.Emails.list({"limit": 20, "status": "delivered"})
for e in page["data"]:
    print(e["id"], e["subject"])
if page["next_cursor"]:
    page = eusend.Emails.list({"cursor": page["next_cursor"]})
```

Filter by `status`, `from`, `to`. Statuses: `queued` `scheduled` `sending` `sent`
`delivered` `bounced` `complained` `suppressed` `failed`.

---

## Domains

```python
created = eusend.Domains.create("yourdomain.com")
print(created["dkim"]["name"], created["dkim"]["value"])  # DNS records to add
print(created["spf"], created["dmarc"])

eusend.Domains.verify(created["id"])   # after publishing the DNS records
eusend.Domains.list()
eusend.Domains.get(created["id"])
removed = eusend.Domains.remove(created["id"])
print(removed["canceled_scheduled_emails"])  # scheduled emails from the domain are canceled

# Receive mail at any address on in.yourdomain.com: publish the returned MX record.
inbound = eusend.Domains.enable_inbound(created["id"], subdomain="in")
print(inbound["record"])  # {'type': 'MX', 'name': 'in.yourdomain.com', 'value': 'inbound.eusend.dev', 'priority': 10}
eusend.Domains.disable_inbound(created["id"])
```

---

## Inbound

Custom receiving MX records are monitored every five minutes. The workspace owner is emailed
on discovery, confirmed loss, and restoration. Temporary DNS failures do not trigger loss notices.

Every paid workspace receives mail at any address on its own `eusend.app` host, and on the
domains you turn receiving on for. Each message arrives as an `email.received` webhook; fetch
the content with `Inbound.get`.

```python
print(eusend.Inbound.address()["address"])  # anything@3e44228d8f38.eusend.app

page = eusend.Inbound.list({"limit": 20, "order": "asc"})
email = eusend.Inbound.get(page["data"][0]["id"])
print(email["subject"], email["authentication"]["dmarc"]["result"], email["reply_to_email_id"])

pdf = eusend.Inbound.attachment(email["id"], 0)  # bytes
eml = eusend.Inbound.raw(email["id"])  # bytes, message/rfc822
```

Received mail is written by whoever sent it. Check `authentication["dmarc"]` before trusting
`from`, and treat the body as untrusted input.

---

## API keys

```python
key = eusend.ApiKeys.create({"name": "Production"})
print(key["key"])  # eu_live_... — returned only once

eusend.ApiKeys.create({"name": "Sandbox", "test_mode": True})  # eu_test_... key
eusend.ApiKeys.list()                                          # prefixes only
eusend.ApiKeys.remove(key["id"])
```

Emails sent with a test key are accepted and tracked but never delivered.

`permission` defaults to `FULL_ACCESS` — every resource. `SENDING_ACCESS` limits the key to
sending email (plus rescheduling and canceling a scheduled send); every other endpoint,
including reading email logs, returns `403 FORBIDDEN`. Such a key can also be pinned to one
sending domain with `domain_id`, which is rejected on a full-access key.

```python
eusend.ApiKeys.create({
    "name": "Billing service",
    "permission": eusend.SENDING_ACCESS,
    "domain_id": domain_id,  # omit for any verified domain
})
```

Deleting a domain revokes every key restricted to it.

---

## Audiences & contacts

Contact operations are grouped under `Audiences` (they live under a specific audience).

```python
audience = eusend.Audiences.create("Newsletter")

eusend.Audiences.create_contact(
    audience["id"],
    {
        "email": "user@example.com",
        "first_name": "Jane",
        # Custom properties become {{plan}} in a broadcast body.
        "properties": {"plan": "pro"},
    },
)

# Bulk upsert (up to 1,000) → {"count": N}
eusend.Audiences.batch_create_contacts(audience["id"], [
    {"email": "alice@example.com", "first_name": "Alice"},
    {"email": "bob@example.com", "first_name": "Bob"},
])

page = eusend.Audiences.list_contacts(audience["id"], {"subscribed": True, "search": "gmail.com"})
contact = page["data"][0]

eusend.Audiences.update_contact(audience["id"], contact["id"], {"unsubscribed": True})
eusend.Audiences.get_contact(audience["id"], contact["id"])
eusend.Audiences.remove_contact(audience["id"], contact["id"])

eusend.Audiences.list()
eusend.Audiences.get(audience["id"])   # includes contact_count
eusend.Audiences.update(audience["id"], {"name": "Product updates"})
eusend.Audiences.remove(audience["id"])
```

### Contact properties

The custom fields your contacts carry. Declaring one is optional — a property you send on
a contact registers itself as a string — but a declared property can have a type and a
fallback rendered for contacts that have no value of their own.

```python
eusend.ContactProperties.create({"key": "plan", "type": "string", "fallback_value": "free"})

properties = eusend.ContactProperties.list()
eusend.ContactProperties.get(properties[0]["id"])

# The fallback is the only mutable field: key and type are fixed at creation.
eusend.ContactProperties.update(properties[0]["id"], {"fallback_value": "trial"})

# Deletes the definition AND strips the key from every contact. Not undoable.
eusend.ContactProperties.remove(properties[0]["id"])
```

---

## Suppressions

Addresses the account will not send to. Hard bounces and spam complaints are added
automatically; these methods cover the ones you manage yourself. A send to a suppressed
address is skipped and recorded with status `suppressed`; if every recipient is
suppressed the send fails with `ALL_SUPPRESSED`.

Test-mode keys can read the list but not modify it.

```python
# Everything suppressed for a hard bounce, or at one domain
page = eusend.Suppressions.list({"reason": "bounce", "limit": 50})
eusend.Suppressions.list({"email": "@acme.com"})

# Suppress an address. Already suppressed? The existing entry comes back unchanged —
# a manual add never rewrites a real bounce or complaint.
eusend.Suppressions.create({"email": "opted-out@example.com"})

# Import up to 1,000 at a time — do this before your first send when migrating, so
# addresses that already bounced elsewhere don't get a fresh attempt from a new IP.
# (Named import_list because `import` is a Python keyword.)
res = eusend.Suppressions.import_list([
    "one@example.com",
    {"email": "two@example.com", "reason": "complaint"},
])
print(res["count"], res["already_suppressed"], res["duplicates"])

# Un-suppress by entry id or by address
eusend.Suppressions.remove("invalid@example.com")

# The whole list as CSV (bytes)
csv = eusend.Suppressions.export()
```

---

## Reputation

Your bounce and complaint rates exactly as the sending limits judge them: what counted, what did not, and how far you are from a halved daily limit or a pause. Not available to sending-only keys.

```python
r = eusend.Reputation.get()
print(r["state"])  # healthy, warning, limited or paused
nxt = r["next"]
if nxt and nxt["bounces"] is not None and nxt["bounces"] <= 3:
    print(f"{nxt['bounces']} more bounces would move this account to {nxt['state']}")
```

---

## Templates

`{{variable}}` placeholders are substituted at send time; values are HTML-escaped.

```python
tpl = eusend.Templates.create({
    "name": "Welcome email",
    "subject": "Welcome, {{name}}!",
    "html": "<h1>Hi {{name}}</h1><p>Welcome to {{product}}.</p>",
})

eusend.Emails.send({
    "from": "you@yourdomain.com", "to": "user@example.com",
    "template_id": tpl["id"],
    "variables": {"name": "Jane", "product": "Acme"},
})

eusend.Templates.list()
eusend.Templates.get(tpl["id"])
eusend.Templates.update(tpl["id"], {"subject": "New subject"})
html = eusend.Templates.preview(tpl["id"], {"first_name": "Alex"})  # rendered HTML
eusend.Templates.remove(tpl["id"])
```

---

## Webhooks

```python
hook = eusend.Webhooks.create({
    "url": "https://yourapp.com/webhooks/eusend",
    "events": ["email.delivered", "email.bounced", "email.complained"],  # or ["*"]
})
print(hook["secret"])  # signing secret — store it securely; get_secret reads it again

eusend.Webhooks.list()
eusend.Webhooks.get(hook["id"])   # includes recent deliveries
eusend.Webhooks.update(hook["id"], {"events": ["email.bounced"]})
eusend.Webhooks.update(hook["id"], {"enabled": True})  # re-enable a paused or auto-disabled endpoint
eusend.Webhooks.test(hook["id"])  # send a signed webhook.test event
eusend.Webhooks.get_secret(hook["id"])     # {"secret": ...}
eusend.Webhooks.rotate_secret(hook["id"])  # new secret, effective immediately
eusend.Webhooks.remove(hook["id"])
```

Events: `email.sent` `email.delivered` `email.bounced` `email.complained`
`email.opened` `email.clicked` `email.failed` `email.suppressed` `email.received`. The endpoint must be a public `http(s)` URL
returning `2xx` directly (redirects count as failures).

### Verifying signatures

Every delivery is signed with HMAC-SHA256 over `{webhook-id}.{webhook-timestamp}.{body}`:

```python
import base64
import hashlib
import hmac

def verify(headers, body: bytes, secret: str) -> bool:
    signed = f"{headers['webhook-id']}.{headers['webhook-timestamp']}.{body.decode()}"
    mac = hmac.new(secret.encode(), signed.encode(), hashlib.sha256)
    expected = "v1," + base64.b64encode(mac.digest()).decode()
    return hmac.compare_digest(headers["webhook-signature"], expected)
```

---

## Broadcasts

Send one email to every contact in an audience. `{{first_name}}`, `{{last_name}}`,
`{{full_name}}`, and `{{email}}` are available per recipient, and RFC 8058
one-click unsubscribe headers are added automatically.

```python
bc = eusend.Broadcasts.create({
    "name": "May newsletter",
    "audience_id": audience["id"],
    "from": "Sivert <hello@yourdomain.com>",
    "reply_to": "support@yourdomain.com",
    "subject": "May update",
    "html": "<p>Hi {{first_name}}, your monthly update is here...</p>",
})

eusend.Broadcasts.send(bc["id"])                                  # send now
eusend.Broadcasts.send(bc["id"], {"scheduled_at": "2026-06-01T09:00:00Z"})  # or schedule
eusend.Broadcasts.cancel(bc["id"])

eusend.Broadcasts.list()
eusend.Broadcasts.get(bc["id"])   # includes delivery stats
eusend.Broadcasts.update(bc["id"], {"subject": "Updated subject"})
eusend.Broadcasts.remove(bc["id"])
```

Calling `send` on a paused broadcast resumes it from where it stopped.

---

## Error handling

Any non-2xx response raises a subclass of `eusend.EusendError`. Network failures
that never reach the server raise `ApplicationError` (with `status_code == None`).

```python
import eusend
from eusend import EusendError, RateLimitError

try:
    eusend.Emails.send({"from": "you@yourdomain.com", "to": "user@example.com",
                        "subject": "Hi", "html": "<p>Hi</p>"})
except RateLimitError as e:
    print(e.code)         # "MONTHLY_LIMIT_EXCEEDED"
    print(e.status_code)  # 429
except EusendError as e:
    print(e.code, e.message, e.status_code)
```

Exception classes: `MissingApiKeyError`, `InvalidApiKeyError`, `ValidationError`,
`NotFoundError`, `RateLimitError`, `ApplicationError` — all subclasses of
`EusendError`. Branch on `e.code`:

| Code                               | Status | Exception                            |
| ---------------------------------- | ------ | ------------------------------------ |
| `UNAUTHORIZED`                     | 401    | `InvalidApiKeyError`                 |
| `FORBIDDEN`                        | 403    | `EusendError`                        |
| `NOT_FOUND`                        | 404    | `NotFoundError`                      |
| `VALIDATION_ERROR` / `BAD_REQUEST` | 400    | `ValidationError`                    |
| `CONFLICT`                         | 409    | `EusendError`                        |
| `RATE_LIMITED`                     | 429    | `RateLimitError`                     |
| `MONTHLY_LIMIT_EXCEEDED`           | 429    | `RateLimitError`                     |
| `DAILY_LIMIT_EXCEEDED`             | 429    | `RateLimitError`                     |
| `PLAN_LIMIT_EXCEEDED`              | 403    | `EusendError`                        |
| `DOMAIN_NOT_VERIFIED`              | 403    | `EusendError`                        |
| `SENDING_SUSPENDED`                | 403    | `EusendError`                        |
| `LIST_SEND_HELD`                   | 403    | `EusendError`                        |
| `BROADCAST_HELD`                   | 403    | `EusendError`                        |
| `ALL_SUPPRESSED`                   | 422    | `EusendError`                        |
| `SERVICE_PAUSED`                   | 503    | `EusendError`                        |
| `INTERNAL_ERROR`                   | 500    | `ApplicationError`                   |
| `application_error`                | —      | `ApplicationError` (network failure) |

---

## Configuration

```python
import eusend

eusend.api_key = "eu_live_..."             # or EUSEND_API_KEY
eusend.api_url = "https://api.eusend.dev"  # override for testing
```
