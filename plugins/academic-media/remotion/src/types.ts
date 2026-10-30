export type SlideType = 'title' | 'section' | 'bullets' | 'table' | 'closing';

export type Table = {header: string[]; rows: string[][]};

// Время — секунды от начала ролика; reveal и audioOffset — от начала слайда.
export type SlideData = {
  n: number;
  type: SlideType;
  title: string;
  subtitle: string;
  bullets: string[];
  table: Table | null;
  start: number;
  duration: number;
  audio: string | null;
  audioOffset: number;
  reveal: number[];
};

export type Cue = {start: number; end: number; text: string};

export type Meta = {
  title: string;
  course: string;
  teacher: string;
  accent: string;
  lang: string;
  partLabel: string;
  topic: string;
  sectionLabel: string;
  endLabel: string;
  slideCount: number;
};

export type LectureProps = {
  meta: Meta;
  intro: number;
  outro: number;
  slides: SlideData[];
  cues: Cue[];
  totalFrames: number;
};
