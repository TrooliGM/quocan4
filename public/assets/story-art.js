// Minh họa vector gốc cho La Bàn. Mỗi cảnh có đạo cụ và bố cục riêng.
const ink = '#26473e', skin = '#dfaa84', paper = '#fffdf3';
const line = `stroke="${ink}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"`;
function person(x, y, color = '#f5c66d', pose = 'talk', doctor = false, flip = false) {
  return `<g transform="translate(${x} ${y})${flip ? ' scale(-1 1)' : ''}">
    <ellipse cx="0" cy="188" rx="48" ry="10" fill="#476c4c" opacity=".1"/>
    <path d="M-23 127l-4 54h20l7-44 9 44h20l-3-54" fill="#496d68" ${line}/>
    <path d="M-30 180h23v9h-34q-1-9 11-9m39 0h20l11 9H9z" fill="${ink}"/>
    <path d="M-26 50Q-43 64-37 119l10 13h53l10-14q4-52-13-68Z" fill="${doctor ? paper : color}" ${line}/>
    <path d="M-10 41v16q11 12 20 0V41" fill="${skin}" ${line}/>
    <ellipse cx="0" cy="19" rx="29" ry="34" fill="${skin}" ${line}/>
    <path d="M-28 19Q-38-26 8-18q26 2 25 34L19 6 4 1Q-5 20-28 19Z" fill="${ink}"/>
    <circle cx="-8" cy="23" r="2.2" fill="${ink}"/><circle cx="12" cy="23" r="2.2" fill="${ink}"/>
    <path d="M-3 36q6 4 11-1" fill="none" ${line}/>
    ${pose === 'work' ? `<path class="moving-hand" d="M-32 72l-7 28 34 6M28 72l22 24 20-3" fill="none" stroke="${doctor ? paper : color}" stroke-width="18" stroke-linecap="round"/><circle cx="-4" cy="106" r="8" fill="${skin}"/><circle cx="69" cy="93" r="8" fill="${skin}"/>` : `<path d="M-30 73l-14 46" fill="none" stroke="${doctor ? paper : color}" stroke-width="18" stroke-linecap="round"/><circle cx="-45" cy="122" r="8" fill="${skin}"/><g class="moving-hand"><path d="M30 71l23 15 20-25" fill="none" stroke="${doctor ? paper : color}" stroke-width="18" stroke-linecap="round"/><circle cx="75" cy="58" r="8" fill="${skin}"/></g>`}
    ${doctor ? `<path d="M-14 56v31q13 20 27 0V56" fill="none" stroke="#568c84" stroke-width="5"/><circle cx="13" cy="87" r="7" fill="#568c84"/><path d="M1 61v65" stroke="#a6c8b3" stroke-width="2"/><rect x="15" y="105" width="12" height="9" rx="2" fill="#e4ae75"/>` : `<rect x="-12" y="71" width="22" height="14" rx="3" fill="${paper}" opacity=".6"/>`}
  </g>`;
}
function windowArt(night = false) {
  return `<g ${line}><rect x="45" y="68" width="125" height="125" rx="45" fill="${night ? '#45645f' : '#c3dfdf'}"/><path d="M108 68v125M45 130h125" fill="none"/><circle cx="135" cy="99" r="16" fill="#f7d480" stroke="none"/>${night ? '<path d="M140 80a16 16 0 0 0 12 26 19 19 0 0 1-12-26" fill="#45645f" stroke="none"/>' : '<path d="M53 169q30-20 55 0 35-28 61 0v23H53Z" fill="#9fc7ab" stroke="none"/>'}</g>`;
}
function plant(x=628,y=272) {return `<g transform="translate(${x} ${y})" ${line}><path d="M-19 24h38l-6 48h-26Z" fill="#d69475"/><path d="M0 24v-58" fill="none"/><path d="M0 1q-40-3-34-31 31-1 34 31M0-15q34-3 30-32Q3-47 0-15" fill="#85ab80"/></g>`;}
function board(x=330,y=116,type='notes') {
  const inside = {
    notes:'<rect x="18" y="19" width="45" height="35" fill="#e6b68d"/><rect x="80" y="19" width="45" height="35" fill="#9fbf9f"/><rect x="18" y="68" width="45" height="35" fill="#f1d68c"/><path d="M80 74h43m-43 12h30m-30 12h35"/>',
    chart:'<path d="M19 18v88h125" fill="none"/><path class="draw-line" d="M27 88l26-17 28 9 24-40 31-12" fill="none" stroke="#cb7457" stroke-width="5"/><circle class="signal" cx="105" cy="40" r="6" fill="#edc777"/>',
    lesson:'<path d="M82 106V53m0 20Q29 75 40 34q37 0 42 39m0-9q46-2 38-41-34 3-38 41" fill="#a8c593"/><path d="M22 106h25m69 0h24"/>',
    medical:'<path d="M71 29v28H44v20h27v27h22V77h27V57H93V29Z" fill="#c8755a" stroke="none"/>',
    poster:'<rect x="20" y="12" width="124" height="106" fill="#ebc97d" stroke="none"/><circle cx="58" cy="50" r="23" fill="#c7775f" stroke="none"/><path d="M89 36h39m-39 13h28M34 92h95m-95 13h66" stroke-width="5"/>',
    flow:'<rect x="17" y="34" width="34" height="30" rx="4" fill="#a3c8b3"/><path d="M52 49h18m-5-5 6 5-6 5" fill="none"/><rect x="74" y="34" width="34" height="30" rx="4" fill="#f1d386"/><path d="M90 65v19H33" fill="none"/><circle cx="29" cy="86" r="7" fill="#c37958"/>',
  };
  return `<g transform="translate(${x} ${y})" ${line}><rect width="168" height="132" rx="6" fill="${paper}"/><g stroke-width="2">${inside[type]||inside.notes}</g></g>`;
}
function desk(x=270,y=302) {return `<g transform="translate(${x} ${y})" ${line}><path d="M5 9v61m180-61v61" stroke-width="7"/><rect x="-10" y="0" width="218" height="15" rx="5" fill="#c69773"/></g>`;}
function laptop(x=320,y=254,kind='code') {return `<g transform="translate(${x} ${y})" ${line}><path d="M-11 42h103l-10-61H0Z" fill="#41685f"/><path d="M7-10h66l7 42H0Z" fill="#e9f0dd" stroke="none"/>${kind==='code'?'<path class="draw-line" d="M21 2l-9 8 11 7m30-15 10 8-9 7M43-1l-9 22" fill="none" stroke="#568473" stroke-width="3"/>':kind==='poster'?'<circle cx="30" cy="11" r="13" fill="#ca795b" stroke="none"/><path d="M49 1h15m-15 9h13m-46 16h45" stroke-width="2"/>':'<path class="draw-line" d="M12 25l15-14 16 7L65-1" fill="none" stroke="#c3765a"/>'}<path d="M-20 43h120v8H-20Z" fill="#91b3a2"/></g>`;}
function paperPile(x=307,y=282) {return `<g transform="translate(${x} ${y})" ${line}><path d="M0 6l47-11 29 22-51 12Z" fill="#e7e4cd"/><path d="M0 0l47-11 29 22-51 12Z" fill="${paper}"/><path d="M23-1l21-5m-14 13 21-5" stroke-width="2"/></g>`;}
const staff=(x,y,flip=false)=>person(x,y,'#e7b670','talk',true,flip);
const pair=(color='#d59a79')=>person(210,167,'#84ad9b','work')+person(524,177,color,'talk',false,true);
const scenes={
  records:()=>board(375,122,'chart')+person(220,170,'#d0ba72','work')+desk(286,309)+laptop(347,258,'chart')+paperPile(438,289),
  consult:()=>board(344,142,'medical')+person(458,180,'#d5b268','talk',false,true)+staff(237,158)+desk(284,306)+paperPile(310,294),
  conference:()=>board(311,121,'chart')+staff(201,170)+staff(533,174,true)+desk(286,311)+paperPile(304,298),
  prescription:()=>person(490,186,'#c79b74','talk',false,true)+staff(214,171)+desk(288,311)+paperPile(320,292)+'<path class="draw-line" d="M377 271l-22 24" stroke="#b56747" stroke-width="5"/>',
  emergency:()=>board(475,135,'chart')+staff(183,173)+staff(581,181,true)+'<g '+line+'><rect x="287" y="267" width="234" height="37" rx="13" fill="#94bfb4"/><path d="M297 305v39m211-39v39"/><circle cx="298" cy="352" r="10" fill="#496960"/><circle cx="508" cy="352" r="10" fill="#496960"/><ellipse cx="327" cy="252" rx="22" ry="17" fill="#dfaa84"/><path d="M349 246q117-25 154 21H348Z" fill="#f3e6c3"/></g>',
  planning:()=>board(325,116,'flow')+pair()+desk()+paperPile(),
  coding:()=>board(367,134,'notes')+person(239,172,'#93b5a0','work')+desk(300,307)+laptop(351,256)+'<g class="floating-prop" '+line+'><rect x="515" y="214" width="51" height="39" rx="7" fill="#f2d382"/><path d="m528 233 8 7 18-19" fill="none"/></g>',
  testing:()=>board(339,130,'chart')+pair('#e6bb69')+desk()+laptop(320,249)+'<g class="signal"><circle cx="404" cy="270" r="12" fill="#ce7858"/><path d="M404 264v6m0 4v2" stroke="#fffdf3" stroke-width="3"/></g>',
  demo:()=>board(351,132,'flow')+pair('#d7a288')+desk()+laptop(320,249,'chart'),
  brief:()=>board(338,118,'notes')+pair('#d9bd78')+desk()+paperPile(),
  sketch:()=>board(360,133,'poster')+person(238,175,'#cf9679','work')+desk(295,308)+paperPile(335,289)+'<path class="draw-line" d="M356 273l-23 27" stroke="#d69650" stroke-width="6"/>',
  layout:()=>person(237,173,'#cf9679','work')+desk(285,309)+laptop(325,258,'poster')+board(477,161,'poster'),
  review:()=>board(343,124,'poster')+pair('#a9bd82')+desk()+paperPile(),
  lesson:()=>board(349,113,'lesson')+person(230,170,'#e1b269','work')+desk(282,307)+paperPile(),
  classroom:()=>board(307,112,'lesson')+person(208,158,'#e1b269')+'<g transform="translate(90 105) scale(.74)">'+person(420,180,'#93afa5','work')+person(610,180,'#cd9b85','work')+'</g>'+desk(360,321),
  marking:()=>board(376,127,'notes')+person(249,174,'#e1b269','work')+desk(302,310)+paperPile(333,294)+'<path class="draw-line" d="M385 278l-15 24" stroke="#bc6c52" stroke-width="5"/>',
  mentoring:()=>board(350,118,'lesson')+person(224,170,'#e1b269')+'<g transform="translate(102 77) scale(.83)">'+person(494,180,'#8ea99a','talk',false,true)+'</g>'+desk(293,313)+paperPile(),
  sampling:()=>'<path d="M0 286q149-31 283 7t417-3v110H0Z" fill="#a6cdb8"/><path d="M322 278q-60 47 63 73t88 49h170q26-73-91-80t-71-42Z" fill="#a4d1da"/><path class="draw-line" d="M347 311h82m-45 53h119" fill="none" stroke="#f0faf3" stroke-width="5"/>'+person(220,151,'#e3b86b','work')+'<g class="floating-prop" '+line+'><rect x="335" y="248" width="32" height="49" rx="7" fill="#d6e9df"/><path d="M339 273h24v16h-24Z" fill="#9cc5cf" stroke="none"/><path d="M334 248h35" stroke-width="7"/></g>',
  analysis:()=>board(375,122,'chart')+person(220,170,'#d0ba72','work',true)+desk(286,309)+laptop(347,258,'chart')+'<g '+line+'><path d="M290 264v33h21v-33" fill="#a4d0d0"/><path d="M285 262h31"/></g>',
  system:()=>board(332,119,'flow')+pair('#dcbb72')+desk()+paperPile(),
  monitoring:()=>board(306,99,'chart')+person(203,162,'#dbbb71')+person(550,174,'#8aaf9f','work',false,true)+'<g '+line+'><rect x="318" y="282" width="73" height="67" rx="10" fill="#97bdb2"/><rect x="420" y="269" width="73" height="80" rx="10" fill="#a6c8d0"/><path d="M391 307h29M326 319h57m47-18h55" fill="none"/></g>',
  editorial:()=>board(338,119,'notes')+pair('#e4bc77')+desk()+paperPile(),
  interview:()=>person(235,171,'#bc9e86')+person(503,181,'#a3b97e','talk',false,true)+'<g '+line+'><rect x="299" y="213" width="31" height="45" rx="13" fill="#496b66"/><path d="M314 257v30" stroke-width="7"/><path d="M306 223h16m-16 7h16" stroke="#c6d9c8" stroke-width="2"/></g>',
  editing:()=>board(360,120,'notes')+person(229,172,'#bc9e86','work')+desk(294,307)+laptop(332,257)+paperPile(448,290),
  feedback:()=>board(353,123,'chart')+pair('#d9b96f')+desk()+laptop(320,249,'chart'),
};
export function storyArt(art) {
  const outdoors=art==='sampling', night=art==='emergency';
  return `<svg viewBox="0 0 700 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><rect width="700" height="400" fill="${outdoors?'#e0eada':night?'#ccdcd7':'#dfeae0'}"/>
    ${outdoors?'<circle cx="560" cy="96" r="37" fill="#eed38b"/><path d="M0 246q104-116 209-22 96-131 191-29 154-81 300 35v170H0Z" fill="#b5c8a1"/>':windowArt(night)+'<path d="M0 305h700v95H0Z" fill="#e7dcc2"/><path d="M0 305h700" stroke="#a7b8a3" stroke-width="2"/>'}
    ${!outdoors?plant():''}${(scenes[art]||scenes.planning)()}
    <path d="M44 367h36m549 13h34" stroke="#a8b3a0" stroke-width="2" stroke-linecap="round"/>
  </svg>`;
}
