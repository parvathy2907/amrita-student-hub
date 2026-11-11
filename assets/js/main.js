// AMRITA Student Hub — site-wide interactions.
// Everything here is progressive enhancement: the pages work without JavaScript.
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const header = $('.site-header');

  // ------------------------------------------------------------ header
  // Solid after scrolling, hides on scroll down and returns on scroll up,
  // with a reading-progress bar along its bottom edge.
  const bar = $('.progress-bar');
  let lastY = window.scrollY;
  let ticking = false;
  function onScroll() {
    const y = window.scrollY;
    header?.classList.toggle('scrolled', y > 40);
    const goingDown = y > lastY && y > 400;
    const hide = goingDown && !document.body.classList.contains('menu-open');
    header?.classList.toggle('hide', hide);
    document.body.classList.toggle('header-hidden', hide);
    lastY = y;
    if (bar) {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = `scaleX(${max > 0 ? Math.min(1, y / max) : 0})`;
    }
    toTop?.classList.toggle('show', y > 900);
    parallax(y);
    ticking = false;
  }
  window.addEventListener('scroll', () => {
    if (!ticking) { requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });

  // ------------------------------------------------------------ mobile menu
  const toggle = $('.nav-toggle');
  const nav = $('#site-nav');
  function setMenu(open) {
    nav.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('menu-open', open);
    if (open) setTimeout(() => $('a', nav)?.focus({ preventScroll: true }), 300);
  }
  if (toggle && nav) {
    toggle.addEventListener('click', () => setMenu(!nav.classList.contains('open')));
    $$('a', nav).forEach((a) => a.addEventListener('click', () => setMenu(false)));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); toggle.focus(); }
    });
    window.matchMedia('(min-width: 901px)').addEventListener('change', (e) => { if (e.matches) setMenu(false); });
  }

  // ------------------------------------------------------------ back to top
  const toTop = document.createElement('button');
  toTop.className = 'to-top';
  toTop.type = 'button';
  toTop.setAttribute('aria-label', 'Back to top');
  toTop.innerHTML = '<i class="fa-solid fa-arrow-up" aria-hidden="true"></i>';
  toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' }));
  document.body.appendChild(toTop);

  // ------------------------------------------------------------ scroll reveal
  const revealEls = $$('[data-reveal]');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('in'));
  }

  // ------------------------------------------------------------ count-up numbers
  const counters = $$('[data-count]');
  if (counters.length && !reduceMotion && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        const el = en.target;
        const target = Number(el.dataset.count);
        const suffix = el.querySelector('sup')?.outerHTML || '';
        const start = performance.now() + Number(el.dataset.delay || 0);
        const tick = (t) => {
          const p = Math.min(1, Math.max(0, (t - start) / 1400));
          el.innerHTML = Math.round(target * (1 - Math.pow(1 - p, 4))) + suffix;
          if (p < 1) requestAnimationFrame(tick);
        };
        el.innerHTML = '0' + suffix;
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.5 });
    counters.forEach((c) => io.observe(c));
  }

  // ------------------------------------------------------------ parallax hero
  const parallaxEls = reduceMotion ? [] : $$('[data-parallax]');
  function parallax(y) {
    parallaxEls.forEach((el) => {
      if (y < window.innerHeight * 1.2) el.style.transform = `translate3d(0, ${y * Number(el.dataset.parallax)}px, 0)`;
    });
  }

  // ------------------------------------------------------------ club filters
  const grid = $('#club-grid');
  if (grid) {
    const cards = $$('.club-card-home', grid);
    const chips = $$('.chip');
    const chipBox = $('.chips');
    const search = $('#club-search');
    const empty = $('#no-results');
    let category = 'All';

    const indicator = document.createElement('span');
    indicator.className = 'chip-indicator';
    chipBox.prepend(indicator);
    const moveIndicator = () => {
      const active = chips.find((c) => c.getAttribute('aria-pressed') === 'true');
      if (!active) return;
      indicator.style.width = `${active.offsetWidth}px`;
      indicator.style.height = `${active.offsetHeight}px`;
      indicator.style.transform = `translate(${active.offsetLeft}px, ${active.offsetTop}px)`;
    };
    moveIndicator();
    window.addEventListener('resize', moveIndicator);
    document.fonts?.ready.then(moveIndicator);

    const apply = () => {
      const q = (search?.value || '').trim().toLowerCase();
      let shown = 0;
      cards.forEach((card) => {
        const ok = (category === 'All' || card.dataset.category === category) && (!q || card.textContent.toLowerCase().includes(q));
        card.hidden = !ok;
        card.classList.remove('pop');
        if (ok) {
          card.style.setProperty('--d', `${Math.min(shown, 8) * 45}ms`);
          void card.offsetWidth;
          card.classList.add('pop');
          shown++;
        }
      });
      if (empty) empty.hidden = shown > 0;
    };
    const setCategory = (cat) => {
      category = cat;
      chips.forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.filter === cat)));
      moveIndicator();
      apply();
    };
    chips.forEach((chip) => chip.addEventListener('click', () => setCategory(chip.dataset.filter)));
    search?.addEventListener('input', apply);

    // Links like #clubs?cat=Technical (from the "what are you into" tiles)
    $$('[data-filter-link]').forEach((a) => a.addEventListener('click', () => setCategory(a.dataset.filterLink)));
  }

  // ------------------------------------------------------------ section tabs (club pages)
  const tabs = $$('.tabs a[href^="#"]');
  if (tabs.length && 'IntersectionObserver' in window) {
    const sections = tabs.map((a) => $(a.getAttribute('href'))).filter(Boolean);
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          tabs.forEach((a) => a.classList.toggle('active', a.getAttribute('href') === `#${en.target.id}`));
          const active = tabs.find((a) => a.classList.contains('active'));
          active?.scrollIntoView({ block: 'nearest', inline: 'center' });
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach((s) => io.observe(s));
  }

  // ------------------------------------------------------------ lightbox
  const triggers = $$('[data-lightbox]');
  if (triggers.length) {
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Photo viewer');
    box.innerHTML = `
      <img alt="">
      <button class="lb-close" type="button" aria-label="Close"><i class="fa-solid fa-xmark"></i></button>
      <button class="lb-prev" type="button" aria-label="Previous photo"><i class="fa-solid fa-chevron-left"></i></button>
      <button class="lb-next" type="button" aria-label="Next photo"><i class="fa-solid fa-chevron-right"></i></button>
      <div class="lb-count" aria-live="polite"></div>`;
    document.body.appendChild(box);
    const img = $('img', box);
    const count = $('.lb-count', box);
    let index = 0;
    let lastFocus = null;
    const show = (i) => {
      index = (i + triggers.length) % triggers.length;
      const t = triggers[index];
      img.classList.add('swap');
      const next = new Image();
      next.onload = next.onerror = () => {
        img.src = t.dataset.lightbox;
        img.alt = $('img', t)?.alt || '';
        requestAnimationFrame(() => img.classList.remove('swap'));
      };
      next.src = t.dataset.lightbox;
      count.textContent = `${index + 1} / ${triggers.length}`;
    };
    const open = (i) => {
      lastFocus = document.activeElement;
      show(i);
      box.classList.add('open');
      document.body.style.overflow = 'hidden';
      $('.lb-close', box).focus();
    };
    const close = () => {
      box.classList.remove('open');
      document.body.style.overflow = '';
      lastFocus?.focus();
    };
    triggers.forEach((t, i) => t.addEventListener('click', (e) => { e.preventDefault(); open(i); }));
    $('.lb-close', box).addEventListener('click', close);
    $('.lb-prev', box).addEventListener('click', () => show(index - 1));
    $('.lb-next', box).addEventListener('click', () => show(index + 1));
    box.addEventListener('click', (e) => { if (e.target === box) close(); });
    document.addEventListener('keydown', (e) => {
      if (!box.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(index - 1);
      if (e.key === 'ArrowRight') show(index + 1);
      if (e.key === 'Tab') { // keep focus inside the viewer
        const f = $$('button', box);
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      }
    });
    // Swipe on touch screens
    let sx = null;
    box.addEventListener('touchstart', (e) => { sx = e.touches[0].clientX; }, { passive: true });
    box.addEventListener('touchend', (e) => {
      if (sx === null) return;
      const dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
      sx = null;
    });
  }

  // ------------------------------------------------------------ videos play only on screen
  const videos = $$('video[data-autoplay]');
  if (videos.length && 'IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(({ target, isIntersecting }) => {
        if (isIntersecting) target.play().catch(() => {});
        else target.pause();
      });
    }, { threshold: 0.4 });
    videos.forEach((v) => io.observe(v));
  }

  // ------------------------------------------------------------ video cards (click to play with sound)
  $$('.video-card').forEach((card) => {
    const video = $('video', card);
    const btn = $('.play', card);
    btn.addEventListener('click', () => {
      $$('.video-card.playing video').forEach((v) => { if (v !== video) v.pause(); });
      video.controls = true;
      video.muted = false;
      video.play().catch(() => {});
      card.classList.add('playing');
      video.focus({ preventScroll: true });
    });
    video.addEventListener('ended', () => { card.classList.remove('playing'); video.controls = false; });
  });

  // ------------------------------------------------------------ mobile join bar (club pages)
  const joinBar = $('.join-bar');
  const hero = $('.club-hero2');
  const finale = $('.finale');
  if (joinBar && hero && 'IntersectionObserver' in window) {
    let heroVisible = true;
    let finaleVisible = false;
    const sync = () => joinBar.classList.toggle('show', !heroVisible && !finaleVisible);
    new IntersectionObserver(([en]) => { heroVisible = en.isIntersecting; sync(); }).observe(hero);
    if (finale) new IntersectionObserver(([en]) => { finaleVisible = en.isIntersecting; sync(); }).observe(finale);
  }

  onScroll();
})();
