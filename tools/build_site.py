"""Builds the static Senrex website from data/products.json.

Usage:  python3 tools/build_site.py
To add or change products, edit data/products.json (and put photos in assets/img/...),
then run this script again and commit the generated .html files.
"""
import json, html, os, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'data', 'products.json'), encoding='utf-8'))

CO = {
    'en': 'Tianchang Xianrui New Energy Technology Co., Ltd.',
    'zh': '天长市先锐新能源科技有限公司',
    'contact_en': 'Mr. Liu Xianguo', 'contact_zh': '刘先国',
    'mobile': '+86 190 1805 6828', 'wa': '8619018056828',
    'tel': '0550 7702777', 'tel_link': '+865507702777',
    'email': '834645912@qq.com', 'web': 'www.senrex.cc',
    'addr_zh': '安徽省天长市经济开发区经十三路天盛智谷产业园A1-4栋',
    'addr_en': 'Building A1-4, Tiansheng Zhigu Industrial Park, Jing 13th Road, Economic Development Zone, Tianchang City, Anhui Province, China',
}
WA_LINK = 'https://wa.me/' + CO['wa']
CERTGRID_HTML = '<div class="certgrid">' + ''.join(f'<img src="assets/img/certs/cert{i}.jpg" alt="Inspection report {i}" loading="lazy" data-zoom>' for i in range(1, 6)) + '</div>'

def e(s):
    return html.escape(str(s))

def t(en, zh, tag='span'):
    return f'<{tag} class="en">{en}</{tag}><{tag} class="zh">{zh}</{tag}>'

def wa(text):
    return WA_LINK + '?text=' + urllib.parse.quote(text)

WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7a2.8 2.8 0 0 0 1.8-1.3 2.3 2.3 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg>'
MAIL_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm1 2.4V17h16V7.4l-8 5.3-8-5.3zM5.4 7 12 11.4 18.6 7H5.4z"/></svg>'

CATS = [
    ('power', 'Portable Power Stations', '便携式储能电源', 'Outdoor & home backup power, 150W to 11,000W, NMC and LiFePO4.', '户外及家庭备用电源，150W–11000W，三元锂 / 磷酸铁锂。', 'assets/img/power/ps05.jpg'),
    ('battery', 'Lithium Battery Packs', '动力锂电池组', '48V / 60V / 72V packs from 12Ah to 230Ah, NMC and LiFePO4.', '48V / 60V / 72V，12Ah–230Ah，三元锂 / 磷酸铁锂。', 'assets/img/battery/72V150Ah.jpg'),
    ('solar', 'Solar Storage & Inverters', '光储一体机与逆变器', 'GSL-LinkI all-in-one systems, GBP-Pro I batteries, GST hybrid inverters.', 'GSL-LinkI 光储一体机、GBP-Pro I 低压电池、GST 逆变器。', 'assets/img/solar/gsl.jpg'),
    ('remote', 'Remote Controls', '遥控器', 'Replacement AC and TV remotes for all major brands.', '各大品牌空调与电视替换遥控器。', 'assets/img/remote/ac-universal.jpg'),
]
COUNTS = {'power': len(D['power']), 'battery': len(D['battery']), 'solar': len(D['solar']),
          'remote': sum(len(r['models']) for r in D['remote'])}
TOTAL = sum(COUNTS.values())

def head(title_en, page, desc='Senrex lithium battery factory: portable power stations, 48V/60V/72V lithium battery packs, solar storage systems, inverters and remote controls. Wholesale and export.'):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title_en)} | Senrex 赛恩力</title>
<meta name="description" content="{e(desc)}">
<link rel="icon" href="assets/img/logo_mark.png">
<link rel="stylesheet" href="assets/css/style.css">
<script>try{{var l=localStorage.getItem('senrex-lang');if(!l){{l=(navigator.language||'').toLowerCase().indexOf('zh')===0?'zh-CN':'en'}}document.documentElement.lang=l}}catch(e){{}}</script>
</head>
<body data-page="{page}">
<div class="top"><div class="wrap">
  <a href="tel:{CO['tel_link']}">☎ {CO['tel']}</a>
  <a href="{WA_LINK}" target="_blank" rel="noopener">WhatsApp {CO['mobile']}</a>
  <a href="mailto:{CO['email']}">✉ {CO['email']}</a>
