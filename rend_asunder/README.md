# Rend Asunder (Hacker101)

Headless-browser style challenge: you submit JavaScript that runs in a sandboxed context; the server renders the result as an image. **Three flags** on a full run.

> Replace `BASE` with your instance URL (`https://<id>.ctf.hacker101.com/`).

This repo documents **Flag 0** only. Flags **1** and **2** were not completed here.

| Flag | Status | Write-up |
|------|--------|----------|
| 0 | Documented | [flag0](flag0/) |
| 1 | Not pursued | *(hint: the rendered page looks a bit odd)* |
| 2 | Not pursued | — |

---

## Quick context

- The UI is a **Script** box (POST to `saveScript`) and a **Rendered** preview (`GET image`).
- Your code can use the DOM and `XMLHttpRequest` (including synchronous calls to `http://localhost/…` from the server’s perspective).
- Flag 0 is solved by **inspecting the page you actually have in the browser**, not only what you see in the textarea.

---

## License

Challenge content is © HackerOne / Hacker101. These notes are for education only.
