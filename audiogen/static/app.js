'use strict';
/* Audio Generator front-end. Vanilla JS, no dependencies.
   All dynamic text is inserted via textContent (see h()), never innerHTML. */

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

/** Create an element; children that are strings become text nodes (safe). */
function h(tag, attrs, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') n.className = v;
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
    else if (k === 'value' || k === 'checked' || k === 'disabled' || k === 'selected') n[k] = v;
    else n.setAttribute(k, v === true ? '' : v);
  }
  for (const c of kids.flat(Infinity)) {
    if (c === null || c === undefined || c === false) continue;
    n.append(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return n;
}
const clear = (n) => { n.replaceChildren(); return n; };

const S = {
  langs: [], lang: null, locale: '', health: {},
  plan: null, source: {}, kind: '',
  filt: { units: new Set(), folders: new Set(), text: '' },
  sel: new Set(),            // selected dialogue indexes
  speakerVoice: {},          // speaker name -> "edge:..." ref
  voices: null,              // /api/voices response for current language
  job: null, timer: null, lastRun: null,
};

// ------------------------------------------------------------------ api
function detailText(d) {
  if (d === null || d === undefined) return '';
  if (typeof d === 'string') return d;
  if (Array.isArray(d)) return d.map(detailText).join('; ');
  if (d.message) return d.message + (d.problems ? ' ' + d.problems.length + ' problem(s).' : '');
  if (d.msg) return (d.loc ? d.loc.join('.') + ': ' : '') + d.msg;
  return JSON.stringify(d);
}
async function api(path, body, opts = {}) {
  const init = { method: body === undefined ? 'GET' : 'POST', ...opts };
  if (body instanceof FormData) init.body = body;
  else if (body !== undefined) {
    init.headers = { 'Content-Type': 'application/json' };
    init.body = JSON.stringify(body);
  }
  let r;
  try { r = await fetch(path, init); }
  catch (e) { throw Object.assign(new Error('Cannot reach the server: ' + e.message), { detail: null }); }
  if (!r.ok) {
    let detail = null, msg = r.status + ' ' + r.statusText;
    try { detail = (await r.json()).detail; msg = detailText(detail) || msg; } catch (e) { /* not JSON */ }
    throw Object.assign(new Error(msg), { detail, status: r.status });
  }
  return (r.headers.get('content-type') || '').includes('json') ? r.json() : r.blob();
}
const fileUrl = (p) => '/api/file?path=' + encodeURIComponent(p);
const say = (node, text, cls) => { clear(node); node.className = cls || ''; if (text) node.textContent = text; };
const joinPath = (a, b) => a.replace(/\/+$/, '') + '/' + b;

// ------------------------------------------------------------------ tabs
function showTab(name) {
  $$('.tabs button').forEach((b) => {
    b.classList.toggle('on', b.dataset.tab === name);
    b.setAttribute('aria-selected', b.dataset.tab === name);
  });
  $$('main > section').forEach((s) => { s.hidden = s.id !== 'tab-' + name; });
  if (name === 'voices') loadVoices();
  if (name === 'speak') fillSpeakVoices();
}
$$('.tabs button').forEach((b) => b.addEventListener('click', () => showTab(b.dataset.tab)));

// ------------------------------------------------------------------ languages
const LS = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } },
};

async function init() {
  $('#apibase').textContent = location.origin + '/api';
  try {
    S.health = await api('/api/health');
    const bad = [];
    if (S.health.edge_tts === false) bad.push('edge-tts is not available' + (S.health.problem ? ' (' + S.health.problem + ')' : ''));
    if (S.health.ffmpeg === false) bad.push('ffmpeg is missing (needed for MP3 output)');
    if (bad.length) { const b = $('#banner'); b.hidden = false; b.textContent = bad.join('. ') + '.'; }
    $('#sout').placeholder = 'blank = ' + (S.health.output_root || 'default') + '/<lang>/speak/phrase.mp3';
  } catch (e) { const b = $('#banner'); b.hidden = false; b.textContent = 'Health check failed: ' + e.message; }
  try { S.langs = (await api('/api/languages')).languages || []; }
  catch (e) { const b = $('#banner'); b.hidden = false; b.textContent = 'Could not load languages: ' + e.message; return; }
  const sel = $('#lang');
  S.langs.forEach((l) => sel.append(h('option', { value: l.code }, `${l.name} — ${l.native} (${l.n_voices} voices)`)));
  const want = location.hash.slice(1) || LS.get('ag.lang');
  setLang(S.langs.some((l) => l.code === want) ? want : (S.langs[0] || {}).code);
}

