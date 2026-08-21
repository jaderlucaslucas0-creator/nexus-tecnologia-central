const form = document.getElementById('loginForm');
const password = document.getElementById('password');
const togglePassword = document.getElementById('togglePassword');
const message = document.getElementById('loginMessage');

togglePassword.addEventListener('click', () => {
  const visible = password.type === 'text';
  password.type = visible ? 'password' : 'text';
  togglePassword.textContent = visible ? 'Mostrar' : 'Ocultar';
  togglePassword.setAttribute('aria-label', visible ? 'Mostrar senha' : 'Ocultar senha');
});

form.addEventListener('submit', (event) => {
  event.preventDefault();
  message.textContent = 'A autenticação será configurada na próxima etapa.';
});
