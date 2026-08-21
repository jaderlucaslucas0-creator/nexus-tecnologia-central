const form = document.getElementById('loginForm');
const password = document.getElementById('password');
const togglePassword = document.getElementById('togglePassword');
const message = document.getElementById('loginMessage');

// Acesso inicial do usuário único do sistema Render.
// Depois podemos trocar estes dados por autenticação segura em banco.
const ACCESS_USER = 'admin';
const ACCESS_PASSWORD = '1234';

togglePassword.addEventListener('click', () => {
  const visible = password.type === 'text';
  password.type = visible ? 'password' : 'text';
  togglePassword.textContent = visible ? 'Mostrar' : 'Ocultar';
  togglePassword.setAttribute('aria-label', visible ? 'Mostrar senha' : 'Ocultar senha');
});

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const username = document.getElementById('username').value.trim();
  const enteredPassword = password.value;

  if (username === ACCESS_USER && enteredPassword === ACCESS_PASSWORD) {
    sessionStorage.setItem('renderAuthenticated', 'true');
    message.textContent = 'Acesso autorizado. Abrindo o Render...';
    message.classList.remove('error');
    message.classList.add('success');

    setTimeout(() => {
      window.location.href = './dashboard.html';
    }, 500);
    return;
  }

  message.textContent = 'Usuário ou senha incorretos.';
  message.classList.remove('success');
  message.classList.add('error');
});
