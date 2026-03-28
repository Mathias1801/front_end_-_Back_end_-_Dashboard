/* ============================================================
   AURUM TEMPUS — script.js
   Shared JavaScript for all pages
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Custom Cursor ──────────────────────────────────────────
  const cursor     = document.querySelector('.cursor');
  const cursorRing = document.querySelector('.cursor-ring');

  if (cursor && cursorRing) {
    let mouseX = 0, mouseY = 0;
    let ringX  = 0, ringY  = 0;

    document.addEventListener('mousemove', e => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      cursor.style.left = mouseX + 'px';
      cursor.style.top  = mouseY + 'px';
    });

    const animateRing = () => {
      ringX += (mouseX - ringX) * 0.12;
      ringY += (mouseY - ringY) * 0.12;
      cursorRing.style.left = ringX + 'px';
      cursorRing.style.top  = ringY + 'px';
      requestAnimationFrame(animateRing);
    };
    animateRing();

    document.querySelectorAll('a, button, .btn, .filter-tab, .card').forEach(el => {
      el.addEventListener('mouseenter', () => {
        cursor.style.width  = '14px';
        cursor.style.height = '14px';
        cursorRing.style.width  = '48px';
        cursorRing.style.height = '48px';
        cursorRing.style.borderColor = 'rgba(184,147,63,0.9)';
      });
      el.addEventListener('mouseleave', () => {
        cursor.style.width  = '8px';
        cursor.style.height = '8px';
        cursorRing.style.width  = '32px';
        cursorRing.style.height = '32px';
        cursorRing.style.borderColor = 'rgba(184,147,63,0.6)';
      });
    });
  }

  // ── Navigation Scroll Effect ───────────────────────────────
  const nav = document.querySelector('.nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 60);
    }, { passive: true });
  }

  // ── Mobile Navigation ──────────────────────────────────────
  const hamburger = document.querySelector('.nav-hamburger');
  const mobileNav = document.querySelector('.nav-mobile');

  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', () => {
      const isOpen = mobileNav.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';

      const bars = hamburger.querySelectorAll('span');
      if (isOpen) {
        bars[0].style.transform = 'rotate(45deg) translate(4px, 4px)';
        bars[1].style.opacity   = '0';
        bars[2].style.transform = 'rotate(-45deg) translate(4px, -4px)';
      } else {
        bars[0].style.transform = '';
        bars[1].style.opacity   = '';
        bars[2].style.transform = '';
      }
    });

    mobileNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileNav.classList.remove('open');
        document.body.style.overflow = '';
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.querySelectorAll('span').forEach(b => {
          b.style.transform = '';
          b.style.opacity   = '';
        });
      });
    });
  }

  // ── Scroll Reveal (IntersectionObserver) ──────────────────
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

    reveals.forEach(el => revealObserver.observe(el));
  }

  // ── Count-Up Animation ────────────────────────────────────
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    const countObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el        = entry.target;
          const target    = parseFloat(el.dataset.count);
          const suffix    = el.dataset.suffix || '';
          const prefix    = el.dataset.prefix || '';
          const decimals  = el.dataset.decimals || 0;
          const duration  = 2000;
          const start     = performance.now();

          const tick = (now) => {
            const elapsed  = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const ease     = 1 - Math.pow(1 - progress, 3);
            const current  = target * ease;
            el.textContent = prefix + current.toFixed(decimals) + suffix;
            if (progress < 1) requestAnimationFrame(tick);
          };

          requestAnimationFrame(tick);
          countObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(el => countObserver.observe(el));
  }

  // ── Live Clock (Watch face) ────────────────────────────────
  const updateClock = () => {
    const now = new Date();
    const h = now.getHours() % 12;
    const m = now.getMinutes();
    const s = now.getSeconds();
    const ms = now.getMilliseconds();

    const hourDeg   = (h / 12) * 360 + (m / 60) * 30;
    const minDeg    = (m / 60) * 360 + (s / 60) * 6;
    const secDeg    = (s / 60) * 360 + (ms / 1000) * 6;

    const hourHand = document.getElementById('hour-hand');
    const minHand  = document.getElementById('min-hand');
    const secHand  = document.getElementById('sec-hand');

    if (hourHand) hourHand.style.transform = `rotate(${hourDeg}deg)`;
    if (minHand)  minHand.style.transform  = `rotate(${minDeg}deg)`;
    if (secHand)  secHand.style.transform  = `rotate(${secDeg}deg)`;
  };

  if (document.getElementById('hour-hand')) {
    updateClock();
    setInterval(updateClock, 50);
  }

  // ── Filter Tabs ───────────────────────────────────────────
  document.querySelectorAll('.filter-tabs').forEach(tabGroup => {
    const tabs  = tabGroup.querySelectorAll('.filter-tab');
    const grid  = tabGroup.nextElementSibling;
    if (!grid) return;

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const filter = tab.dataset.filter;
        grid.querySelectorAll('[data-category]').forEach(item => {
          if (filter === 'all' || item.dataset.category === filter) {
            item.style.display = '';
            setTimeout(() => item.classList.add('visible'), 10);
          } else {
            item.style.display = 'none';
            item.classList.remove('visible');
          }
        });
      });
    });
  });

  // ── Email Form Submission ─────────────────────────────────
  document.querySelectorAll('.email-form').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const input = form.querySelector('input[type="email"]');
      const btn   = form.querySelector('button');
      if (!input || !btn) return;

      const originalText = btn.textContent;
      btn.textContent = 'Subscribed ✦';
      btn.style.background = '#5a8a5a';
      input.value = '';

      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
      }, 3000);
    });
  });

  // ── Contact Form Submission ───────────────────────────────
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', e => {
      e.preventDefault();
      const btn = contactForm.querySelector('button[type="submit"]');
      if (btn) {
        btn.textContent = 'Message Received ✦';
        btn.style.background = '#5a8a5a';
        setTimeout(() => {
          btn.textContent = 'Send Enquiry';
          btn.style.background = '';
          contactForm.reset();
        }, 3000);
      }
    });
  }

  // ── Page Transition ───────────────────────────────────────
  const pageTransition = document.querySelector('.page-transition');
  if (pageTransition) {
    // Entry animation
    setTimeout(() => {
      pageTransition.style.transform = 'translateY(-100%)';
      setTimeout(() => pageTransition.style.display = 'none', 500);
    }, 100);

    // Exit on internal links
    document.querySelectorAll('a[href]').forEach(link => {
      const href = link.getAttribute('href');
      if (!href || href.startsWith('#') || href.startsWith('mailto') || href.startsWith('http')) return;
      link.addEventListener('click', e => {
        e.preventDefault();
        pageTransition.style.display = 'block';
        pageTransition.style.transform = 'translateY(0)';
        setTimeout(() => window.location.href = href, 500);
      });
    });
  }

  // ── Smooth Scroll for Anchor Links ───────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Parallax on hero watch ───────────────────────────────
  const heroWatch = document.querySelector('.hero-watch-wrapper');
  if (heroWatch) {
    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY;
      heroWatch.style.transform = `translateY(calc(-50% + ${scrollY * 0.15}px))`;
    }, { passive: true });
  }

});