function setLang(code) {
  S.lang = S.langs.find((l) => l.code === code) || S.langs[0];
  if (!S.lang) return;
  $('#lang').value = S.lang.code;
  LS.set('ag.lang', S.lang.code);
  if (location.hash.slice(1) !== S.lang.code) history.replaceState(null, '', '#' + S.lang.code);
  const loc = LS.get('ag.locale.' + S.lang.code);
  S.locale = S.lang.locales.some((l) => l.locale === loc) ? loc : S.lang.default_locale;
  const ls = clear($('#locale'));
  S.lang.locales.forEach((l) => ls.append(h('option', { value: l.locale }, `${l.label} (${l.n} voice${l.n === 1 ? '' : 's'})`)));
  ls.value = S.locale;
  const special = ['la', 'lat', 'bfi', 'bsl', 'sgn'].includes(S.lang.code) || /latin|sign language/i.test(S.lang.name);
  const note = $('#langnote');
  note.textContent = S.lang.note || '';
  note.className = 'langnote' + (special && S.lang.note ? ' special' : '');
  const rtl = S.lang.rtl ? 'rtl' : 'ltr';
  ['text', 'stext'].forEach((id) => { $('#' + id).dir = rtl; });
  document.documentElement.lang = 'en';
  $('#vtext').value = S.lang.sample_text || '';
  $('#vtext').dir = rtl;
  $('#stext').value = S.lang.sample_text || '';
  S.voices = null; S.plan = null; clear($('#plan')).hidden = true;
  if (!$('#tab-voices').hidden) loadVoices();
  if (!$('#tab-speak').hidden) fillSpeakVoices();
}
$('#lang').addEventListener('change', (e) => setLang(e.target.value));
$('#locale').addEventListener('change', (e) => {
  S.locale = e.target.value; LS.set('ag.locale.' + S.lang.code, S.locale);
  if (S.plan && S.plan.kind === 'dialogues') renderPlan();   // voice ordering depends on locale
});
window.addEventListener('hashchange', () => {
  const c = location.hash.slice(1);
  if (c && S.lang && c !== S.lang.code && S.langs.some((l) => l.code === c)) setLang(c);
});

// ------------------------------------------------------------------ source / inspect
function srcPayload() {
  const text = $('#text').value.trim(), path = $('#path').value.trim();
  return text ? { text: $('#text').value } : { path };
}
function base() {
  return { lang: S.lang.code, locale: S.locale, ...srcPayload() };
}
$('#upload').addEventListener('change', async (e) => {
  const f = e.target.files[0];
  if (!f) return;
  const fd = new FormData(); fd.append('file', f);
  const m = $('#inspectmsg');
  say(m, 'Uploading...');
  try { const r = await api('/api/upload', fd); $('#path').value = r.path; $('#text').value = ''; say(m, 'Uploaded ' + r.name); }
  catch (err) { say(m, 'Upload failed: ' + err.message, 'error'); }
  e.target.value = '';
});

$('#inspect').addEventListener('click', async () => {
  const m = $('#inspectmsg'), s = srcPayload();
  if (!s.path && !s.text) { say(m, 'Enter a file path, upload a file or paste text first.', 'error'); return; }
  say(m, 'Reading...');
  const body = { ...base() };
  if ($('#kindsel').value) body.kind = $('#kindsel').value;
  try {
    S.plan = await api('/api/inspect', body);
    S.source = s; S.kind = S.plan.kind;
    S.filt = { units: new Set(S.plan.units || []), folders: new Set((S.plan.items || []).map((i) => i.kind)), text: '' };
    S.sel = new Set((S.plan.dialogues || []).map((d) => d.index));
    S.speakerVoice = {};
    (S.plan.speakers || []).forEach((sp) => { S.speakerVoice[sp.name] = sp.voice || ''; });
    say(m, '');
    renderPlan();
  } catch (err) { S.plan = null; clear($('#plan')).hidden = true; say(m, err.message, 'error'); }
});

