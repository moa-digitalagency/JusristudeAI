document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Connexion réussie!', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 500);
        } else {
            showAlert(data.error || 'Erreur de connexion', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
});

function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    
    alertContainer.innerHTML = `
        <div class="alert ${alertClass}">
            ${message}
        </div>
    `;
}
