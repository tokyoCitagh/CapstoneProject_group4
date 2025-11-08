// Function to send data to the Django update_item view using AJAX
function updateUserOrder(productId, action){
    console.log('User is logged in, sending data...');

    // The endpoint path
    var url = '/store/update_item/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // CRITICAL: Assumes 'csrftoken' is globally defined in base.html
            'X-CSRFToken': csrftoken, 
        },
        // Send the data as a JSON string
        body: JSON.stringify({'productId': productId, 'action': action}) 
    })
    .then((response) => {
        if (!response.ok) {
            // Include status in error for better debugging
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then((data) => {
        console.log('Success:', data);
        
        // --- INSTANT UI UPDATE ---
        var cartTotalElement = document.getElementById('cart-total');
        
        if (cartTotalElement && data.cartItems !== undefined) {
            // Update the cart counter instantly using the count returned by the Django view
            cartTotalElement.innerText = data.cartItems;
            console.log('Cart count updated to:', data.cartItems);
        } 
        
        // --- RELOAD LOGIC FOR CART PAGE ---
        // If the current path is /store/cart/, we must reload the page 
        // to update all item quantities, totals, and remove deleted items.
        // This is the most reliable way to update the whole cart view.
        if (window.location.pathname.includes('/store/cart/')) {
            window.location.reload();
        }
        // --- END RELOAD LOGIC ---

    })
    .catch((error) => {
        console.error('Fetch Error:', error);
        // Replaced alert() with console error message
        console.error('Could not update cart. Check the console for details or ensure user is logged in.');
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
        btn.addEventListener('click', function(e){ 
            e.preventDefault(); // Stop default button/link action
            
            var productId = this.dataset.product;
            var action = this.dataset.action; 
            
            console.log(`Button Clicked. Product ID: ${productId}, Action: ${action}`);

            // Check if user variable is globally defined and not AnonymousUser
            // Assumes 'user' is correctly set in base.html 
            if (typeof user !== 'undefined' && user !== 'AnonymousUser'){
                updateUserOrder(productId, action);
            } else {
                // Replaced alert() with console warn message
                console.warn("Authentication required: Please log in to update the cart.");
            }
        });
    });
});
