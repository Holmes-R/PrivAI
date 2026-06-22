function showAlert(msg, type = 'info') {
    const container = document.getElementById('alerts');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `${msg}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    container.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const btn = document.getElementById('darkModeToggle');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark ? '1' : '0');
    if (btn) btn.innerHTML = isDark ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-fill"></i>';
}

document.addEventListener('DOMContentLoaded', () => {
    const authNav = document.getElementById('authNav');
    const indexAuth = document.getElementById('indexAuth');
    const indexApp = document.getElementById('indexApp');

    if (localStorage.getItem('darkMode') === '1') {
        document.body.classList.add('dark-mode');
        const btn = document.getElementById('darkModeToggle');
        if (btn) btn.innerHTML = '<i class="bi bi-sun-fill"></i>';
    }

    if (api.isAuthenticated()) {
        if (authNav) {
            authNav.innerHTML = `
                <li class="nav-item"><a class="nav-link" href="#" onclick="api.logout()"><i class="bi bi-box-arrow-right me-1"></i>Logout</a></li>
            `;
        }
        if (indexAuth && indexApp) {
            indexAuth.classList.add('d-none');
            indexApp.classList.remove('d-none');
        }
    } else {
        if (authNav) {
            authNav.innerHTML = `
                <li class="nav-item"><a class="nav-link" href="/login/"><i class="bi bi-box-arrow-in-right me-1"></i>Login</a></li>
                <li class="nav-item"><a class="nav-link" href="/register/"><i class="bi bi-person-plus me-1"></i>Register</a></li>
            `;
        }
        const protectedLinks = document.querySelectorAll('#navLinks .nav-link');
        protectedLinks.forEach(l => l.addEventListener('click', (e) => {
            if (!api.isAuthenticated()) {
                e.preventDefault();
                window.location.href = '/login/';
            }
        }));
    }
});
