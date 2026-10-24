const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').toLowerCase();
export function explorationQuestion(career, survey) {
  const tasks=(career.daily_tasks.length>=5 ? career.daily_tasks.slice(2,4) : career.daily_tasks.slice(0,2)).map(s=>s.replace(/[.!?]+$/,''));
  const goal=normalize(survey?.answers?.[4] || '');
  let angle='Em có thể bắt đầu khám phá những việc này bằng hoạt động nhỏ nào khi còn đi học?';
  if (/ky nang|ren luyen|mon hoc|chuan bi/.test(goal)) angle=`Để làm được những việc ấy, em nên rèn kỹ năng ${career.skills[0].toLocaleLowerCase('vi')} qua hoạt động nào ở trường?`;
  else if (/kho khan|thu thach|trach nhiem/.test(goal)) angle=`Người làm nghề xử lý thử thách “${career.challenges[0].replace(/[.!?]+$/,'')}” như thế nào?`;
  else if (/moi truong|noi lam|mot ngay|hang ngay/.test(goal)) angle=`Những việc đó được sắp xếp thế nào trong một ngày làm việc, tại ${career.work_environment.replace(/[.!?]+$/,'')}?`;
  return `Em muốn tìm hiểu nghề ${career.name}. Những việc như “${tasks[0]}” và “${tasks[1]}” diễn ra thế nào trong thực tế? ${angle}`.slice(0,1800);
}
