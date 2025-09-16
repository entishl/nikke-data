export const formatGradeAndCore = (character) => {
  if (!character) return '';
  const grade = character.limit_break_grade || 0;
  const core = character.core || 0;

  let stars = '';
  const totalStars = 3;
  for (let i = 0; i < totalStars; i++) {
    stars += i < grade ? '★' : '☆';
  }

  let coreDisplay;
  if (core === 7) {
    coreDisplay = '+max';
  } else if (core > 0) {
    coreDisplay = `+${core}`;
  } else {
    coreDisplay = '';
  }
  return `${stars} ${coreDisplay}`.trim();
};

export const formatItem = (character) => {
  if (!character || !character.item_rare) return '';
  return `${character.item_rare}-${character.item_level}`;
};

export const formatKilo = (value) => {
  if (typeof value !== 'number') return '';
  return `${(value / 10000).toFixed(0)}`;
};