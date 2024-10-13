document.addEventListener('DOMContentLoaded', function() {
    const loginSection = document.getElementById('login-section');
    const registerSection = document.getElementById('register-section');
    const analysisSection = document.getElementById('analysis-section');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const registerLink = document.getElementById('register-link');
    const loginLink = document.getElementById('login-link');
    const signOutBtn = document.getElementById('sign-out-btn');

    function showSection(section) {
        loginSection.style.display = 'none';
        registerSection.style.display = 'none';
        analysisSection.style.display = 'none';
        section.style.display = 'block';
    }

    function checkLoggedIn() {
        const currentUser = localStorage.getItem('currentUser');
        if (currentUser) {
            showSection(analysisSection);
        } else {
            showSection(loginSection);
        }
    }

    loginBtn.addEventListener('click', function() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const users = JSON.parse(localStorage.getItem('users')) || {};
        
        if (users[username] && users[username].password === password) {
            localStorage.setItem('currentUser', username);
            showSection(analysisSection);
        } else {
            alert('Invalid username or password');
        }
    });

    registerBtn.addEventListener('click', function() {
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;
        const confirmPassword = document.getElementById('reg-confirm-password').value;
        const users = JSON.parse(localStorage.getItem('users')) || {};
        
        if (users[username]) {
            alert('Username already exists');
        } else if (password !== confirmPassword) {
            alert('Passwords do not match');
        } else {
            users[username] = { password: password, results: [] };
            localStorage.setItem('users', JSON.stringify(users));
            localStorage.setItem('currentUser', username);
            showSection(analysisSection);
        }
    });

    registerLink.addEventListener('click', function(e) {
        e.preventDefault();
        showSection(registerSection);
    });

    loginLink.addEventListener('click', function(e) {
        e.preventDefault();
        showSection(loginSection);
    });

    signOutBtn.addEventListener('click', function() {
        localStorage.removeItem('currentUser');
        showSection(loginSection);
        // Clear any sensitive data from the page
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        // Optionally, reload the page to clear any remaining state
        // window.location.reload();
    });

    checkLoggedIn();
});

// Add these functions at the end of the file

function signOut() {
    localStorage.removeItem('currentUser');
    showSection(document.getElementById('login-section'));
}

function goToMyResults() {
    window.location.href = '/my_results';
}

// Add these event listeners in the DOMContentLoaded function
document.getElementById('sign-out-btn').addEventListener('click', signOut);
document.getElementById('my-results-btn').addEventListener('click', goToMyResults);
