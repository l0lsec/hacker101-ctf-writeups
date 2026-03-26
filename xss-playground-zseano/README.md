# XSS Playground by zseano (Hacker101)

Profile-style app with feedback, comments, reporting, and client-side scripts. The modal lists **many** XSS objectives (reflective, stored, DOM, CSP bypass, and **one** “leak something”). This note documents the **email / flag leak** via the **`getemail`** API, matching [8r0wn13’s walkthrough](https://github.com/8r0wn13/hacker101_ctf/blob/main/XSS%20Playground%20by%20zseano.md).

> Replace `BASE` with your instance, e.g. `https://cf6e6e2d6df8b0232db7a71eed2ef432.ctf.hacker101.com`.

---

## Leaking the email + flag (`getemail`)

### Where the secret header comes from

Open **`/custom.js`** (linked from the profile page). The minified code defines **`retrieveEmail`** and sets:

`X-SAFEPROTECTION: enNlYW5vb2Zjb3Vyc2U=`

That value is Base64 for **`zseanoofcourse`** (`printf 'zseanoofcourse' | base64`).

The same script uses that header on other `api/action.php` calls (e.g. **`editbio`**).

### Request shape

`GET BASE/api/action.php?act=getemail` with header **`X-SAFEPROTECTION: enNlYW5vb2Zjb3Vyc2U=`**.

On some stacks, **HTTP/2** normalizes header names (e.g. to title case). The backend may expect the exact casing **`X-SAFEPROTECTION`**, so tools that alter casing can break the check. Forcing **HTTP/1.1** avoids that (as noted in [8r0wn13’s write-up](https://github.com/8r0wn13/hacker101_ctf/blob/main/XSS%20Playground%20by%20zseano.md)).

```bash
curl -sS --http1.1 "$BASE/api/action.php?act=getemail" \
  -H 'X-SAFEPROTECTION: enNlYW5vb2Zjb3Vyc2U='
```

**Example (this instance):** JSON includes email and flag:

`^FLAG^dee5022e8ceb9c164abf2f3c23e9d7dd4be95899d6b1d985f0426bb04044e47e$FLAG$`

*(Some deployments return JSON with a truncated flag suffix; append **`$FLAG$`** if needed, per the reference notes.)*

---

## Broader challenge (XSS checklist)

The in-app modal asks for **5 reflective**, **3 stored**, **2 DOM-based**, **1 CSP-bypass**, and **1 leak** — mostly discovered by testing **URL parameters**, **hash fragments**, **feedback**, **comments**, **report user**, and **`custom.js`** DOM sinks (e.g. `document.write` / `innerHTML` patterns). Treat the rest as deliberate hunting rather than a single scripted solve.

---

## Quick map

| Goal | Idea |
|------|------|
| Leak email + flag | `GET api/action.php?act=getemail` + **`X-SAFEPROTECTION`** + prefer **`curl --http1.1`** |
| Find header value | Read **`/custom.js`** (`retrieveEmail` / `editProfile`) |

---

## License

Challenge content is © HackerOne / Hacker101 / contributors. These notes are for education only.
