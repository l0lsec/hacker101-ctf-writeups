# Micro-CMS (Hacker101)

Small CMS with pages, markdown, and a few classic web issues. **Four flags.**

> Replace `BASE` with your instance URL.

---

## 1. Private page — IDOR on **edit**

- `GET BASE/page/7` → **403**
- `GET BASE/page/edit/7` → **200** with editor; the private body contains the flag.

**Why:** View and edit enforce authorization differently.

**Example flag:** `^FLAG^47a7fcd32b1c68c00ddb31eb31d666642508e9e95fb187cfb9b1becf4ac695ca$FLAG$`

---

## 2. XSS in **markdown body**

Create a page whose body includes something like `<img src=x onerror=alert(1)>`. On **view**, a checker simulates an admin and injects the flag into a `flag="..."` attribute on the tag (inspect the DOM / response).

**Example flag:** `^FLAG^a4ca746917354da13a4e367ad2f372576d326da46bace102a5cf7d175d04a1b5$FLAG$`

---

## 3. XSS in **title** (homepage)

The title is escaped on the single-page view but **not** on the home list. Set the title to HTML/JS (e.g. `<script>alert(1)</script>`); the index executes or reflects in a way that surfaces the flag.

**Example flag:** `^FLAG^2ae28e96bd9acfed9107077ec0d490e0ded8787618834e2a1e5c3d0709536a95$FLAG$`

---

## 4. SQL injection on **edit** route

Break the query with a quote in the id:

`GET BASE/page/edit/1'`  
(or `.../page/edit/1%27`)

Error / debug output leaks the flag.

**Example flag:** `^FLAG^fcc0b7d6213046fde9a50eea4bb2c1a6b93d951647fa2121d85d136077072e70$FLAG$`

---

## Quick map

| # | Class | Location |
|---|--------|----------|
| 1 | IDOR | `/page/edit/7` vs `/page/7` |
| 2 | XSS + bot | Body on view |
| 3 | XSS | Title on `/` |
| 4 | SQLi | `/page/edit/<id>'` |

**Example instance:** `https://e719465642bbf603767d789c885eed86.ctf.hacker101.com/`