</div></div>
<header class="nav"><div class="wrap">
  <a class="brand" href="index.html"><img src="assets/img/logo_mark.png" alt="Senrex logo"><span><b>SENREX</b><small>{t('Xianrui New Energy','先锐新能源')}</small></span></a>
  <nav class="menu" id="menu">
    <a href="index.html" data-p="home">{t('Home','首页')}</a>
    <a href="products.html" data-p="products">{t('Products','产品中心')}</a>
    <a href="about.html" data-p="about">{t('About Us','关于我们')}</a>
    <a href="contact.html" data-p="contact">{t('Contact','联系我们')}</a>
    <div class="lang"><button data-l="en">EN</button><button data-l="zh-CN">中文</button></div>
  </nav>
  <button class="burger" id="burger" aria-label="Menu">☰</button>
</div></header>
'''

def inquiry_form(prefill_id='inq'):
    LINE_OPTS = ''.join(f'<option value="{en}">{en} / {zh}</option>' for k, en, zh, *_ in CATS)
    return f'''<form class="inq" id="{prefill_id}" novalidate>
  <div class="row">
    <div><label>{t('Your name *','您的姓名 *')}</label><input name="name" required></div>
    <div><label>{t('Company','公司名称')}</label><input name="company"></div>
  </div>
  <div class="row">
    <div><label>{t('Email *','邮箱 *')}</label><input name="email" type="email" required></div>
    <div><label>{t('Phone / WhatsApp','电话 / WhatsApp')}</label><input name="phone" type="tel" placeholder="+86 …"></div>
  </div>
  <div class="row">
    <div><label>{t('Country','国家')}</label><select name="country" class="country-select"><option value="">—</option></select></div>
    <div><label>{t('Order quantity','采购数量')}</label><input name="quantity" placeholder="e.g. 200 pcs"></div>
  </div>
  <div class="row">
    <div><label>{t('Product line','产品线')}</label><select name="product_line"><option value="">—</option>{LINE_OPTS}</select></div>
    <div><label>{t('Model','型号')}</label><input name="product" placeholder="e.g. 48V100Ah"></div>
  </div>
  <div><label>{t('Message * (specs, battery type, packaging, target price, delivery date)','留言 *（规格、电池类型、包装、目标价格、交期）')}</label><textarea name="message" required></textarea></div>
  <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
  <button class="btn btn-green" type="submit">{t('Send Inquiry','发送询盘')}</button>
  <p class="note msg" aria-live="polite"></p>
  <p class="note">{t('Your inquiry goes straight to our sales email. We reply within 24 hours.','询盘将直接发送至我们的销售邮箱，24小时内回复。')}</p>
</form>'''

def foot():
    return f'''
<footer><div class="wrap">
  <div class="cols">
    <div>
      <div class="logo"><img src="assets/img/logo.png" alt="Senrex 赛恩力"></div>
      <p>{t(CO['en'], CO['zh'])}</p>
      <p>{t('Lithium battery source factory · Wholesale from stock · Dropshipping · Export','锂电池源头工厂 · 现货批发 · 一件代发 · 外贸出口')}</p>
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
</div></footer>
<div class="float">
  <a class="wa" href="{wa('Hello Senrex, I am interested in your products.')}" target="_blank" rel="noopener" aria-label="WhatsApp">{WA_SVG}</a>
  <a class="em" href="contact.html#form" aria-label="Inquiry">{MAIL_SVG}</a>
</div>
<div class="modal" id="pmodal"><div class="box"><button class="x" data-close aria-label="Close">×</button><div class="gal"></div><div class="info"></div></div></div>
<div class="modal zoom" id="zmodal"><div class="box"><button class="x" data-close aria-label="Close">×</button><img alt=""></div></div>
<div class="modal" id="imodal"><div class="box" style="display:block;max-width:640px"><button class="x" data-close aria-label="Close">×</button><div class="info"><h2>{t('Send an inquiry','发送询盘')}</h2>{inquiry_form('inq-modal')}</div></div></div>
<script>window.SENREX={{email:{json.dumps(CO['email'])},wa:{json.dumps(CO['wa'])}}};</script>
<script src="assets/js/data.js"></script>
<script src="assets/js/main.js"></script>
</body></html>'''

# ---------------- HOME ----------------
def page_home():
    cats = ''.join(f'''<a class="cat" href="products.html#{k}"><div class="pic"><img src="{img}" alt="{e(en)}" loading="lazy"></div>
<div class="txt"><h3>{t(en, zh)}</h3><p>{t(den, dzh)}</p><span class="n">{COUNTS[k]} {t('models','个型号')} →</span></div></a>''' for k, en, zh, den, dzh, img in CATS)
    return head('Lithium Battery Factory', 'home') + f'''
