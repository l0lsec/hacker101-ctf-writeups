# Intentional Exercise — Hacker101 Android (Level 13)

WebView loads **`/appRoot`** on the challenge host. The server checks a **SHA-256** query parameter built from a **hard-coded secret** in the APK plus a **path suffix**. **One flag** (Hacker101 lists this challenge as a single-flag objective).

**Example instance:** `https://ec1110c74428b27df25130228307bfd4.ctf.hacker101.com/`  
**APK:** `level13.apk` (the site may show *“APK is building”* until you **`POST /build`** once with `url=<this page>` from the inline script, then refresh).

---

## What the app does (`com.hacker101.level13.MainActivity`)

1. Base URL: `https://<host>/appRoot`.
2. If the activity was opened with **`Intent` data** (deep link), it sets  
   `strSubstring = data.toString().substring(28)`  
   and appends that to the base URL. The magic number **28** matches the length of the **default intent URL** in the manifest (e.g. `http://level13.hacker101.com` — no path), so the remainder is often **`/flagBearer`** when you use a deep link like `http://level13.hacker101.com/flagBearer`.
3. Ensures **`?`** is present, then appends **`&hash=`** where  
   **`hash = SHA-256( UTF-8("s00p3rs3cr3tk3y") || UTF-8(strSubstring) )`**  
   as a **64-hex-character** string (`MessageDigest` + `BigInteger` formatting in code).

Default launch (no path): `strSubstring` is empty → hash is **`SHA-256("s00p3rs3cr3tk3y")`**.

---

## Solve (forge the hash — works on any host shape)

1. Decompile the APK (**jadx**) and read **`MainActivity`**: recover the secret **`s00p3rs3cr3tk3y`**.
2. From the **`/appRoot`** page, follow the **Flag** link target: **`appRoot/flagBearer`** → full path suffix **`/flagBearer`**.
3. Compute:

   ```text
   hash = SHA256( "s00p3rs3cr3tk3y" + "/flagBearer" )
   ```

   (Same as `update(secret); update(suffix);` in Java.)

4. Request:

   ```text
   GET https://<host>/appRoot/flagBearer?&hash=<64-hex>
   ```

**Example flag (one instance):**  
`^FLAG^ba1c374dc2b54ab8eba7265b6adb50ad217b704b2420ca7d2735de97fad44f59$FLAG$`

### One-liner

```bash
BASE="https://YOUR_INSTANCE.ctf.hacker101.com"
H=$(python3 -c "import hashlib;print(hashlib.sha256(b's00p3rs3cr3tk3y'+b'/flagBearer').hexdigest())")
curl -sS "$BASE/appRoot/flagBearer?&hash=$H"
```

---

## Alternate solve (deep link)

Launch the activity with an intent whose **string form** is exactly **28 characters** before **`/flagBearer`**, so `substring(28)` is **`/flagBearer`** and the app computes the same hash as above. On older builds this was often:

```bash
adb shell am start -a android.intent.action.VIEW \
  -d "http://level13.hacker101.com/flagBearer" com.hacker101.level13
```

Your manifest / host may differ; if the prefix length is not 28, use the **forged hash** method instead.

---

## Tools

**jadx**, **curl**, **Python** (`hashlib`).

---

## References

- [Hacker101 Android challenge write-ups (Intentional Exercise)](https://infosecwriteups.com/hacker101-ctf-android-challenge-writeups-f830a382c3ce) — same core idea (secret + `/flagBearer`, optional deep link).
