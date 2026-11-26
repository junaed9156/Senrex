"""Builds the static Senrex website from data/products.json.

Usage:  python3 tools/build_site.py
To add or change products, edit data/products.json (and put photos in assets/img/...),
then run this script again and commit the generated .html files.
"""
import json, html, os, urllib.parse
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'data', 'products.json'), encoding='utf-8'))
_site_path = os.path.join(ROOT, 'data', 'site.json')
SITE = json.load(open(_site_path, encoding='utf-8')) if os.path.exists(_site_path) else {}
TEXTS = SITE.get('texts', {})      # {english default: {"en": ..., "zh": ...}} edited in admin
IMAGES = SITE.get('images', {})    # {default path: new path} edited in admin
CATALOG = {}                       # every bilingual text used, written for the admin page
_news_path = os.path.join(ROOT, 'data', 'news.json')
NEWS = (json.load(open(_news_path, encoding='utf-8')) if os.path.exists(_news_path) else {}).get('posts', [])
NEWS = sorted([n for n in NEWS if not n.get('hidden')], key=lambda n: n.get('date', ''), reverse=True)

def img(path):
    return IMAGES.get(path) or path

def pimg(kind, f):
    return f if '/' in f else f'assets/img/{kind}/{f}'

def thumb(src, width=480):
    """Small copy of a product photo for the list pages (the full photo still opens in the pop-up)."""
    full = os.path.join(ROOT, src)
    if not os.path.exists(full) or not src.startswith('assets/img/'):
        return src
    out_rel = 'assets/img/thumbs/' + src[len('assets/img/'):]
    out = os.path.join(ROOT, out_rel)
    try:
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(full):
            os.makedirs(os.path.dirname(out), exist_ok=True)
            im = Image.open(full)
            im.thumbnail((width, width * 2), Image.LANCZOS)
            if src.lower().endswith(('.jpg', '.jpeg')):
                im.convert('RGB').save(out, 'JPEG', quality=78, optimize=True, progressive=True)
            elif src.lower().endswith('.webp'):
                im.save(out, 'WEBP', quality=80, method=6)
            elif src.lower().endswith('.png'):
                im.save(out, 'PNG', optimize=True)
            else:
                return src
        return out_rel if os.path.getsize(out) < os.path.getsize(full) else src
    except Exception:
        return src

CO_DEFAULT = {
    'en': 'Tianchang Xianrui New Energy Technology Co., Ltd.',
    'zh': '天长市先锐新能源科技有限公司',
    'contact_en': 'Mr. Liu Xianguo', 'contact_zh': '刘先国',
    'mobile': '+86 190 1805 6828', 'wa': '8619018056828',
    'tel': '0550 7702777', 'tel_link': '+865507702777',
    'email': '834645912@qq.com', 'web': 'www.senrex.cc',
    'addr_zh': '安徽省天长市经济开发区经十三路天盛智谷产业园A1-4栋',
    'addr_en': 'Building A1-4, Tiansheng Zhigu Industrial Park, Jing 13th Road, Economic Development Zone, Tianchang City, Anhui Province, China',
    'ceo_name': 'Jack Liu', 'ceo_mobile': '+86 158 5501 5888', 'ceo_wa': '8615855015888', 'ceo_wechat': '15855015888', 'ceo_email': 'Jack@senrex.cc',
    'ceo2_name': 'Jason Liu', 'ceo2_name_zh': '刘先国', 'ceo2_mobile': '+86 131 3550 7999', 'ceo2_wa': '8613135507999', 'ceo2_wechat': '13135507999', 'ceo2_email': 'Jason@senrex.cc',
}
CO = dict(CO_DEFAULT, **{k: v for k, v in SITE.get('company', {}).items() if v})
WA_LINK = 'https://wa.me/' + CO['wa']
import hashlib
def _ver(*paths):
    h = hashlib.md5()
    for p in paths:
        try: h.update(open(os.path.join(ROOT, p), 'rb').read())
        except Exception: pass
    return h.hexdigest()[:8]
VER = _ver('assets/css/style.css', 'assets/css/alpine.css', 'assets/js/main.js', 'data/products.json', 'data/site.json')
CERTGRID_HTML = '<div class="certgrid">' + ''.join(f'<img src="{thumb(img(f"assets/img/certs/cert{i}.jpg"))}" data-full="{img(f"assets/img/certs/cert{i}.jpg")}" alt="Inspection report {i}" loading="lazy" data-zoom>' for i in range(1, 6)) + '</div>'

def e(s):
    return html.escape(str(s))

def t(en, zh, tag='span'):
    key = en
    CATALOG.setdefault(key, {'en': en, 'zh': zh})
    o = TEXTS.get(key) or {}
    en, zh = o.get('en') or en, o.get('zh') or zh
    return f'<{tag} class="en">{en}</{tag}><{tag} class="zh">{zh}</{tag}>'

def wa(text, number=None):
    return 'https://wa.me/' + (number or CO['wa']) + '?text=' + urllib.parse.quote(text)

def wa_remote(text):
    # Remote control inquiries go to the remote control business (Jason Liu)
    return wa(text, CO['ceo2_wa'])

WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7a2.8 2.8 0 0 0 1.8-1.3 2.3 2.3 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg>'
MAIL_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm1 2.4V17h16V7.4l-8 5.3-8-5.3zM5.4 7 12 11.4 18.6 7H5.4z"/></svg>'

