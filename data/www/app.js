'use strict';
// Kameralarm – webpagina
// Lokaal testen zonder ESP32: open index.html rechtstreeks of voeg ?mock=1 toe.

const $ = (id) => document.getElementById(id);
const MOCK = location.protocol === 'file:' || new URLSearchParams(location.search).has('mock');

let state = null;
let soundUnlocked = false;
let audioCtx = null;
let sirenTimer = null;
let lastLogRefresh = 0;
let lastStateName = null;

// ---------- Pincode ----------
function getPin() { try { return localStorage.getItem('pin') || ''; } catch { return ''; } }
function setPin(p) { try { localStorage.setItem('pin', p); } catch {} }

function askPin() {
  return new Promise((resolve) => {
    const dlg = $('pinDialog');
    $('pinInput').value = '';
    dlg.returnValue = '';
    dlg.onclose = () => resolve(dlg.returnValue === 'ok' ? $('pinInput').value.trim() : null);
    dlg.showModal();
    $('pinInput').focus();
  });
}

// POST met pincode; vraagt de pincode opnieuw bij een fout.
async function post(path, params = {}) {
  let pin = getPin();
  for (let attempt = 0; attempt < 3; attempt++) {
    if (!pin) { pin = await askPin(); if (!pin) return null; }
    const res = await api(path, { ...params, pin });
    if (res.status === 429) { toast('Te veel foute pogingen – wacht 1 minuut'); return null; }
    if (res.status !== 403) { setPin(pin); return res; }
    toast('Verkeerde pincode');
    pin = '';
  }
  return null;
}

async function api(path, params) {
  if (MOCK) return mockApi(path, params);
  const body = new URLSearchParams(params);
  return fetch(path, { method: 'POST', body });
}

// ---------- Live status ----------
function connect() {
  if (MOCK) { setInterval(() => render(mockState()), 300); $('conn').className = 'conn on'; return; }
  const ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onopen = () => { $('conn').className = 'conn on'; };
  ws.onmessage = (ev) => { try { render(JSON.parse(ev.data)); } catch {} };
  ws.onclose = () => { $('conn').className = 'conn off'; setTimeout(connect, 2000); };
  ws.onerror = () => ws.close();
}

const STATE_INFO = {
  uit: 'Alarm staat uit',
  inschakelen: 'Verlaat nu de kamer…',
  kalibreren: 'Basisafstand meten… blijf uit de straal',
  bewaken: 'Je kamer wordt bewaakt',
  controle: 'Tripwire onderbroken – wacht op bewegingssensor',
  vooralarm: 'Voorwaarschuwing – schakel nu uit!',
  alarm: 'ALARM!',
};

function render(s) {
  state = s;
  const card = $('statusCard');
  card.dataset.state = s.state;
  $('stateText').textContent = s.state;
  $('countdown').textContent = (STATE_INFO[s.state] || '') + (s.left ? ` (${s.left} s)` : '');

  const armed = s.state !== 'uit';
  const btn = $('armBtn');
  btn.textContent = armed ? 'Uitschakelen' : 'Inschakelen';
  btn.classList.toggle('disarm', armed);

  $('distance').textContent = s.distance < 0 ? 'geen echo' : `${s.distance} cm`;
  $('baseline').textContent = s.baseline == null ? 'nog niet gemeten' : s.baseline < 0 ? 'geen echo' : `${s.baseline} cm`;
  $('pir').textContent = s.pir ? '🟠 beweging' : '⚪ rust';
  $('entries').textContent = s.entries;

  const max = 250;
  $('meterBar').style.width = s.distance < 0 ? '100%' : `${Math.min(100, (s.distance / max) * 100)}%`;
  const base = $('meterBase');
  if (s.baseline > 0) { base.style.display = 'block'; base.style.left = `${Math.min(100, (s.baseline / max) * 100)}%`; }
  else base.style.display = 'none';

  $('soundInfo').textContent = s.sound
    ? '✅ Eigen mp3 staat op het apparaat.'
    : 'Nog geen mp3 – er speelt een ingebouwde sirene. Kies hieronder een mp3 (max. ~1,5 MB).';
  $('irCode').textContent = s.irLearning ? 'wacht op knop…' : s.settings.irToggleCode;

  fillSettings(s.settings);
  handleSound(s);

  if (s.state !== lastStateName || Date.now() - lastLogRefresh > 15000) loadLog();
  lastStateName = s.state;
}

