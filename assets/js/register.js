// Registration: a three-step form with validation, a club picker, a review
// step, and a confetti + member-pass finish.
//
// Where submissions go:
//   Add data-endpoint="https://..." to <form id="register-form"> to POST the
//   answers as JSON to a form service (Formspree, Getform, a Google Apps Script
//   web app, your own API...). Without it the form runs in demo mode: everything
//   works, but the answers are not stored anywhere.
(() => {
  const form = document.getElementById('register-form');
  if (!form) return;

  const MAX_CLUBS = 3;
  const EMAIL_RE = /^[^\s@]+@([a-z0-9-]+\.)*amrita\.edu$/i;
  const ROLL_RE = /^[A-Z]{2}\.[A-Z]{2,4}\.[A-Z0-9]{3,6}\d{3,5}$/i;
  const PHONE_RE = /^(\+91)?[6-9]\d{9}$/;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const steps = $$('.step', form);
  const alertBox = $('#form-alert');
  const clubBoxes = $$('input[name="clubs"]', form);
  const success = $('#register-success');
  let current = 1;

  // ---------------------------------------------------------------- rules
  const rules = {
    name: (v) => (v.trim().length >= 2 ? '' : 'Please enter your full name.'),
    email: (v) => (!v.trim() ? 'Please enter your college email.'
      : EMAIL_RE.test(v.trim()) ? '' : 'Use your Amrita email, e.g. name@cb.students.amrita.edu'),
    roll: (v) => (!v.trim() ? 'Please enter your roll number.'
      : ROLL_RE.test(v.trim()) ? '' : 'That doesn’t look like a roll number (e.g. CB.EN.U4CSE23001).'),
    programme: (v) => (v ? '' : 'Please choose your programme.'),
    phone: (v) => (!v.trim() || PHONE_RE.test(v.replace(/[\s-]/g, '')) ? '' : 'Enter a 10-digit Indian mobile number.'),
    year: () => ($('input[name="year"]:checked', form) ? '' : 'Please choose your year of study.'),
    clubs: () => (clubBoxes.some((b) => b.checked) ? '' : 'Pick at least one club to continue.'),
    consent: () => (form.elements.consent.checked ? '' : 'Please tick this box to submit.'),
  };
  const stepFields = { 1: ['name', 'email', 'roll', 'programme', 'phone', 'year'], 2: ['clubs'], 3: ['consent'] };
  const fieldEl = (name) => $(`[data-field="${name}"]`, form);
  const valueOf = (name) => {
    const el = form.elements[name];
    return el && typeof el.value === 'string' ? el.value : '';
  };

  function check(name, { showValid = true } = {}) {
    const msg = rules[name](valueOf(name));
    const f = fieldEl(name);
    if (!f) return msg;
    f.classList.toggle('invalid', Boolean(msg));
    if (f.classList.contains('fl')) f.classList.toggle('valid', !msg && showValid && valueOf(name).trim() !== '');
    const err = $('.error', f);
    if (err) err.textContent = msg;
    const input = $('input, select, textarea', f);
    if (input && f.classList.contains('fl')) input.setAttribute('aria-invalid', String(Boolean(msg)));
    return msg;
  }

  function shake(el) {
    if (reduceMotion || !el) return;
    el.classList.remove('shake');
    void el.offsetWidth; // restart the animation
    el.classList.add('shake');
    el.addEventListener('animationend', () => el.classList.remove('shake'), { once: true });
  }

  // Validate when leaving a field, then live while fixing it.
  Object.keys(rules).forEach((name) => {
    const f = fieldEl(name);
    if (!f) return;
    f.addEventListener('focusout', (e) => {
      if (!f.classList.contains('fl')) return;
      if (e.target.value !== '' || f.classList.contains('invalid')) check(name);
    });
    const live = () => { if (f.classList.contains('invalid') || f.classList.contains('valid')) check(name); };
    f.addEventListener('input', live);
    f.addEventListener('change', live);
  });

  // Floating label for <select> (no :placeholder-shown for selects).
  const programme = form.elements.programme;
  const syncSelect = () => programme.classList.toggle('filled', programme.value !== '');
  programme.addEventListener('change', syncSelect);
  programme.addEventListener('input', syncSelect);
  syncSelect();
  // Browser autofill and back/forward restores can fill fields without events.
  window.addEventListener('pageshow', syncSelect);
  setTimeout(syncSelect, 600);

  form.elements.roll.addEventListener('input', (e) => {
    const pos = e.target.selectionStart;
    e.target.value = e.target.value.toUpperCase().replace(/\s/g, '');
    e.target.setSelectionRange(pos, pos);
  });

  // ---------------------------------------------------------------- steps
  function showAlert(text) {
    $('span', alertBox).textContent = text;
    alertBox.classList.add('show');
  }
  const hideAlert = () => alertBox.classList.remove('show');
  // Clear the message as soon as everything on the current step is fixed.
  const maybeHideAlert = () => {
    if (alertBox.classList.contains('show') && stepFields[current].every((n) => !rules[n](valueOf(n)))) hideAlert();
  };
  form.addEventListener('input', maybeHideAlert);
  form.addEventListener('change', maybeHideAlert);

  function goTo(n, { focus = true } = {}) {
    const back = n < current;
    current = n;
    steps.forEach((s) => {
      const active = Number(s.dataset.step) === n;
      s.classList.toggle('active', active);
      s.classList.toggle('back', active && back);
    });
    $$('#progress li').forEach((li) => {
      const i = Number(li.dataset.step);
      li.classList.toggle('active', i === n);
      li.classList.toggle('done', i < n);
      if (i === n) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
    });
    $('#progress-fill').style.width = `${(n / 3) * 100}%`;
    hideAlert();
    if (n === 3) renderReview();
    const top = $('.reg-panel').getBoundingClientRect().top + window.scrollY - 80;
    if (window.scrollY > top) window.scrollTo({ top, behavior: reduceMotion ? 'auto' : 'smooth' });
    if (focus) {
      const h2 = $('.step.active h2');
      h2.setAttribute('tabindex', '-1');
      setTimeout(() => h2.focus({ preventScroll: true }), 60);
    }
  }

  function validateStep(n) {
    const bad = stepFields[n].filter((name) => check(name));
    if (!bad.length) return true;
    const first = fieldEl(bad[0]);
    showAlert(bad.length === 1 ? (n === 2 ? rules.clubs() : 'Please fix the highlighted field.') : `Please fix the ${bad.length} highlighted fields.`);
    bad.forEach((name) => shake(fieldEl(name)));
    $('input:not([disabled]), select, textarea', first)?.focus({ preventScroll: true });
    first.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
    return false;
  }

  $$('[data-next]', form).forEach((btn) => btn.addEventListener('click', () => {
    if (validateStep(current)) goTo(current + 1);
  }));
  $$('[data-back]', form).forEach((btn) => btn.addEventListener('click', () => goTo(current - 1)));

  // Enter moves forward on step 1 (but not inside the textarea).
  form.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'BUTTON') return;
    if (current < 3) {
      e.preventDefault();
      if (validateStep(current)) goTo(current + 1);
    }
  });

  // ---------------------------------------------------------------- clubs
  const slots = $('#slots');
  function renderTray() {
    const chosen = clubBoxes.filter((b) => b.checked);
    $('#pick-count').textContent = chosen.length;
    clubBoxes.forEach((b) => { b.disabled = !b.checked && chosen.length >= MAX_CLUBS; });
    slots.innerHTML = '';
    for (let i = 0; i < MAX_CLUBS; i++) {
      const b = chosen[i];
      const slot = document.createElement('span');
      if (b) {
        slot.className = 'slot filled';
        const img = document.createElement('img');
        img.src = b.dataset.img; img.alt = '';
        const remove = document.createElement('button');
        remove.type = 'button';
        remove.setAttribute('aria-label', `Remove ${b.dataset.name}`);
        remove.innerHTML = '<i class="fa-solid fa-xmark" aria-hidden="true"></i>';
        remove.addEventListener('click', () => {
          b.checked = false; renderTray();
          b.closest('.club-card').querySelector('input').focus({ preventScroll: true });
        });
        slot.append(img, document.createTextNode(b.dataset.name), remove);
      } else {
        slot.className = 'slot empty';
        slot.textContent = 'Empty';
      }
      slots.appendChild(slot);
    }
    if (chosen.length) check('clubs');
  }
  clubBoxes.forEach((b) => b.addEventListener('change', renderTray));

  // Pre-select a club when arriving from a club page (?club=nss).
  const wanted = new URLSearchParams(location.search).get('club');
  const pre = clubBoxes.find((b) => b.value === wanted);
  if (pre) pre.checked = true;
  renderTray();

  // ---------------------------------------------------------------- review
  const why = form.elements.why;
  const whyCount = $('#why-count');
  why.addEventListener('input', () => { whyCount.textContent = `${why.value.length} / ${why.maxLength}`; });

  function renderReview() {
    const review = $('#review');
    const year = $('input[name="year"]:checked', form)?.value || '';
    const rows = [
      ['Name', valueOf('name').trim(), 1],
      ['Email', valueOf('email').trim().toLowerCase(), 1],
      ['Roll number', valueOf('roll').trim(), 1],
      ['Programme', `${valueOf('programme')} · ${year}`, 1],
    ];
    if (valueOf('phone').trim()) rows.push(['Mobile', valueOf('phone').trim(), 1]);
    review.innerHTML = '';
    const addRow = (label, content, step) => {
      const row = document.createElement('div');
      row.className = 'review-row';
      const dt = document.createElement('dt'); dt.textContent = label;
      const dd = document.createElement('dd');
      if (typeof content === 'string') dd.textContent = content; else dd.appendChild(content);
      const edit = document.createElement('button');
      edit.type = 'button'; edit.className = 'edit'; edit.textContent = 'Edit';
      edit.setAttribute('aria-label', `Edit ${label.toLowerCase()}`);
      edit.addEventListener('click', () => goTo(step));
      row.append(dt, dd, edit);
      review.appendChild(row);
    };
    rows.forEach(([l, v, s]) => addRow(l, v, s));
    const chips = document.createElement('div');
    chips.className = 'review-clubs';
    clubBoxes.filter((b) => b.checked).forEach((b) => {
      const chip = document.createElement('span');
      const img = document.createElement('img'); img.src = b.dataset.img; img.alt = '';
      chip.append(img, document.createTextNode(b.dataset.name));
      chips.appendChild(chip);
    });
    addRow('Clubs', chips, 2);
  }

  // ---------------------------------------------------------------- submit
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (current !== 3) return;
    for (const n of [1, 2]) {
      if (stepFields[n].some((name) => rules[name](valueOf(name)))) { goTo(n); validateStep(n); return; }
    }
    if (!validateStep(3)) return;

    const data = {
      name: valueOf('name').trim(),
      email: valueOf('email').trim().toLowerCase(),
      roll: valueOf('roll').trim(),
      programme: valueOf('programme'),
      year: $('input[name="year"]:checked', form).value,
      phone: valueOf('phone').trim(),
      clubs: clubBoxes.filter((b) => b.checked).map((b) => b.dataset.name),
      why: why.value.trim(),
      submittedAt: new Date().toISOString(),
    };

    const btn = $('#submit-btn');
    const label = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner" aria-hidden="true"></span> Sending…';

    try {
      const endpoint = form.dataset.endpoint;
      if (endpoint) {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(data),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
      } else {
        await new Promise((r) => setTimeout(r, 900));
      }
      showSuccess(data, !endpoint);
    } catch {
      showAlert('Something went wrong while sending. Check your connection and try again.');
    } finally {
      btn.disabled = false;
      btn.innerHTML = label;
    }
  });

  // ---------------------------------------------------------------- success
  function showSuccess(data, demo) {
    $('[data-first-name]', success).textContent = data.name.split(/\s+/)[0];
    $('[data-email]', success).textContent = data.email;
    $('[data-pass-name]', success).textContent = data.name;
    $('[data-pass-sub]', success).textContent = `${data.programme} · ${data.year}`;
    $('[data-pass-roll]', success).textContent = data.roll;
    const clubs = $('[data-pass-clubs]', success);
    clubs.innerHTML = '';
    clubBoxes.filter((b) => b.checked).forEach((b) => {
      const s = document.createElement('span');
      const img = document.createElement('img'); img.src = b.dataset.img; img.alt = '';
      s.append(img, document.createTextNode(b.dataset.name));
      clubs.appendChild(s);
    });
    // Decorative barcode, unique to the roll number.
    const bars = $('[data-barcode]', success);
    bars.innerHTML = '';
    let h = 0;
    for (const ch of data.roll) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
    for (let i = 0; i < 28; i++) {
      h = (h * 1103515245 + 12345) >>> 0;
      const bar = document.createElement('i');
      bar.style.height = `${40 + (h % 60)}%`;
      bar.style.width = `${1 + (h % 3)}px`;
      bars.appendChild(bar);
    }
    $('#demo-note').hidden = !demo;

    form.hidden = true;
    $('#progress').hidden = true;
    success.hidden = false;
    success.classList.remove('show'); void success.offsetWidth; success.classList.add('show');
    // Re-run the pass and tick animations each time.
    $$('.pass, .check-anim circle, .check-anim path', success).forEach((el) => {
      el.style.animation = 'none'; void el.getBoundingClientRect(); el.style.animation = '';
    });
    window.scrollTo({ top: Math.max(0, $('.reg-panel').getBoundingClientRect().top + window.scrollY - 80), behavior: reduceMotion ? 'auto' : 'smooth' });
    $('h2', success).focus({ preventScroll: true });
    if (!reduceMotion) setTimeout(confetti, 350);
  }

  $('#register-again').addEventListener('click', () => {
    form.reset();
    syncSelect();
    $$('.invalid, .valid', form).forEach((f) => f.classList.remove('invalid', 'valid'));
    whyCount.textContent = `0 / ${why.maxLength}`;
    renderTray();
    success.hidden = true;
    form.hidden = false;
    $('#progress').hidden = false;
    goTo(1);
    form.elements.name.focus();
  });

  // 3D tilt on the member pass
  const pass = $('#pass');
  if (!reduceMotion && window.matchMedia('(hover: hover)').matches) {
    pass.addEventListener('mousemove', (e) => {
      const r = pass.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      pass.style.transform = `rotateY(${x * 14}deg) rotateX(${-y * 14}deg) translateZ(0)`;
    });
    pass.addEventListener('mouseleave', () => { pass.style.transform = ''; });
  }

  // ---------------------------------------------------------------- confetti
  function confetti() {
    const canvas = $('#confetti');
    const ctx = canvas.getContext('2d');
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = (canvas.width = innerWidth * dpr);
    const H = (canvas.height = innerHeight * dpr);
    canvas.style.width = `${innerWidth}px`;
    canvas.style.height = `${innerHeight}px`;
    const colors = ['#a4123f', '#e0457b', '#f6c453', '#ffffff', '#12b76a', '#7a0d2f'];
    const origin = $('.check-anim').getBoundingClientRect();
    const ox = (origin.left + origin.width / 2) * dpr;
    const oy = (origin.top + origin.height / 2) * dpr;
    const pieces = Array.from({ length: 170 }, (_, i) => {
      const fromSides = i % 3 === 0;
      const angle = fromSides ? (i % 2 ? -Math.PI / 3 : -2 * Math.PI / 3) + (Math.random() - 0.5) * 0.6
        : Math.random() * Math.PI * 2;
      const speed = (fromSides ? 14 + Math.random() * 10 : 5 + Math.random() * 9) * dpr;
      return {
        x: fromSides ? (i % 2 ? 0 : W) : ox,
        y: fromSides ? H * 0.85 : oy,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        w: (6 + Math.random() * 6) * dpr,
        h: (8 + Math.random() * 10) * dpr,
        rot: Math.random() * Math.PI,
        vr: (Math.random() - 0.5) * 0.3,
        color: colors[i % colors.length],
        shape: i % 4 === 0 ? 'circle' : 'rect',
        life: 0,
      };
    });
    let frame = 0;
    (function tick() {
      ctx.clearRect(0, 0, W, H);
      let alive = 0;
      pieces.forEach((p) => {
        p.life++;
        p.vy += 0.32 * dpr;
        p.vx *= 0.985; p.vy *= 0.985;
        p.x += p.vx; p.y += p.vy; p.rot += p.vr;
        if (p.y < H + 40) alive++;
        const fade = Math.max(0, 1 - p.life / 220);
        ctx.save();
        ctx.globalAlpha = fade;
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.fillStyle = p.color;
        if (p.shape === 'circle') { ctx.beginPath(); ctx.arc(0, 0, p.w / 2, 0, Math.PI * 2); ctx.fill(); }
        else ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * Math.abs(Math.cos(p.rot * 2)));
        ctx.restore();
      });
      if (alive && ++frame < 260) requestAnimationFrame(tick);
      else ctx.clearRect(0, 0, W, H);
    })();
  }

  // Count-up for the stats on the left
  if (!reduceMotion) {
    $$('[data-count]').forEach((el) => {
      const target = Number(el.dataset.count);
      const start = performance.now() + 500;
      const step = (t) => {
        const p = Math.min(1, Math.max(0, (t - start) / 900));
        el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      };
      el.textContent = '0';
      requestAnimationFrame(step);
    });
  }
})();
