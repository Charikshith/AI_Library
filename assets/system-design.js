// ============================== THEME TOGGLE ==============================
(function () {
  const themeToggle = document.getElementById('themeToggle');
  const html = document.documentElement;
  const saved = localStorage.getItem('theme') ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  html.setAttribute('data-theme', saved);
  if (themeToggle) {
    themeToggle.textContent = saved === 'dark' ? '☀️' : '🌙';
    themeToggle.addEventListener('click', () => {
      const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      themeToggle.textContent = next === 'dark' ? '☀️' : '🌙';
    });
  }
})();

// ============================== READING PROGRESS ==============================
(function () {
  const bar = document.getElementById('progressBar');
  if (!bar) return;
  window.addEventListener('scroll', () => {
    const h = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
  }, { passive: true });
})();

// ============================== TOC ACTIVE LINK ==============================
(function () {
  const tocLinks = document.querySelectorAll('#tocList a');
  if (!tocLinks.length) return;
  const sections = Array.from(tocLinks)
    .map(a => document.querySelector(a.getAttribute('href')))
    .filter(Boolean);
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const id = entry.target.id;
      const link = document.querySelector(`#tocList a[href="#${id}"]`);
      if (entry.isIntersecting && link) {
        tocLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
      }
    });
  }, { rootMargin: '-80px 0px -70% 0px', threshold: 0 });
  sections.forEach(s => observer.observe(s));
})();

// ============================== MOBILE MENU ==============================
(function () {
  const menuBtn = document.getElementById('menuBtn');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');
  if (!menuBtn || !sidebar) return;
  menuBtn.addEventListener('click', () => {
    sidebar.classList.add('open');
    if (overlay) overlay.classList.add('show');
  });
  if (overlay) overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
  });
  document.querySelectorAll('#tocList a').forEach(a => {
    a.addEventListener('click', () => {
      sidebar.classList.remove('open');
      if (overlay) overlay.classList.remove('show');
    });
  });
})();

// ============================== COPY CODE BUTTONS ==============================
(function () {
  document.querySelectorAll('pre').forEach(pre => {
    if (pre.querySelector('.copy-btn')) return;
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = 'Copy';
    btn.addEventListener('click', async () => {
      const code = pre.querySelector('code') ? pre.querySelector('code').innerText : pre.innerText;
      try {
        await navigator.clipboard.writeText(code);
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1500);
      } catch (e) { btn.textContent = 'Failed'; }
    });
    pre.appendChild(btn);
  });
})();

// ============================== FLIP CARDS ==============================
(function () {
  document.querySelectorAll('.flip-card').forEach(card => {
    card.addEventListener('click', () => card.classList.toggle('flipped'));
  });
})();

// ============================== PRISM HIGHLIGHT ==============================
if (typeof Prism !== 'undefined') Prism.highlightAll();
