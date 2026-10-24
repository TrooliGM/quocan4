// Hình biên tập tự vẽ bằng SVG; không giả làm ảnh chụp hoặc thumbnail YouTube.
const symbols={technology:'⌘',health:'✚',education:'▤',engineering:'⚙',business:'◇',finance:'▥',design:'✳',media:'◉','public-service':'⚖',environment:'♧',hospitality:'☀',science:'⚗'};
export function comicCover(category){
  const mark=symbols[category]||'✦';
  return `<svg viewBox="0 0 640 360" aria-hidden="true" focusable="false"><rect width="640" height="360" fill="#e9ede3"/><path d="M0 280Q150 180 300 270T640 250V360H0" fill="#dce4d4"/><rect x="98" y="70" width="290" height="205" rx="15" fill="#fffdf5" transform="rotate(-7 240 170)"/><path d="M150 128H280M146 151H246M140 217H218" stroke="#b7c7b3" stroke-width="10" stroke-linecap="round"/><rect x="300" y="105" width="220" height="170" rx="22" fill="#183f34" transform="rotate(6 410 190)"/><text x="410" y="222" text-anchor="middle" fill="#f3e5c9" font-family="sans-serif" font-size="96">${mark}</text><circle cx="508" cy="72" r="16" fill="#ce8b67"/><path d="M83 302h65m359-15h40" stroke="#b7c7b3" stroke-width="5" stroke-linecap="round"/></svg>`;
}
