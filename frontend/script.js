/* ============================================================
   AURUM TEMPUS — script.js
   ============================================================ */

const API_BASE = 'http://localhost:8000';

// ── Session ID (persists for the browser session) ──────────
const SESSION_ID = (() => {
  let id = sessionStorage.getItem('at_session_id');
  if (!id) { id = crypto.randomUUID(); sessionStorage.setItem('at_session_id', id); }
  return id;
})();

// ── Event Logger ───────────────────────────────────────────
async function logEvent(eventType, productId = null) {
  try {
    await fetch(`${API_BASE}/events`, {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({
        event_type : eventType,
        product_id : productId,
        session_id : SESSION_ID,
      }),
    });
  } catch (err) {
    // Fail silently — analytics must never break UX
    console.debug('[AT] event log failed:', err);
  }
}

document.addEventListener('DOMContentLoaded', () => {

  // ── Log page view on every page load ──────────────────────
  logEvent('page_view');

  // ── Log product views when cards scroll into view ─────────
  const productCards = document.querySelectorAll('[data-product-id]');
  if (productCards.length) {
    const pvObs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const productId = parseInt(entry.target.closest('article')?.dataset?.productId
            || entry.target.dataset?.productId);
          if (productId) logEvent('product_view', productId);
          pvObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    productCards.forEach(el => pvObs.observe(el.closest('article') || el));
  }

  // ── Custom Cursor ──────────────────────────────────────────
  const cursor     = document.querySelector('.cursor');
  const cursorRing = document.querySelector('.cursor-ring');
  if (cursor && cursorRing) {
    let mouseX = 0, mouseY = 0, ringX = 0, ringY = 0;
    document.addEventListener('mousemove', e => {
      mouseX = e.clientX; mouseY = e.clientY;
      cursor.style.left = mouseX + 'px'; cursor.style.top = mouseY + 'px';
    });
    const animateRing = () => {
      ringX += (mouseX - ringX) * 0.12; ringY += (mouseY - ringY) * 0.12;
      cursorRing.style.left = ringX + 'px'; cursorRing.style.top = ringY + 'px';
      requestAnimationFrame(animateRing);
    };
    animateRing();
    document.querySelectorAll('a, button, .btn, .filter-tab, .card').forEach(el => {
      el.addEventListener('mouseenter', () => { cursor.style.width='14px';cursor.style.height='14px';cursorRing.style.width='48px';cursorRing.style.height='48px';cursorRing.style.borderColor='rgba(184,147,63,0.9)'; });
      el.addEventListener('mouseleave', () => { cursor.style.width='8px';cursor.style.height='8px';cursorRing.style.width='32px';cursorRing.style.height='32px';cursorRing.style.borderColor='rgba(184,147,63,0.6)'; });
    });
  }

  // ── Navigation Scroll Effect ───────────────────────────────
  const nav = document.querySelector('.nav');
  if (nav) window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 60), { passive: true });

  // ── Mobile Navigation ──────────────────────────────────────
  const hamburger = document.querySelector('.nav-hamburger');
  const mobileNav = document.querySelector('.nav-mobile');
  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', () => {
      const isOpen = mobileNav.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
      const bars = hamburger.querySelectorAll('span');
      if (isOpen) { bars[0].style.transform='rotate(45deg) translate(4px,4px)';bars[1].style.opacity='0';bars[2].style.transform='rotate(-45deg) translate(4px,-4px)'; }
      else { bars.forEach(b => { b.style.transform=''; b.style.opacity=''; }); }
    });
    mobileNav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
      mobileNav.classList.remove('open'); document.body.style.overflow=''; hamburger.setAttribute('aria-expanded','false');
      hamburger.querySelectorAll('span').forEach(b => { b.style.transform=''; b.style.opacity=''; });
    }));
  }

  // ── Scroll Reveal ─────────────────────────────────────────
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    const obs = new IntersectionObserver(entries => entries.forEach(e => { if(e.isIntersecting){e.target.classList.add('visible');obs.unobserve(e.target);} }), { threshold:0.12, rootMargin:'0px 0px -60px 0px' });
    reveals.forEach(el => obs.observe(el));
  }

  // ── Count-Up ──────────────────────────────────────────────
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    const cObs = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el=entry.target, target=parseFloat(el.dataset.count), suffix=el.dataset.suffix||'', prefix=el.dataset.prefix||'', decimals=el.dataset.decimals||0, duration=2000, start=performance.now();
        const tick = now => { const p=Math.min((now-start)/duration,1), ease=1-Math.pow(1-p,3); el.textContent=prefix+(target*ease).toFixed(decimals)+suffix; if(p<1)requestAnimationFrame(tick); };
        requestAnimationFrame(tick); cObs.unobserve(el);
      }
    }), { threshold:0.5 });
    counters.forEach(el => cObs.observe(el));
  }

  // ── Live Clock ────────────────────────────────────────────
  const updateClock = () => {
    const now=new Date(), h=now.getHours()%12, m=now.getMinutes(), s=now.getSeconds(), ms=now.getMilliseconds();
    const hh=document.getElementById('hour-hand'), mh=document.getElementById('min-hand'), sh=document.getElementById('sec-hand');
    if(hh) hh.style.transform=`rotate(${(h/12)*360+(m/60)*30}deg)`;
    if(mh) mh.style.transform=`rotate(${(m/60)*360+(s/60)*6}deg)`;
    if(sh) sh.style.transform=`rotate(${(s/60)*360+(ms/1000)*6}deg)`;
  };
  if (document.getElementById('hour-hand')) { updateClock(); setInterval(updateClock, 50); }

  // ── Filter Tabs ───────────────────────────────────────────
  document.querySelectorAll('.filter-tabs').forEach(tabGroup => {
    const tabs=tabGroup.querySelectorAll('.filter-tab'), grid=tabGroup.nextElementSibling;
    if(!grid) return;
    tabs.forEach(tab => tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active')); tab.classList.add('active');
      const filter=tab.dataset.filter;
      grid.querySelectorAll('[data-category]').forEach(item => {
        if(filter==='all'||item.dataset.category===filter){item.style.display='';setTimeout(()=>item.classList.add('visible'),10);}
        else{item.style.display='none';item.classList.remove('visible');}
      });
    }));
  });

  // ── Email Form ────────────────────────────────────────────
  document.querySelectorAll('.email-form').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const input=form.querySelector('input[type="email"]'), btn=form.querySelector('button');
      if(!input||!btn) return;
      const orig=btn.textContent; btn.textContent='Subscribed ✦'; btn.style.background='#5a8a5a'; input.value='';
      setTimeout(()=>{btn.textContent=orig;btn.style.background='';}, 3000);
    });
  });

  // ── Page Transition ───────────────────────────────────────
  const pt = document.querySelector('.page-transition');
  if (pt) {
    setTimeout(()=>{pt.style.transform='translateY(-100%)';setTimeout(()=>pt.style.display='none',500);},100);
    document.querySelectorAll('a[href]').forEach(link => {
      const href=link.getAttribute('href');
      if(!href||href.startsWith('#')||href.startsWith('mailto')||href.startsWith('http')) return;
      link.addEventListener('click', e => { e.preventDefault(); pt.style.display='block'; pt.style.transform='translateY(0)'; setTimeout(()=>window.location.href=href,500); });
    });
  }

  // ── Smooth Scroll ─────────────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => { const t=document.querySelector(link.getAttribute('href')); if(t){e.preventDefault();t.scrollIntoView({behavior:'smooth',block:'start'});} });
  });

  // ── Parallax ──────────────────────────────────────────────
  const heroWatch = document.querySelector('.hero-watch-wrapper');
  if (heroWatch) window.addEventListener('scroll', () => { heroWatch.style.transform=`translateY(calc(-50% + ${window.scrollY*0.15}px))`; }, { passive:true });

  // ══════════════════════════════════════════════════════════
  // ── CART SYSTEM ───────────────────────────────────────────
  // ══════════════════════════════════════════════════════════

  let cart = JSON.parse(localStorage.getItem('at_cart') || '[]');

  const saveCart    = () => localStorage.setItem('at_cart', JSON.stringify(cart));
  const formatPrice = (n, currency='USD') => `${currency} ${Number(n).toLocaleString('en-US')}`;

  // Update count badge
  const updateCartCount = () => {
    document.querySelectorAll('.cart-count').forEach(el => {
      el.textContent = cart.reduce((s, i) => s + i.qty, 0);
    });
  };

  // Render cart items in drawer
  const renderCart = () => {
    const container = document.getElementById('cart-items');
    const footer    = document.getElementById('cart-footer');
    const totalEl   = document.getElementById('cart-total-price');
    if (!container) return;

    if (cart.length === 0) {
      container.innerHTML = '<p class="cart-empty">Your cart is empty.</p>';
      if (footer) footer.style.display = 'none';
      return;
    }

    let total = 0;
    container.innerHTML = cart.map((item, i) => {
      total += item.price * item.qty;
      return `
        <div class="cart-item">
          <div class="cart-item-info">
            <span class="cart-item-name">${item.name}</span>
            <span class="cart-item-price">${formatPrice(item.price, item.currency)}</span>
          </div>
          <div class="cart-item-controls">
            <button class="qty-btn" data-index="${i}" data-action="dec">−</button>
            <span>${item.qty}</span>
            <button class="qty-btn" data-index="${i}" data-action="inc">+</button>
            <button class="qty-btn remove-btn" data-index="${i}" data-action="remove">✕</button>
          </div>
        </div>`;
    }).join('');

    if (footer) { footer.style.display = 'block'; }
    if (totalEl) { totalEl.textContent = formatPrice(total, cart[0]?.currency || 'CHF'); }

    // Qty controls
    container.querySelectorAll('.qty-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.dataset.index);
        const action = btn.dataset.action;
        if (action === 'inc') cart[idx].qty++;
        if (action === 'dec') { cart[idx].qty--; if(cart[idx].qty<=0) cart.splice(idx,1); }
        if (action === 'remove') cart.splice(idx,1);
        saveCart(); updateCartCount(); renderCart();
      });
    });
  };

  // Open / close drawer
  const openCart  = () => { document.getElementById('cart-drawer')?.setAttribute('aria-hidden','false'); document.getElementById('cart-overlay')?.classList.add('active'); document.body.style.overflow='hidden'; renderCart(); };
  const closeCart = () => { document.getElementById('cart-drawer')?.setAttribute('aria-hidden','true');  document.getElementById('cart-overlay')?.classList.remove('active'); document.body.style.overflow=''; };

  document.querySelectorAll('.cart-toggle').forEach(btn => btn.addEventListener('click', openCart));
  document.getElementById('cart-close')?.addEventListener('click', closeCart);
  document.querySelector('.cart-close')?.addEventListener('click', closeCart);
  document.getElementById('cart-overlay')?.addEventListener('click', closeCart);

  // Add to cart — with API event logging
  document.querySelectorAll('.add-to-cart').forEach(btn => {
    btn.addEventListener('click', () => {
      const name      = btn.dataset.name;
      const price     = parseFloat(btn.dataset.price);
      const currency  = btn.dataset.currency || 'CHF';
      const productId = parseInt(btn.dataset.productId) || null;

      const existing = cart.find(i => i.name === name);
      if (existing) { existing.qty++; }
      else { cart.push({ name, price, currency, productId, qty: 1 }); }
      saveCart(); updateCartCount();

      // Log add_to_cart event
      if (productId) logEvent('add_to_cart', productId);

      // Flash feedback
      const orig = btn.textContent;
      btn.textContent = 'Added ✦';
      btn.style.background = '#5a8a5a';
      setTimeout(() => { btn.textContent = orig; btn.style.background = ''; }, 1500);
    });
  });

  // ── CHECKOUT FLOW ─────────────────────────────────────────
  const showStep = (n) => {
    document.querySelectorAll('.checkout-step').forEach((s,i) => s.classList.toggle('active', i===n-1));
  };

  document.getElementById('checkout-btn')?.addEventListener('click', () => {
    closeCart();
    document.getElementById('checkout-modal')?.setAttribute('aria-hidden','false');
    // Log checkout_start event (no specific product)
    logEvent('checkout_start');
    showStep(1);
  });

  document.querySelector('.checkout-close')?.addEventListener('click', () => {
    document.getElementById('checkout-modal')?.setAttribute('aria-hidden','true');
  });

  document.getElementById('step-1-next')?.addEventListener('click', () => {
    const name  = document.getElementById('c-name')?.value.trim();
    const email = document.getElementById('c-email')?.value.trim();
    if (!name || !email) { alert('Please fill in your name and email.'); return; }
    showStep(2);
  });

  document.getElementById('step-2-back')?.addEventListener('click', () => showStep(1));

  document.getElementById('step-2-next')?.addEventListener('click', async () => {
    const cardNum = document.getElementById('c-card-number')?.value.trim();
    if (!cardNum) { alert('Please enter a card number.'); return; }

    const name     = document.getElementById('c-name')?.value;
    const email    = document.getElementById('c-email')?.value;
    const orderNum = 'AT-' + Math.floor(Math.random() * 90000 + 10000);
    const total    = cart.reduce((s,i) => s + i.price * i.qty, 0);

    // ── POST order to FastAPI ────────────────────────────────
    try {
      const orderPayload = {
        session_id     : SESSION_ID,
        customer_name  : name,
        customer_email : email,
        items          : cart.map(i => ({
          product_id : i.productId,
          quantity   : i.qty,
          unit_price : i.price,
        })),
        total_chf      : total,
      };
      await fetch(`${API_BASE}/orders`, {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify(orderPayload),
      });
    } catch (err) {
      console.debug('[AT] order POST failed:', err);
    }

    // Log a purchase event per cart line
    cart.forEach(item => {
      if (item.productId) logEvent('purchase', item.productId);
    });

    document.getElementById('confirmation-msg').innerHTML =
      `Thank you, <strong>${name}</strong>. A confirmation has been sent to <strong>${email}</strong>.<br/>
       <span style="color:var(--accent);letter-spacing:0.15em">Order ${orderNum}</span>`;

    document.getElementById('order-summary').innerHTML = cart.map(i =>
      `<div class="cart-item"><div class="cart-item-info"><span class="cart-item-name">${i.name} × ${i.qty}</span><span class="cart-item-price">${formatPrice(i.price * i.qty, i.currency)}</span></div></div>`
    ).join('') + `<div class="cart-item" style="border-top:1px solid var(--accent);margin-top:0.5rem"><div class="cart-item-info"><strong>Total</strong><strong>${formatPrice(total, cart[0]?.currency||'CHF')}</strong></div></div>`;

    cart = []; saveCart(); updateCartCount();
    showStep(3);
  });

  document.getElementById('step-3-close')?.addEventListener('click', () => {
    document.getElementById('checkout-modal')?.setAttribute('aria-hidden','true');
    window.location.href = 'collections.html';
  });

  updateCartCount();

});