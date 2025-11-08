// static/js/checkout.js

var total = '{{ order.get_cart_total }}' // Total value passed from checkout.html

// Look for the Submit Order button/form
var form = document.getElementById('form-button');

if (form) {
    form.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Submit button clicked...');
        
        // Hide the payment form and show the loading spinner/message
        document.getElementById('shipping-info').style.display = 'none';
        document.getElementById('user-info').style.display = 'none';
        document.getElementById('payment-info').innerHTML = '<h3>Processing Payment...</h3>';

        submitFormData();
    });
}

// Function to handle the actual AJAX submission
function submitFormData() {
    console.log('Sending data to backend...');
    
    // Get CSRF Token from cookie
    var csrftoken = getCookie('csrftoken');
    
    // 1. Gather User & Shipping Information
    var userFormData = {
        'name': null,
        'email': null,
        'total': total,
    };

    var shippingInfo = {
        'address': null,
        'city': null,
        'state': null,
        'zipcode': null,
        'country': null,
    };
    
    // Collect data from the form fields
    shippingInfo.address = form.querySelector('#shipping-address').value;
    shippingInfo.city = form.querySelector('#shipping-city').value;
    shippingInfo.state = form.querySelector('#shipping-state').value;
    shippingInfo.zipcode = form.querySelector('#shipping-zipcode').value;
    shippingInfo.country = form.querySelector('#shipping-country').value; // Added country
    
    userFormData.name = form.querySelector('#user-name').value;
    userFormData.email = form.querySelector('#user-email').value;


    // 2. Prepare the data payload
    var url = "/process_order/";
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'form': userFormData,
            'shipping': shippingInfo
        })
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('Success:', data);
        alert('Transaction completed! Your order is being processed.');

        // Clear local cart (if used for anonymous/guest users)
        // document.cookie = 'cart' + '=' + JSON.stringify({}) + ";domain=;path=/";

        window.location.href = "{% url 'store:home' %}"; // Redirect to home or a confirmation page
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('payment-info').innerHTML = '<h3>An error occurred during payment processing. Please try again.</h3>';
    });
}


// Function to get the CSRF token from cookies (required for AJAX POST)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}