CATS = [
    ('power', 'Portable Power Stations', '便携式储能电源', 'Outdoor & home backup power, 150W to 11,000W, NMC and LiFePO4.', '户外及家庭备用电源，150W–11000W，三元锂 / 磷酸铁锂。', 'assets/img/showcase/power.webp'),
    ('battery', 'Lithium Battery Packs', '动力锂电池组', '48V / 60V / 72V packs from 12Ah to 230Ah, NMC and LiFePO4.', '48V / 60V / 72V，12Ah–230Ah，三元锂 / 磷酸铁锂。', 'assets/img/showcase/battery.webp'),
    ('solar', 'Solar Storage & Inverters', '光储一体机与逆变器', 'GSL-LinkI all-in-one systems, GBP-Pro I batteries, GST hybrid inverters and portable folding solar panels.', 'GSL-LinkI 光储一体机、GBP-Pro I 低压电池、GST 逆变器及便携式折叠太阳能板。', 'assets/img/showcase/solar.webp'),
    ('remote', 'Remote Controls', '遥控器', 'Replacement AC and TV remotes for all major brands.', '各大品牌空调与电视替换遥控器。', 'assets/img/showcase/remote.webp'),
]
COUNTS = {'power': len(D['power']), 'battery': len(D['battery']), 'solar': len(D['solar']),
          'remote': sum(len(r['models']) for r in D['remote'])}
TOTAL = sum(COUNTS.values())

# Closely spaced silhouettes give the original mark a visible edge as it turns.
LOGO_EDGES = ''.join(f'<i style="--depth:{z}px"></i>' for z in range(-3, 4))

def head(title_en, page, desc='Senrex lithium battery factory: portable power stations, 48V/60V/72V lithium battery packs, solar storage systems, inverters and remote controls. Wholesale and export.'):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title_en)} | Senrex 赛恩力</title>
<meta name="description" content="{e(desc)}">
<link rel="icon" href="assets/img/logo_mark.png">
<link rel="stylesheet" href="assets/css/style.css?v={VER}">
<link rel="stylesheet" href="assets/css/alpine.css?v={VER}">
<script>try{{var l=localStorage.getItem('senrex-lang');if(!l){{l=(navigator.language||'').toLowerCase().indexOf('zh')===0?'zh-CN':'en'}}document.documentElement.lang=l}}catch(e){{}}</script>
</head>
<body data-page="{page}">
<div class="top"><div class="wrap">
  <a href="tel:{CO['tel_link']}">☎ {CO['tel']}</a>
  <a href="https://wa.me/{CO['ceo_wa']}" target="_blank" rel="noopener">WhatsApp {e(CO['ceo_name'].split()[0])} {CO['ceo_mobile']}</a>
  <a href="https://wa.me/{CO['ceo2_wa']}" target="_blank" rel="noopener">WhatsApp {e(CO['ceo2_name'].split()[0])} {CO['ceo2_mobile']}</a>
  <a href="mailto:{CO['ceo_email']}">✉ {CO['ceo_email']}</a>
  <a href="mailto:{CO['ceo2_email']}">✉ {CO['ceo2_email']}</a>
  <a href="mailto:{CO['email']}">✉ {CO['email']}</a>
</div></div>
<header class="nav"><div class="wrap">
  <a class="brand" href="index.html"><span class="brand-depth" aria-hidden="true"><img src="{img('assets/img/logo_mark.png')}" width="158" height="160" alt="">{LOGO_EDGES}</span><span><b>SENREX</b><small>{t('Xianrui New Energy','先锐新能源')}</small></span></a>
  <nav class="menu" id="menu">
    <a href="index.html" data-p="home">{t('Home','首页')}</a>
    <a href="products.html" data-p="products">{t('Products','产品中心')}</a>
    <a href="news.html" data-p="news">{t('News','新闻动态')}</a>
    <a href="about.html" data-p="about">{t('About Us','关于我们')}</a>
    <a href="contact.html" data-p="contact">{t('Contact','联系我们')}</a>
    <div class="lang"><button data-l="en">EN</button><button data-l="zh-CN">中文</button></div>
  </nav>
  <button class="burger" id="burger" aria-label="Menu">☰</button>
</div></header>
'''

def inquiry_form(prefill_id='inq'):
    line_options = ''.join(f'<option value="{en}">{en} / {zh}</option>' for _, en, zh, *_ in CATS)
    def field(name, en, zh, attrs='', tag='input', options=''):
        field_id = f'{prefill_id}-{name}'
        control = f'<{tag} id="{field_id}" name="{name}" {attrs}>'
        if tag != 'input':
            control += options + f'</{tag}>'
        return f'<div class="field"><label for="{field_id}">{t(en, zh)}</label>{control}</div>'

    empty = '<option value="">—</option>'
    name = field('name', 'Your name *', '您的姓名 *', 'autocomplete="name" required')
    email = field('email', 'Email address *', '电子邮箱 *', 'type="email" autocomplete="email" required')
    message = field('message', 'What do you need? *', '您的需求 *', 'rows="4" required', tag='textarea')
    company = field('company', 'Company', '公司名称', 'autocomplete="organization"')
    phone = field('phone', 'Mobile number / WhatsApp', '手机号码 / WhatsApp', 'type="tel" autocomplete="tel" placeholder="+86 138 0000 0000"')
    country = field('country', 'Country', '国家', 'class="country-select"', tag='select', options=empty)
    quantity = field('quantity', 'Order quantity', '采购数量')
    line = field('product_line', 'Product line', '产品线', tag='select', options=empty + line_options)
    model = field('product', 'Model', '型号', 'placeholder="48V100Ah"')
    return f'''<form class="inq" id="{prefill_id}" novalidate>
  <div class="inquiry-intro"><span class="mail-seal" aria-hidden="true">{MAIL_SVG}</span>
    <div><h2 id="{prefill_id}-title">{t('Request a quotation', '获取报价')}</h2><p>{t('Tell our sales team what you’re sourcing and when you need it.', '告诉销售团队您想采购的产品及交付时间。')}</p></div>
  </div>
  <div class="row">{name}{email}</div>
  <div class="row">{country}{phone}</div>
  {message}
  <details class="order-details"><summary>{t('Product & order details','产品与订单信息')}</summary>
    <div class="order-fields"><div class="row">{line}{model}</div><div class="row">{quantity}{company}</div></div>
  </details>
  <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
  <div class="inquiry-send"><button class="btn btn-green" type="submit">{MAIL_SVG}{t('Open email draft','打开邮件草稿')}</button>
    <span>{t('Reply within 24 hours','24 小时内回复')}</span></div>
  <p class="note msg" role="status" aria-live="polite"></p>
