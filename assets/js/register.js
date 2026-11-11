// Registration form: validation, club picker, and the confirmation screen.
//
// Where submissions go:
//   Set data-endpoint="https://..." on <form id="register-form"> to POST the
//   answers as JSON to a form service (Formspree, Getform, a Google Apps Script
//   web app, your own API...). With no endpoint the form runs in demo mode:
//   it validates and shows the confirmation, but the answers are not stored anywhere.
(() => {
  const form = document.getElementById('register-form');
  if (!form) return;

  const MAX_CLUBS = 3;
  const EMAIL_RE = /^[^\s@]+@([a-z0-9-]+\.)*amrita\.edu$/i;
  const ROLL_RE = /^[A-Z]{2}\.[A-Z]{2,4}\.[A-Z0-9]{3,6}\d{3,5}$/i;
  const PHONE_RE = /^(\+91[\s-]?)?[6-9]\d{9}$/;

  const summary = document.getElementById('form-summary');
  const success = document.getElementById('register-success');
  const clubBoxes = [...form.querySelectorAll('input[name="clubs"]')];
  const pickerStatus = document.getElementById('picker-status');
  const why = form.elements.why;
  const whyCount = document.getElementById('why-count');

  const rules = {
    name: (v) => (v.trim().length >= 2 ? '' : 'Please enter your full name.'),
    email: (v) => {
      if (!v.trim()) return 'Please enter your college email.';
      return EMAIL_RE.test(v.trim()) ? '' : 'Use your Amrita email, e.g. name@cb.students.amrita.edu.';
    },
    roll: (v) => {
      if (!v.trim()) return 'Please enter your roll number.';
      return ROLL_RE.test(v.trim()) ? '' : 'Roll numbers look like CB.EN.U4CSE23001.';
    },
    programme: (v) => (v ? '' : 'Please choose your programme.'),
    year: () => (form.querySelector('input[name="year"]:checked') ? '' : 'Please choose your year.'),
    phone: (v) => (!v.trim() || PHONE_RE.test(v.replace(/\s/g, '')) ? '' : 'Enter a 10-digit Indian mobile number.'),
    clubs: () => (clubBoxes.some((b) => b.checked) ? '' : 'Pick at least one club.'),
    consent: () => (form.elements.consent.checked ? '' : 'Please agree before submitting.'),
  };

  const fieldOf = (name) => form.querySelector(`[data-field="${name}"]`);

  function check(name) {
    const el = form.elements[name];
    const value = el && 'value' in el ? el.value : '';
    const message = rules[name](value);
    const field = fieldOf(name);
    if (field) {
      field.classList.toggle('invalid', Boolean(message));
      const err = field.querySelector('.error');
      if (err) err.textContent = message;
      const input = field.querySelector('input, select, textarea');
      if (input && name !== 'clubs' && name !== 'year') input.setAttribute('aria-invalid', String(Boolean(message)));
    }
    return message;
  }

  // Validate a field once the person leaves it, then live while they fix it.
  Object.keys(rules).forEach((name) => {
    const field = fieldOf(name);
    if (!field) return;
    field.addEventListener('focusout', (e) => {
      if (name === 'clubs' || name === 'year') return;
      if (e.target.value !== '' || field.classList.contains('invalid')) check(name);
    });
    field.addEventListener('input', () => { if (field.classList.contains('invalid')) check(name); });
    field.addEventListener('change', () => { if (field.classList.contains('invalid')) check(name); });
  });

  // Tidy up the roll number as it's typed.
  form.elements.roll.addEventListener('input', (e) => { e.target.value = e.target.value.toUpperCase().replace(/\s/g, ''); });

  // Club picker: limit to MAX_CLUBS and keep a live count.
  function updatePicker() {
    const chosen = clubBoxes.filter((b) => b.checked);
    clubBoxes.forEach((b) => { b.disabled = !b.checked && chosen.length >= MAX_CLUBS; });
    pickerStatus.textContent = chosen.length
      ? `${chosen.length} of ${MAX_CLUBS} selected: ${chosen.map((b) => b.dataset.name).join(', ')}`
      : `Choose up to ${MAX_CLUBS} clubs.`;
  }
  clubBoxes.forEach((b) => b.addEventListener('change', updatePicker));

  // Pre-select a club when arriving from a club page (?club=nss).
  const wanted = new URLSearchParams(location.search).get('club');
  const pre = clubBoxes.find((b) => b.value === wanted);
  if (pre) pre.checked = true;
  updatePicker();

  // Character counter for the "why" box.
  const updateCount = () => { whyCount.textContent = `${why.value.length} / ${why.maxLength}`; };
  why.addEventListener('input', updateCount);
  updateCount();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const errors = Object.keys(rules).map((name) => [name, check(name)]).filter(([, m]) => m);
    if (errors.length) {
      summary.textContent = errors.length === 1
        ? 'Please fix the highlighted field.'
        : `Please fix the ${errors.length} highlighted fields.`;
      summary.classList.add('show');
      const first = fieldOf(errors[0][0]).querySelector('input:not([disabled]), select, textarea');
      first?.focus();
      fieldOf(errors[0][0]).scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    summary.classList.remove('show');

    const data = {
      name: form.elements.name.value.trim(),
      email: form.elements.email.value.trim().toLowerCase(),
      roll: form.elements.roll.value.trim(),
      programme: form.elements.programme.value,
      year: form.querySelector('input[name="year"]:checked').value,
      phone: form.elements.phone.value.trim(),
      clubs: clubBoxes.filter((b) => b.checked).map((b) => b.dataset.name),
      why: why.value.trim(),
      submittedAt: new Date().toISOString(),
    };

    const button = form.querySelector('button[type="submit"]');
    const label = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i> Submitting…';

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
        await new Promise((r) => setTimeout(r, 600)); // demo mode
      }
      showSuccess(data);
    } catch (err) {
      summary.textContent = 'Something went wrong while submitting. Please check your connection and try again.';
      summary.classList.add('show');
      button.disabled = false;
      button.innerHTML = label;
    }
  });

  function showSuccess(data) {
    const firstName = data.name.split(/\s+/)[0];
    success.querySelector('[data-first-name]').textContent = firstName;
    success.querySelector('[data-email]').textContent = data.email;
    const list = success.querySelector('.success-list');
    list.innerHTML = '';
    clubBoxes.filter((b) => b.checked).forEach((b) => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `../clubs/${b.value}/`;
      const img = document.createElement('img');
      img.src = b.dataset.img;
      img.alt = '';
      const span = document.createElement('span');
      span.textContent = 'View club →';
      a.append(img, document.createTextNode(b.dataset.name), span);
      li.appendChild(a);
      list.appendChild(li);
    });
    form.hidden = true;
    success.hidden = false;
    success.querySelector('h2').focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  document.getElementById('register-again')?.addEventListener('click', () => {
    form.reset();
    form.querySelectorAll('.invalid').forEach((f) => f.classList.remove('invalid'));
    form.querySelector('button[type="submit"]').disabled = false;
    form.querySelector('button[type="submit"]').innerHTML = '<i class="fa-solid fa-paper-plane" aria-hidden="true"></i> Submit registration';
    updatePicker();
    updateCount();
    success.hidden = true;
    form.hidden = false;
    form.elements.name.focus();
  });
})();