let settingsFilled = false;
function fillSettings(st) {
  const form = $('settingsForm');
  if (settingsFilled && form.contains(document.activeElement)) return;
  for (const [k, v] of Object.entries(st)) {
    const el = form.elements[k];
    if (!el) continue;
    if (el.type === 'checkbox') el.checked = !!v; else el.value = v;
  }
  settingsFilled = true;
}

// ---------- Geluid ----------
function unlockSound() {
  audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
  audioCtx.resume();
  const a = $('alarmAudio');
  a.src = MOCK ? '' : '/alarm.mp3';
  a.muted = true;
  a.play().then(() => { a.pause(); a.muted = false; a.currentTime = 0; }).catch(() => { a.muted = false; });
  soundUnlocked = true;
  beep(880, 0.15);
  const b = $('soundBtn');
  b.textContent = '🔊 Geluid staat aan op dit toestel';
  b.classList.add('ok');
}

function beep(freq = 1000, dur = 0.12, vol = 0.3) {
  if (!audioCtx) return;
  const o = audioCtx.createOscillator();
  const g = audioCtx.createGain();
  o.frequency.value = freq;
  o.type = 'square';
  g.gain.value = vol;
  o.connect(g).connect(audioCtx.destination);
  o.start();
  o.stop(audioCtx.currentTime + dur);
}

function startSiren() {
  if (sirenTimer) return;
  let high = false;
  sirenTimer = setInterval(() => { high = !high; beep(high ? 960 : 640, 0.45, 0.4); }, 500);
}
function stopSiren() { clearInterval(sirenTimer); sirenTimer = null; }

let playingFor = null;
function handleSound(s) {
  const a = $('alarmAudio');
  if (s.state === 'alarm') {
    if (playingFor === 'alarm') return;
    playingFor = 'alarm';
    if (navigator.vibrate) navigator.vibrate([400, 200, 400, 200, 400]);
    if (!soundUnlocked) { toast('🚨 ALARM! Tik op "Geluid inschakelen" om het geluid te horen.'); return; }
    if (s.sound && !MOCK) {
      a.src = '/alarm.mp3?' + Date.now();
      a.play().catch(startSiren);
    } else startSiren();
  } else {
    if (playingFor === 'alarm') { a.pause(); a.currentTime = 0; stopSiren(); }
    playingFor = s.state;
  }
}

// rustige piep elke seconde tijdens het vooralarm
setInterval(() => { if (state && state.state === 'vooralarm' && soundUnlocked) beep(1200, 0.1, 0.25); }, 1000);

// ---------- Logboek ----------
const ICONS = {
  'opstart': '🔌', 'ingeschakeld': '🟢', 'uitgeschakeld': '⚪', 'binnenkomst': '🚪',
  'alarm': '🚨', 'tripwire zonder PIR': '❔', 'alarm gestopt': '⏹️',
};