</form>'''

def foot():
    return f'''
<footer><div class="wrap">
  <div class="cols">
    <div>
      <div class="logo"><img src="{thumb(img('assets/img/logo.png'), 240)}" alt="Senrex 赛恩力"></div>
      <p>{t(CO['en'], CO['zh'])}</p>
      <p>{t('Energy storage batteries &amp; remote controls · Source factory · Wholesale from stock · Dropshipping · Export','储能电池与遥控器源头工厂 · 现货批发 · 一件代发 · 外贸出口')}</p>
    </div>
    <div>
      <h4>{t('Products','产品中心')}</h4>
      {''.join(f'<p><a href="products.html#{k}">{t(en, zh)}</a></p>' for k, en, zh, *_ in CATS)}
    </div>
    <div>
      <h4>{t('Contact','联系我们')}</h4>
      <p>{t(CO['contact_en'], CO['contact_zh'])}</p>
      <p><a href="{WA_LINK}" target="_blank" rel="noopener">WhatsApp / WeChat: {CO['mobile']}</a></p>
      <p><a href="tel:{CO['tel_link']}">Tel: {CO['tel']}</a></p>
      <p><a href="mailto:{CO['email']}">{CO['email']}</a></p>
      <p>{t(CO['addr_en'], CO['addr_zh'])}</p>
    </div>
  </div>
  <div class="copy"><span>© 2026 {t(CO['en'], CO['zh'])}</span><span>{t('Reliable quality · Timely delivery · Superior service','可靠的质量 · 及时的供货 · 最佳的服务')}</span></div>
  <div class="jr-credit" style="text-align:center;font-size:10px;line-height:1.5;margin-top:10px;display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap"><img src="assets/img/jr-enterprise-logo.webp" width="45" height="24" alt="JR Enterprise" loading="lazy" style="height:24px;width:auto;display:block"><span style="opacity:.65">Powered by JR Enterprise · Mobile/WhatsApp: <a href="https://wa.me/8801876284203" target="_blank" rel="noopener" style="color:inherit;text-decoration:none">+8801876284203</a> · <a href="mailto:junaedm333@gmail.com" style="color:inherit;text-decoration:none">junaedm333@gmail.com</a></span></div>
</div></footer>
<div class="float">
  <a class="wa wa-name" href="https://wa.me/{CO['ceo_wa']}?text={urllib.parse.quote('Hello ' + CO['ceo_name'].split()[0] + ', I am interested in Senrex energy storage products.')}" target="_blank" rel="noopener" aria-label="WhatsApp {e(CO['ceo_name'])}">{WA_SVG}<span>{e(CO['ceo_name'])}</span></a>
  <a class="wa wa-name" href="https://wa.me/{CO['ceo2_wa']}?text={urllib.parse.quote('Hello ' + CO['ceo2_name'].split()[0] + ', I am interested in Senrex remote controls.')}" target="_blank" rel="noopener" aria-label="WhatsApp {e(CO['ceo2_name'])}">{WA_SVG}<span>{e(CO['ceo2_name'])}</span></a>
  <a class="em" href="contact.html#form">{MAIL_SVG}{t('Email sales','邮件询价')}</a>
