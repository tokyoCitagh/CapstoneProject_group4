// Function to send data to the Django update_item view using AJAX
function updateUserOrder(productId, action){
    console.log('User is logged in, sending data...');

    // The endpoint path
    var url = '/store/update_item/';

    fetch(url, {
        method: 'POST',
        // Ensure cookies (session) are sent so Django recognizes the authenticated user
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            // CRITICAL: Assumes 'csrftoken' is globally defined in base.html
            'X-CSRFToken': csrftoken,
        },
        // Send the data as a JSON string
        body: JSON.stringify({'productId': productId, 'action': action}) 
    })
    .then((response) => response.json().then((data) => ({ response, data })))
    .then(({ response, data }) => {
        if (!response.ok) {
            // Handle stock insufficiency error
            if (data.error === 'insufficient_stock') {
                alert(data.message || 'Insufficient stock available.');
                // Still update cart count if provided
                if (data.cartItems !== undefined) {
                    var cartTotalElement = document.getElementById('cart-total');
                    if (cartTotalElement) {
                        cartTotalElement.innerText = data.cartItems;
                    }
                }
                return; // Stop further processing
            }
            // show error toast
            showToast('Could not update cart: ' + (data.message || response.status));
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        console.log('Success:', data);
        
        // --- INSTANT UI UPDATE ---
        var cartTotalElement = document.getElementById('cart-total');
        
        if (cartTotalElement && data.cartItems !== undefined) {
            // Update the cart counter using the authoritative count returned by the server
            cartTotalElement.innerText = data.cartItems;
            console.log('Cart count updated to:', data.cartItems);
            // sync mobile count too
            var mobileCountEl = document.getElementById('mobile-cart-count');
            if (mobileCountEl) mobileCountEl.innerText = data.cartItems;
                // sync mobile menu cart count if present
                var mobileMenuCount = document.getElementById('mobile-menu-cart-count');
                if (mobileMenuCount) mobileMenuCount.innerText = data.cartItems;
                // update any generic cart-count elements
                try {
                    document.querySelectorAll('.cart-count').forEach(function(el){ el.innerText = data.cartItems; });
                    document.querySelectorAll('[data-cart-count]').forEach(function(el){ el.innerText = data.cartItems; });
                } catch(e) { /* ignore */ }
            // show toast with confirmation
            showToast('Cart updated: ' + data.cartItems + ' item' + (data.cartItems === 1 ? '' : 's'));
        } 
        // Also update mobile floating cart button if present
        try {
            var mobileCount = document.getElementById('mobile-cart-count');
            var mobileBtnWrap = document.getElementById('mobile-floating-cart');
            if (mobileCount && data.cartItems !== undefined) {
                mobileCount.innerText = data.cartItems;
            }
            if (mobileBtnWrap) {
                if ((data.cartItems || 0) > 0) {
                    mobileBtnWrap.classList.remove('hidden');
                } else {
                    mobileBtnWrap.classList.add('hidden');
                }
            }
        } catch (e) {
            console.debug('mobile cart update skipped', e);
        }
        // If server returned header_html, replace header immediately (avoids extra fetch)
        try {
            if (data.header_html) {
                var parser = new DOMParser();
                var doc = parser.parseFromString(data.header_html, 'text/html');
                var newHeader = doc.querySelector('header');
                var curHeader = document.querySelector('header');
                if (newHeader && curHeader) {
                    curHeader.innerHTML = newHeader.innerHTML;
                    try { initHeaderBehavior(); } catch (e) { console.debug('initHeaderBehavior after header_html failed', e); }
                }
            }
        } catch (e) { console.debug('apply header_html failed', e); }
        
        // --- RELOAD LOGIC FOR CART PAGE ---
        // If the current path is /store/cart/, we must reload the page 
        // to update all item quantities, totals, and remove deleted items.
        // This is the most reliable way to update the whole cart view.
        if (window.location.pathname.includes('/store/cart/')) {
            window.location.reload();
        }
        // show small debug badge (helps mobile debugging)
        try {
            showCartDebug(data && data.cartItems !== undefined ? data.cartItems : null);
        } catch (e) { /* ignore */ }
        // Refresh the server-rendered header so visible counts always match server state
        try { refreshHeaderFromServer(); } catch (e) { console.debug('header refresh failed', e); }
        // On small screens, force a quick reload so the full page reflects server state
        try {
            if (window.innerWidth && window.innerWidth <= 640) {
                setTimeout(function(){ window.location.reload(); }, 300);
            }
        } catch (e) { /* ignore */ }
        // --- END RELOAD LOGIC ---

    })
    .catch((error) => {
        console.error('Fetch Error:', error);
        // Replaced alert() with console error message
        console.error('Could not update cart. Check the console for details or ensure user is logged in.');
        showToast('Cart update failed. Try again.');
    });
}