async function loadLog() {
  lastLogRefresh = Date.now();
  const ul = $('log');
  const pin = getPin();
  if (!MOCK && !pin) { showLogLocked(); return; }
  try {
    let data;
    if (MOCK) data = mockLog();
    else {
      const res = await fetch('/api/log?pin=' + encodeURIComponent(pin));
      if (res.status === 403) { setPin(''); showLogLocked(); return; }
      if (!res.ok) return;
      data = await res.json();
    }
    $('logCount').textContent = `${data.count} binnenkomst${data.count === 1 ? '' : 'en'}`;
    ul.innerHTML = '';
    if (!data.entries.length) { ul.innerHTML = '<li><span class="empty">Nog niets gebeurd.</span></li>'; return; }
    for (const e of [...data.entries].reverse()) {
      const li = document.createElement('li');
      const when = e.t
        ? new Date(e.t * 1000).toLocaleString('nl-BE', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit' })
        : `tijd onbekend (${e.up} s na opstart)`;
      li.innerHTML = `<span class="ico"></span><span class="what"></span><span class="when"></span>`;
      li.querySelector('.ico').textContent = ICONS[e.type] || '•';
      li.querySelector('.what').textContent = e.type;
      if (e.detail) {
        const d = document.createElement('span');
        d.className = 'detail';
        d.textContent = ' – ' + e.detail;
        li.querySelector('.what').append(d);
      }
      li.querySelector('.when').textContent = when;
      ul.append(li);
    }
  } catch { /* volgende keer opnieuw */ }
}

// Logboek is beveiligd met de pincode: zonder pincode een knop tonen.
function showLogLocked() {
  $('logCount').textContent = '';
  const ul = $('log');
  ul.innerHTML = '<li><button id="unlockLogBtn" class="btn">🔒 Logboek tonen</button></li>';
  $('unlockLogBtn').onclick = async () => {
    const pin = await askPin();
    if (pin) { setPin(pin); loadLog(); }
  };
}

// ---------- Acties ----------
function toast(msg, ms = 3000) {
  const t = $('toast');
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { t.hidden = true; }, ms);
}

$('armBtn').onclick = async () => {
  if (!soundUnlocked) unlockSound();
  const armed = state && state.state !== 'uit';
  const res = await post(armed ? '/api/disarm' : '/api/arm');
  if (res && res.ok) toast(armed ? 'Alarm uitgeschakeld' : 'Alarm wordt ingeschakeld – verlaat de kamer');
};

$('soundBtn').onclick = unlockSound;

$('calBtn').onclick = async () => {
  const res = await post('/api/calibrate');
  if (res && res.ok) toast('Basisafstand wordt gemeten…');
};

$('clearLogBtn').onclick = async () => {
  const res = await post('/api/log/clear');
  if (res && res.ok) { toast('Logboek gewist'); loadLog(); }
};

$('irLearnBtn').onclick = async () => {
  const res = await post('/api/irlearn');
  if (res && res.ok) toast('Druk nu op de gewenste knop van de afstandsbediening', 5000);
};

$('testNotifyBtn').onclick = async () => {
  const res = await post('/api/testnotify');
  if (res && res.ok) toast('Testmelding verstuurd – kijk op je gsm');
};

$('logoutBtn').onclick = () => { setPin(''); toast('Pincode vergeten op dit toestel'); };

$('settingsForm').onsubmit = async (ev) => {
  ev.preventDefault();
  const f = ev.target.elements;
  const params = {};
  for (const el of f) {
    if (!el.name) continue;
    params[el.name] = el.type === 'checkbox' ? (el.checked ? '1' : '0') : el.value;
  }
  const res = await post('/api/settings', params);
  if (res && res.ok) toast('Instellingen opgeslagen');
};

$('previewBtn').onclick = () => {
  if (!soundUnlocked) unlockSound();
  const a = $('alarmAudio');
  const file = $('mp3').files[0];
  if (!a.paused) { a.pause(); a.currentTime = 0; $('previewBtn').textContent = '▶️ Beluisteren'; return; }
  a.src = file ? URL.createObjectURL(file) : '/alarm.mp3?' + Date.now();
  a.play().then(() => { $('previewBtn').textContent = '⏹️ Stop'; }).catch(() => toast('Geen mp3 om af te spelen'));
};

$('deleteSoundBtn').onclick = async () => {
  const res = await post('/api/sound/delete');
  if (res && res.ok) toast('mp3 verwijderd – de ingebouwde sirene wordt gebruikt');
};

