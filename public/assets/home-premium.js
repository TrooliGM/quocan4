/* Presentation only: app.js owns the menu toggle and link activation. */
(() => {
  const header = document.querySelector('.home-premium .site-header');
  if (!header) return;
  const toggle = header.querySelector('#menu-toggle');
  const nav = header.querySelector('#nav-links');
  const compact = window.matchMedia('(max-width: 1279px)');
  const close = (restoreFocus = false) => {
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    if (restoreFocus) toggle.focus();
  };
  header.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      event.preventDefault();
      close(true);
    }
  });
  document.addEventListener('click', (event) => {
    if (!header.contains(event.target)) close();
  });
  header.addEventListener('focusout', (event) => {
    if (!header.contains(event.relatedTarget)) close();
  });
  compact.addEventListener('change', () => close(compact.matches && nav.contains(document.activeElement)));
})();