<section class="hero" style="background-image:url(assets/img/solar/hero_gst.jpg)"><div class="wrap"><div class="glass">
  <span class="tag">{t('Lithium battery source factory','锂电池源头工厂')}</span>
  <h1>{t('Power for every journey, from cell to system','锂时代生活 · 驱动未来，不止于远')}</h1>
  <p>{t('Portable power stations, 48V–72V lithium battery packs, solar storage systems and inverters, made in Tianchang, Anhui. Wholesale from stock, dropshipping and export.','便携式储能电源、48V–72V 动力锂电池、光储一体机与逆变器，安徽天长生产。现货批发、一件代发、外贸出口。')}</p>
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
    <div><i>⚡</i><h3>{t('Source factory','源头工厂')}</h3><p>{t('We produce lithium batteries ourselves, so you buy at factory price.','自主生产锂电池，工厂直供价格。')}</p></div>
    <div><i>✓</i><h3>{t('Tested quality','品质检测')}</h3><p>{t('Products pass national quality inspection and are insured by Ping An China.','产品通过国家质量检测认证，由中国平安承保。')}</p></div>
    <div><i>⚙</i><h3>{t('Full R&D system','完善研发体系')}</h3><p>{t('Core technology for high energy density and long cycle life.','掌握高能量密度、长循环寿命核心技术。')}</p></div>
    <div><i>✈</i><h3>{t('Stock & export','现货与出口')}</h3><p>{t('Wholesale from stock, single-piece dropshipping and worldwide export.','现货批发，一件代发，全球出口。')}</p></div>
  </div>
</div></section>
<section class="s"><div class="wrap split">
  <div>
    <div class="kicker">{t('About us','关于我们')}</div>
    <h2 style="color:var(--navy);font-size:30px;margin:6px 0 12px">{t(CO['en'], CO['zh'])}</h2>
    <p>{t('A technology-based enterprise deeply involved in the lithium battery industry chain, located in the New Energy Industry Base of Tianchang City, Anhui Province. We produce and sell lithium batteries, photovoltaic modules and inverters, and also design and build solar power and electrical projects.','一家深耕锂电池产业链的科技型企业，坐落于安徽省天长市新能源产业基地。主营锂电池、光伏组件、逆变器等产品生产销售，同时承接光伏发电及电力工程设计施工业务。')}</p>
    <a class="btn btn-navy" href="about.html">{t('Learn more','了解更多')}</a>
  </div>
  {CERTGRID_HTML}
</div></section>
<section class="s alt" id="inquiry"><div class="wrap contact">
  <div class="cbox">
    <div class="kicker">{t('Contact us','联系我们')}</div>
    <h3 style="font-size:24px;margin-top:6px">{t('Get a quotation in 24 hours','24小时内获取报价')}</h3>
    <p style="color:var(--muted)">{t('Send your inquiry below. It goes straight to our sales email. You can also reach us directly:','请填写右侧询盘表单，询盘将直接发送至我们的销售邮箱。您也可以直接联系我们：')}</p>
    <div class="cline"><b>WhatsApp</b><a href="{WA_LINK}" target="_blank" rel="noopener">{CO['mobile']}</a></div>
    <div class="cline"><b>{t('WeChat','微信')}</b><span>{CO['mobile']}</span></div>
    <div class="cline"><b>{t('Tel','座机')}</b><a href="tel:{CO['tel_link']}">{CO['tel']}</a></div>
    <div class="cline"><b>{t('Email','邮箱')}</b><a href="mailto:{CO['email']}">{CO['email']}</a></div>
    <div class="qr">
      <figure><img src="assets/img/qr_wechat.png" alt="WeChat QR code"><figcaption>{t('WeChat','微信')}</figcaption></figure>
      <figure><img src="assets/img/qr_whatsapp.png" alt="WhatsApp QR code"><figcaption>WhatsApp</figcaption></figure>
    </div>
  </div>
  <div class="cbox">
    <h3>{t('Send an inquiry','发送询盘')}</h3>
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
}

