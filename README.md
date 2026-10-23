# api-v3-client-python

Sample code for authenticating with the BTC Markets API v3. Tested on Python 3.12.

BTC Markets supports two authentication schemes:

* **Ed25519** (recommended). You hold a private key; BTC Markets holds only the matching
  public key. Each request is signed as a short-lived JWT, so nothing you send can be
  reused for any other request.
* **HMAC**. A shared secret, known to both you and BTC Markets, signs each request.
  Existing integrations use this; new ones should use Ed25519.

| File | What it shows |
| --- | --- |
| `auth.py` | How a request is signed under each scheme (`Ed25519Auth`, `HmacAuth`). This is the part to port to your own code. |
| `btcmarkets_client.py` | A minimal HTTP client that attaches the auth headers. |
| `main.py` | Reads your credentials from the environment and calls the API. |
| `generate_key.py` | Only for option B below: generate your own Ed25519 key pair. |

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Ed25519

### Step 1: get a key pair

Pick one of the two options.

**Option A: let BTC Markets generate the key pair.** On the BTC Markets website, create
an API key with the Ed25519 type. You are shown the API key id (`btcm_...`) and your
private key. Save the private key securely; it is shown only once.

**Option B: generate the key pair yourself.** Only the public key is ever sent to
BTC Markets.

```bash
python generate_key.py btcmarkets_ed25519.pem
```

This writes your private key to `btcmarkets_ed25519.pem` (readable only by you) and
prints your public key as a JWK:

```json
{"kty": "OKP", "crv": "Ed25519", "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo"}
```

On the BTC Markets website, create an API key with the Ed25519 type and paste that
public key. You are shown the API key id (`btcm_...`).

Either way, never share your private key with anyone, including BTC Markets, and never
commit it to source control.

### Step 2: call the API

```bash
export BTCMARKETS_API_KEY=btcm_...                                # your API key id
export BTCMARKETS_PRIVATE_KEY="$(cat btcmarkets_ed25519.pem)"    # or paste the key shown by the website
python main.py
```

### How a request is signed

See `Ed25519Auth` in `auth.py`. Each request carries `Authorization: Bearer <jwt>`,
a JWT signed with your private key that is valid for this one request only:

| | Value |
| --- | --- |
| header | `{"alg": "EdDSA", "typ": "JWT", "kid": "<your API key id>"}` |
| `iss` | `btcm-developer-platform` |
| `aud` | the API host, `api.btcmarkets.net` |
| `iat`, `exp` | issued-at and expiry, in seconds. `exp - iat` must be at most 60 |
| `jti` | a unique id for this token |
| `uri` | `"<METHOD> <host><path>"`, e.g. `"POST api.btcmarkets.net/v3/orders"`. Upper-case method, no query string, no trailing slash |
| `body_hash` | SHA-256 of the exact request body as sent, lowercase hex. Omitted when there is no body |

Keep your clock synchronised (NTP): a token issued in the future or already expired is
rejected.

## HMAC

```bash
export BTCMARKETS_AUTH_METHOD=HMAC
export BTCMARKETS_API_KEY=...          # your API key
export BTCMARKETS_PRIVATE_KEY=...      # your base64-encoded API private key
python main.py
```

See `HmacAuth` in `auth.py`: the signature is HMAC-SHA512 over
`method + path + timestamp_ms + body`, sent in the `BM-AUTH-APIKEY`,
`BM-AUTH-TIMESTAMP` and `BM-AUTH-SIGNATURE` headers.
