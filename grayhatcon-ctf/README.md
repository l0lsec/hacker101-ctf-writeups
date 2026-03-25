# Grayhatcon CTF / HackerBay (Hacker101)

Auction site themed as **HackerBay**. Recon surfaces a hidden admin path, **IP-based access control** that trusts client-supplied forwarding headers, **password-reset leaks**, and **extra registration / sub-user parameters** that are not shown on the default form.

> Replace `BASE` with your instance (e.g. `https://<id>.ctf.hacker101.com`).  
> Example: `https://bddae40402773c77b30d51778f97c09e.ctf.hacker101.com/`

Community walkthrough: [8r0wn13 — Grayhatcon CTF.md](https://github.com/8r0wn13/hacker101_ctf/blob/main/Grayhatcon%20CTF.md) · [raw](https://raw.githubusercontent.com/8r0wn13/hacker101_ctf/main/Grayhatcon%20CTF.md).

---

## Flag 1 — Hidden directory + IP allowlist bypass

1. **`GET /robots.txt`** disallows **`s3cr3t-4dm1n/`** (or fuzz common files from the site root).
2. **`GET /s3cr3t-4dm1n/`** returns **403** from Apache-style rules.
3. With a spoofed client IP header allowed by **`.htaccess`** in that folder, the admin UI loads. Fetch the config:

```bash
curl -sS -H 'X-Forwarded-For: 8.8.8.8' "$BASE/s3cr3t-4dm1n/.htaccess"
# Allow from 8.8.8.8
# Allow from 8.8.4.4
```

4. Repeat the same header on the directory (or **`X-Real-IP`** if the app honors it) to load the admin login page; the flag is shown in the page body.

```bash
curl -sS -H 'X-Forwarded-For: 8.8.8.8' "$BASE/s3cr3t-4dm1n/" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example (this instance):** `^FLAG^0e4437e5917277dc7e9d374398b39831388db0020bee3ffcb40a11eb96b1338d$FLAG$`

---

## Flag 2 — “Registration form might have fields you missed”

### A) `account_hash` from password reset (classic flow)

1. **`POST /reset`** with `username=hunter2` (only username on the first step).
2. The next page includes a **hidden** `account_hash` tied to that account (value varies by deployment; it is **not** on the initial register form).
3. **`POST /register`** with body parameters:

   `account_hash=<leaked_value>&new_username=<you>&new_password=<you>`

   This attaches the new user to the victim account (see [8r0wn13](https://github.com/8r0wn13/hacker101_ctf/blob/main/Grayhatcon%20CTF.md)). On many instances the flag appears after **login** on the dashboard.

### B) `owner_hash` on register (same hint, alternate parameter)

Some deployments also honor **`owner_hash=<victim account hash>`** on **`POST /register`** (the victim hash is the same value leaked as `account_hash` from the reset flow). The response may be an **“Awaiting Activation”** page that includes the flag.

```bash
curl -sS -L -X POST "$BASE/register" \
  -d 'owner_hash=cf505baebbaf25a0a4c63eb93331eb36&new_username=u1&new_password=pass12345' \
  | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example flag from (B) on this instance:** `^FLAG^2f3bbc4e6a3bca35b68d044126df4495dc5cc03887886b294520a3348f826e38$FLAG$`

*(The `cf505bae…` value above is the `account_hash` for `hunter2` on this instance, obtained via the reset flow.)*

---

## Further flags (sub-users, SSRF-ish logic, etc.)

The Hacker101 Grayhatcon track has **more flags** than the two above. The [8r0wn13 write-up](https://github.com/8r0wn13/hacker101_ctf/blob/main/Grayhatcon%20CTF.md) continues with:

- Enabling **sub-users**, then **tampering** the “create subuser” request: supply **`hash=`** (a target subuser row), **`owner_hash=`** (victim owner), **`enable_toggle=enable`**, and (in the original Burp recipe) **adjusting the session / `userhash` cookie** across two forwarded requests so the server accepts the owner check while still enabling the victim’s disabled subuser—then **log in as that subuser** for the next flag.
- Additional steps (parameters such as **`verbose`**, other admin-only paths, etc.) as in the linked guide.
- The same notes mention a **later flag was broken** on their run; if you hit a dead end, try a fresh instance or check for errata.

Work through the rest on your deployment with Burp (Intercept) or a scripted client that can replay **paired** requests with different cookies.

---

## Quick map

| Step | Idea |
|------|------|
| 1 | **`robots.txt`** → **`/s3cr3t-4dm1n/`** → read **`.htaccess`** with spoofed IP → browse admin UI with same header |
| 2 | **`POST /reset`** → leak **`account_hash`** → **`POST /register`** with extra **`account_hash`** and/or **`owner_hash`** |
| 3+ | Sub-user **feature toggle**, **create** + **enable** parameter abuse, follow [8r0wn13](https://github.com/8r0wn13/hacker101_ctf/blob/main/Grayhatcon%20CTF.md) |

---

## License

Challenge content is © HackerOne / Hacker101. These notes are for education only.
