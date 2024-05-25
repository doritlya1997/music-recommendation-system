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

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const errorData = await response.json();
                loginError.textContent = `Error ${response.status}: ${errorData.message || response.statusText}`;
                return;
            }

            const data = await response.json();
            console.log('user logged in:', data);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', data.user_name);
            window.location.href = '/static/recommendation/index.html';
        } catch (error) {
            loginError.textContent = "An unexpected error occurred.";
        }
    });

    registerForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;

        try {
            const response = await fetch('/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const errorData = await response.json();
                registerError.textContent = `Error ${response.status}: ${errorData.message || response.statusText}`;
                return;
            }

            const data = await response.json();
            console.log('user logged in:', data);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', data.user_name);
            window.location.href = '/static/recommendation/index.html';
        } catch (error) {
            registerError.textContent = "An unexpected error occurred.";
        }
    });

    // Check if user is logged in
    const user_id = localStorage.getItem('user_id');
    if (user_id) {
        window.location.href = '/static/recommendation/index.html';
    }
});
