// static/js/cart.js (v6) — floating cart pill with clear button

const CART_KEY = 'kt_cart_v1';

function parsePrice(raw){
  if(raw == null) return 0;
  const s = String(raw).replace(/[^0-9,.\-]/g,'').replace(',', '.');
  const n = parseFloat(s);
  return isNaN(n) ? 0 : n;
}
function formatPLN(v){
  try { return new Intl.NumberFormat('pl-PL',{style:'currency',currency:'PLN'}).format(v||0); }
  catch { return (v||0).toFixed(2)+' zł'; }
}

function getCart(){ try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch { return []; } }
function saveCart(items){ localStorage.setItem(CART_KEY, JSON.stringify(items)); updateBadge(); }
function addItem(item){
  const cart = getCart();
  const keyMatch = x => (item.id && x.id && String(x.id)===String(item.id)) || (x.name===item.name);
  const i = cart.findIndex(keyMatch);
  if(i >= 0){ cart[i].qty += item.qty || 1; }
  else { cart.push({ id: item.id || null, name: item.name || 'Produkt', price: parsePrice(item.price), image: item.image || null, qty: item.qty || 1 }); }
  saveCart(cart);
}
function clearCart(){
  localStorage.removeItem(CART_KEY);
  updateBadge();
  // Tiny toast feedback on clear
  showToast('Koszyk wyczyszczony');
}

function cartCount(){
  return getCart().reduce((s,i)=> s + (i.qty||1), 0);
}

function updateBadge(){
  const count = cartCount();
  document.querySelectorAll('[data-cart-count]').forEach(el => el.textContent = count);
}

/* ------- Floating pill ------- */
function mountFloatingCart(){
  if(document.querySelector('.cart-fab')) { updateBadge(); return; }

  const wrap = document.createElement('div');
  wrap.className = 'cart-fab';
  wrap.setAttribute('role','region');
  wrap.setAttribute('aria-label','Koszyk');

  // Main area → go to checkout
  const main = document.createElement('a');
  main.className = 'cart-fab-main';
  main.href = '/zamowienie';
  main.innerHTML = `🧺 <span class="label">Koszyk</span> <span class="count" data-cart-count>0</span>`;

  // Clear button
  const clear = document.createElement('button');
  clear.type = 'button';
  clear.className = 'cart-fab-clear';
  clear.title = 'Wyczyść koszyk';
  clear.setAttribute('aria-label','Wyczyść koszyk');
  clear.textContent = 'Wyczyść';

  wrap.appendChild(main);
  wrap.appendChild(clear);
  document.body.appendChild(wrap);

  clear.addEventListener('click', (e)=>{
    e.preventDefault();
    if(confirm('Na pewno wyczyścić koszyk?')) clearCart();
  });
}

/* ------- Order page helpers ------- */
function populateOrderForm(){
  const field = document.getElementById('cart_json');
  const wrap  = document.getElementById('cart_summary');
  const totalEl = document.getElementById('cart_total');

  const cart = getCart();
  if(field) field.value = JSON.stringify(cart);

  if(wrap){
    if(cart.length === 0){
      wrap.textContent = 'Koszyk jest pusty.';
    }else{
      wrap.innerHTML = cart.map(i => {
        const qty = i.qty || 1;
        const price = parsePrice(i.price);
        const line = qty * price;
        return `<div class="d-flex justify-content-between border-bottom border-opacity-25 py-1">
                  <span>${qty}× ${i.name || 'Produkt'}</span>
                  <span>${formatPLN(line)}</span>
                </div>`;
      }).join('');
    }
  }
  if(totalEl){
    const sum = cart.reduce((s,i)=> s + (parsePrice(i.price) * (i.qty||1)), 0);
    totalEl.textContent = formatPLN(sum);
  }
}

/* ------- Tiny toast ------- */
function showToast(text){
  const t = document.createElement('div');
  t.className = 'kt-toast';
  t.textContent = text;
  document.body.appendChild(t);
  requestAnimationFrame(()=> t.classList.add('show'));
  setTimeout(()=> {
    t.classList.remove('show');
    setTimeout(()=> t.remove(), 200);
  }, 1300);
}

/* ------- Events ------- */
document.addEventListener('click', (e)=>{
  const btn = e.target.closest('.add-to-cart');
  if(!btn) return;

  e.preventDefault();
  const name  = btn.dataset.name  || btn.getAttribute('data-name')  || 'Produkt';
  const price = parsePrice(btn.dataset.price || btn.getAttribute('data-price') || '0');
  const id    = btn.dataset.id || btn.getAttribute('data-id') || null;
  const img   = btn.dataset.image || btn.getAttribute('data-image') || null;

  addItem({ id, name, price, image: img, qty: 1 });

  const old = btn.textContent;
  btn.classList.add('disabled');
  btn.textContent = 'Dodano ✓';
  setTimeout(()=>{ btn.classList.remove('disabled'); btn.textContent = old || 'Dodaj do koszyka'; }, 900);
});

document.addEventListener('click', (e)=>{
  const go = e.target.closest('.go-checkout, .btn-checkout, .order-now');
  if(!go) return;
  e.preventDefault();
  window.location.href = '/zamowienie';
});

/* Serialize latest cart just before submit */
document.addEventListener('submit', (e)=>{
  const form = e.target.closest('#order-form');
  if(!form) return;
  const field = form.querySelector('#cart_json');
  if(field) field.value = JSON.stringify(getCart());
});

/* Init */
document.addEventListener('DOMContentLoaded', ()=>{
  mountFloatingCart();
  updateBadge();
  populateOrderForm();

  // Clear after successful order (?order=ok)
  const qs = new URLSearchParams(window.location.search);
  if(qs.get('order') === 'ok'){ clearCart(); }
});