</div>
<div class="modal" id="pmodal"><div class="box"><button class="x" data-close aria-label="Close">×</button><div class="gal"></div><div class="info"></div></div></div>
<div class="modal zoom" id="zmodal"><div class="box"><button class="x" data-close aria-label="Close">×</button><img alt=""></div></div>
<div class="modal" id="imodal" role="dialog" aria-modal="true" aria-labelledby="inq-modal-title"><div class="box" style="display:block;max-width:640px"><button class="x" data-close aria-label="Close">×</button><div class="info">{inquiry_form('inq-modal')}</div></div></div>
<script>window.SENREX={{email:{json.dumps(CO['email'])},wa:{json.dumps(CO['wa'])}}};</script>
<script src="assets/js/data.js?v={VER}"></script>
<script src="assets/js/main.js?v={VER}"></script>
</body></html>'''

def ceo_section():
    def card(photo, name, name_zh, role, bio, wa, mobile, wechat=None, email=None):
        wa_l = 'https://wa.me/' + wa + '?text=' + urllib.parse.quote('Hello ' + name.split()[0] + ', I am interested in Senrex products.')
        wc = (f'''<button class="btn btn-wechat" type="button" data-wechat="{e(wechat)}"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M9.2 4C5.2 4 2 6.7 2 10c0 1.9 1 3.6 2.7 4.7L4 17l2.6-1.3c.8.2 1.7.4 2.6.4h.6a5.6 5.6 0 0 1-.2-1.5c0-3.4 3.2-6.1 7.2-6.1h.5C16.6 5.9 13.2 4 9.2 4zM6.8 8.2a.9.9 0 1 1 0 1.8.9.9 0 0 1 0-1.8zm4.8 0a.9.9 0 1 1 0 1.8.9.9 0 0 1 0-1.8zM16.8 10c-3.4 0-6.1 2.2-6.1 5s2.7 5 6.1 5c.7 0 1.4-.1 2-.3L21 21l-.6-2c1.2-.9 2-2.3 2-3.9 0-2.9-2.6-5.1-5.6-5.1zm-2 2.9a.8.8 0 1 1 0 1.5.8.8 0 0 1 0-1.5zm4 0a.8.8 0 1 1 0 1.5.8.8 0 0 1 0-1.5z"/></svg>{t('Add on WeChat','添加微信')}</button>''' if wechat else '')
        note = f'<p class="ceo-note">{t("WeChat ID","微信号")}: <b>{e(wechat)}</b></p>' if wechat else ''
        zh = f' <span class="ceo-zh">{e(name_zh)}</span>' if name_zh else ''
        em = (f'''<a class="btn btn-mail" href="mailto:{e(email)}?subject={urllib.parse.quote('Senrex inquiry')}">✉ {e(email)}</a>''' if email else '')
        return f'''<div class="ceo">
    <div class="ceo-photo"><img src="{img(photo)}" alt="{e(name)}, CEO" loading="lazy"></div>
    <div class="ceo-info">
      <h2>{e(name)}{zh}</h2>
      <p class="ceo-role">{role}</p>
      <p>{bio}</p>
      <div class="ceo-btns">
        <a class="btn btn-wa" href="{wa_l}" target="_blank" rel="noopener">{WA_SVG.replace('<svg','<svg width="20" height="20" fill="currentColor"')} WhatsApp</a>{wc}{em}
        <a class="btn btn-call" href="tel:+{wa}">☎ {e(mobile)}</a>
      </div>{note}
    </div>
  </div>'''
    c1 = card('assets/img/team/jack-liu.webp', CO['ceo_name'], CO.get('ceo_name_zh', ''), t('CEO · Energy Storage Power Supply','首席执行官 · 储能电源'),
              t('Leads our energy storage power supply business, from portable power stations to complete solar storage systems. Talk to him directly about projects, OEM orders and distribution.','负责储能电源业务，涵盖便携式储能电源到完整光储系统。项目合作、OEM定制与代理经销，欢迎直接联系。'),
              CO['ceo_wa'], CO['ceo_mobile'], CO['ceo_wechat'], CO.get('ceo_email'))
    c2 = card('assets/img/team/jason-liu.webp', CO['ceo2_name'], CO.get('ceo2_name_zh', ''), t('CEO · Remote Controls','首席执行官 · 遥控器'),
              t('Leads our remote control business: replacement AC and TV remotes for all major brands. Contact him directly for wholesale prices, OEM and bulk orders.','负责遥控器业务，提供各大品牌空调与电视替换遥控器。批发价格、OEM定制及大批量订单，欢迎直接联系。'),
              CO['ceo2_wa'], CO['ceo2_mobile'], CO.get('ceo2_wechat'), CO.get('ceo2_email'))
    return f'''<section class="s ceo-s"><div class="wrap">
  <div class="head"><div class="kicker">{t('Leadership','公司领导')}</div><h2>{t('Talk to our CEOs directly','直接联系我们的负责人')}</h2></div>
  <div class="leaders">{c1}{c2}</div>
</div></section>
'''

# ---------------- NEWS ----------------
def bi(en, zh, tag='span'):
    """Bilingual text written by the admin (not part of the fixed site texts)."""
    en, zh = (en or '').strip(), (zh or '').strip()
    en, zh = e(en or zh), e(zh or en)
    if tag == 'p':
        en = ''.join(f'<p class="en">{x}</p>' for x in en.split('\n') if x.strip())
        zh = ''.join(f'<p class="zh">{x}</p>' for x in zh.split('\n') if x.strip())
        return en + zh
    return f'<{tag} class="en">{en}</{tag}><{tag} class="zh">{zh}</{tag}>'

def news_media(m, small=False):
    src = m.get('src', '')
    if not src:
        return ''
    if m.get('type') == 'video':
        return f'<video src="{e(src)}#t=0.1" controls playsinline preload="metadata"></video>'
    return f'<img src="{thumb(src, 480 if small else 900)}" data-full="{e(src)}" alt="" loading="lazy" data-zoom>'

def news_date(d):
    try:
        y, mth, day = d.split('-')
        return f'<time datetime="{e(d)}">{t_plain(int(y), int(mth), int(day))}</time>'
    except Exception:
        return f'<time>{e(d)}</time>'

def t_plain(y, m, d):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return f'<span class="en">{d} {months[m - 1]} {y}</span><span class="zh">{y}年{m}月{d}日</span>'

def news_post(n, idx, short=False):
    media = [m for m in n.get('media', []) if m.get('src')]
    if short:
        media = media[:1]
    gal = ''.join(news_media(m, short) for m in media)
    cls = 'media one' if len(media) == 1 else 'media'
    body = n.get('body_en') or n.get('body_zh')
    text = bi(n.get('body_en'), n.get('body_zh'), 'p') if body else ''
    if short:
        return f'''<a class="post short" href="news.html#post-{idx}">{f'<div class="{cls}">{gal}</div>' if gal else ''}<div class="post-txt">{news_date(n.get('date', ''))}<h3>{bi(n.get('title_en'), n.get('title_zh'))}</h3><span class="go">{t('Read more →','查看详情 →')}</span></div></a>'''
    return f'''<article class="post" id="post-{idx}">{f'<div class="{cls}">{gal}</div>' if gal else ''}<div class="post-txt">{news_date(n.get('date', ''))}<h3>{bi(n.get('title_en'), n.get('title_zh'))}</h3>{text}</div></article>'''

def news_home():
    if not NEWS:
        return ''
    posts = ''.join(news_post(n, i, short=True) for i, n in enumerate(NEWS[:3]))
    return f'''<section class="s"><div class="wrap">
  <div class="head"><div class="kicker">{t('News','新闻动态')}</div><h2>{t('Updated news &amp; content','最新动态')}</h2></div>
  <div class="news-grid">{posts}</div>
  <p style="margin-top:22px"><a class="btn btn-line" href="news.html">{t('All news →','全部动态 →')}</a></p>
</div></section>
'''

