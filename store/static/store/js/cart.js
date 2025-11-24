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
        // --- END RELOAD LOGIC ---

    })
    .catch((error) => {
        console.error('Fetch Error:', error);
        // Replaced alert() with console error message
        console.error('Could not update cart. Check the console for details or ensure user is logged in.');
        showToast('Cart update failed. Try again.');
    });
}


document.addEventListener('DOMContentLoaded', function() {
    
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

                e.preventDefault(); // Stop default button/link action

                var productId = btn.dataset.product;
                var action = btn.dataset.action;

                console.log(`Cart button activated. Product ID: ${productId}, Action: ${action}, event=${e.type}`);

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
                    } catch (uiErr) { console.debug('optimistic UI update failed', uiErr); }

                    updateUserOrder(productId, action);
                } else {
                    console.warn('Authentication required: Please log in to update the cart.');
                }
            } catch (ex) {
                console.error('Cart handler error', ex);
            }
        }

        // Prefer pointerdown for better mobile responsiveness; also listen to click as fallback
        btn.addEventListener('pointerdown', handler);
        btn.addEventListener('click', handler);
        // Mark button for debugging
        btn.setAttribute('data-listener', '1');
    });
});

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
