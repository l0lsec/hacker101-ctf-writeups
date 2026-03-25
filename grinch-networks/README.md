# Grinch Networks (Hacker101 / Hacky Holidays style)

Large multi-app holiday CTF: **up to 12 objectives** (depending how Hacker101 counts them). Below is a **technique map** plus **example flag bodies** from one solved instance (`https://fe8187457beab040b2fccb13266aa620.ctf.hacker101.com/`). Your hashes will differ on a new instance.

Further reading: [DotSlashTX/h1_Grinch_CTF](https://github.com/DotSlashTX/h1_Grinch_CTF), [Grinch Networks write-up (Medium)](https://10nf0x.medium.com/h1-ctf-grinch-networks-writeup-cb09295c8a74).

---

## Summary table (example instance)

| # | Area | Technique |
|---|------|-----------|
| 1 | `robots.txt` | Read disallowed path + flag in file |
| 2 | `/s3cr3t-ar3a/` | Flag in **`data-info`** on `#alertbox`, set by trojan **`/assets/js/jquery.min.js`** (not in raw HTML) |
| 3 | People Rater | Base64 JSON in `id`; IDOR → `{"id":1}` |
| 4 | Swag Shop | `/swag-shop/api/sessions` → decode sessions; fuzz **`uuid`** + cookie on `/swag-shop/api/user` |
| 5 | Secure login | User enumerate `access` / pass `computer`; forge `securelogin` cookie `admin:true`; ZIP `hahahaha` |
| 6 | My Diary | LFI / filter bypass → `secretadmin.php` via `template=` |
| 7 | Hate Mail | SSTI / template include via preview + admin template name |
| 8 | Forum | OSINT **Grinch-Networks/forum** → `Db.php` creds → phpMyAdmin → crack `grinch` hash → Secret Plans post |
| 9 | Evil Quiz | Session cookie + `/evil-quiz/admin/` (`admin` / `S3creT_p4ssw0rd-$`) |
| 10 | SignUp Manager | README logic; validation bypass (e.g. `age` / field tricks) to become admin |
| 11 | Recon + Attack Box | Nested SQLi on recon album `hash` → SSRF to internal API; creds → login **`POST /attack-box/login/`** → `/attack-box/` |
| 12 | Attack Box DDoS | Signed payload `md5("mrgrinch463"+target)`; **DNS rebinding** (e.g. `08080808.7f000001.rbndr.us`); poll **`/attack-box/launch/<hash>.json?id=`** (not `/attack-box/<hash>.json`). Rate limits may apply. |

---

## Example flag bodies (same instance as above)

```
^FLAG^bdd12bb69dae75aad0fd95a718a38d8ef9b0344e1f59a1928f6e9b46c977dbc6$FLAG$
^FLAG^ec24bf118b7d80020e0610483f87c18c173d2ba4eb893a9f32809df8cfe4396e$FLAG$
^FLAG^8ef545c7c0d5dd3946dd5e6960371f4c581d79b4603c2dd0025a1a37483e9aa1$FLAG$
^FLAG^bd5bf310c42fa1fc5ec84d67da0f8298b88eac13b410bcc878cd74226a754320$FLAG$
^FLAG^8e65e4d5a50d5882bf52aba9bceec38e841d22957083cc118699733f2a4a2612$FLAG$
^FLAG^8020989bb567151edcd37287af1e57a1747e9f0cee8a2f70daf914534c8c5e71$FLAG$
^FLAG^0707ca68c979b06012b06d37e67d1ae10bf7cc5a6d72f83f6d2865d99ca62a18$FLAG$
^FLAG^51383122d6cdcde12f802874c56f61bd8934e2d2ca28307c788c34168219a77a$FLAG$
^FLAG^96eb3f2a7d1402d37c1717d974ba662b19503f1262f313cb8af808313403b37a$FLAG$
^FLAG^10b52f1ffd9628ebb2b65a36b2653a74af89e9cc73cbab8653a4d2cb548a044b$FLAG$
^FLAG^ee8564a98885a857d06ccf3327751c2eced8e151de26d38878410558ac8bd446$FLAG$
```

Flag **12** is returned in the DDoS console JSON stream after a successful rebind-assisted hit; obtain it on your own instance with the steps in row 12 (respect program rules / rate limits).

---

## Notes

- **Forum:** phpMyAdmin user **`forum`**, password from leaked **`models/Db.php`**; **`grinch` / `BahHumbug`** after MD5 crack.
- **Attack Box:** Must use **`POST /attack-box/login/`** so the **`attackbox`** cookie is set; **`POST /attack-box/`** alone may redirect without cookie.
- **Salt for launch payload:** `mrgrinch463` (classic write-up: append test IP to rockyou lines and crack MD5).

---

## Paths (relative to instance root)

- `/robots.txt`, `/s3cr3t-ar3a/`, `/assets/js/jquery.min.js`
- `/people-rater/`, `/swag-shop/api/sessions`, `/swag-shop/api/user`
- `/secure-login/`, `/my_secure_files_not_for_you.zip`, `/my-diary/`
- `/hate-mail-generator/`, `/forum/`, `/forum/phpmyadmin/`
- `/evil-quiz/`, `/signup-manager/`
- `/r3c0n_server_*/`, `/attack-box/login/`, `/attack-box/`, `/attack-box/launch/`
