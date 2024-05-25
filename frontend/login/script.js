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

        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        })
        .then(response => response.json())
        .then(data => {
            console.log('user logged in:', data);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', data.user_name);
            window.location.href = '/static/recommendation/index.html';
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            loginError.textContent = error.message;
        });
    });

    registerForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;

        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        })
        .then(response => response.json())
        .then(data => {
            console.log('user registered:', data);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', data.user_name);
            window.location.href = '/static/recommendation/index.html';
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            registerError.textContent = error.message;
        });
    });

    // Check if user is logged in
    const user_id = localStorage.getItem('user_id');
    if (user_id) {
        window.location.href = '/static/recommendation/index.html';
    }
});
