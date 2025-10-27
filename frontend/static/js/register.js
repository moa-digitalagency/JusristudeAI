document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (password !== confirmPassword) {
        showAlert('Les mots de passe ne correspondent pas', 'error');
        return;
    }
    
    if (password.length < 8) {
        showAlert('Le mot de passe doit contenir au moins 8 caractères', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            showAlert(data.error || 'Erreur lors de l\'inscription', 'error');
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