// Initialize cart button listeners. Exposed so we can call it even if the script is injected after DOMContentLoaded.
function initCartListeners(){
    // Select all buttons with the update-cart or add-to-cart class
    var updateBtns = document.querySelectorAll('.update-cart, .add-to-cart'); 

    // --- FINAL DIAGNOSTIC LOGS ---
    console.log("--- cart.js listeners attached ---");
    console.log(`Found ${updateBtns.length} total cart buttons.`);
    // -----------------------------

    updateBtns.forEach(function(btn) {
        // Use pointer events to support mouse, touch and pen consistently on mobile
        var lastHandled = 0;

        function handler(e){
            try {
                // Prevent duplicate handling (pointerdown + click)
                var now = Date.now();
                if (now - lastHandled < 500) {
                    return;
                }
                lastHandled = now;

                try { if (e && e.preventDefault) e.preventDefault(); } catch(ignore){}

                var productId = btn.dataset.product;
                var action = btn.dataset.action;

                console.log(`Cart button activated. Product ID: ${productId}, Action: ${action}, event=${e && e.type}`);

                if (typeof user !== 'undefined' && user !== 'AnonymousUser'){
                    // Optimistic UI update: update counters immediately for better perceived responsiveness
                    try {
                        var cartTotalElement = document.getElementById('cart-total');
                        var mobileCount = document.getElementById('mobile-cart-count');
                        if (action === 'add') {
                            if (cartTotalElement) {
                                var headerVal = parseInt(cartTotalElement.innerText || '0', 10) || 0;
                                cartTotalElement.innerText = headerVal + 1;
                            }
                            if (mobileCount) {
                                var mobileVal = parseInt(mobileCount.innerText || '0', 10) || 0;
                                mobileCount.innerText = mobileVal + 1;
                            }
                        } else if (action === 'remove') {
                            if (cartTotalElement) {
                                var headerVal = parseInt(cartTotalElement.innerText || '0', 10) || 0;
                                cartTotalElement.innerText = Math.max(0, headerVal - 1);
                            }
                            if (mobileCount) {
                                var mobileVal = parseInt(mobileCount.innerText || '0', 10) || 0;
                                mobileCount.innerText = Math.max(0, mobileVal - 1);
                            }
                        }
                        // Also update any visible textual Cart(...) labels immediately
                        try { updateAllCartDisplays(); } catch(e){}
                    } catch (uiErr) { console.debug('optimistic UI update failed', uiErr); }

                    updateUserOrder(productId, action);
                } else {
                    console.warn('Authentication required: Please log in to update the cart.');
                }
            } catch (ex) {
                console.error('Cart handler error', ex);
            }
        }

        // Prefer pointerdown for better mobile responsiveness; also listen to click and touchstart as fallback
        try { btn.addEventListener('pointerdown', handler); } catch(e){}
        try { btn.addEventListener('touchstart', handler); } catch(e){}
        try { btn.addEventListener('click', handler); } catch(e){}
        // Mark button for debugging
        btn.setAttribute('data-listener', '1');
    });
}

// If the document is already loaded (script injected after DOMContentLoaded), run immediately.
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCartListeners);
} else {
    // Already ready — initialize now so dynamically injected scripts bind correctly on mobile.
    try { initCartListeners(); } catch(e){ console.debug('initCartListeners failed', e); }
}

