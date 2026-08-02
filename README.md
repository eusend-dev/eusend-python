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

| Key | Type | Notes |
|-----|------|-------|
| `from` | `str` | Verified domain; bare or display-name form. |
| `to` `cc` `bcc` `reply_to` | `str \| list[str]` | Max 50 each. |
| `subject` | `str` | |
| `html` / `text` | `str` | |
| `template_id` | `str` | Saved template. |
| `variables` | `dict` | Template substitutions (HTML-escaped). |
| `headers` | `dict[str, str]` | No line breaks in names or values. |
| `track_opens` / `track_clicks` | `bool` | Default `True`. |
| `attachments` | `list[Attachment]` | See below. Up to 20, 10 MB combined. |
| `scheduled_at` | `str` | Future send, ≤ 30 days. |

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
eusend.Domains.remove(created["id"])
```

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

---

## Audiences & contacts

Contact operations are grouped under `Audiences` (they live under a specific audience).

```python
audience = eusend.Audiences.create("Newsletter")

eusend.Audiences.create_contact(audience["id"], {"email": "user@example.com", "first_name": "Jane"})

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
eusend.Audiences.remove(audience["id"])
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
eusend.Templates.remove(tpl["id"])
```

---

## Webhooks

```python
hook = eusend.Webhooks.create({
    "url": "https://yourapp.com/webhooks/eusend",
    "events": ["email.delivered", "email.bounced", "email.complained"],  # or ["*"]
})
print(hook["secret"])  # signing secret — returned only once

eusend.Webhooks.list()
eusend.Webhooks.get(hook["id"])   # includes recent deliveries
eusend.Webhooks.update(hook["id"], {"events": ["email.bounced"]})
eusend.Webhooks.remove(hook["id"])
```

Events: `email.sent` `email.delivered` `email.bounced` `email.complained`
`email.opened` `email.clicked`. The endpoint must be a public `http(s)` URL
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

| Code | Status | Exception |
|------|--------|-----------|
| `UNAUTHORIZED` | 401 | `InvalidApiKeyError` |
| `FORBIDDEN` | 403 | `EusendError` |
| `NOT_FOUND` | 404 | `NotFoundError` |
| `VALIDATION_ERROR` / `BAD_REQUEST` | 400 | `ValidationError` |
| `CONFLICT` | 409 | `EusendError` |
| `RATE_LIMITED` | 429 | `RateLimitError` |
| `MONTHLY_LIMIT_EXCEEDED` | 429 | `RateLimitError` |
| `DAILY_LIMIT_EXCEEDED` | 429 | `RateLimitError` |
| `PLAN_LIMIT_EXCEEDED` | 403 | `EusendError` |
| `DOMAIN_NOT_VERIFIED` | 403 | `EusendError` |
| `SENDING_SUSPENDED` | 403 | `EusendError` |
| `LIST_SEND_HELD` | 403 | `EusendError` |
| `BROADCAST_HELD` | 403 | `EusendError` |
| `ALL_SUPPRESSED` | 422 | `EusendError` |
| `SERVICE_PAUSED` | 503 | `EusendError` |
| `INTERNAL_ERROR` | 500 | `ApplicationError` |
| `application_error` | — | `ApplicationError` (network failure) |

---

## Configuration

```python
import eusend

eusend.api_key = "eu_live_..."             # or EUSEND_API_KEY
eusend.api_url = "https://api.eusend.dev"  # override for testing
```
