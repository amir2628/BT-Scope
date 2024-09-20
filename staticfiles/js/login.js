document.addEventListener('DOMContentLoaded', function() {
    const forgotPasswordButton = document.getElementById('forgot-password');
    const modal = document.getElementById('forgot-password-modal');
    const closeButton = document.getElementById('close-modal');
    const forgotPasswordForm = document.getElementById('forgot-password-form');
    const responseMessage = document.getElementById('response-message');

    forgotPasswordButton.addEventListener('click', function() {
        modal.style.display = 'block';
    });

    closeButton.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    forgotPasswordForm.addEventListener('submit', function(event) {
        event.preventDefault();
    
        const email = document.getElementById('email').value;
    
        if (email) {
            fetch('/api/password_reset/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')  // Ensure CSRF token is correctly set
                },
                body: JSON.stringify({ email: email })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'OK') {
                    responseMessage.textContent = 'Password reset link sent to your email.';
                    responseMessage.style.color = 'green';
                    forgotPasswordForm.reset();
                } else {
                    responseMessage.textContent = data.message || 'An error occurred. Please try again.';
                    responseMessage.style.color = 'red';
                }
            })
            .catch(error => {
                responseMessage.textContent = 'An error occurred. Please try again.';
                responseMessage.style.color = 'red';
            });
        } else {
            responseMessage.textContent = 'Please enter a valid email address.';
            responseMessage.style.color = 'red';
        }
    });
    

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});









document.getElementById('register').addEventListener('click', function() {
    window.location.href = '/register/';
});

document.getElementById('homeButton').addEventListener('click', function() {
    window.location.href = '/';
});
