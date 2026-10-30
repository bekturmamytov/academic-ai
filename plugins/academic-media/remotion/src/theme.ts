export const W = 1920;
export const H = 1080;
export const FPS = 30;

export const FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif";
export const C = {
  bg: '#FFFFFF',
  ink: '#1B1F24',
  muted: '#5B6573',
  line: '#D9DEE5',
  panel: '#F4F6F9',
};
export const PAD_X = 140;
// Нижняя полоса под титры: контент слайда в неё не заходит.
export const CAPTION_ZONE = 210;

export const tint = (hex: string, alpha: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
};
