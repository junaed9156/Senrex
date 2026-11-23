(function () {
  var CFG = window.SENREX || {};
  var DATA = window.SENREX_DATA || { power: [], battery: [] };
  var html = document.documentElement;
  function isZh() { return html.lang === 'zh-CN'; }
  function L(en, zh) { return '<span class="en">' + en + '</span><span class="zh">' + zh + '</span>'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function waLink(text) { return 'https://wa.me/' + CFG.wa + '?text=' + encodeURIComponent(text); }

  /* language */
  function setLang(l) {
    html.lang = l;
    try { localStorage.setItem('senrex-lang', l); } catch (e) {}
    document.querySelectorAll('.lang button').forEach(function (b) { b.classList.toggle('on', b.dataset.l === l); });
  }
  document.querySelectorAll('.lang button').forEach(function (b) { b.addEventListener('click', function () { setLang(b.dataset.l); }); });
  setLang(html.lang === 'zh-CN' ? 'zh-CN' : 'en');

  /* menu */
  var page = document.body.dataset.page;
  document.querySelectorAll('.menu a[data-p]').forEach(function (a) { if (a.dataset.p === page) a.classList.add('on'); });
  var burger = document.getElementById('burger');
  if (burger) burger.addEventListener('click', function () { document.getElementById('menu').classList.toggle('open'); });

  /* modals */
  function open(id) { document.getElementById(id).classList.add('open'); document.body.style.overflow = 'hidden'; }
  function close(m) { m.classList.remove('open'); document.body.style.overflow = ''; }
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
      imgs = p.imgs.map(function (f) { return 'assets/img/power/' + f; });
      name = 'Portable Power Station ' + p.id;
      title = L('Portable Power Station', '便携式储能电源');
      rows = row('Output power', '输出功率', p.power) + row('Capacity', '容量', p.capacity) + row('Battery type', '电池类型', p.battery) +
        row('Input voltage', '输入电压', p.input) + row('Waveform', '输出波形', p.wave) + row('AC outlets', 'AC 插座', p.ac) +
        row('USB', 'USB', p.usb) + row('Type-C', 'Type-C', p.typec) + row('Car port', '点烟器', p.car) + row('Solar input', '太阳能输入', p.solar) +
        row('Size', '尺寸', p.size) + row('Net weight', '净重', p.weight);
    } else {
      p = DATA.battery.filter(function (x) { return x.id === id; })[0];
      imgs = ['assets/img/battery/' + p.img];
      name = p.v + 'V ' + p.ah + 'Ah lithium battery';
      title = p.v + 'V ' + p.ah + 'Ah ' + L('Lithium Battery Pack', '锂电池组');
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
      '<button class="btn btn-navy" type="button" data-inq="' + esc(name + ' (' + p.id + ')') + '" data-line="' + (kind === 'power' ? 'Portable Power Stations' : 'Lithium Battery Packs') + '">' + L('Send inquiry', '发送询盘') + '</button></div>';
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
    var f = document.getElementById('inq-modal');
    f.product.value = b.dataset.inq;
    if (b.dataset.line) f.product_line.value = b.dataset.line;
    open('imodal');
  });

  /* inquiry submit: sent to the company email through FormSubmit */
  document.querySelectorAll('form.inq').forEach(function (f) {
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var msg = f.querySelector('.msg');
      if (f._honey.value) return;
      if (!f.elements['name'].value.trim() || !f.email.value.trim() || !f.message.value.trim()) {
        msg.textContent = isZh() ? '请填写姓名、邮箱和留言。' : 'Please fill in your name, email and message.'; msg.style.color = '#c0392b'; return;
      }
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email.value.trim())) {
        msg.textContent = isZh() ? '请输入有效的邮箱地址。' : 'Please enter a valid email address.'; msg.style.color = '#c0392b'; return;
      }
      var data = {
        _subject: 'Website inquiry: ' + (f.product.value || f.product_line.value || 'General') + ' — ' + f.elements['name'].value,
        _template: 'table', _captcha: 'false', _replyto: f.email.value,
        Name: f.elements['name'].value, Company: f.company.value, Email: f.email.value, 'Phone / WhatsApp': f.phone.value,
        Country: f.country.value, 'Order quantity': f.quantity.value, 'Product line': f.product_line.value,
        Model: f.product.value, Message: f.message.value, Page: location.href
      };
      var btn = f.querySelector('button[type=submit]'); btn.disabled = true;
      msg.style.color = ''; msg.textContent = isZh() ? '正在发送…' : 'Sending…';
      fetch('https://formsubmit.co/ajax/' + CFG.email, {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data)
      }).then(function (r) { return r.json(); }).then(function (r) {
        if (r && (r.success === true || r.success === 'true')) {
          msg.style.color = '#2e7d32';
          msg.textContent = isZh() ? '询盘已发送，我们将在24小时内回复您。' : 'Thank you! Your inquiry has been sent. We will reply within 24 hours.';
          f.reset();
        } else { throw new Error('fail'); }
      }).catch(function () {
        var body = Object.keys(data).filter(function (k) { return k.charAt(0) !== '_'; }).map(function (k) { return k + ': ' + data[k]; }).join('\n');
        msg.style.color = '#c0392b';
        msg.innerHTML = (isZh() ? '发送失败，请直接' : 'Could not send. Please ') +
          '<a style="text-decoration:underline" href="mailto:' + CFG.email + '?subject=' + encodeURIComponent(data._subject) + '&body=' + encodeURIComponent(body) + '">' + (isZh() ? '发邮件' : 'email us') + '</a>' +
          (isZh() ? '或' : ' or ') + '<a style="text-decoration:underline" target="_blank" rel="noopener" href="' + waLink(body) + '">WhatsApp</a>.';
      }).then(function () { btn.disabled = false; });
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
