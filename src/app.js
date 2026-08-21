const password = document.getElementById('password');
const togglePassword = document.getElementById('togglePassword');

if (togglePassword && password) {
  togglePassword.addEventListener('click', () => {
    const visible = password.type === 'text';
    password.type = visible ? 'password' : 'text';
    togglePassword.textContent = visible ? 'Mostrar' : 'Ocultar';
    togglePassword.setAttribute('aria-label', visible ? 'Mostrar senha' : 'Ocultar senha');
  });
}

const params = new URLSearchParams(window.location.search);
const message = document.getElementById('loginMessage');
if (message && params.get('error') === '1') {
  message.textContent = 'Usuário ou senha incorretos.';
  message.classList.add('error');
}
