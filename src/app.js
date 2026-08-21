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

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  message.textContent = 'Entrando...';
  message.className = 'login-message';

  const formData = new FormData(form);

  try {
    const response = await fetch('/login', {
      method: 'POST',
      body: formData,
      redirect: 'follow'
    });

    if (response.redirected) {
      window.location.href = response.url;
      return;
    }

    const data = await response.json();
    message.textContent = data.message || 'Não foi possível entrar.';
    message.className = 'login-message error';
  } catch (error) {
    message.textContent = 'Erro de conexão com o servidor.';
    message.className = 'login-message error';
  }
});