def page_products():
    tabs = ''.join(f'<a href="#{k}" data-t="{k}">{t(en, zh)}<em>{COUNTS[k]}</em></a>' for k, en, zh, *_ in CATS)
    # power
    pcards = ''
    for p in D['power']:
        pcards += f'''<div class="card" data-kind="power" data-id="{p['id']}"><div class="pic"><img src="assets/img/power/{p['imgs'][0]}" alt="Portable power station {e(p['power'])}" loading="lazy"></div>
<div class="body"><span class="code">{p['id']}</span><h3>{t('Portable Power Station','便携式储能电源')}</h3><div class="meta">{e(p['power'])}</div>
<div class="chips"><span class="chip">{e(p['capacity'][:40])}</span><span class="chip">{e(p['battery'])}</span></div><span class="go">{t('View specs →','查看参数 →')}</span></div></div>'''
    bcards = ''
    for b in D['battery']:
        chem = 'NMC' + (' · LiFePO4' if b['lfp'][0] != '—' else '')
        bcards += f'''<div class="card" data-kind="battery" data-id="{b['id']}"><div class="pic"><img src="assets/img/battery/{b['img']}" alt="{b['v']}V {b['ah']}Ah lithium battery pack" loading="lazy"></div>
<div class="body"><span class="code">{b['id']}</span><h3>{b['v']}V {b['ah']}Ah {t('Lithium Battery','锂电池组')}</h3><div class="meta">{b['wh']:,} Wh</div>
<div class="chips"><span class="chip">{chem}</span></div><span class="go">{t('View specs →','查看参数 →')}</span></div></div>'''
    sol = ''
    for key, (en, zh, den, dzh) in SERIES.items():
        cards = ''
        for i, x in enumerate(D['solar']):
            if x['series'] != key: continue
            sub = (e(x['cap']) if key == 'gbp' else f"{e(x['rated'])} W")
            cards += f'''<div class="card" data-kind="solar" data-id="{i}"><div class="pic"><img src="assets/img/solar/{key}.jpg" alt="{e(en)} {e(x['model'])}" loading="lazy"></div>
<div class="body"><span class="code">{key.upper()}</span><h3>{e(x['model'])}</h3><div class="meta">{t(en, zh)}</div>
<div class="chips"><span class="chip">{sub}</span><span class="chip">{e(x['bv'])}</span></div><span class="go">{t('View specs →','查看参数 →')}</span></div></div>'''
        sol += f'''<div class="series-head" id="{key}"><h3>{t(en, zh)}</h3><p>{t(den, dzh)}</p></div><div class="grid">{cards}</div>'''
    rem = ''
    for r in D['remote']:
        ty = t('AC remote', '空调遥控器') if r['type'] == 'AC' else t('TV remote', '电视遥控器')
        models = ''.join(f'<a href="{wa("Hello Senrex, I am interested in remote control " + m + " (" + r["brand"] + ")")}" target="_blank" rel="noopener">{e(m)}</a>' for m in r['models'])
        rem += f'''<div class="rem"><img src="assets/img/remote/{r['img']}" alt="{e(r['brand'])} {r['type']} remote controls" loading="lazy" data-zoom>
<div class="body"><h3>{e(r['brand'])}<span class="ty">{ty}</span></h3><div class="models">{models}</div></div></div>'''
    return head('Products', 'products') + f'''
<div class="ptitle"><div class="wrap"><h1>{t('Products','产品中心')}</h1><p>{TOTAL} {t('models across 4 product lines. Click any product for full specifications.','个型号，4大产品线。点击产品查看完整参数。')}</p></div></div>
<div class="tabs"><div class="wrap">{tabs}</div></div>
<div class="wrap">
  <div class="group" id="power"><h2>{t('Portable Power Stations','便携式储能电源')}</h2><p class="sub">{t('150W to 11,000W · NMC and LiFePO4 · AC, USB, Type-C and solar input','150W–11000W · 三元锂 / 磷酸铁锂 · AC、USB、Type-C 输出，支持太阳能充电')}</p><div class="grid">{pcards}</div></div>
  <div class="group" id="battery"><h2>{t('Lithium Battery Packs','动力锂电池组')}</h2><p class="sub">{t('48V, 60V and 72V · 12Ah to 230Ah · each model available in NMC (ternary) and LiFePO4','48V / 60V / 72V · 12Ah–230Ah · 每款均有三元锂与磷酸铁锂两种')}</p><div class="grid">{bcards}</div></div>
  <div class="group" id="solar"><h2>{t('Solar Storage & Inverters','光储一体机与逆变器')}</h2><p class="sub">{t('Complete solar energy storage for homes and businesses','户用及工商业光伏储能整体方案')}</p>{sol}</div>
  <div class="group" id="remote"><h2>{t('Remote Controls','遥控器')}</h2><p class="sub">{t('Replacement AC and TV remotes · tap a model number to ask on WhatsApp','空调与电视替换遥控器 · 点击型号即可通过 WhatsApp 询价')}</p><div class="remotes">{rem}</div></div>
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
    <div class="en">
      <p>Tianchang Xianrui New Energy Technology Co., Ltd. (brand: Senrex) is a technology-based enterprise deeply involved in the lithium battery industry chain. The company is located in the New Energy Industry Base of Tianchang City, Anhui Province.</p>
      <p>Lithium batteries are our core business. We produce and sell photovoltaic modules, inverters and related products, and we also design and build solar power and electrical engineering projects. With a complete R&amp;D and testing system, we master the core technologies behind high energy density and long cycle life, and our products meet strict performance requirements.</p>
      <p>As an important participant in Tianchang's 10-billion-yuan new energy vehicle parts industrial base, Xianrui New Energy is part of the local new energy industrial cluster. We stay technology-driven and quality-first, and aim to become an influential company in the regional new energy field.</p>
    </div>
    <div class="zh">
      <p>天长市先锐新能源科技有限公司（品牌：赛恩力 Senrex）是一家深耕锂电池产业链的科技型企业，公司坐落于安徽省天长市新能源产业基地。</p>
      <p>公司以锂电池产业为核心方向，主营光伏组件、逆变器等产品生产销售，同时承接光伏发电及电力工程设计施工业务。依托完善的研发测试体系，公司掌握了支撑高能量密度、长循环寿命电池需求的核心技术，产品性能满足严苛要求。</p>
      <p>作为天长市百亿新能源汽车零部件产业基地的重要参与者，先锐新能源积极融入本地新能源产业集群，借助完善的协作配套与产业政策优势，持续提升自主创新能力。未来，公司将继续坚持科技驱动、质量为本，致力于成为区域新能源领域具有较强影响力的企业。</p>
    </div>
  </div>
  <img src="assets/img/solar/hero_gsl.jpg" alt="Senrex solar storage systems" style="border-radius:14px">
</div></section>
<section class="s alt"><div class="wrap">
  <div class="head"><div class="kicker">{t('Quality','品质保障')}</div><h2>{t('Inspection reports','检验检测报告')}</h2><p>{t('Our products pass national quality inspection and are insured by Ping An China.','本公司产品通过国家质量检测认证，由中国平安承保。')}</p></div>
  {CERTGRID_HTML}
</div></section>
<section class="s"><div class="wrap">
  <div class="why">
    <div><i>①</i><h3>{t('Reliable quality','可靠的质量')}</h3><p>{t('Every product is tested before shipping.','每件产品出厂前均经检测。')}</p></div>
    <div><i>②</i><h3>{t('Timely delivery','及时的供货')}</h3><p>{t('Stock available for fast wholesale and dropshipping.','现货充足，批发与一件代发快速发货。')}</p></div>
    <div><i>③</i><h3>{t('Superior service','最佳的服务')}</h3><p>{t('One-to-one support by WhatsApp, WeChat and email.','WhatsApp、微信、邮箱一对一服务。')}</p></div>
    <div><i>④</i><h3>{t('Full solutions','整体方案')}</h3><p>{t('From battery cells to complete solar storage systems.','从电池到完整光储系统。')}</p></div>
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
      <figure><img src="assets/img/qr_wechat.png" alt="WeChat QR code"><figcaption>{t('WeChat','微信')}</figcaption></figure>
      <figure><img src="assets/img/qr_whatsapp.png" alt="WhatsApp QR code"><figcaption>WhatsApp</figcaption></figure>
    </div>
    <p style="margin-top:18px"><a class="btn btn-green" href="{wa('Hello Senrex, I would like a quotation.')}" target="_blank" rel="noopener">{t('Chat on WhatsApp','WhatsApp 咨询')}</a></p>
  </div>
  <div class="cbox" id="form">
    <h3>{t('Send an inquiry','发送询盘')}</h3>
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
open(os.path.join(ROOT, 'assets', 'js', 'data.js'), 'w', encoding='utf-8').write(
    'window.SENREX_DATA=' + json.dumps({'power': D['power'], 'battery': D['battery'], 'solar': D['solar'],
    'series': {k: [v[0], v[1]] for k, v in SERIES.items()}}, ensure_ascii=False) + ';\nwindow.SENREX_COUNTRIES='
    + json.dumps(json.load(open(os.path.join(ROOT, 'data', 'countries.json'), encoding='utf-8')), ensure_ascii=False) + ';')
print('built', TOTAL, 'models')
