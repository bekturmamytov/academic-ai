import '@fontsource/inter/400.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';
import {continueRender, delayRender} from 'remotion';

// Шрифт лежит в node_modules (без сети); ждём все начертания с кириллицей и ң ө ү.
const SAMPLE = 'AaЖжҢңӨөҮү';
const handle = delayRender('Загрузка шрифта Inter');
Promise.all(['400', '600', '700'].map((w) => document.fonts.load(`${w} 40px Inter`, SAMPLE)))
  .then(() => continueRender(handle))
  .catch(() => continueRender(handle));
