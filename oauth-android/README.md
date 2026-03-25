# OAuth (Hacker101 Android)

Same content as the standalone repository [hacker101-oauth-android-ctf](https://github.com/l0lsec/hacker101-oauth-android-ctf); duplicated here for the monorepo index.

**Base URL (example):** `https://ccc6741428256094a4547cd2602c9b2d.ctf.hacker101.com/`  
**Artifact:** `oauth.apk`

---

## Summary

| Flag | Idea |
|------|------|
| 1 | OAuth authorization page leaks the token in the redirect URL query string. |
| 2 | `WebView` exposes `getFlagPath()` via `@JavascriptInterface`; a small VM derives a secret `.html` path. |

---

## Flag 1 — Token in the authorize link

`MainActivity` opens `/oauth?redirect_url=…&response_type=token&scope=all`.

Request:

```text
GET /oauth?redirect_url=https%3A%2F%2Fexample.com%2F&response_type=token&scope=all
```

The HTML link’s `href` includes `?token=` — the token value is flag 1.

---

## Flag 2 — JavaScript bridge

`Browser` registers `WebAppInterface` as `iface`. `getFlagPath()` runs bytecode derived from an `int[]` (with `R.styleable` constants) and returns `*.html`.

Emulate the VM offline or call from JS on `/authed`, then:

```text
GET /<derived-hex>.html
```

**Example derived filename (one instance):** `48ce217fea4529a070a9d3e3c87db512b1596d413e580f7b2e1eab65f3948ab8.html`

---

## Tools

**jadx**, **curl**, optional **Python** for the VM.

---

## Mitigations

Use authorization code + PKCE instead of implicit tokens in URLs; restrict `WebView` JS bridges; do not rely on client-side obfuscation for secrets.