def page_news():
    posts = ''.join(news_post(n, i) for i, n in enumerate(NEWS)) or f'<p class="empty">{t("News is coming soon.","新闻动态即将更新。")}</p>'
    return head('News', 'news', 'Senrex news: new products, factory updates, photos and videos.') + f'''
<div class="ptitle"><div class="wrap"><h1>{t('Updated News &amp; Content','最新动态')}</h1><p>{t('New products, factory updates, photos and short videos from Senrex.','赛恩力新品发布、工厂动态、图片与短视频。')}</p></div></div>
<section class="s"><div class="wrap"><div class="news-list">{posts}</div></div></section>
''' + foot()

def page_home():
    cats = ''.join(f'''<a class="cat cat-{k}" href="products.html#{k}"><div class="pic"><img src="{thumb(img(im), 640)}" alt="{e(en)}" loading="lazy"></div>
<div class="txt"><h3>{t(en, zh)}</h3><p>{t(den, dzh)}</p><span class="n">{COUNTS[k]} {t('models','个型号')} →</span></div></a>''' for k, en, zh, den, dzh, im in CATS)
    return head('Lithium Battery Factory', 'home') + f'''
<section class="hero alpine">
  <picture class="alpine-scene">
    <img src="{img('assets/img/showcase/alpine-1536.webp')}" {'' if IMAGES.get('assets/img/showcase/alpine-1536.webp') else 'srcset="assets/img/showcase/alpine-900.webp 900w, assets/img/showcase/alpine-1536.webp 1536w"'} sizes="100vw" width="1536" height="1024" fetchpriority="high" alt="">
  </picture>
  <div class="wrap"><div class="hero-copy">
  <span class="tag">{t('Energy storage &amp; remote control factory','储能电池 · 遥控器 源头工厂')}</span>
  <h1>{t('Power for<br>every <em>journey.</em>','澎湃动力<br><em>随行致远。</em>')}</h1>
  <p>{t('Portable power stations, lithium battery packs, solar storage systems and replacement remote controls for all major brands. Factory-direct from Tianchang, China.','便携式储能电源、动力锂电池、光储系统，以及各大品牌替换遥控器。安徽天长，厂家直供。')}</p>
  <div class="cta">
    <a class="btn btn-green" href="products.html">{t('View products','浏览产品')}</a>
    <a class="btn btn-line" href="{wa('Hello Senrex, I would like a quotation.')}" target="_blank" rel="noopener">{WA_SVG.replace('<svg','<svg width="18" height="18" fill="currentColor"')} WhatsApp</a>
  </div>
</div></div></section>
<div class="stats"><div class="wrap">
  <div class="stat"><b>{TOTAL}</b><span>{t('product models','个产品型号')}</span></div>
  <div class="stat"><b>4</b><span>{t('product lines','大产品线')}</span></div>
  <div class="stat"><b>≥6000</b><span>{t('battery cycle life','次电池循环寿命')}</span></div>
  <div class="stat"><b>24h</b><span>{t('inquiry reply','询盘回复')}</span></div>
</div></div>
<section class="s"><div class="wrap">
  <div class="head"><div class="kicker">{t('Products','产品中心')}</div><h2>{t('Our product lines','我们的产品线')}</h2><p>{t('Choose a category to see every model with full specifications.','选择类别，查看所有型号及完整参数。')}</p></div>
  <div class="cats">{cats}</div>
</div></section>
<section class="s alt"><div class="wrap">
  <div class="head"><div class="kicker">{t('Why Senrex','为什么选择赛恩力')}</div><h2>{t('Factory direct, export ready','工厂直供，外贸无忧')}</h2></div>
  <div class="why">
    <div><i>⚡</i><h3>{t('Source factory','源头工厂')}</h3><p>{t('We make our own lithium batteries and remote controls, so you buy at factory price.','自主生产锂电池与遥控器，工厂直供价格。')}</p></div>
    <div><i>✓</i><h3>{t('Tested quality','品质检测')}</h3><p>{t('Products pass national quality inspection and are insured by Ping An China.','产品通过国家质量检测认证，由中国平安承保。')}</p></div>
    <div><i>⚙</i><h3>{t('Full R&D system','完善研发体系')}</h3><p>{t('Long-life, high-density batteries and reliable, fully compatible remote controls.','掌握高能量密度、长循环寿命电池技术，遥控器兼容稳定、经久耐用。')}</p></div>
    <div><i>✈</i><h3>{t('Stock & export','现货与出口')}</h3><p>{t('Wholesale from stock, single-piece dropshipping and worldwide export.','现货批发，一件代发，全球出口。')}</p></div>
  </div>
</div></section>
<section class="s"><div class="wrap split">
  <div>
    <div class="kicker">{t('About us','关于我们')}</div>
    <h2 style="color:var(--navy);font-size:30px;margin:6px 0 12px">{t(CO['en'], CO['zh'])}</h2>
    <p>{t('A technology-based enterprise in the New Energy Industry Base of Tianchang City, Anhui Province, with two main business lines: <b>energy storage</b> (lithium battery packs, portable power stations, photovoltaic modules, inverters and solar storage systems) and <b>remote controls</b> (replacement air-conditioner and TV remotes for all major brands). We also design and build solar power and electrical projects.','一家坐落于安徽省天长市新能源产业基地的科技型企业，拥有两大主营业务：<b>储能电池</b>（动力锂电池组、便携式储能电源、光伏组件、逆变器及光储系统）与<b>遥控器</b>（各大品牌空调、电视替换遥控器）。同时承接光伏发电及电力工程设计施工业务。')}</p>
    <a class="btn btn-navy" href="about.html">{t('Learn more','了解更多')}</a>
  </div>
  {CERTGRID_HTML}
</div></section>
''' + news_home() + ceo_section() + f'''<section class="s alt" id="inquiry"><div class="wrap contact single">
  <div class="cbox">
    {inquiry_form('inq-home')}
  </div>
</div></section>
<section class="ctaband"><div class="wrap">
  <div><h2>{t('Need a quotation?','需要报价？')}</h2><p>{t('Tell us the model and quantity. We reply within 24 hours.','告诉我们型号和数量，24小时内回复。')}</p></div>
  <div style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-green" href="{wa('Hello Senrex, I would like a quotation.')}" target="_blank" rel="noopener">WhatsApp</a><a class="btn btn-line" href="#inquiry">{t('Send inquiry','发送询盘')}</a></div>
</div></section>
''' + foot()

