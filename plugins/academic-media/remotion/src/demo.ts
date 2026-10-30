import type {LectureProps} from './types';

// Пример для `npm run studio`; настоящие данные приходят из render.py (--props).
export const DEMO: LectureProps = {
  meta: {
    title: 'Нормализация реляционных баз данных', course: 'Базы данных', teacher: 'Преподаватель',
    accent: '#1F4E79', lang: 'ru', partLabel: '', topic: '', sectionLabel: 'Раздел',
    endLabel: 'Спасибо за внимание', slideCount: 2,
  },
  intro: 5,
  outro: 4,
  slides: [
    {n: 1, type: 'section', title: 'Зачем нормализовать', subtitle: '', bullets: [], table: null,
      start: 5, duration: 4, audio: null, audioOffset: 0.5, reveal: []},
    {n: 2, type: 'bullets', title: 'Аномалии таблиц', subtitle: '',
      bullets: ['Аномалия вставки', 'Аномалия обновления', 'Аномалия удаления'], table: null,
      start: 9, duration: 6, audio: null, audioOffset: 0.5, reveal: [0.5, 2, 3.5]},
  ],
  cues: [{start: 9.5, end: 12, text: 'Таблица без нормализации страдает от трёх аномалий.'}],
  totalFrames: 19 * 30,
};
