
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

// ─── Hub page redirect ──────────────────────────────────────
document.addEventListener('click', e => {
  const tile = e.target.closest('.clickable-section');
  if (tile && tile.dataset.target) {
    window.location.href = tile.dataset.target;   // jump to chosen port
  }
});

// ─── Initialize ──────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', initTheme);