# ---------------- PRODUCTS ----------------
SERIES = {
    'gsl': ('GSL-LinkI Series All-in-One', 'GSL-LinkI 系列光储锂电一体机', 'Integrates PV, storage, inverter and power distribution in one cabinet. 3.5kW to 50kW, 5kWh to 112kWh, for homes, shops and factories.', '集光伏、储能、逆变、配电于一体，3.5kW–50kW，5kWh–112kWh，适用户用及工商业。'),
    'gbp': ('GBP-Pro I Series Low-Voltage Battery', 'GBP-Pro I 系列低压锂电屏幕版', 'Wall or floor battery with display, ≥6000 cycles, CAN/RS485, up to 20 units in parallel.', '带显示屏，循环寿命≥6000次，CAN/RS485通信，最多20台并联。'),
    'gst': ('GST Series Single-Phase Hybrid Inverter', 'GST 系列单相光储逆变器', 'All-in-one solar charge inverter, pure sine wave, four charging modes, app monitoring, 3.5kW to 12.5kW.', '一体式太阳能充电逆变器，纯正弦波，四种充电模式，APP监控，3.5kW–12.5kW。'),
    'spv': ('Portable Folding Solar Panels', '便携式折叠太阳能板', 'Waterproof and splash-resistant folding panels for camping, vehicles, RVs, the wild and power outages. Pair them with our portable power stations.', '防水防泼溅折叠太阳能板，露营、车载、房车、野外及停电应急均可使用，可搭配便携式储能电源。'),
}

