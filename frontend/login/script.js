document.addEventListener('DOMContentLoaded', () => {
    const showLoginPassword = document.getElementById('showLoginPassword');
    const showRegisterPassword = document.getElementById('showRegisterPassword');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginError = document.getElementById('loginError');
    const registerError = document.getElementById('registerError');

    showLoginPassword.addEventListener('click', function() {
        const passwordField = document.getElementById('loginPassword');
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            this.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            passwordField.type = 'password';
            this.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });

    showRegisterPassword.addEventListener('click', function() {
        const passwordField = document.getElementById('registerPassword');
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            this.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            passwordField.type = 'password';
            this.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });

    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            alert('login successful!');
            const data = await response.json();
            localStorage.setItem('userId', data.userId);
            window.location.href = '/static/recommendation/index.html';
        } else {
            const errorData = await response.json();
            loginError.textContent = errorData.message;
        }
    });

    registerForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;

        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        if (response.ok) {
            alert('Registration successful!');
            const data = await response.json();
            localStorage.setItem('userId', data.userId);
            window.location.href = '/static/recommendation/index.html';
        } else {
            const errorData = await response.json();
            registerError.textContent = errorData.message;
        }
    });

    // Check if user is logged in
    const userId = localStorage.getItem('userId');
    if (userId) {
        window.location.href = '/static/recommendation/index.html';
    }
});
