// app.js

// utilities: show/hide
const show = el => el.classList.remove('hidden');
const hide = el => el.classList.add('hidden');

// element refs & state
const grid = document.getElementById('tileGrid');
const hero = document.querySelector('.hero p');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const chooseBtn = document.getElementById('chooseFileBtn');
const uploadBtn = document.getElementById('uploadBtn');
const imgPreview = document.getElementById('imgPreview');

const resultCon = document.getElementById('resultContainer');
const rawOutput = document.getElementById('rawOutput');
const translateBtn = document.getElementById('translateBtn');
const transOutput = document.getElementById('translatedOutput');
const ttsSection = document.getElementById('ttsSection');
const ttsBtn = document.getElementById('ttsBtn');
const ttsAudio = document.getElementById('ttsAudio');
const backBtn = document.getElementById('backBtn');
const langSelect = document.getElementById('langSelect');
const previewSection = document.getElementById('previewSection');
const outlinedImage = document.getElementById('outlinedImage');
const lineOutputs = document.getElementById('lineOutputs');
const loadingOverlay = document.getElementById('loadingOverlay');


let currentModel = null;
let selectedFile = null;

// ─── Theme management ─────────────────────────────────────────────────────────

function initTheme() {
  const saved = localStorage.getItem('theme')
    || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
}

function toggleTheme() {
  const curr = document.documentElement.getAttribute('data-theme');
  const next = curr === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const sun = 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z';
  const moon = 'M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z';
  document.querySelectorAll('#themeIcon path').forEach(path => {
    path.setAttribute('d', theme === 'dark' ? sun : moon);
  });
}

// expose toggleTheme globally for inline onclick
window.toggleTheme = toggleTheme;

// ─── Model selection & drop-zone ─────────────────────────────────────────────

grid.addEventListener('click', e => {
  const tile = e.target.closest('.clickable-section');
  if (!tile) return;

  currentModel = tile.dataset.view;
  hide(grid);
  hide(hero);
  show(dropZone);

  // Show lang selector only for General OCR (model1)
  if (currentModel === 'model1') {
    show(document.getElementById('langSelectContainer'));
  } else {
    hide(document.getElementById('langSelectContainer'));
  }

});

// dragenter/dragover highlight
['dragenter', 'dragover'].forEach(evt =>
  dropZone.addEventListener(evt, e => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  })
);

// dragleave/drop & file-picker → prepareFiles
['dragleave', 'drop'].forEach(evt =>
  dropZone.addEventListener(evt, e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (evt === 'drop') prepareFiles(e.dataTransfer.files);
  })
);

chooseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => prepareFiles(fileInput.files));

// ─── Preview & submit ────────────────────────────────────────────────────────

function prepareFiles(files) {
  if (!files.length) return;
  selectedFile = files[0];
  imgPreview.src = URL.createObjectURL(selectedFile);
  imgPreview.onload = () => URL.revokeObjectURL(imgPreview.src);
  show(imgPreview);
  show(uploadBtn);
}

uploadBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  hide(uploadBtn);
  hide(imgPreview);
  hide(dropZone);
  show(loadingOverlay);                     // 🔄 show loader here

  const form = new FormData();
  form.append('file', selectedFile);
  form.append('lang', langSelect.value);

  try {
    const res = await fetch(`/api/${currentModel}`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();

    if (currentModel === 'model1') {
      rawOutput.textContent = data.text;
      lineOutputs.innerHTML = data.lines
        .map((l, i) => <div class="line-box">${i + 1}: ${l}</div>).join('');
    } else {                // model2 → show markdown
      rawOutput.textContent = data.markdown;
      lineOutputs.innerHTML = '';     // no boxes
    }
    outlinedImage.src = data.image;     // already fixed key
    show(outlinedImage);

    lineOutputs.innerHTML = data.lines
      .map((l, i) => `<div class="line-box">${i + 1}: ${l}</div>`)
      .join('');

    show(previewSection);
    show(resultCon);
    if (data.lang === 'en') show(ttsSection);

  } catch (err) {
    alert('Upload failed: ' + err.message);
    show(dropZone);
  } finally {
    hide(loadingOverlay);                   // ✅ always hide overlay
  }
});



// ─── Translate & TTS ─────────────────────────────────────────────────────────

translateBtn.addEventListener('click', async () => {
  const res = await fetch('/api/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: rawOutput.textContent, target: 'en' })
  });
  const { translatedText } = await res.json();
  transOutput.textContent = translatedText;
  show(translateResultWrap);
  show(transOutput);
  show(document.querySelector('button[data-copy="#translatedOutput"]'));
  show(document.querySelector('button[data-download="#translatedOutput"]'));
});

ttsBtn.addEventListener('click', async () => {
  const res = await fetch('/api/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: rawOutput.textContent, voice: 'default' })
  });
  const blob = await res.blob();
  ttsAudio.src = URL.createObjectURL(blob);
  show(ttsAudio);
});

// ─── Copy, Download & Back ───────────────────────────────────────────────────

resultCon.addEventListener('click', e => {
  let btn;
  if (btn = e.target.closest('button[data-copy]')) {
    const txt = document.querySelector(btn.dataset.copy).textContent;
    navigator.clipboard.writeText(txt);
  }
  if (btn = e.target.closest('button[data-download]')) {
    const txt = document.querySelector(btn.dataset.download).textContent;
    const blob = new Blob([txt], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = btn.dataset.filename;
    a.click();
    URL.revokeObjectURL(url);
  }
});

backBtn.addEventListener('click', () => {
  hide(resultCon);
  hide(ttsSection);
  hide(transOutput);
  hide(document.getElementById('langSelectContainer')); // hide when going back
  rawOutput.textContent = '';
  transOutput.textContent = '';
  show(grid);
});


// ─── Initialize ──────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', initTheme);
