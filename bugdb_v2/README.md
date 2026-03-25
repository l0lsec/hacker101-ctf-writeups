# BugDB v2 (Hacker101)

GraphQL bug tracker (GraphiQL at **`/graphql`**). Like [BugDB v1](../bugdb_v1/), but **users and bugs are listed separately**, and **private bugs are omitted** from `allBugs` until you change them.

> Replace `BASE` with your instance (e.g. `https://<id>.ctf.hacker101.com`).

| Flag | Directory |
|------|-----------|
| 0 | [flag0](flag0/) |

---

## Quick map

| # | Idea |
|---|------|
| 0 | `allBugs` only shows **non-private** rows at first; use **`modifyBug`** to flip **`private`** on the hidden bug (typically id **`2`**), then re-query `allBugs` for the flag in **`text`**. |

**Example instance:** `https://f12add6383c9d337e203a4feb230035d.ctf.hacker101.com/`

---

## License

Challenge content is © HackerOne / Hacker101. These notes are for education only.
