# Senrex 赛恩力 — Tianchang Xianrui New Energy Technology Co., Ltd.

Bilingual (English / 中文) product website: portable power stations, 48V/60V/72V lithium battery packs,
solar storage systems & inverters, and AC/TV remote controls.

- Pages: `index.html`, `products.html`, `about.html`, `contact.html` (static, works on GitHub Pages)
- Inquiry form prepares a draft addressed to 834645912@qq.com in the visitor’s email app; WhatsApp +86 190 1805 6828
- To add or edit products: change `data/products.json`, add photos under `assets/img/`, then run
  `python3 tools/build_site.py` and commit.

## Admin (edit without code)
Open `admin.html` (or tap the logo 3 times on the home page). First time: paste a GitHub fine-grained token
(repo junaed9156/Senrex, Contents: Read and write) and choose an admin password; the token is stored encrypted
in `data/admin.json`. Edits are saved to `data/products.json` and `data/site.json`; the workflow
`.github/workflows/rebuild.yml` then rebuilds the pages automatically (about 1–2 minutes).
