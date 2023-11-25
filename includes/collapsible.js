const collapsibles = document.querySelectorAll('.collapsible');

for (const collapsible of collapsibles) {
  const toggle = collapsible.querySelector('.collapsible-toggle');
  const content = collapsible.querySelector('.collapsible-content');

  toggle.addEventListener('click', () => {
    content.style.display = content.style.display === 'none' ? 'block' : 'none';
  });
}