function renderPlan() {
  const root = clear($('#plan'));
  root.hidden = false;
  const p = S.plan;
  const badge = h('p', {}, 'Detected: ', h('span', { class: 'badge' }, p.kind),
    ` from ${p.source}` + ($('#kindsel').value ? ' (manual override)' : ''));
  root.append(h('div', { class: 'card' }, h('h2', {}, '2. What the file asks for'), badge));
  const card = root.lastChild;
  if (p.kind === 'audio-list') renderList(card); else renderDialogues(card);
}

// ------------------------------------------------------------------ audio-list
function listFilters() {
  const f = S.filt, p = S.plan;
  const folders = [...new Set(p.items.map((i) => i.kind))];
  let re = null;
  const m = ($('#f-match') || {}).value || '';
  try { re = m ? new RegExp(m) : null; } catch (e) { re = null; }
  const q = f.text.toLowerCase();
  const ids = (($('#f-ids') || {}).value || '').split(/[,\s]+/).filter(Boolean);
  const hit = p.items.filter((i) => f.units.has(i.unit) && f.folders.has(i.kind) &&
    (!re || re.test(i.id)) && (!ids.length || ids.includes(i.id)) &&
    (!q || (i.id + ' ' + i.text + ' ' + i.save_as).toLowerCase().includes(q)));
  return { folders, ids, match: m, hit, badRe: !!m && !re };
}

function renderList(card) {
  const p = S.plan, rtl = S.lang.rtl ? 'rtl' : 'ltr';
  card.append(h('div', { class: 'stats' },
    stat(p.files_to_make, 'files to make'), stat(p.reuse_rows, 'reused rows'), stat((p.units || []).length, 'units'),
    h('span', { class: p.problems.length ? 'error' : 'ok' }, h('b', {}, p.problems.length), 'problems')));
  if (p.problems.length) card.append(h('ul', { class: 'error' }, p.problems.map((x) => h('li', {}, detailText(x)))));
  card.append(h('h3', {}, 'Voices that will be used'),
    h('div', { class: 'chips' }, Object.entries(p.voices || {}).map(([t, v]) => h('span', { class: 'chip' }, `${t}: ${v}`))));

  card.append(h('h3', {}, 'Filters'));
  const unitRow = h('div', { class: 'chips', role: 'group', 'aria-label': 'Units' });
  (p.units || []).forEach((u) => unitRow.append(checkChip('unit ' + u, S.filt.units.has(u), (on) => {
    on ? S.filt.units.add(u) : S.filt.units.delete(u); refreshTable();
  })));
  const folders = [...new Set(p.items.map((i) => i.kind))];
  const folderRow = h('div', { class: 'chips', role: 'group', 'aria-label': 'Kinds' });
  folders.forEach((k) => folderRow.append(checkChip(k, S.filt.folders.has(k), (on) => {
    on ? S.filt.folders.add(k) : S.filt.folders.delete(k); refreshTable();
  })));
  card.append(h('div', { class: 'row' }, h('div', {}, h('div', { class: 'muted' }, 'Units'), unitRow),
    h('div', {}, h('div', { class: 'muted' }, 'Kinds / folders'), folderRow)));
  card.append(h('div', { class: 'row' },
    h('label', { class: 'grow' }, 'ID regex', h('input', { id: 'f-match', type: 'text', placeholder: '^U03-B', oninput: refreshTable })),
    h('label', { class: 'grow' }, 'Only these IDs (comma separated)', h('input', { id: 'f-ids', type: 'text', oninput: refreshTable })),
    h('label', { class: 'grow' }, 'Search the table', h('input', { id: 'f-text', type: 'search', oninput: (e) => { S.filt.text = e.target.value; refreshTable(); } }))));
  card.append(h('p', { id: 'tcount', class: 'muted', 'aria-live': 'polite' }),
    h('div', { class: 'scroll', id: 'tbox', dir: rtl === 'rtl' ? 'ltr' : 'ltr' }));

  card.append(h('h3', {}, 'Options'),
    h('div', { class: 'row' },
      h('label', {}, 'Speed override (blank = list)', h('input', { id: 'o-rate', type: 'number', min: '0.5', max: '1.5', step: '0.05', placeholder: 'auto' })),
      h('label', {}, 'Parallel jobs (1-8)', h('input', { id: 'o-jobs', type: 'number', min: '1', max: '8', value: '4' })),
      h('label', { class: 'grow' }, 'Output folder', h('input', { id: 'o-out', type: 'text', placeholder: (S.health.output_root || 'default') + '/' + S.lang.code + '/list' })),
      h('label', { class: 'inline' }, h('input', { id: 'o-force', type: 'checkbox' }), 'Force re-render'),
      h('label', { class: 'inline' }, h('input', { id: 'o-ignore', type: 'checkbox' }), 'Ignore problems')),
    h('div', { class: 'row' }, h('button', { class: 'primary', id: 'gen', onclick: startList }, 'Generate'),
      h('button', { onclick: copyCli }, 'Copy CLI command'), h('span', { id: 'climsg', class: 'muted', 'aria-live': 'polite' })));
  refreshTable();
}
const stat = (n, label) => h('span', {}, h('b', {}, n), label);
function checkChip(label, on, fn) {
  return h('label', { class: 'chip inline' }, h('input', { type: 'checkbox', checked: on, onchange: (e) => fn(e.target.checked) }), label);
}