// Toast helper (mobile)
function showToast(msg, timeout) {
    try {
        timeout = timeout || 2200;
        var wrap = document.getElementById('mobile-toast-inner');
        if (!wrap) return;
        wrap.textContent = msg;
        wrap.classList.remove('hidden');
        wrap.style.opacity = '1';
        setTimeout(function(){
            wrap.classList.add('hidden');
        }, timeout);
    } catch (e) {
        console.debug('toast error', e);
    }
}

// --- Debug badge helper (inserted dynamically) ---
function ensureCartDebug(){
    try{
        var dbg = document.getElementById('cart-debug');
        if (dbg) return dbg;
        dbg = document.createElement('div');
        dbg.id = 'cart-debug';
        dbg.style.position = 'fixed';
        dbg.style.top = '8px';
        dbg.style.right = '8px';
        dbg.style.zIndex = 99999;
        dbg.style.background = 'rgba(0,0,0,0.7)';
        dbg.style.color = '#fff';
        dbg.style.padding = '6px 8px';
        dbg.style.fontSize = '12px';
        dbg.style.borderRadius = '6px';
        dbg.style.pointerEvents = 'none';
        dbg.style.opacity = '0';
        dbg.style.transition = 'opacity 220ms ease';
        document.body.appendChild(dbg);
        return dbg;
    }catch(e){ return null; }
}

function showCartDebug(cartItems){
    try{
        var d = ensureCartDebug();
        if (!d) return;
        var ts = new Date().toLocaleTimeString();
        d.textContent = 'Cart updated: ' + (cartItems !== null ? cartItems + ' items' : 'ok') + ' @ ' + ts;
        d.style.opacity = '1';
        // hide after 2s
        setTimeout(function(){ d.style.opacity = '0'; }, 2000);
    }catch(e){/* ignore */}
}

// Fetch the site's home page and replace the <header> element with the server-rendered header.
// This ensures the header reflects authoritative server-side cart counts and navigation state.
function refreshHeaderFromServer(){
    try{
        // Append a cache-busting query param and set cache:'no-store' to avoid CDN/browser cached responses
        var url = '/?cart_refresh=' + Date.now();
        fetch(url, { credentials: 'same-origin', cache: 'no-store' })
            .then(function(resp){ if (!resp.ok) throw new Error('Failed to fetch header'); return resp.text(); })
            .then(function(html){
                try{
                    var parser = new DOMParser();
                    var doc = parser.parseFromString(html, 'text/html');
                    var newHeader = doc.querySelector('header');
                    var curHeader = document.querySelector('header');
                    if (newHeader && curHeader) {
                        curHeader.innerHTML = newHeader.innerHTML;
                        // Reinitialize header behavior (nav toggle, mobile cart click) since listeners were lost
                        try { initHeaderBehavior(); } catch (e) { console.debug('initHeaderBehavior failed', e); }
                    }
                }catch(e){ console.debug('parse header failed', e); }
            }).catch(function(e){ console.debug('refreshHeaderFromServer error', e); });
    }catch(e){ /* ignore */ }
}

// Reattach header-related event handlers after header is replaced dynamically
function initHeaderBehavior(){
    try{
        // Mobile nav toggle
        var btn = document.getElementById('nav-toggle');
        var menu = document.getElementById('mobile-menu');
        if (btn && menu) {
            // remove existing handlers by cloning
            var newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            newBtn.addEventListener('click', function(){
                if (menu.classList.contains('hidden')) menu.classList.remove('hidden'); else menu.classList.add('hidden');
            });
        }

        // Mobile floating cart button click behavior
        var mobileBtn = document.getElementById('mobile-cart-btn');
        if (mobileBtn) {
            var newMobileBtn = mobileBtn.cloneNode(true);
            mobileBtn.parentNode.replaceChild(newMobileBtn, mobileBtn);
            newMobileBtn.addEventListener('click', function(e){
                if (typeof user !== 'undefined' && user !== 'AnonymousUser') {
                    window.location.href = '/store/cart/';
                } else {
                    window.location.href = '/accounts/login/';
                }
            });
        }

        // Sync header cart count visibility from count element
        try{
            var headerCt = document.getElementById('cart-total');
            var mobileWrap = document.getElementById('mobile-floating-cart');
            if (headerCt && mobileWrap) {
                var parsed = parseInt(headerCt.innerText || '0', 10) || 0;
                if (parsed > 0) mobileWrap.classList.remove('hidden'); else mobileWrap.classList.add('hidden');
            }
        }catch(e){}
    }catch(e){ console.debug('initHeaderBehavior overall failed', e); }
}

