(function () {
  var CFG = window.SENREX || {};
  var DATA = window.SENREX_DATA || { power: [], battery: [] };
  var html = document.documentElement;
  function isZh() { return html.lang === 'zh-CN'; }
  function L(en, zh) { return '<span class="en">' + en + '</span><span class="zh">' + zh + '</span>'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function pimg(kind, f) { return f.indexOf('/') >= 0 ? f : 'assets/img/' + kind + '/' + f; }
  function nm(p, en, zh) { return p.name_en ? L(esc(p.name_en), esc(p.name_zh || p.name_en)) : L(en, zh); }
  function waLink(text) { return 'https://wa.me/' + CFG.wa + '?text=' + encodeURIComponent(text); }

  /* language */
  function setLang(l) {
    html.lang = l;
    try { localStorage.setItem('senrex-lang', l); } catch (e) {}
    document.querySelectorAll('.lang button').forEach(function (b) { b.classList.toggle('on', b.dataset.l === l); });
  }
  document.querySelectorAll('.lang button').forEach(function (b) { b.addEventListener('click', function () { setLang(b.dataset.l); }); });
  setLang(html.lang === 'zh-CN' ? 'zh-CN' : 'en');

  /* hidden admin door: tap the logo 3 times quickly */
  var brand = document.querySelector('.brand'), taps = 0, tapTimer;
  if (brand) brand.addEventListener('click', function (ev) {
    ev.preventDefault();
    taps++; clearTimeout(tapTimer);
    if (taps >= 3) { taps = 0; location.href = 'admin.html'; return; }
    tapTimer = setTimeout(function () {
      var n = taps; taps = 0;
      if (n && document.body.dataset.page !== 'home') location.href = brand.getAttribute('href');
    }, 650);
  });

  /* WeChat button: copy the WeChat ID, then try to open WeChat */
  document.querySelectorAll('[data-wechat]').forEach(function (b) {
    b.addEventListener('click', function () {
      var id = b.dataset.wechat, zh = html.lang === 'zh-CN';
      var done = function () {
        var t = document.createElement('div'); t.className = 'toast';
        t.textContent = zh ? ('微信号 ' + id + ' 已复制，请在微信中添加好友') : ('WeChat ID ' + id + ' copied. Open WeChat › Add Contacts and paste it.');
        document.body.appendChild(t); setTimeout(function () { t.remove(); }, 4500);
        setTimeout(function () { location.href = 'weixin://'; }, 900);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(id).then(done, done); else done();
    });
  });

  /* menu */
  var page = document.body.dataset.page;
  document.querySelectorAll('.menu a[data-p]').forEach(function (a) { if (a.dataset.p === page) a.classList.add('on'); });
  var burger = document.getElementById('burger');
  if (burger) burger.addEventListener('click', function () { document.getElementById('menu').classList.toggle('open'); });

  /* modals */
  var returnFocus;
  var inertBackground = [];
  function open(id) {
    var modal = document.getElementById(id);
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
    if (id === 'imodal') {
      inertBackground = Array.from(document.body.children).filter(function (element) {
        return element !== modal && element.tagName !== 'SCRIPT' && !element.inert;
      });
      inertBackground.forEach(function (element) { element.inert = true; });
      modal.querySelector('[name="name"]').focus();
    }
  }
  function close(m) {
    m.classList.remove('open');
    document.body.style.overflow = '';
    if (m.id === 'imodal') {
      inertBackground.forEach(function (element) { element.inert = false; });
      inertBackground = [];
      if (returnFocus) returnFocus.focus({ preventScroll: true });
    }
  }
  document.querySelectorAll('.modal').forEach(function (m) {
    m.addEventListener('click', function (ev) { if (ev.target === m || ev.target.hasAttribute('data-close')) close(m); });
  });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') document.querySelectorAll('.modal.open').forEach(close); });

  /* image zoom */
  document.querySelectorAll('[data-zoom]').forEach(function (img) {
    img.style.cursor = 'zoom-in';
    img.addEventListener('click', function () {
      var z = document.getElementById('zmodal'); z.querySelector('img').src = img.src; z.querySelector('img').alt = img.alt; open('zmodal');
    });
  });

  /* product detail */
  function row(en, zh, v) { return '<tr><th>' + L(en, zh) + '</th><td>' + esc(v) + '</td></tr>'; }
  function showProduct(kind, id) {
    var p, imgs, title, rows, name;
    if (kind === 'power') {
      p = DATA.power.filter(function (x) { return x.id === id; })[0];
      imgs = p.imgs.map(function (f) { return pimg('power', f); });
      name = (p.name_en || 'Portable Power Station') + ' ' + p.id;
      title = nm(p, 'Portable Power Station', '便携式储能电源');
      rows = row('Output power', '输出功率', p.power) + row('Capacity', '容量', p.capacity) + row('Battery type', '电池类型', p.battery) +
        row('Input voltage', '输入电压', p.input) + row('Waveform', '输出波形', p.wave) + row('AC outlets', 'AC 插座', p.ac) +
        row('USB', 'USB', p.usb) + row('Type-C', 'Type-C', p.typec) + row('Car port', '点烟器', p.car) + row('Solar input', '太阳能输入', p.solar) +
        row('Size', '尺寸', p.size) + row('Net weight', '净重', p.weight);
    } else if (kind === 'solar') {
      p = DATA.solar[+id];
      var sn = DATA.series[p.series];
      imgs = [p._img || ('assets/img/solar/' + p.series + '.jpg')];
      name = (p.name_en || sn[0] + ' ' + p.model);
      title = (p.name_en ? nm(p, '', '') : esc(p.model)) + ' <small style="display:block;font-size:15px;color:var(--muted);font-weight:600">' + L(sn[0], sn[1]) + '</small>';
      p = Object.assign({}, p, { id: p.series.toUpperCase() + ' ' + p.model });
      rows = (p.rated !== '—' ? row('Rated power (W)', '额定功率 (W)', p.rated) + row('Peak power (W)', '峰值功率 (W)', p.peak) : '') +
        row('Battery voltage', '电池电压', p.bv) + (p.cap !== '—' ? row('Battery capacity', '电池容量', p.cap) : '') +
        row('Key specs', '主要参数', p.specs) + row('Size (mm)', '尺寸 (mm)', p.size) + row('Weight (kg)', '重量 (kg)', p.weight);
    } else {
      p = DATA.battery.filter(function (x) { return x.id === id; })[0];
      imgs = [pimg('battery', p.img)];
      name = p.name_en || (p.v + 'V ' + p.ah + 'Ah lithium battery');
      title = p.name_en ? nm(p, '', '') : (p.v + 'V ' + p.ah + 'Ah ' + L('Lithium Battery Pack', '锂电池组'));
      var hasL = p.lfp[0] !== '—';
      rows = '<tr><th></th><th>' + L('NMC (ternary)', '三元锂') + '</th>' + (hasL ? '<th>' + L('LiFePO4', '磷酸铁锂') + '</th>' : '') + '</tr>' +
        '<tr><th>' + L('Rated voltage', '额定电压') + '</th><td>' + p.v + ' V</td>' + (hasL ? '<td>' + p.v + ' V</td>' : '') + '</tr>' +
        '<tr><th>' + L('Rated capacity', '额定容量') + '</th><td>' + p.ah + ' Ah</td>' + (hasL ? '<td>' + p.ah + ' Ah</td>' : '') + '</tr>' +
        '<tr><th>' + L('Energy', '能量') + '</th><td>' + p.wh.toLocaleString() + ' Wh</td>' + (hasL ? '<td>' + p.wh.toLocaleString() + ' Wh</td>' : '') + '</tr>' +
        '<tr><th>' + L('Size (mm)', '尺寸 (mm)') + '</th><td>' + esc(p.nmc[0]) + '</td>' + (hasL ? '<td>' + esc(p.lfp[0]) + '</td>' : '') + '</tr>' +
        '<tr><th>' + L('Charge limit voltage', '充电上限电压') + '</th><td>' + p.nmc[1] + ' V</td>' + (hasL ? '<td>' + p.lfp[1] + ' V</td>' : '') + '</tr>' +
        '<tr><th>' + L('Max discharge current', '最大放电电流') + '</th><td>' + p.nmc[2] + ' A</td>' + (hasL ? '<td>' + p.lfp[2] + ' A</td>' : '') + '</tr>';
    }
    var m = document.getElementById('pmodal');
    m.querySelector('.gal').innerHTML = '<img src="' + imgs[0] + '" alt="' + esc(name) + '">' +
      (imgs.length > 1 ? '<div class="thumbs">' + imgs.map(function (s) { return '<img src="' + s + '" alt="">'; }).join('') + '</div>' : '');
    m.querySelectorAll('.thumbs img').forEach(function (t) { t.addEventListener('click', function () { m.querySelector('.gal > img').src = t.src; }); });
    m.querySelector('.info').innerHTML = '<span class="code" style="color:var(--green-2);font-weight:800;font-size:13px">' + esc(p.id) + '</span><h2>' + title + '</h2>' +
      '<div class="tscroll"><table class="t">' + rows + '</table></div>' +
      '<div class="actions"><a class="btn btn-green" target="_blank" rel="noopener" href="' + waLink('Hello Senrex, I am interested in ' + name + ' (' + p.id + '). Please send me the price.') + '">WhatsApp</a>' +
      '<button class="btn btn-navy" type="button" data-inq="' + esc(name + ' (' + p.id + ')') + '" data-line="' + ({ power: 'Portable Power Stations', battery: 'Lithium Battery Packs', solar: 'Solar Storage & Inverters' })[kind] + '">' + L('Send inquiry', '发送询盘') + '</button></div>';
    open('pmodal');
  }
  document.querySelectorAll('.card[data-kind]').forEach(function (c) {
    c.addEventListener('click', function () { showProduct(c.dataset.kind, c.dataset.id); });
  });

  /* inquiry modal from product */
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-inq]');
    if (!b) return;
    close(document.getElementById('pmodal'));
    returnFocus = document.querySelector('.float .em');
    var f = document.getElementById('inq-modal');
    f.product.value = b.dataset.inq;
    if (b.dataset.line) f.product_line.value = b.dataset.line;
    f.querySelector('.order-details').open = true;
    open('imodal');
  });

  var emailLink = document.querySelector('.float .em');
  emailLink.addEventListener('click', function (event) {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    returnFocus = emailLink;
    open('imodal');
  });

  /* country list with automatic dial code */
  var COUNTRIES = window.SENREX_COUNTRIES || [];
  document.querySelectorAll('select.country-select').forEach(function (sel) {
    var pri = ['CN', 'US', 'GB', 'DE', 'AE', 'SA', 'IN', 'BD', 'PK', 'NG', 'BR', 'RU'];
    function opt(c) { var o = document.createElement('option'); o.value = c[1]; o.dataset.code = c[3]; o.textContent = c[1] + ' / ' + c[2] + ' (+' + c[3] + ')'; return o; }
    var g1 = document.createElement('optgroup'); g1.label = '★';
    pri.forEach(function (k) { var c = COUNTRIES.filter(function (x) { return x[0] === k; })[0]; if (c) g1.appendChild(opt(c)); });
    var g2 = document.createElement('optgroup'); g2.label = 'A–Z';
    COUNTRIES.forEach(function (c) { g2.appendChild(opt(c)); });
    sel.appendChild(g1); sel.appendChild(g2);
    sel.addEventListener('change', function () {
      var o = sel.options[sel.selectedIndex]; if (!o || !o.dataset.code) return;
      var ph = sel.form.elements['phone'], v = ph.value.trim().replace(/^\+\d{1,4}\s*/, '');
      ph.value = '+' + o.dataset.code + ' ' + v; ph.focus();
    });
  });

  /* Send the inquiry straight to the sales mailbox (FormSubmit). If that fails, fall back to a draft in the visitor's mail app. */
  document.querySelectorAll('form.inq').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (form.elements._honey.value) return;
      var status = form.querySelector('.msg');
      var btn = form.querySelector('[type=submit]');
      var missing = ['name', 'email', 'message'].map(function (key) { return form.elements[key]; })
        .find(function (field) { return !field.value.trim(); });
      if (missing || !form.elements.email.validity.valid) {
        (missing || form.elements.email).focus();
        status.dataset.state = 'error';
        status.textContent = missing
          ? (isZh() ? '请填写姓名、邮箱和留言。' : 'Please fill in your name, email and message.')
          : (isZh() ? '请输入有效的电子邮箱。' : 'Please enter a valid email address.');
        return;
      }
      var labels = {name: 'Name', email: 'Email', company: 'Company', phone: 'Mobile / WhatsApp',
        country: 'Country', quantity: 'Order quantity', product_line: 'Product line', product: 'Model'};
      var data = {};
      Object.keys(labels).forEach(function (key) { var v = form.elements[key].value.trim(); if (v) data[labels[key]] = v; });
      var lines = Object.keys(data).map(function (k) { return k + ': ' + data[k]; });
      var subject = 'Senrex quotation — ' + (form.elements.product.value || form.elements.product_line.value || form.elements.name.value);
      var message = form.elements.message.value.trim();
      function draft() {
        var body = lines.join('\n') + '\n\n' + message;
        status.dataset.state = 'draft';
        status.textContent = (isZh() ? '在邮件应用中确认并发送。若未打开，请发邮件至 ' :
          'Review and send in your email app. If it didn’t open, email ') + CFG.email + '.';
        window.location.href = 'mailto:' + CFG.email + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      }
      var payload = Object.assign({}, data, {
        Message: message, Page: location.href,
        _subject: subject, _replyto: form.elements.email.value.trim(), _template: 'table', _captcha: 'false', _honey: ''
      });
      status.dataset.state = 'sending';
      status.textContent = isZh() ? '正在发送…' : 'Sending…';
      if (btn) btn.disabled = true;
      fetch('https://formsubmit.co/ajax/' + encodeURIComponent(CFG.email), {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(payload)
      }).then(function (r) { return r.json().catch(function () { return {}; }); })
        .then(function (res) {
          if (btn) btn.disabled = false;
          if (String(res.success) === 'true') {
            status.dataset.state = 'ok';
            status.textContent = isZh() ? '✓ 询价已发送！我们会尽快与您联系。' : '✓ Inquiry sent! We will contact you soon.';
            form.reset();
          } else { draft(); }
        })
        .catch(function () { if (btn) btn.disabled = false; draft(); });
    });
  });

  /* product tabs highlight */
  var tabs = document.querySelectorAll('.tabs a[data-t]');
  if (tabs.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (en.isIntersecting) tabs.forEach(function (a) { a.classList.toggle('on', a.dataset.t === en.target.id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    document.querySelectorAll('.group[id]').forEach(function (g) { io.observe(g); });
  }
})();
