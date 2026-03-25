# Thermostat (Hacker101 Android)

Two flags embedded in the APK logic; no separate server flag hunt required for this level.

> **Instance example:** `https://66a1cdd3e918928a1ceb195b75d1118c.ctf.hacker101.com/` — artifact **`thermostat.apk`**.

---

## Approach

1. Download **`thermostat.apk`** from the challenge host.
2. Decompile with **jadx** (or **apktool** + smali).
3. Open **`com.hacker101.level11.PayloadRequest`**. Both flag strings live in that class.

---

## Protocol detail

The app **POST**s to the same host with:

- Form field **`d`**: Base64(JSON payload).
- Header **`X-MAC`**: Base64(MD5(`<secret>` + `<same Base64 string as d>`)).
- Header **`X-Flag`**: static string (second flag).

The **first flag string** is the **key material** fed to `MessageDigest` before the payload Base64 (MAC prefix). The **second** is exactly the **`X-Flag`** header value.

---

## Example flags (that build)

```
^FLAG^ac95bb7ecd0ed56ddeb9a12efc69ce42e6a5485aebf39d0a57190223f58e0cba$FLAG$
^FLAG^2315b1a01466bc2f243841711d65d1d7cbf1341430fa393173f966aa13924da2$FLAG$
```

---

## Optional sanity check

With the recovered secret as the MAC prefix and a body like `{"cmd":"getTemp"}`, compute **`X-MAC`** the same way the app does and POST; the server returns Base64 JSON (e.g. temperature). That confirms the extracted strings; responses do not add a third flag on this build.

---

## Tools

**jadx**, **curl** (optional replay), **Python** (optional MAC verification).