function refreshTable() {
  const box = $('#tbox'); if (!box) return;
  const { hit, badRe } = listFilters();
  $('#tcount').textContent = badRe ? 'Invalid regular expression.' : `${hit.length} of ${S.plan.items.length} items match`;
  const shown = hit.slice(0, 500);
  const tb = h('tbody', {}, shown.map((i) => h('tr', {}, h('td', { class: 'mono' }, i.id), h('td', {}, i.kind), h('td', {}, i.voice),
    h('td', { class: 'mono' }, i.save_as), h('td', { dir: S.lang.rtl ? 'rtl' : 'auto' }, (i.text || '').slice(0, 120)))));
  clear(box).append(h('table', {}, h('thead', {}, h('tr', {}, ['ID', 'Kind', 'Voice', 'Save as', 'Text'].map((t) => h('th', {}, t)))), tb));
  if (hit.length > shown.length) box.append(h('p', { class: 'muted' }, `Showing the first ${shown.length}.`));
}

function listConfig() {
  const { folders, ids, match, badRe } = listFilters();
  const units = [...S.filt.units], kinds = [...S.filt.folders];
  const rate = parseFloat($('#o-rate').value);
  const cfg = {
    kind: 'audio-list',
    units: units.length === (S.plan.units || []).length ? [] : units,
    folders: kinds.length === folders.length ? [] : kinds,
    ids, match: match || null, badRe,
    force: $('#o-force').checked, jobs: Math.min(8, Math.max(1, parseInt($('#o-jobs').value, 10) || 4)),
    out_dir: $('#o-out').value.trim(), ignore_problems: $('#o-ignore').checked,
  };
  if (rate) cfg.rate = rate;
  return cfg;
}

function startList() {
  const c = listConfig();
  if (c.badRe) { alert('The ID regex is not valid.'); return; }
  if (S.filt.units.size === 0 || S.filt.folders.size === 0) { alert('No unit or kind is selected.'); return; }
  const body = { ...base(), kind: 'audio-list', units: c.units, folders: c.folders, ids: c.ids, match: c.match,
    force: c.force, jobs: c.jobs };
  if (c.rate) body.rate = c.rate;
  if (c.out_dir) body.out_dir = c.out_dir;
  if (c.ignore_problems) body.ignore_problems = true;
  S.lastRun = c;
  startJob(body);
}

// ------------------------------------------------------------------ dialogues
function voiceOptions(selected) {
  const cat = (S.voices && S.voices.voices) || [];
  const loc = S.locale.replace('-', '_');
  const mine = cat.filter((v) => v.locale === loc), other = cat.filter((v) => v.locale !== loc);
  const opt = (v) => h('option', { value: v.ref, selected: v.ref === selected },
    `${v.name} (${v.gender}) — ${(v.personalities || []).join(', ') || v.locale}${v.locale !== loc ? ' [' + v.locale + ']' : ''}`);
  const nodes = [];
  if (selected && !cat.some((v) => v.ref === selected)) nodes.push(h('option', { value: selected, selected: true }, selected));
  if (mine.length) nodes.push(h('optgroup', { label: 'This variety (' + loc + ')' }, mine.map(opt)));
  if (other.length) nodes.push(h('optgroup', { label: 'Other varieties' }, other.map(opt)));
  return nodes;
}

