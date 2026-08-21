document.querySelectorAll('nav a').forEach(link => {
  link.addEventListener('click', () => {
    document.querySelectorAll('nav a').forEach(item => item.classList.remove('active'));
    link.classList.add('active');
  });
});

function addSystemMessage() {
  alert('O cadastro de sistemas será implementado na próxima etapa.');
}

document.getElementById('newSystem').addEventListener('click', addSystemMessage);
document.getElementById('emptyAction').addEventListener('click', addSystemMessage);
