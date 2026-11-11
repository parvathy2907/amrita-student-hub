// AMRITA Student Hub — small progressive enhancements (the site works without JS).
(() => {
  // Mobile navigation toggle
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  // Club filter + search on the home page
  const grid = document.getElementById('club-grid');
  if (grid) {
    const cards = [...grid.querySelectorAll('.card')];
    const chips = [...document.querySelectorAll('.chip')];
    const search = document.getElementById('club-search');
    const empty = document.getElementById('no-results');
    let category = 'All';
    const apply = () => {
      const q = (search?.value || '').trim().toLowerCase();
      let shown = 0;
      cards.forEach((card) => {
        const okCat = category === 'All' || card.dataset.category === category;
        const okText = !q || card.textContent.toLowerCase().includes(q);
        card.hidden = !(okCat && okText);
        if (!card.hidden) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    };
    chips.forEach((chip) => chip.addEventListener('click', () => {
      category = chip.dataset.filter;
      chips.forEach((c) => c.setAttribute('aria-pressed', String(c === chip)));
      apply();
    }));
    search?.addEventListener('input', apply);
  }

  // Lightbox for gallery images
  const triggers = [...document.querySelectorAll('[data-lightbox]')];
  if (triggers.length) {
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Image viewer');
    box.innerHTML = `
      <img alt="">
      <button class="lb-close" aria-label="Close"><i class="fa-solid fa-xmark"></i></button>
      <button class="lb-prev" aria-label="Previous image"><i class="fa-solid fa-chevron-left"></i></button>
      <button class="lb-next" aria-label="Next image"><i class="fa-solid fa-chevron-right"></i></button>
      <div class="lb-count"></div>`;
    document.body.appendChild(box);
    const img = box.querySelector('img');
    const count = box.querySelector('.lb-count');
    let index = 0;
    let lastFocus = null;
    const show = (i) => {
      index = (i + triggers.length) % triggers.length;
      const t = triggers[index];
      img.src = t.dataset.lightbox;
      img.alt = t.querySelector('img')?.alt || '';
      count.textContent = `${index + 1} / ${triggers.length}`;
    };
    const open = (i) => {
      lastFocus = document.activeElement;
      show(i);
      box.classList.add('open');
      document.body.style.overflow = 'hidden';
      box.querySelector('.lb-close').focus();
    };
    const close = () => {
      box.classList.remove('open');
      document.body.style.overflow = '';
      lastFocus?.focus();
    };
    triggers.forEach((t, i) => t.addEventListener('click', (e) => { e.preventDefault(); open(i); }));
    box.querySelector('.lb-close').addEventListener('click', close);
    box.querySelector('.lb-prev').addEventListener('click', () => show(index - 1));
    box.querySelector('.lb-next').addEventListener('click', () => show(index + 1));
    box.addEventListener('click', (e) => { if (e.target === box) close(); });
    document.addEventListener('keydown', (e) => {
      if (!box.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(index - 1);
      if (e.key === 'ArrowRight') show(index + 1);
    });
  }

  // Only play videos while they are on screen (saves data and battery)
  const videos = document.querySelectorAll('video[data-autoplay]');
  if (videos.length && 'IntersectionObserver' in window) {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const io = new IntersectionObserver((entries) => {
      entries.forEach(({ target, isIntersecting }) => {
        if (isIntersecting && !reduce) target.play().catch(() => {});
        else target.pause();
      });
    }, { threshold: 0.35 });
    videos.forEach((v) => io.observe(v));
  }
})();