async function renderDialogues(card) {
  const p = S.plan, rtl = S.lang.rtl ? 'rtl' : 'ltr';
  if (!S.voices) { try { S.voices = await api('/api/voices?lang=' + encodeURIComponent(S.lang.code)); } catch (e) { card.append(h('p', { class: 'error' }, 'Voice list failed: ' + e.message)); S.voices = { voices: [] }; } }
  if (p.variety) card.append(h('p', {}, 'Detected variety: ', h('b', {}, typeof p.variety === 'string' ? p.variety : JSON.stringify(p.variety))));
  if ((p.skipped || []).length) {
    card.append(h('details', {}, h('summary', {}, `${p.skipped.length} section(s) ignored`),
      h('ul', {}, p.skipped.map((s) => h('li', {}, typeof s === 'string' ? s : `${s.title || ''}${s.heading ? ' (heading: ' + s.heading + ')' : ''}`)))));
  }
  const count = h('span', { class: 'muted', 'aria-live': 'polite' });
  const list = h('div', {});
  const upd = () => { count.textContent = `${S.sel.size} of ${p.dialogues.length} selected`; };
  const drawList = () => {
    clear(list).append(...p.dialogues.map((d) => h('label', { class: 'dlg inline' },
      h('input', { type: 'checkbox', checked: S.sel.has(d.index), onchange: (e) => { e.target.checked ? S.sel.add(d.index) : S.sel.delete(d.index); upd(); } }),
      h('span', { dir: rtl }, d.title), h('small', {}, `#${d.index} · ${d.n_lines} lines · ${(d.speakers || []).join(', ')}`))));
    upd();
  };
  card.append(h('h3', {}, 'Dialogues'), h('div', { class: 'row' },
    h('button', { onclick: () => { S.sel = new Set(p.dialogues.map((d) => d.index)); drawList(); } }, 'Select all'),
    h('button', { onclick: () => { S.sel = new Set(); drawList(); } }, 'Deselect all'),
    h('button', { onclick: () => { S.sel = new Set(p.dialogues.filter((d) => !S.sel.has(d.index)).map((d) => d.index)); drawList(); } }, 'Invert'), count),
    h('div', { class: 'scroll' }, list));
  drawList();

  card.append(h('h3', {}, 'Speakers and voices'));
  const sample = (name) => {
    for (const d of p.dialogues) for (const l of d.lines || []) if (l.speaker === name && l.text) return l.text;
    return S.lang.sample_text;
  };
  const rows = p.speakers.map((sp) => {
    const sel = h('select', { 'aria-label': 'Voice for ' + sp.name, onchange: (e) => { S.speakerVoice[sp.name] = e.target.value; } }, voiceOptions(S.speakerVoice[sp.name]));
    const st = h('span', { class: 'muted' });
    return h('tr', {}, h('td', { dir: 'auto' }, sp.name), h('td', {}, sp.gender), h('td', {}, sp.lines), h('td', {}, sel),
      h('td', {}, h('button', { onclick: () => previewVoice(sel.value.replace(/^edge:/, ''), sample(sp.name), 1, st) }, 'Preview'), ' ', st));
  });
  card.append(h('div', { class: 'scroll' }, h('table', {}, h('thead', {}, h('tr', {}, ['Speaker', 'Gender', 'Lines', 'Voice', ''].map((t) => h('th', {}, t)))), h('tbody', {}, rows))));
  card.append(h('div', { class: 'row' },
    h('label', {}, 'Speed (blank = default)', h('input', { id: 'o-rate', type: 'number', min: '0.5', max: '1.5', step: '0.05' })),
    h('label', { class: 'grow' }, 'Output folder', h('input', { id: 'o-out', type: 'text', placeholder: (S.health.output_root || 'default') + '/' + S.lang.code + '/dialogues' }))),
    h('div', { class: 'row' }, h('button', { class: 'primary', onclick: startDialogues }, 'Generate'),
      h('button', { onclick: copyCli }, 'Copy CLI command'), h('span', { id: 'climsg', class: 'muted', 'aria-live': 'polite' })));
}

function dialogueConfig() {
  const voices = {};
  for (const [n, v] of Object.entries(S.speakerVoice)) if (v) voices[n] = { voice: v };
  const rate = parseFloat($('#o-rate').value);
  return { kind: 'dialogues', only: [...S.sel].sort((a, b) => a - b), voices, rate: rate || null, out_dir: $('#o-out').value.trim() };
}
function startDialogues() {
  const c = dialogueConfig();
  if (!c.only.length) { alert('Select at least one dialogue.'); return; }
  const body = { ...base(), kind: 'dialogues', only: c.only, voices: c.voices, options: {} };
  if (c.rate) body.rate = c.rate;
  if (c.out_dir) body.out_dir = c.out_dir;
  S.lastRun = c;
  startJob(body);
}