$('uploadBtn').onclick = async () => {
  const file = $('mp3').files[0];
  if (!file) return toast('Kies eerst een mp3-bestand');
  if (file.size > 1.6 * 1024 * 1024) return toast('Te groot: max. ~1,5 MB. Knip of comprimeer de mp3.');
  let pin = getPin() || await askPin();
  if (!pin) return;
  if (MOCK) return toast('(mock) mp3 zou nu geüpload worden');

  const fd = new FormData();
  fd.append('file', file, 'alarm.mp3');
  const xhr = new XMLHttpRequest();
  const bar = $('uploadProgress');
  bar.hidden = false;
  xhr.upload.onprogress = (e) => { if (e.lengthComputable) bar.value = (e.loaded / e.total) * 100; };
  xhr.onload = () => {
    bar.hidden = true;
    if (xhr.status === 200) { setPin(pin); toast('✅ mp3 opgeslagen'); }
    else if (xhr.status === 403) { setPin(''); toast('Verkeerde pincode'); }
    else toast(xhr.responseText || 'Upload mislukt');
  };
  xhr.onerror = () => { bar.hidden = true; toast('Upload mislukt'); };
  xhr.open('POST', '/upload?pin=' + encodeURIComponent(pin));
  xhr.send(fd);
};

// ---------- Mock (testen zonder ESP32) ----------
const mock = {
  state: 'uit', until: 0, baseline: null, entries: 2, pinOk: '1234',
  settings: { thresholdCm: 20, confirmCount: 2, pirConfirm: true, pirWindowS: 10, exitDelayS: 8, entryDelayS: 6, alarmDurationS: 15, buzzerEnabled: true, irToggleCode: '0xFFA25D' },
  log: [
    { t: Date.now() / 1000 - 7200, up: 10, type: 'opstart', detail: '' },
    { t: Date.now() / 1000 - 7000, up: 200, type: 'ingeschakeld', detail: 'via afstandsbediening' },
    { t: Date.now() / 1000 - 3600, up: 3600, type: 'binnenkomst', detail: 'afstand 41 cm (basis 96 cm), PIR bevestigd' },
    { t: Date.now() / 1000 - 3590, up: 3610, type: 'alarm', detail: '' },
  ],
};
function mockSet(s, secs) { mock.state = s; mock.until = secs ? Date.now() + secs * 1000 : 0; mock.log.push({ t: Date.now() / 1000, up: 0, type: s, detail: '(mock)' }); }
function mockState() {
  const left = mock.until ? Math.max(0, Math.ceil((mock.until - Date.now()) / 1000)) : 0;
  if (mock.until && left === 0) {
    if (mock.state === 'inschakelen') { mock.baseline = 96; mockSet('bewaken'); setTimeout(() => { if (mock.state === 'bewaken') { mock.entries++; mockSet('vooralarm', mock.settings.entryDelayS); } }, 6000); }
    else if (mock.state === 'vooralarm') mockSet('alarm', mock.settings.alarmDurationS);
    else if (mock.state === 'alarm') mockSet('bewaken');
  }
  const near = mock.state === 'vooralarm' || mock.state === 'alarm';
  return {
    state: mock.state, left, distance: near ? 40 + Math.round(Math.random() * 10) : 95 + Math.round(Math.random() * 2),
    baseline: mock.baseline, pir: near, entries: mock.entries, sound: false, irLearning: false, settings: mock.settings,
  };
}
function mockApi(path, params) {
  if (params.pin !== mock.pinOk) return { ok: false, status: 403 };
  if (path === '/api/arm' && mock.state === 'uit') mockSet('inschakelen', mock.settings.exitDelayS);
  if (path === '/api/disarm') mockSet('uit');
  if (path === '/api/settings') for (const k in mock.settings) if (k in params) mock.settings[k] = params[k] === '1' ? true : params[k] === '0' && typeof mock.settings[k] === 'boolean' ? false : params[k];
  if (path === '/api/log/clear') { mock.log = []; mock.entries = 0; }
  return { ok: true, status: 200 };
}
function mockLog() { return { count: mock.entries, entries: mock.log }; }

if (MOCK) toast('Testmodus zonder ESP32 – pincode is 1234', 5000);
connect();
