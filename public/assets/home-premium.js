/* Scroll/hash navigation; all links keep native navigation behavior. */
(() => {
  const nav = document.querySelector('.journey-nav');
  if (!nav) return;
  const links = [...nav.querySelectorAll('a')];
  const sections = links.map(a => a.hash && document.querySelector(a.hash)).filter(Boolean);
  function update() {
    const offset = nav.getBoundingClientRect().height + 24;
    let id = 'main';
    for (const section of sections) if (section.getBoundingClientRect().top <= Math.max(offset, (parseFloat(getComputedStyle(section).scrollMarginTop) || 0) + (parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0) + 2)) id = section.id;
    for (const link of links) {
      if (link.hash === '#' + id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }
  let frame;
  function schedule() { cancelAnimationFrame(frame); frame = requestAnimationFrame(update); }
  addEventListener('scroll', schedule, {passive:true});
  addEventListener('resize', schedule);
  addEventListener('hashchange', schedule);
  addEventListener('pageshow', schedule);
  update();
})();