def page_products():
    tabs = ''.join(f'<a href="#{k}" data-t="{k}">{t(en, zh)}<em>{COUNTS[k]}</em></a>' for k, en, zh, *_ in CATS)
    # power
    pcards = ''
    for p in D['power']:
        src = pimg('power', p['imgs'][0])
        try:
            _w, _h = Image.open(os.path.join(ROOT, src)).size
        except Exception:
            _w, _h = 1, 1
        fit = ' fit' if _w / _h > 0.8 else ''
        name = t(p['name_en'], p.get('name_zh') or p['name_en']) if p.get('name_en') else t('Portable Power Station','便携式储能电源')
        pcards += f'''<div class="card" data-kind="power" data-id="{p['id']}"><div class="pic{fit}"><img src="{thumb(src)}" alt="Portable power station {e(p['power'])}" loading="lazy"></div>
<div class="body"><span class="code">{p['id']}</span><h3>{name}</h3><div class="meta">{e(p['power'])}</div>
<div class="chips"><span class="chip">{e(p['capacity'][:40])}</span><span class="chip">{e(p['battery'])}</span></div><span class="go">{t('View specs →','查看参数 →')}</span></div></div>'''
    bcards = ''
    for b in D['battery']:
        chem = 'NMC' + (' · LiFePO4' if b['lfp'][0] != '—' else '')
        b['wh'] = int(float(b['v']) * float(b['ah']))
        name = t(b['name_en'], b.get('name_zh') or b['name_en']) if b.get('name_en') else f"{b['v']}V {b['ah']}Ah {t('Lithium Battery','锂电池组')}"
        bcards += f'''<div class="card" data-kind="battery" data-id="{b['id']}"><div class="pic"><img src="{thumb(pimg('battery', b['img']))}" alt="{b['v']}V {b['ah']}Ah lithium battery pack" loading="lazy"></div>
<div class="body"><span class="code">{b['id']}</span><h3>{name}</h3><div class="meta">{b['wh']:,} Wh</div>
<div class="chips"><span class="chip">{chem}</span></div><span class="go">{t('View specs →','查看参数 →')}</span></div></div>'''
    sol = ''
    for key, (en, zh, den, dzh) in SERIES.items():
        cards = ''
        for i, x in enumerate(D['solar']):
            if x['series'] != key: continue
            sub = (e(x['cap']) if key == 'gbp' else f"{e(x['rated'])} W")
            chip2 = f'<span class="chip">{e(x["bv"])}</span>'
            if key == 'spv':
                sub = t(x.get('fold_en', ''), x.get('fold_zh') or x.get('fold_en', ''))
                chip2 = f'<span class="chip">{t("Waterproof", "防水防泼溅")}</span>'
            simg = pimg('solar', x['img']) if x.get('img') else img(f'assets/img/solar/{key}.jpg')
            x['_img'] = simg
            cards += f'''<div class="card" data-kind="solar" data-id="{i}"><div class="pic"><img src="{thumb(simg)}" alt="{e(en)} {e(x['model'])}" loading="lazy"></div>
<div class="body"><span class="code">{key.upper()}</span><h3>{t(x['name_en'], x.get('name_zh') or x['name_en']) if x.get('name_en') else e(x['model'])}</h3><div class="meta">{t(en, zh)}</div>
<div class="chips"><span class="chip">{sub}</span>{chip2}</div><span class="go">{t('View specs →','查看参数 →')}</span></div></div>'''
        if not cards: continue
        sol += f'''<div class="series-head" id="{key}"><h3>{t(en, zh)}</h3><p>{t(den, dzh)}</p></div><div class="grid">{cards}</div>'''
    rem = ''
    for r in D['remote']:
        ty = t('AC remote', '空调遥控器') if r['type'] == 'AC' else t('TV remote', '电视遥控器')
        models = ''.join(f'<a href="{wa_remote("Hello " + CO["ceo2_name"].split()[0] + ", I am interested in remote control " + m + " (" + r["brand"] + "). Please send me the price.")}" target="_blank" rel="noopener">{e(m)}</a>' for m in r['models'])
        rem += f'''<div class="rem"><img src="{thumb(pimg('remote', r['img']), 480)}" data-full="{pimg('remote', r['img'])}" alt="{e(r['brand'])} {r['type']} remote controls" loading="lazy" data-zoom>
<div class="body"><h3>{t(r['brand'], r.get('brand_zh') or r['brand'])}<span class="ty">{ty}</span></h3><div class="models">{models}</div></div></div>'''
    return head('Products', 'products') + f'''
<div class="ptitle"><div class="wrap"><h1>{t('Products','产品中心')}</h1><p>{TOTAL} {t('models across 4 product lines. Click any product for full specifications.','个型号，4大产品线。点击产品查看完整参数。')}</p></div></div>
<div class="tabs"><div class="wrap">{tabs}</div></div>
<div class="wrap">
  <div class="group" id="power"><h2>{t('Portable Power Stations','便携式储能电源')}</h2><p class="sub">{t('150W to 11,000W · NMC and LiFePO4 · AC, USB, Type-C and solar input','150W–11000W · 三元锂 / 磷酸铁锂 · AC、USB、Type-C 输出，支持太阳能充电')}</p><div class="grid">{pcards}</div></div>
  <div class="group" id="battery"><h2>{t('Lithium Battery Packs','动力锂电池组')}</h2><p class="sub">{t('48V, 60V and 72V · 12Ah to 230Ah · each model available in NMC (ternary) and LiFePO4','48V / 60V / 72V · 12Ah–230Ah · 每款均有三元锂与磷酸铁锂两种')}</p><div class="grid">{bcards}</div></div>
  <div class="group" id="solar"><h2>{t('Solar Storage & Inverters','光储一体机与逆变器')}</h2><p class="sub">{t('Complete solar energy storage for homes and businesses, plus portable folding solar panels','户用及工商业光伏储能整体方案，以及便携式折叠太阳能板')}</p>{sol}</div>
  <div class="group" id="remote"><h2>{t('Remote Controls','遥控器')}</h2><p class="sub">{t('Replacement AC and TV remotes · tap a model number to ask on WhatsApp','空调与电视替换遥控器 · 点击型号即可通过 WhatsApp 询价')}</p>
  <div class="remote-contact" style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:4px 0 22px"><span style="font-weight:700">{t('Remote control sales','遥控器销售')}: {e(CO['ceo2_name'])}{(' ' + e(CO['ceo2_name_zh'])) if CO.get('ceo2_name_zh') else ''}</span><a class="btn btn-wa" href="{wa_remote('Hello ' + CO['ceo2_name'].split()[0] + ', I would like the price of your remote controls.')}" target="_blank" rel="noopener">{WA_SVG.replace('<svg','<svg width="20" height="20" fill="currentColor"')} WhatsApp {CO['ceo2_mobile']}</a></div>
  <div class="remotes">{rem}</div></div>
</div>
''' + foot()

# ---------------- ABOUT ----------------
def page_about():
    return head('About Us', 'about') + f'''
<div class="ptitle"><div class="wrap"><h1>{t('About Us','关于我们')}</h1><p>{t(CO['en'], CO['zh'])}</p></div></div>
<section class="s"><div class="wrap split">
  <div>
    <div class="kicker">{t('Company profile','公司简介')}</div>
    <h2 style="color:var(--navy);font-size:28px;margin:6px 0 14px">{t('Technology · Manufacturing · Quality','科技缔造 · 专业品质')}</h2>
    {t('Tianchang Xianrui New Energy Technology Co., Ltd. (brand: Senrex) is a technology-based enterprise specialising in energy storage batteries and remote controls. The company is located in the New Energy Industry Base of Tianchang City, Anhui Province.', '天长市先锐新能源科技有限公司（品牌：赛恩力 Senrex）是一家专注于储能电池与遥控器的科技型企业，公司坐落于安徽省天长市新能源产业基地。', 'p')}
    {t('Energy storage is our core business: lithium battery packs, portable power stations, photovoltaic modules, inverters and complete solar storage systems, together with solar power and electrical engineering projects. Our second business line is remote controls: hundreds of replacement air-conditioner and TV remote models for all major brands, available for wholesale, OEM and bulk orders. With a complete R&D and testing system, we master the core technologies behind high energy density and long cycle life, and every product meets strict performance requirements.', '公司以储能电池为核心业务，涵盖动力锂电池组、便携式储能电源、光伏组件、逆变器及完整光储系统，并承接光伏发电及电力工程设计施工业务。遥控器是公司另一大主营业务，提供各大品牌空调、电视替换遥控器，型号达数百款，支持批发、OEM定制及大批量订单。依托完善的研发测试体系，公司掌握了高能量密度、长循环寿命电池的核心技术，每件产品均满足严苛的性能要求。', 'p')}
    {t("As an important participant in Tianchang's 10-billion-yuan new energy vehicle parts industrial base, Xianrui New Energy is part of the local new energy industrial cluster. We stay technology-driven and quality-first, and aim to become an influential company in the regional new energy field.", '作为天长市百亿新能源汽车零部件产业基地的重要参与者，先锐新能源积极融入本地新能源产业集群，借助完善的协作配套与产业政策优势，持续提升自主创新能力。未来，公司将继续坚持科技驱动、质量为本，致力于成为区域新能源领域具有较强影响力的企业。', 'p')}
  </div>
  <img src="{img('assets/img/solar/hero_gsl.jpg')}" alt="Senrex solar storage systems" style="border-radius:14px">
</div></section>
''' + ceo_section() + f'''<section class="s alt"><div class="wrap">
  <div class="head"><div class="kicker">{t('Quality','品质保障')}</div><h2>{t('Inspection reports','检验检测报告')}</h2><p>{t('Our products pass national quality inspection and are insured by Ping An China.','本公司产品通过国家质量检测认证，由中国平安承保。')}</p></div>
  {CERTGRID_HTML}
</div></section>
<section class="s"><div class="wrap">
  <div class="why">
    <div><i>①</i><h3>{t('Reliable quality','可靠的质量')}</h3><p>{t('Every product is tested before shipping.','每件产品出厂前均经检测。')}</p></div>
    <div><i>②</i><h3>{t('Timely delivery','及时的供货')}</h3><p>{t('Stock available for fast wholesale and dropshipping.','现货充足，批发与一件代发快速发货。')}</p></div>
    <div><i>③</i><h3>{t('Superior service','最佳的服务')}</h3><p>{t('One-to-one support by WhatsApp, WeChat and email.','WhatsApp、微信、邮箱一对一服务。')}</p></div>
    <div><i>④</i><h3>{t('Full solutions','整体方案')}</h3><p>{t('From batteries and solar storage systems to remote controls for every major brand.','从电池、光储系统到各大品牌遥控器，一站式供应。')}</p></div>
  </div>
</div></section>
''' + foot()

