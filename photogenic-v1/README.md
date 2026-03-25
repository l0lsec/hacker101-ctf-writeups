# Photogenic v1 (Hacker101 Level 0)

## Idea

The landing page looks empty except for a welcome line. The real hint is in the **CSS**: a `background-image` points at `background.png`.

## Solve

1. View page source and note `url("background.png")`.
2. Request `GET /background.png` on the same host.

The response is **not** a real PNG; the body is a short text line containing the flag (`^FLAG^…$FLAG$`).

## Example instance (historical)

- Host: `https://e50989beb1a6b06f4326cbfec25feb3c.ctf.hacker101.com/`
- Flag body from that run: `^FLAG^1a25446edf837ead6ef30d4659a64f28eadcc42369762e885bce4705e298d7fc$FLAG$`

## Takeaway

Follow every asset URL referenced by the app; “image” paths are not always images.
