// static/js/cart.js
const CART_KEY = 'kt_cart_v1';

function getCart(){ try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch { return []; } }
function saveCart(items){ localStorage.setItem(CART_KEY, JSON.stringify(items)); updateBadge(); }
function addItem(item){
  const cart = getCart();
  const i = cart.findIndex(x => (x.id && item.id && x.id==item.id) || x.name===item.name);
  if(i >= 0){ cart[i].qty += item.qty || 1; }
  else { cart.push({ id: item.id || null, name: item.name || 'Produkt', price: item.price || 0, image: item.image || null, qty: item.qty || 1 }); }
  saveCart(cart);
}
function clearCart(){ localStorage.removeItem(CART_KEY); updateBadge(); }

function formatPLN(v){
  try { return new Intl.NumberFormat('pl-PL', {style:'currency', currency:'PLN'}).format(v||0); } catch { return (v||0).toFixed(2)+' zł'; }
}

/* ---- Navbar/cart badge injection (no template changes required) ---- */
function ensureCartBadge(){
  // Try to attach to a nav link that points to the order/checkout page
  const cand = Array.from(document.querySelectorAll('a.nav-link, a.navbar-brand, a'))
    .find(a => /zamow|order|checkout/i.test((a.getAttribute('href')||'') + ' ' + a.textContent));

  if (cand && !cand.querySelector('[data-cart-count]')) {
    const span = document.createElement('span');
    span.className = 'ms-1 cart-badge';
    span.innerHTML = '(<span data-cart-count>0</span>)';
    cand.appendChild(span);
    return true;
  }
  return false;
}

function createFloatingCheckout(){
  // If there is no obvious checkout link, add a small floating button.
  if (document.querySelector('.cart-fab')) return;
  const btn = document.createElement('a');
  btn.className = 'cart-fab';
  btn.href = '/zamowienie';
  btn.innerHTML = `Koszyk <span data-cart-count>0</span>`;
  document.body.appendChild(btn);
}

function updateBadge(){
  const count = getCart().reduce((s,i)=>s+i.qty,0);
  document.querySelectorAll('[data-cart-count]').forEach(el => el.textContent = count);
}

/* ---- Add-to-cart (works across Menu & Products) ---- */
document.addEventListener('click', (e)=>{
  const btn = e.target.closest('.add-to-cart');
  if(!btn) return;
  e.preventDefault();

  const name  = btn.dataset.name  || btn.getAttribute('data-name')  || 'Produkt';
  const priceRaw = (btn.dataset.price || btn.getAttribute('data-price') || '0').toString().replace(',', '.');
  const price = parseFloat(priceRaw) || 0;
  const id    = btn.dataset.id || btn.getAttribute('data-id') || null;
  const img   = btn.dataset.image || btn.getAttribute('data-image') || null;

  addItem({ id, name, price, image: img, qty: 1 });

  // Small feedback
  const old = btn.textContent;
  btn.classList.add('disabled');
  btn.textContent = 'Dodano ✓';
  setTimeout(()=>{ btn.classList.remove('disabled'); btn.textContent = old || 'Dodaj do koszyka'; }, 900);
});

/* ---- Any “go to checkout” click → /zamowienie ---- */
document.addEventListener('click', (e)=>{
  const go = e.target.closest('.go-checkout, .btn-checkout, .order-now');
  if(!go) return;
  e.preventDefault();
  window.location.href = '/zamowienie';
});

/* ---- Expose helpers for order page ---- */
window.KT_CART = { getCart, saveCart, clearCart, updateBadge, formatPLN };

/* ---- Init ---- */
document.addEventListener('DOMContentLoaded', ()=>{
  const attached = ensureCartBadge();
  if (!attached) createFloatingCheckout();
  updateBadge();
});
