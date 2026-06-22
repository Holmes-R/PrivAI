const api = {
    getToken: () => localStorage.getItem('access_token'),
    setToken: (access, refresh) => {
        localStorage.setItem('access_token', access);
        if (refresh) localStorage.setItem('refresh_token', refresh);
    },
    clearToken: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
    isAuthenticated: () => !!localStorage.getItem('access_token'),

    request: async (url, method = 'GET', body = null) => {
        const attempt = async (retryCount = 0) => {
            const headers = { 'Content-Type': 'application/json' };
            const token = api.getToken();
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const opts = { method, headers };
            if (body) opts.body = JSON.stringify(body);

            const resp = await fetch(url, opts);
            if (resp.status === 401 && retryCount < 1) {
                const refreshed = await api.refreshToken();
                if (refreshed) return attempt(1);
                api.clearToken();
                window.location.href = '/login/';
                return null;
            }
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                showAlert(err.detail || Object.values(err).flat().join(', ') || 'Request failed', 'danger');
                return null;
            }
            const text = await resp.text();
            return text ? JSON.parse(text) : null;
        };

        try {
            return await attempt(0);
        } catch (e) {
            showAlert('Network error. Is the server running?', 'danger');
            return null;
        }
    },

    upload: async (url, formData) => {
        const token = api.getToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        try {
            const resp = await fetch(url, { method: 'POST', headers, body: formData });
            if (resp.status === 401) {
                const refreshed = await api.refreshToken();
                if (refreshed) {
                    headers['Authorization'] = `Bearer ${api.getToken()}`;
                    const retry = await fetch(url, { method: 'POST', headers, body: formData });
                    return retry.ok ? retry.json() : null;
                }
                api.clearToken();
                window.location.href = '/login/';
                return null;
            }
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                showAlert(Object.values(err).flat().join(', '), 'danger');
                return null;
            }
            showAlert('Upload successful!', 'success');
            return resp.json();
        } catch (e) {
            showAlert('Upload failed. Is the server running?', 'danger');
            return null;
        }
    },

    login: async (email, password) => {
        const data = await api.request('/auth/login/', 'POST', { email, password });
        if (data) {
            api.setToken(data.access, data.refresh);
            return data;
        }
        return null;
    },

    register: async (firstName, lastName, email, password) => {
        const data = await api.request('/auth/register/', 'POST', {
            first_name: firstName, last_name: lastName, email, password
        });
        if (data) {
            api.setToken(data.access, data.refresh);
            return data;
        }
        return null;
    },

    logout: () => { api.clearToken(); window.location.href = '/'; },

    refreshToken: async () => {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) return false;
        try {
            const resp = await fetch('/auth/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh })
            });
            if (resp.ok) {
                const data = await resp.json();
                api.setToken(data.access);
                return true;
            }
            return false;
        } catch { return false; }
    }
};