// ------------------------------------------------------------------ CLI command
const q = (s) => /^[\w@%+=:,./-]+$/.test(s) ? s : "'" + String(s).replace(/'/g, "'\\''") + "'";
function buildCli() {
  const c = S.kind === 'dialogues' ? dialogueConfig() : listConfig();
  const file = S.source.path || 'FILE.md';
  const a = ['./audiogen.sh generate', q(file), '--lang', S.lang.code, '--locale', S.locale.replace('_', '-')];
  if (c.out_dir) a.push('-o', q(c.out_dir));
  if ($('#kindsel').value) a.push('--kind', $('#kindsel').value);
  if (c.rate) a.push('--rate', c.rate);
  if (S.kind === 'dialogues') {
    if (c.only.length !== S.plan.dialogues.length) a.push('--only', q(c.only.join(',')));
    for (const [n, v] of Object.entries(c.voices)) {
      if (v.voice !== (S.plan.speakers.find((s) => s.name === n) || {}).voice) a.push('--voice', q(n + '=' + v.voice.replace(/^edge:/, '')));
    }
  } else {
    if (c.units.length) a.push('--unit', q(c.units.join(',')));
    if (c.folders.length) a.push('--folder', q(c.folders.join(',')));
    if (c.ids.length) a.push('--id', q(c.ids.join(',')));
    if (c.match) a.push('--match', q(c.match));
    if (c.force) a.push('--force');
    if (c.jobs !== 4) a.push('--jobs', c.jobs);
    if (c.ignore_problems) a.push('--ignore-problems');
  }
  return a.join(' ');
}
async function copyCli() {
  const cmd = buildCli(), m = $('#climsg');
  try { await navigator.clipboard.writeText(cmd); say(m, 'Copied: ' + cmd + (S.source.path ? '' : '  (save your pasted text to a file and use its path)')); }
  catch (e) { say(m, cmd); }
}

// ------------------------------------------------------------------ jobs
async function startJob(body) {
  const card = $('#jobcard'); card.hidden = false;
  clear($('#result')); $('#joblog').hidden = true; $('#barfill').style.width = '0';
  $('#jobmsg').textContent = 'Starting...'; $('#jobmsg').className = 'mono';
  $('#stop').disabled = false;
  clearTimeout(S.timer);
  card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  try {
    const r = await api('/api/generate', body);
    S.job = { id: r.job, out: r.out, kind: r.kind };
    poll();
  } catch (err) {
    const m = $('#jobmsg'); m.className = 'mono error'; m.textContent = err.message;
    const probs = err.detail && err.detail.problems;
    if (probs) $('#result').append(h('ul', { class: 'error' }, probs.map((x) => h('li', {}, detailText(x)))),
      h('p', { class: 'muted' }, 'Fix the file, or tick "Ignore problems" to render the rest.'));
  }
}
async function poll() {
  const job = S.job; if (!job) return;
  let j;
  try { j = await api('/api/jobs/' + job.id); }
  catch (e) { $('#jobmsg').textContent = 'Lost contact with the job: ' + e.message; return; }
  $('#barfill').style.width = (j.pct || 0) + '%';
  $('#jobmsg').textContent = `${j.pct || 0}% — ${j.message || ''}`;
  if (j.log && j.log.length) { const l = $('#joblog'); l.hidden = false; l.textContent = j.log.join('\n'); l.scrollTop = l.scrollHeight; }
  if (j.state === 'running') { S.timer = setTimeout(poll, 700); return; }
  $('#stop').disabled = true;
  if (j.state === 'error') { $('#jobmsg').className = 'mono error'; $('#jobmsg').textContent = j.error || j.message; return; }
  showResult(j.result || {}, job);
}
$('#stop').addEventListener('click', async () => {
  if (!S.job) return;
  try { await api('/api/jobs/' + S.job.id + '/stop', {}); } catch (e) { $('#jobmsg').textContent = e.message; }
});

function player(path, label) {
  return h('div', { class: 'voice' }, h('span', { class: 'nm mono' }, label),
    h('audio', { controls: true, preload: 'none', src: fileUrl(path) }));
}
async function showResult(r, job) {
  const box = clear($('#result'));
  if (job.kind === 'audio-list') {
    const n = (x) => Array.isArray(x) ? x.length : (x || 0);
    box.append(h('div', { class: 'stats' }, stat(n(r.written), 'written'), stat(n(r.skipped), 'skipped (already there)'),
      h('span', { class: n(r.errors) ? 'error' : 'ok' }, h('b', {}, n(r.errors)), 'errors'),
      h('span', { class: n(r.missing) ? 'warn' : 'ok' }, h('b', {}, n(r.missing)), 'missing')));
    if (Array.isArray(r.errors) && r.errors.length) box.append(h('pre', { class: 'error' }, r.errors.map(detailText).join('\n')));
    if (Array.isArray(r.missing) && r.missing.length) box.append(h('details', {}, h('summary', {}, 'Missing files'), h('pre', {}, r.missing.join('\n'))));
    const out = r.out || job.out;
    box.append(h('p', {}, 'Output folder: ', h('code', {}, out)));
    try {
      const o = await api('/api/output?dir=' + encodeURIComponent(out));
      const files = o.files.filter((f) => /\.(mp3|wav|m4a|opus|flac)$/.test(f.name));
      box.append(h('h3', {}, `${files.length} audio file(s)` + (files.length > 100 ? ' (first 100 shown)' : '')),
        files.slice(0, 100).map((f) => player(joinPath(o.dir, f.name), f.name)));
    } catch (e) { box.append(h('p', { class: 'error' }, 'Could not list the output: ' + e.message)); }
  } else {
    const out = r.out || job.out;
    const res = r.results || [];
    box.append(h('p', {}, `${res.length} file(s) written to `, h('code', {}, out)));
    if ((r.errors || []).length) box.append(h('pre', { class: 'error' }, r.errors.map((e) => `Dialogue ${e.dialogue}: ${e.error}`).join('\n')));
    res.filter((x) => !x.skipped).forEach((x) => box.append(player(x.path || joinPath(out, x.file), `${x.file} (${x.duration || '?'} s)`)));
  }
}

// ------------------------------------------------------------------ voices tab
async function loadVoices() {
  if (!S.lang) return;
  const msg = $('#vmsg');
  if (!S.voices) {
    say(msg, 'Loading voices...');
    try { S.voices = await api('/api/voices?lang=' + encodeURIComponent(S.lang.code)); say(msg, ''); }
    catch (e) { say(msg, e.message, 'error'); return; }
  }
  if (S.voices.problem) say(msg, S.voices.problem, 'warn');
  const ls = clear($('#vlocale'));
  ls.append(h('option', { value: '' }, 'all'));
  S.lang.locales.forEach((l) => ls.append(h('option', { value: l.locale }, l.label)));
  renderVoices();
}
function renderVoices() {
  if (!S.voices) return;
  const g = $('#vgender').value, loc = $('#vlocale').value, s = $('#vsearch').value.toLowerCase();
  const labels = Object.fromEntries(S.lang.locales.map((l) => [l.locale, l.label]));
  const pairs = S.voices.pairs || {};
  const pr = clear($('#vpairs'));
  const pe = Object.entries(pairs).filter(([l]) => !loc || l === loc);
  if (pe.length) pr.append(h('details', {}, h('summary', {}, 'Default male/female pair per variety'), h('ul', {},
    pe.map(([l, p]) => h('li', {}, `${labels[l] || l}: F = ${String(p.F || '-').replace('edge:', '')}, M = ${String(p.M || '-').replace('edge:', '')}`)))));
  const groups = {};
  S.voices.voices.filter((v) => (!g || v.gender === g) && (!loc || v.locale === loc) &&
    (!s || (v.name + ' ' + v.key + ' ' + (v.personalities || []).join(' ')).toLowerCase().includes(s)))
    .forEach((v) => { (groups[v.locale] = groups[v.locale] || []).push(v); });
  const box = clear($('#vlist'));
  const names = Object.keys(groups).sort((a, b) => (a === S.locale ? -1 : b === S.locale ? 1 : a.localeCompare(b)));
  if (!names.length) box.append(h('p', { class: 'muted' }, 'No voices match.'));
  names.forEach((l) => {
    box.append(h('div', { class: 'vgroup' }, h('h3', {}, `${labels[l] || l} (${groups[l].length})`), groups[l].map((v) => {
      const st = h('span', { class: 'muted', 'aria-live': 'polite' });
      return h('div', { class: 'voice' },
        h('span', { class: 'nm' }, h('b', {}, v.name), ` (${v.gender === 'F' ? 'Female' : v.gender === 'M' ? 'Male' : '?'}) `,
          h('span', { class: 'tag' }, (v.personalities || []).join(', ')), v.multilingual ? h('span', { class: 'chip' }, 'multilingual') : null),
        h('button', { onclick: () => previewVoice(v.key, $('#vtext').value, parseFloat($('#vrate').value), st) }, 'Play'), st);
    })));
  });
}
['vgender', 'vlocale'].forEach((id) => $('#' + id).addEventListener('change', renderVoices));
$('#vsearch').addEventListener('input', renderVoices);
$('#vrate').addEventListener('input', (e) => { $('#vrateout').textContent = (+e.target.value).toFixed(2); });
$('#vrefresh').addEventListener('click', async () => {
  const m = $('#vmsg'), b = $('#vrefresh'); b.disabled = true; say(m, 'Contacting Microsoft...');
  try { const r = await api('/api/voices/refresh', {}); S.voices = null; await loadVoices(); say(m, `Catalogue updated: ${r.voices} voices.`, 'ok'); }
  catch (e) { say(m, e.message, 'error'); }
  b.disabled = false;
});

let player1 = null;
async function previewVoice(voice, text, rate, status) {
  if (status) say(status, 'Synthesising...');
  try {
    const blob = await api('/api/preview', { lang: S.lang.code, voice, text, rate: rate || 1 });
    if (player1) { player1.pause(); URL.revokeObjectURL(player1.src); }
    player1 = new Audio(URL.createObjectURL(blob));
    await player1.play();
    if (status) say(status, '');
    return player1;
  } catch (e) { if (status) say(status, e.message, 'error'); else alert(e.message); }
}

// ------------------------------------------------------------------ quick speak
async function fillSpeakVoices() {
  if (!S.lang) return;
  if (!S.voices) { try { S.voices = await api('/api/voices?lang=' + encodeURIComponent(S.lang.code)); } catch (e) { say($('#smsg'), e.message, 'error'); return; } }
  const sel = clear($('#svoice')), pair = (S.voices.pairs || {})[S.locale] || {};
  const strip = (r) => String(r || '').replace(/^edge:/, '');
  sel.append(h('option', { value: 'gender:F' }, 'Default female' + (pair.F ? ' (' + strip(pair.F) + ')' : '')),
    h('option', { value: 'gender:M' }, 'Default male' + (pair.M ? ' (' + strip(pair.M) + ')' : '')));
  sel.append(h('optgroup', { label: 'Any voice' }, S.voices.voices.map((v) =>
    h('option', { value: v.key }, `${v.key} (${v.gender}) ${(v.personalities || []).join(', ')}`))));
}
$('#srate').addEventListener('input', (e) => { $('#srateout').textContent = (+e.target.value).toFixed(2); });
function speakTarget() {
  const v = $('#svoice').value;
  return v.startsWith('gender:') ? { gender: v.slice(7) } : { voice: v };
}
$('#spreview').addEventListener('click', async () => {
  const m = $('#smsg'), t = $('#stext').value.trim();
  if (!t) { say(m, 'Enter some text.', 'error'); return; }
  let voice = speakTarget().voice;
  if (!voice) { const p = (S.voices.pairs || {})[S.locale] || {}; voice = String(p[speakTarget().gender] || '').replace(/^edge:/, ''); }
  if (!voice) { say(m, 'No default voice for this variety; pick one.', 'error'); return; }
  await previewVoice(voice, t, parseFloat($('#srate').value), m);
});
$('#ssave').addEventListener('click', async () => {
  const m = $('#smsg'), t = $('#stext').value.trim();
  if (!t) { say(m, 'Enter some text.', 'error'); return; }
  const body = { lang: S.lang.code, text: t, locale: S.locale, rate: parseFloat($('#srate').value), ...speakTarget() };
  if ($('#sout').value.trim()) body.out = $('#sout').value.trim();
  say(m, 'Saving...');
  try {
    const r = await api('/api/speak', body);
    say(m, `Saved ${r.file} (${r.seconds} s, ${r.bytes} bytes, voice ${r.voice})`, 'ok');
    const a = $('#saudio'); a.hidden = false; a.src = fileUrl(r.file);
  } catch (e) { say(m, e.message, 'error'); }
});

init();