# ---------------- CONTACT ----------------
def page_contact():
    return head('Contact', 'contact') + f'''
<div class="ptitle"><div class="wrap"><h1>{t('Contact Us','联系我们')}</h1><p>{t('Send an inquiry or reach us directly on WhatsApp, WeChat, phone or email.','发送询盘，或通过 WhatsApp、微信、电话、邮箱直接联系我们。')}</p></div></div>
<section class="s"><div class="wrap contact">
  <div class="cbox">
    <h3>{t(CO['en'], CO['zh'])}</h3>
    <div class="cline"><b>{t('Contact','联系人')}</b><span>{t(CO['contact_en'], CO['contact_zh'])}</span></div>
    <div class="cline"><b>WhatsApp</b><a href="{WA_LINK}" target="_blank" rel="noopener">{CO['mobile']}</a></div>
    <div class="cline"><b>{t('Mobile / WeChat','手机 / 微信')}</b><a href="tel:+{CO['wa']}">{CO['mobile']}</a></div>
    <div class="cline"><b>{t('Tel','座机')}</b><a href="tel:{CO['tel_link']}">{CO['tel']}</a></div>
    <div class="cline"><b>{t('Email','邮箱')}</b><a href="mailto:{CO['email']}">{CO['email']}</a></div>
    <div class="cline"><b>{t('Address','地址')}</b><span>{t(CO['addr_en'], CO['addr_zh'])}</span></div>
    <div class="qr">
      <figure><img src="{img('assets/img/qr_wechat.png')}" alt="WeChat QR code"><figcaption>{t('WeChat','微信')}</figcaption></figure>
      <figure><img src="{img('assets/img/qr_whatsapp.png')}" alt="WhatsApp QR code"><figcaption>WhatsApp</figcaption></figure>
    </div>
    <p style="margin-top:18px"><a class="btn btn-green" href="{wa('Hello Senrex, I would like a quotation.')}" target="_blank" rel="noopener">{t('Chat on WhatsApp','WhatsApp 咨询')}</a></p>
  </div>
  <div class="cbox" id="form">
    {inquiry_form('inq-page')}
  </div>
</div></section>
''' + foot()

def write(name, s):
    open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(s)

write('index.html', page_home())
write('products.html', page_products())
write('about.html', page_about())
write('contact.html', page_contact())
write('news.html', page_news())
open(os.path.join(ROOT, 'assets', 'js', 'data.js'), 'w', encoding='utf-8').write(
    'window.SENREX_DATA=' + json.dumps({'power': D['power'], 'battery': D['battery'], 'solar': D['solar'],
    'series': {k: [v[0], v[1]] for k, v in SERIES.items()}}, ensure_ascii=False) + ';\nwindow.SENREX_COUNTRIES='
    + json.dumps(json.load(open(os.path.join(ROOT, 'data', 'countries.json'), encoding='utf-8')), ensure_ascii=False) + ';')
json.dump([{'key': k, 'en': v['en'], 'zh': v['zh']} for k, v in CATALOG.items()],
          open(os.path.join(ROOT, 'data', 'texts_catalog.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump({'company': CO_DEFAULT, 'images': sorted(set(
    [c[5] for c in CATS] + [f'assets/img/solar/{k}.jpg' for k in SERIES] + [f'assets/img/certs/cert{i}.jpg' for i in range(1, 6)] +
    ['assets/img/logo_mark.png', 'assets/img/logo.png', 'assets/img/qr_wechat.png', 'assets/img/qr_whatsapp.png',
     'assets/img/solar/hero_gsl.jpg', 'assets/img/showcase/alpine-1536.webp', 'assets/img/team/jack-liu.webp', 'assets/img/team/jason-liu.webp']))},
    open(os.path.join(ROOT, 'data', 'site_defaults.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('built', TOTAL, 'models')