// Update any remaining textual Cart labels across the page to reflect the new count.
function updateAllCartDisplays(newCount){
    try{
        // If newCount not provided, read from #cart-total if available
        if (typeof newCount === 'undefined' || newCount === null){
            var ct = document.getElementById('cart-total');
            newCount = ct ? (parseInt(ct.innerText.trim(),10) || 0) : null;
        }
        if (newCount === null) return;

        // Update known IDs
        var el = document.getElementById('cart-total'); if (el) el.innerText = newCount;
        var el2 = document.getElementById('mobile-cart-count'); if (el2) el2.innerText = newCount;
        var el3 = document.getElementById('mobile-menu-cart-count'); if (el3) el3.innerText = newCount;

        // Update .cart-count and [data-cart-count]
        document.querySelectorAll('.cart-count').forEach(function(e){ e.innerText = newCount; });
        document.querySelectorAll('[data-cart-count]').forEach(function(e){ e.innerText = newCount; });

        // Find any element whose visible text looks like "Cart" followed by digits or a parenthesized number
        document.querySelectorAll('a,span,div').forEach(function(node){
            try{
                if (!node || !node.childNodes) return;
                // Only consider nodes that contain the word 'Cart' (case-sensitive as used in templates)
                var text = node.textContent || '';
                if (text.indexOf('Cart') === -1) return;
                // Replace patterns like 'Cart 12' or 'Cart (12)' or 'Cart ( 12 )'
                var replaced = text.replace(/Cart\s*\(?\s*\d+\s*\)?/, 'Cart ('+newCount+')');
                if (replaced !== text) node.textContent = replaced;
            }catch(e){/* ignore per-node errors */}
        });
        // Also ensure the desktop nav cart anchor shows the count correctly by rebuilding its inner HTML
        try{
            var desktopCartAnchor = null;
            document.querySelectorAll('a').forEach(function(a){
                try{
                    if (a.querySelector && a.querySelector('.fa-shopping-cart')) {
                        desktopCartAnchor = a;
                    }
                }catch(e){}
            });
            if (desktopCartAnchor) {
                // Build a safe inner structure: icon + text + span with id 'cart-total'
                var icon = desktopCartAnchor.querySelector('.fa-shopping-cart');
                var iconHtml = icon ? icon.outerHTML : '<i class="fas fa-shopping-cart text-lg"></i>';
                desktopCartAnchor.innerHTML = iconHtml + ' <span>Cart</span> <span id="cart-total" class="bg-red-500 rounded-full px-2 text-xs absolute -top-2 -right-4">' + newCount + '</span>';
            }
        }catch(e){/* ignore */}
    }catch(e){/* ignore */}
}

// Show a transient visible badge when this script loads on the client.
try{
    (function(){
        var dbg = ensureCartDebug();
        if (dbg) {
            var ts = new Date().toLocaleTimeString();
            dbg.textContent = 'cart.js loaded @ ' + ts;
            dbg.style.opacity = '1';
            // Hide after 3s
            setTimeout(function(){ dbg.style.opacity = '0'; }, 3000);
        }
    })();
}catch(e){ console.debug('load-badge failed', e); }

// Also ensure listeners + header behavior are initialized if this script arrived late
try{ initCartListeners(); } catch(e){}
try{ initHeaderBehavior(); } catch(e){}
