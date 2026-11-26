/* Senrex website admin.
   Edits data/products.json and data/site.json in the GitHub repo through the GitHub API.
   A GitHub Action (.github/workflows/rebuild.yml) then rebuilds the pages.
   The GitHub token is kept only in data/admin.json, encrypted with the admin password (PBKDF2 + AES-GCM). */
(function () {
  var OWNER = 'junaed9156', REPO = 'Senrex', BRANCH = 'main';
  var API = 'https://api.github.com/repos/' + OWNER + '/' + REPO;
  var token = null;
  var state = { products: null, productsSha: null, site: null, siteSha: null, catalog: [], defaults: { company: {}, images: [] }, dirty: false };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  function el(tag, attrs, html) { var e = document.createElement(tag); if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]); if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function setMsg(node, text, kind) { node.textContent = text; node.className = 'msg ' + (kind || ''); }
  function status(t) { $('#status').textContent = t; }

  /* ---------- base64 / crypto ---------- */
  function b64(buf) { var s = '', b = new Uint8Array(buf); for (var i = 0; i < b.length; i++) s += String.fromCharCode(b[i]); return btoa(s); }
  function unb64(str) { var s = atob(str), b = new Uint8Array(s.length); for (var i = 0; i < s.length; i++) b[i] = s.charCodeAt(i); return b; }
  function utf8b64(str) { return b64(new TextEncoder().encode(str)); }
  function b64utf8(str) { return new TextDecoder().decode(unb64(str.replace(/\n/g, ''))); }
  async function keyFrom(pw, salt) {
    var base = await crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveKey']);
    return crypto.subtle.deriveKey({ name: 'PBKDF2', salt: salt, iterations: 310000, hash: 'SHA-256' }, base, { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
  }
  async function encryptToken(tok, pw) {
    var salt = crypto.getRandomValues(new Uint8Array(16)), iv = crypto.getRandomValues(new Uint8Array(12));
    var ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv: iv }, await keyFrom(pw, salt), new TextEncoder().encode(tok));
    return { v: 1, kdf: 'PBKDF2-SHA256-310000', salt: b64(salt), iv: b64(iv), ct: b64(ct) };
  }
  async function userHash(u) {
    var d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode('senrex-admin:' + String(u || '').trim().toLowerCase()));
    return b64(d);
  }
  async function decryptToken(blob, pw) {
    var pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: unb64(blob.iv) }, await keyFrom(pw, unb64(blob.salt)), unb64(blob.ct));
    return new TextDecoder().decode(pt);
  }

  /* ---------- GitHub API ---------- */
  async function gh(path, opts) {
    opts = opts || {};
    var r = await fetch(API + path, {
      method: opts.method || 'GET', cache: 'no-store',
      headers: Object.assign({ 'Accept': 'application/vnd.github+json' }, token ? { 'Authorization': 'Bearer ' + token } : {}),
      body: opts.body ? JSON.stringify(opts.body) : undefined
    });
    if (opts.allow404 && r.status === 404) return null;
    if (!r.ok) { var t = ''; try { t = (await r.json()).message; } catch (e) {} var err = new Error(r.status + ' ' + t); err.status = r.status; throw err; }
    return r.status === 204 ? null : r.json();
  }
  async function getJSON(path, allow404) {
    var f = await gh('/contents/' + path + '?ref=' + BRANCH + '&t=' + Date.now(), { allow404: allow404 });
    if (!f) return null;
    var content = f.content;
    if (!content && f.download_url) { content = null; var raw = await (await fetch(f.download_url + '?t=' + Date.now(), { cache: 'no-store' })).text(); return { data: JSON.parse(raw), sha: f.sha }; }
    return { data: JSON.parse(b64utf8(content)), sha: f.sha };
  }
  async function putFile(path, b64content, message, sha) {
    var body = { message: message, content: b64content, branch: BRANCH };
    if (sha) body.sha = sha;
    return gh('/contents/' + path, { method: 'PUT', body: body });
  }
  async function publicJSON(path) {   // files the admin token does not need to write
    var r = await fetch(path + '?t=' + Date.now(), { cache: 'no-store' }); if (!r.ok) return null; return r.json();
  }

  /* ---------- login / setup ---------- */
  var adminBlob = null;
  async function initLogin() {
    try {
      var r = await fetch('data/admin.json?t=' + Date.now(), { cache: 'no-store' });
      adminBlob = r.ok ? await r.json() : null;
    } catch (e) { adminBlob = null; }
    showSetup(!adminBlob);
  }
  function showSetup(on) {
    $('#setupForm').classList.toggle('hide', !on);
    $('#loginForm').classList.toggle('hide', on);
    $('#loginSub').innerHTML = on ? 'First-time setup<br>首次设置' : 'Log in to edit products, photos and texts<br>登录以编辑产品、图片和文字';
  }
  $('#resetLink').addEventListener('click', function (e) { e.preventDefault(); showSetup(true); });
  $('#loginForm').addEventListener('submit', async function (e) {
    e.preventDefault(); var m = $('#loginMsg'); setMsg(m, 'Checking… 验证中…');
    var bad = 'Wrong username or password · 用户名或密码错误';
    if (adminBlob && adminBlob.user && adminBlob.user !== await userHash($('#un').value)) { token = null; setMsg(m, bad, 'err'); return; }
    try { token = await decryptToken(adminBlob, $('#pw').value); }
    catch (err) { token = null; setMsg(m, bad, 'err'); return; }
    try { await gh(''); } catch (err) { token = null; setMsg(m, 'The saved GitHub token no longer works (' + err.message + '). Use "Set up again". 令牌失效，请重新设置。', 'err'); return; }
    try { sessionStorage.setItem('senrex-admin', token); } catch (e2) {}
    startApp();
  });
  $('#setupForm').addEventListener('submit', async function (e) {
    e.preventDefault(); var m = $('#loginMsg');
    var tok = $('#tok').value.trim(), p1 = $('#pw1').value, p2 = $('#pw2').value, u1 = $('#un1').value.trim();
    if (u1.length < 3) return setMsg(m, 'Username must be at least 3 characters · 用户名至少3位', 'err');
    if (p1 !== p2) return setMsg(m, 'Passwords do not match · 两次密码不一致', 'err');
    if (p1.length < 10) return setMsg(m, 'Password must be at least 10 characters · 密码至少10位', 'err');
    token = tok; setMsg(m, 'Checking token… 验证令牌…');
    try { await gh(''); } catch (err) { token = null; return setMsg(m, 'Token does not work: ' + err.message, 'err'); }
    try {
      var blob = await encryptToken(tok, p1); blob.user = await userHash(u1);
      var cur = await gh('/contents/data/admin.json?ref=' + BRANCH, { allow404: true });
      await putFile('data/admin.json', utf8b64(JSON.stringify(blob, null, 1)), 'Admin: set password', cur && cur.sha);
      adminBlob = blob;
    } catch (err) { token = null; return setMsg(m, 'Could not save (needs Contents: Read and write): ' + err.message, 'err'); }
    try { sessionStorage.setItem('senrex-admin', token); } catch (e2) {}
    startApp();
  });
  $('#logoutBtn').addEventListener('click', function () {
    if (state.dirty && !confirmLeave()) return;
    token = null; try { sessionStorage.removeItem('senrex-admin'); } catch (e) {} location.reload();
  });
  function confirmLeave() { return window.confirm ? window.confirm('You have unsaved changes. Leave anyway? 有未保存的修改，确定离开？') : true; }
  window.addEventListener('beforeunload', function (e) { if (state.dirty) { e.preventDefault(); e.returnValue = ''; } });

  /* ---------- load data ---------- */
  async function startApp() {
    $('#login').classList.add('hide'); $('#app').classList.remove('hide');
    status('Loading… 加载中…');
    try {
      var p = await getJSON('data/products.json');
      state.products = p.data; state.productsSha = p.sha;
      var s = await getJSON('data/site.json', true);
      state.site = s ? s.data : {}; state.siteSha = s ? s.sha : null;
      state.site.company = state.site.company || {}; state.site.texts = state.site.texts || {}; state.site.images = state.site.images || {};
      state.catalog = (await publicJSON('data/texts_catalog.json')) || [];
      state.defaults = (await publicJSON('data/site_defaults.json')) || { company: {}, images: [] };
      status('Ready · 就绪'); render('power');
    } catch (err) { status('Load failed: ' + err.message); }
  }
  function markDirty() { state.dirty = true; status('Unsaved changes · 有未保存的修改'); }

  /* ---------- images ---------- */
  function imgUrl(kind, f) { if (!f) return ''; if (f.indexOf('data:') === 0) return f; return (f.indexOf('/') >= 0 ? f : 'assets/img/' + kind + '/' + f); }
  var pendingPreview = {};   // repo path -> data URL, so new uploads show before the site rebuilds
  function shown(path) { return pendingPreview[path] || path; }
  function compress(file) {
    return new Promise(function (resolve, reject) {
      var rd = new FileReader();
      rd.onload = function () {
        var im = new Image();
        im.onload = function () {
          var max = 1800, w = im.naturalWidth, h = im.naturalHeight, s = Math.min(1, max / Math.max(w, h));
          var c = document.createElement('canvas'); c.width = Math.round(w * s); c.height = Math.round(h * s);
          c.getContext('2d').drawImage(im, 0, 0, c.width, c.height);
          var webp = c.toDataURL('image/webp', 0.9);
          if (webp.indexOf('data:image/webp') === 0) resolve({ url: webp, ext: 'webp' });
          else resolve({ url: c.toDataURL(file.type === 'image/png' ? 'image/png' : 'image/jpeg', 0.9), ext: file.type === 'image/png' ? 'png' : 'jpg' });
        };
        im.onerror = reject; im.src = rd.result;
      };
      rd.onerror = reject; rd.readAsDataURL(file);
    });
  }
  async function uploadImage(file) {
    status('Uploading photo… 上传图片中…');
    var c = await compress(file);
    var slug = (file.name.replace(/\.[^.]+$/, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'photo').slice(0, 40);
    var path = 'assets/img/uploads/' + Date.now() + '-' + slug + '.' + c.ext;
    await putFile(path, c.url.split(',')[1], 'Admin: upload ' + path);
    pendingPreview[path] = c.url;
    status('Photo uploaded · 图片已上传 — remember to Save · 请点击保存');
    return path;
  }
  function pickImage(cb) {
    var inp = el('input', { type: 'file', accept: 'image/*' });
    inp.addEventListener('change', async function () {
      if (!inp.files[0]) return;
      try { cb(await uploadImage(inp.files[0])); markDirty(); } catch (err) { status('Upload failed: ' + err.message); }
    });
    inp.click();
  }

  /* ---------- product schemas ---------- */
  var F = function (key, label, type, extra) { return Object.assign({ key: key, label: label, type: type || 'text' }, extra || {}); };
  var SCHEMA = {
    power: { kind: 'power', title: function (p) { return p.id + ' — ' + (p.name_en || 'Portable Power Station'); }, sub: function (p) { return (p.power || '') + ' · ' + (p.capacity || ''); },
      thumb: function (p) { return imgUrl('power', (p.imgs || [])[0]); },
      fields: [F('id', 'Code · 编号'), F('name_en', 'Name (English) · 英文名称', 'text', { ph: 'Portable Power Station' }), F('name_zh', 'Name (中文) · 中文名称', 'text', { ph: '便携式储能电源' }),
        F('power', 'Output power · 输出功率'), F('capacity', 'Capacity · 容量'), F('battery', 'Battery type · 电池类型'), F('input', 'Input voltage · 输入电压'), F('wave', 'Waveform · 波形'),
        F('ac', 'AC outlets · AC插座'), F('usb', 'USB'), F('typec', 'Type-C'), F('car', 'Car port · 点烟器'), F('solar', 'Solar input · 太阳能输入'), F('size', 'Size · 尺寸'), F('weight', 'Weight · 重量'),
        F('imgs', 'Photos (first = main) · 图片（第一张为主图）', 'images')],
      blank: function () { return { id: 'PS-' + String(state.products.power.length + 1).padStart(2, '0'), name_en: '', name_zh: '', power: '', capacity: '', battery: '', input: '', wave: '', ac: '', usb: '', typec: '', car: '', solar: '', size: '', weight: '', imgs: [] }; } },
    battery: { kind: 'battery', title: function (p) { return p.id + ' — ' + (p.name_en || (p.v + 'V ' + p.ah + 'Ah Lithium Battery')); }, sub: function (p) { return (p.v * p.ah || 0) + ' Wh'; },
      thumb: function (p) { return imgUrl('battery', p.img); },
      fields: [F('id', 'Code · 编号'), F('name_en', 'Name (English) · 英文名称', 'text', { ph: 'auto: 48V 100Ah Lithium Battery' }), F('name_zh', 'Name (中文) · 中文名称', 'text', { ph: '自动：48V 100Ah 锂电池组' }),
        F('v', 'Voltage (V) · 电压', 'number'), F('ah', 'Capacity (Ah) · 容量', 'number'), F('_', '', 'spacer'),
        F('nmc', 'NMC (ternary) · 三元锂: size / charge limit V / max discharge A', 'trio'), F('lfp', 'LiFePO4 · 磷酸铁锂: size / charge limit V / max discharge A ("—" = none)', 'trio'),
        F('img', 'Photo · 图片', 'image')],
      blank: function () { return { id: '', name_en: '', name_zh: '', v: 48, ah: 100, nmc: ['', '', ''], lfp: ['', '', ''], img: '' }; } },
    solar: { kind: 'solar', title: function (p) { return (p.series || '').toUpperCase() + ' — ' + (p.name_en || p.model); }, sub: function (p) { return p.bv + ' · ' + p.cap; },
      thumb: function (p) { return p.img ? imgUrl('solar', p.img) : 'assets/img/solar/' + p.series + '.jpg'; },
      fields: [F('series', 'Series · 系列', 'select', { options: [['gsl', 'GSL-LinkI all-in-one'], ['gbp', 'GBP-Pro I battery'], ['gst', 'GST inverter'], ['spv', 'Portable solar panel · 便携太阳能板']] }), F('model', 'Model · 型号'),
        F('name_en', 'Name (English, optional) · 英文名称'), F('name_zh', 'Name (中文, optional) · 中文名称'),
        F('rated', 'Rated power (W) · 额定功率'), F('peak', 'Peak power (W) · 峰值功率'), F('bv', 'Battery voltage · 电池电压'), F('cap', 'Battery capacity · 电池容量'),
        F('size', 'Size (mm) · 尺寸'), F('weight', 'Weight (kg) · 重量'), F('specs', 'Key specs · 主要参数', 'textarea'),
        F('fold_en', 'Solar panel: design (English) · 太阳能板款式（英文）'), F('fold_zh', 'Solar panel: design (中文) · 太阳能板款式（中文）'),
        F('feat_en', 'Solar panel: features (English) · 产品特点（英文）', 'textarea'), F('feat_zh', 'Solar panel: features (中文) · 产品特点（中文）', 'textarea'),
        F('use_en', 'Solar panel: best for (English) · 适用场景（英文）', 'textarea'), F('use_zh', 'Solar panel: best for (中文) · 适用场景（中文）', 'textarea'),
        F('img', 'Own photo (empty = series photo) · 单独图片（留空用系列图）', 'image')],
      blank: function () { return { series: 'gsl', model: '', name_en: '', name_zh: '', rated: '', peak: '', bv: '', cap: '', size: '', weight: '', specs: '', img: '' }; } },
    remote: { kind: 'remote', title: function (p) { return p.brand + ' (' + p.type + ')'; }, sub: function (p) { return (p.models || []).length + ' models · 个型号'; },
      thumb: function (p) { return imgUrl('remote', p.img); },
      fields: [F('type', 'Type · 类型', 'select', { options: [['AC', 'AC remote · 空调'], ['TV', 'TV remote · 电视']] }), F('brand', 'Brand (English) · 品牌英文'), F('brand_zh', 'Brand (中文) · 品牌中文'),
        F('models', 'Model numbers, separated by commas · 型号（用逗号分隔）', 'list'), F('img', 'Photo · 图片', 'image')],
      blank: function () { return { type: 'AC', brand: '', brand_zh: '', models: [], img: '' }; } }
  };

  function field(sc, item, f, refresh) {
    var wrap = el('div', f.type === 'images' || f.type === 'textarea' || f.type === 'list' || f.type === 'trio' ? { class: 'wide' } : null);
    if (f.type === 'spacer') return wrap;
    wrap.appendChild(el('label', null, esc(f.label)));
    var v = item[f.key];
    if (f.type === 'select') {
      var s = el('select'); f.options.forEach(function (o) { var op = el('option', { value: o[0] }, esc(o[1])); if (o[0] === v) op.selected = true; s.appendChild(op); });
      s.addEventListener('change', function () { item[f.key] = s.value; markDirty(); refresh(); }); wrap.appendChild(s);
    } else if (f.type === 'textarea') {
      var ta = el('textarea'); ta.value = v == null ? '' : v; ta.addEventListener('input', function () { item[f.key] = ta.value; markDirty(); }); wrap.appendChild(ta);
    } else if (f.type === 'list') {
      var tl = el('textarea'); tl.value = (v || []).join(', ');
      tl.addEventListener('input', function () { item[f.key] = tl.value.split(',').map(function (x) { return x.trim(); }).filter(Boolean); markDirty(); refresh(); }); wrap.appendChild(tl);
    } else if (f.type === 'trio') {
      var arr = Array.isArray(v) ? v : ['', '', '']; item[f.key] = arr;
      var tr = el('div', { class: 'trio' });
      [0, 1, 2].forEach(function (i) { var x = el('input', { type: 'text' }); x.value = arr[i] == null ? '' : arr[i]; x.addEventListener('input', function () { var n = parseFloat(x.value); arr[i] = (i > 0 && String(n) === x.value.trim()) ? n : x.value; markDirty(); }); tr.appendChild(x); });
      wrap.appendChild(tr);
    } else if (f.type === 'image' || f.type === 'images') {
      var list = f.type === 'images' ? (item[f.key] = item[f.key] || []) : null;
      var box = el('div', { class: 'imgs' });
      var draw = function () {
        box.innerHTML = '';
        var arr2 = list || (item[f.key] ? [item[f.key]] : []);
        arr2.forEach(function (p, i) {
          var fig = el('figure', null, '<img src="' + esc(shown(imgUrl(sc.kind, p))) + '" alt="">');
          var rm = el('span', { class: 'x' }, '✕ remove · 删除');
          rm.addEventListener('click', function () { if (list) list.splice(i, 1); else item[f.key] = ''; markDirty(); draw(); refresh(); });
          fig.appendChild(rm); box.appendChild(fig);
        });
        var add = el('button', { type: 'button', class: 'btn light sm' }, list ? '+ Add photo · 添加图片' : (item[f.key] ? '↺ Replace photo · 更换图片' : '+ Add photo · 添加图片'));
        add.addEventListener('click', function () { pickImage(function (path) { if (list) list.push(path); else item[f.key] = path; draw(); refresh(); }); });
        box.appendChild(add);
      };
      draw(); wrap.appendChild(box);
    } else {
      var inp = el('input', { type: f.type === 'number' ? 'number' : 'text', placeholder: f.ph || '' }); inp.value = v == null ? '' : v;
      if (f.type === 'number') inp.step = 'any';
      inp.addEventListener('input', function () { item[f.key] = f.type === 'number' ? (inp.value === '' ? '' : Number(inp.value)) : inp.value; markDirty(); refresh(); });
      wrap.appendChild(inp);
    }
    return wrap;
  }

  function renderList(kind) {
    var sc = SCHEMA[kind], arr = state.products[kind], main = $('#main');
    main.innerHTML = '';
    var bar = el('div', { class: 'bar' });
    var search = el('input', { type: 'text', placeholder: 'Search · 搜索' });
    var add = el('button', { class: 'btn green' }, '+ Add new · 新增');
    bar.appendChild(search); bar.appendChild(add);
    bar.appendChild(el('span', { class: 'help' }, arr.length + ' items · 项。Click an item to edit · 点击展开编辑'));
    main.appendChild(bar);
    var listBox = el('div'); main.appendChild(listBox);
    function draw(openIndex) {
      listBox.innerHTML = '';
      var q = search.value.trim().toLowerCase();
      arr.forEach(function (item, idx) {
        var text = JSON.stringify(item).toLowerCase();
        if (q && text.indexOf(q) < 0) return;
        var d = el('details', { class: 'item' }); if (idx === openIndex) d.open = true;
        var sum = el('summary');
        var paintSum = function () { sum.innerHTML = '<img src="' + esc(shown(sc.thumb(item))) + '" alt=""><div><div class="t">' + esc(sc.title(item)) + '</div><div class="s">' + esc(sc.sub(item)) + '</div></div>'; };
        paintSum(); d.appendChild(sum);
        d.addEventListener('toggle', function () {
          if (!d.open || d.dataset.built) return; d.dataset.built = '1';
          var fs = el('div', { class: 'fields' });
          sc.fields.forEach(function (f) { fs.appendChild(field(sc, item, f, paintSum)); });
          var act = el('div', { class: 'actions' });
          var up = el('button', { class: 'btn light sm', type: 'button' }, '↑ Move up · 上移');
          var dn = el('button', { class: 'btn light sm', type: 'button' }, '↓ Move down · 下移');
          var dup = el('button', { class: 'btn light sm', type: 'button' }, '⧉ Duplicate · 复制');
          var del = el('button', { class: 'btn red sm', type: 'button' }, '🗑 Delete · 删除');
          up.onclick = function () { if (idx > 0) { arr.splice(idx - 1, 0, arr.splice(idx, 1)[0]); markDirty(); draw(idx - 1); } };
          dn.onclick = function () { if (idx < arr.length - 1) { arr.splice(idx + 1, 0, arr.splice(idx, 1)[0]); markDirty(); draw(idx + 1); } };
          dup.onclick = function () { arr.splice(idx + 1, 0, JSON.parse(JSON.stringify(item))); markDirty(); draw(idx + 1); };
          del.onclick = function () { if (del.dataset.sure) { arr.splice(idx, 1); markDirty(); draw(); } else { del.dataset.sure = '1'; del.textContent = 'Click again to delete · 再次点击确认删除'; } };
          [up, dn, dup, del].forEach(function (b) { act.appendChild(b); });
          fs.appendChild(act); d.appendChild(fs);
        });
        listBox.appendChild(d);
      });
    }
    search.addEventListener('input', function () { draw(); });
    add.addEventListener('click', function () { arr.unshift(sc.blank()); markDirty(); search.value = ''; draw(0); });
    draw();
  }

  function renderTexts() {
    var main = $('#main'); main.innerHTML = '';
    var T = state.site.texts;
    var bar = el('div', { class: 'bar' });
    var search = el('input', { type: 'text', placeholder: 'Search text · 搜索文字' });
    bar.appendChild(search);
    bar.appendChild(el('span', { class: 'help' }, 'Every heading, button and paragraph of the website. Left: English, right: 中文. Empty box = keep the original. 左英文，右中文，留空则保持原文。'));
    main.appendChild(bar);
    var tbl = el('table', { class: 'tx' }); main.appendChild(tbl);
    function draw() {
      tbl.innerHTML = '';
      var q = search.value.trim().toLowerCase();
      state.catalog.forEach(function (row) {
        var o = T[row.key] || {};
        var hay = (row.en + ' ' + row.zh + ' ' + (o.en || '') + ' ' + (o.zh || '')).toLowerCase();
        if (q && hay.indexOf(q) < 0) return;
        var tr = el('tr'); if (o.en || o.zh) tr.className = 'changed';
        ['en', 'zh'].forEach(function (lang) {
          var td = el('td'), ta = el('textarea'); ta.value = o[lang] || row[lang]; ta.placeholder = row[lang];
          ta.addEventListener('input', function () {
            var cur = T[row.key] || {};
            if (ta.value.trim() === '' || ta.value === row[lang]) delete cur[lang]; else cur[lang] = ta.value;
            if (Object.keys(cur).length) T[row.key] = cur; else delete T[row.key];
            tr.className = T[row.key] ? 'changed' : ''; markDirty();
          });
          td.appendChild(ta); tr.appendChild(td);
        });
        tbl.appendChild(tr);
      });
    }
    search.addEventListener('input', draw); draw();
  }

  function renderCompany() {
    var main = $('#main'); main.innerHTML = '';
    var C = state.site.company, D = state.defaults.company || {};
    var labels = { en: 'Company name (English)', zh: 'Company name (中文)', contact_en: 'Contact person (English)', contact_zh: 'Contact person (中文)',
      mobile: 'Mobile shown on site (e.g. +86 190 1805 6828)', wa: 'WhatsApp number, digits only (e.g. 8619018056828)', tel: 'Office phone shown', tel_link: 'Office phone for dialing (e.g. +865507702777)',
      email: 'Sales email (inquiries go here)', web: 'Website', addr_en: 'Address (English)', addr_zh: 'Address (中文)',
      ceo_name: 'CEO (energy storage) name · 储能负责人', ceo_mobile: 'CEO mobile shown · 总经理电话', ceo_wa: 'CEO WhatsApp, digits only · 总经理 WhatsApp（仅数字）', ceo_wechat: 'CEO WeChat ID · 总经理微信号', ceo_email: 'CEO email · 总经理邮箱',
      ceo_name_zh: 'CEO (energy storage) Chinese name · 中文名', ceo2_name: 'CEO (remote controls) name · 遥控器负责人', ceo2_name_zh: 'CEO (remote controls) Chinese name · 中文名', ceo2_mobile: 'CEO (remote controls) mobile shown · 电话', ceo2_wa: 'CEO (remote controls) WhatsApp, digits only', ceo2_wechat: 'CEO (remote controls) WeChat ID · 微信号', ceo2_email: 'CEO (remote controls) email · 邮箱' };
    var box = el('div', { class: 'box' }, '<h3>Company & contact · 公司与联系方式</h3><p class="help">Empty box = keep the original. 留空则保持原文。</p>');
    var g = el('div', { class: 'grid2' });
    Object.keys(labels).forEach(function (k) {
      var w = el('div'); w.appendChild(el('label', null, esc(labels[k])));
      var i = el('input', { type: 'text', placeholder: D[k] || '' }); i.value = C[k] || D[k] || '';
      i.addEventListener('input', function () { if (i.value.trim() === '' || i.value === D[k]) delete C[k]; else C[k] = i.value; markDirty(); });
      w.appendChild(i); g.appendChild(w);
    });
    box.appendChild(g); main.appendChild(box);
    var ib = el('div', { class: 'box' }, '<h3>Site photos · 网站图片</h3><p class="help">Hero, category, series, certificate, logo and QR photos. Replace any of them. 首页、分类、系列、证书、标志、二维码图片均可更换。</p>');
    var grid = el('div', { class: 'imggrid' });
    (state.defaults.images || []).forEach(function (p) {
      var c = el('div', { class: 'c' });
      var paint = function () {
        var cur = state.site.images[p];
        c.innerHTML = '<img src="' + esc(shown(cur || p)) + '" alt="">' + esc(p.replace('assets/img/', '')) + (cur ? ' <span class="badge">changed</span>' : '') + '<br>';
        var b = el('button', { class: 'btn light sm', type: 'button' }, '↺ Replace · 更换');
        b.onclick = function () { pickImage(function (np) { state.site.images[p] = np; paint(); }); };
        c.appendChild(b);
        if (cur) { var r = el('button', { class: 'btn red sm', type: 'button', style: 'margin-left:6px' }, 'Reset'); r.onclick = function () { delete state.site.images[p]; markDirty(); paint(); }; c.appendChild(r); }
      };
      paint(); grid.appendChild(c);
    });
    ib.appendChild(grid); main.appendChild(ib);
  }

  function renderSettings() {
    var main = $('#main'); main.innerHTML = '';
    var box = el('div', { class: 'box' }, '<h3>Change username &amp; password · 修改用户名和密码</h3>' +
      '<label>New username · 新用户名</label><input type="text" id="nu" autocapitalize="off" spellcheck="false" autocomplete="username">' +
      '<label>New password · 新密码</label><input type="password" id="np1" minlength="10" autocomplete="new-password"><label>Repeat · 再次输入</label><input type="password" id="np2" minlength="10" autocomplete="new-password">' +
      '<div class="help">Both are needed to log in. 登录时需要用户名和密码。</div>' +
      '<button class="btn" id="npBtn" style="margin-top:12px">Save · 保存</button><div class="msg" id="npMsg"></div>');
    main.appendChild(box);
    $('#npBtn').onclick = async function () {
      var u = $('#nu').value.trim(), a = $('#np1').value, b = $('#np2').value, m = $('#npMsg');
      if (u.length < 3) return setMsg(m, 'Username: at least 3 characters · 用户名至少3位', 'err');
      if (a !== b) return setMsg(m, 'Passwords do not match · 两次密码不一致', 'err');
      if (a.length < 10) return setMsg(m, 'At least 10 characters · 至少10位', 'err');
      try {
        var blob = await encryptToken(token, a); blob.user = await userHash(u);
        var cur = await gh('/contents/data/admin.json?ref=' + BRANCH, { allow404: true });
        await putFile('data/admin.json', utf8b64(JSON.stringify(blob, null, 1)), 'Admin: change login', cur && cur.sha);
        adminBlob = blob; setMsg(m, 'Saved · 已保存', 'ok');
      } catch (err) { setMsg(m, 'Failed: ' + err.message, 'err'); }
    };
  }

  function render(tab) {
    document.querySelectorAll('#tabs button').forEach(function (b) { b.classList.toggle('on', b.dataset.tab === tab); });
    if (SCHEMA[tab]) renderList(tab); else if (tab === 'texts') renderTexts(); else if (tab === 'company') renderCompany(); else renderSettings();
    window.scrollTo(0, 0);
  }
  document.querySelectorAll('#tabs button').forEach(function (b) { b.addEventListener('click', function () { render(b.dataset.tab); }); });

  /* ---------- save ---------- */
  $('#saveBtn').addEventListener('click', async function () {
    var btn = this; btn.disabled = true; status('Saving… 保存中…');
    try {
      state.products.battery.forEach(function (b) { b.wh = Math.round((Number(b.v) || 0) * (Number(b.ah) || 0)); });
      var r1 = await putFile('data/products.json', utf8b64(JSON.stringify(state.products, null, 1)), 'Admin: update products', state.productsSha);
      state.productsSha = r1.content.sha;
      var r2 = await putFile('data/site.json', utf8b64(JSON.stringify(state.site, null, 1)), 'Admin: update site texts and photos', state.siteSha);
      state.siteSha = r2.content.sha;
      state.dirty = false;
      status('Saved ✓ The website updates in about 2 minutes · 已保存，约2分钟后网站更新');
    } catch (err) {
      status(err.status === 409 ? 'Someone else saved meanwhile. Reload the page and redo your change. 他人已修改，请刷新后重试。' : 'Save failed: ' + err.message);
    }
    btn.disabled = false;
  });

  /* ---------- boot ---------- */
  try { token = sessionStorage.getItem('senrex-admin'); } catch (e) { token = null; }
  if (token) gh('').then(startApp).catch(function () { token = null; initLogin(); });
  else initLogin();
})();
