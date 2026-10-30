import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeIn, fadeUp} from './anim';
import {CAPTION_ZONE, C, PAD_X, tint} from '../theme';
import type {Meta, SlideData} from '../types';

const SUB = /^[–-]\s+/;

const headSize = (s: string) => (s.length > 60 ? 48 : s.length > 40 ? 54 : 60);

const bulletSize = (items: string[]) => {
  const chars = items.reduce((n, b) => n + b.length, 0);
  if (items.length <= 4 && chars < 200) return 50;
  if (chars < 320) return 40;
  if (chars < 460) return 35;
  return 31;
};

const tableSize = (rows: number, cols: number) => (rows <= 4 && cols <= 3 ? 34 : rows <= 7 ? 29 : 25);

const Header: React.FC<{slide: SlideData; meta: Meta}> = ({slide, meta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 10, background: meta.accent}} />
      <div style={{position: 'absolute', right: PAD_X, top: 58, fontSize: 26, color: C.muted, opacity: fadeIn(frame)}}>
        {slide.n} / {meta.slideCount}
      </div>
      <div style={{position: 'absolute', left: PAD_X, right: PAD_X + 140, top: 80, ...fadeUp(frame, fps, 0, 16)}}>
        <div style={{fontSize: headSize(slide.title), fontWeight: 700, lineHeight: 1.15}}>{slide.title}</div>
        <div style={{width: 110, height: 6, background: meta.accent, marginTop: 26}} />
      </div>
    </>
  );
};

const Body: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{position: 'absolute', left: PAD_X, right: PAD_X, top: 290, bottom: CAPTION_ZONE, display: 'flex', flexDirection: 'column', justifyContent: 'flex-start'}}>
    {children}
  </div>
);

const Bullets: React.FC<{slide: SlideData; meta: Meta}> = ({slide, meta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const size = bulletSize(slide.bullets);
  return (
    <Body>
      {slide.bullets.map((b, i) => {
        const at = Math.round((slide.reveal[i] ?? 0.3 + i * 0.8) * fps);
        // «– текст» — подпункт: отступ, мельче, маркер-кружок.
        const sub = SUB.test(b);
        const fs = sub ? Math.round(size * 0.86) : size;
        return (
          <div key={i} style={{display: 'flex', alignItems: 'flex-start', marginLeft: sub ? size * 1.1 : 0, marginBottom: fs * 0.55, ...fadeUp(frame, fps, at, 20)}}>
            <div style={{flex: '0 0 auto', width: fs * 0.3, height: fs * 0.3, background: sub ? C.muted : meta.accent, marginTop: fs * 0.46, marginRight: fs * 0.6, borderRadius: sub ? '50%' : 3}} />
            <div style={{fontSize: fs, lineHeight: 1.32, color: sub ? C.muted : C.ink}}>{b.replace(SUB, '')}</div>
          </div>
        );
      })}
      {slide.type === 'closing' && slide.subtitle ? (
        <div style={{fontSize: 34, color: C.muted, marginTop: 'auto', opacity: fadeIn(frame, 10)}}>{slide.subtitle}</div>
      ) : null}
    </Body>
  );
};

const TableView: React.FC<{slide: SlideData; meta: Meta}> = ({slide, meta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const table = slide.table!;
  const cols = Math.max(table.header.length, ...table.rows.map((r) => r.length));
  const size = tableSize(table.rows.length, cols);
  const cell: React.CSSProperties = {padding: `${size * 0.45}px ${size * 0.7}px`, textAlign: 'left', verticalAlign: 'top', lineHeight: 1.28};
  return (
    <Body>
      <table style={{width: '100%', borderCollapse: 'collapse', fontSize: size, ...fadeUp(frame, fps, 0, 12)}}>
        {table.header.length ? (
          <thead>
            <tr style={{background: meta.accent, color: '#FFFFFF'}}>
              {table.header.map((h, i) => <th key={i} style={{...cell, fontWeight: 600}}>{h}</th>)}
            </tr>
          </thead>
        ) : null}
        <tbody>
          {table.rows.map((r, i) => {
            const at = Math.round((slide.reveal[i] ?? 0.4 + i * 0.4) * fps);
            return (
              <tr key={i}>
                {Array.from({length: cols}, (_, j) => (
                  <td key={j} style={{...cell, fontWeight: j === 0 ? 600 : 400, background: i % 2 ? C.panel : C.bg, borderBottom: `1px solid ${C.line}`, opacity: fadeIn(frame, at, 10)}}>
                    {r[j] ?? ''}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </Body>
  );
};

const TitleSlide: React.FC<{slide: SlideData; meta: Meta}> = ({slide, meta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 28, background: meta.accent}} />
      <div style={{position: 'absolute', left: PAD_X + 20, right: PAD_X, top: 0, bottom: CAPTION_ZONE, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
        {meta.course ? <div style={{...fadeUp(frame, fps, 0), fontSize: 30, letterSpacing: 3, textTransform: 'uppercase', color: C.muted, fontWeight: 600}}>{meta.course}</div> : null}
        <div style={{...fadeUp(frame, fps, 5), fontSize: slide.title.length > 60 ? 68 : 84, fontWeight: 700, lineHeight: 1.12, marginTop: 24, maxWidth: 1500}}>{slide.title}</div>
        <div style={{width: 140, height: 8, background: meta.accent, marginTop: 36, opacity: fadeIn(frame, 10)}} />
        {slide.subtitle ? <div style={{...fadeUp(frame, fps, 12), fontSize: 42, color: C.muted, marginTop: 32}}>{slide.subtitle}</div> : null}
        {meta.teacher ? <div style={{...fadeUp(frame, fps, 16), fontSize: 34, marginTop: 56}}>{meta.teacher}</div> : null}
      </div>
    </AbsoluteFill>
  );
};

const SectionSlide: React.FC<{slide: SlideData; meta: Meta}> = ({slide, meta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: tint(meta.accent, 0.06)}}>
      <div style={{position: 'absolute', left: PAD_X, right: PAD_X, top: 0, bottom: CAPTION_ZONE, display: 'flex', alignItems: 'center'}}>
        <div style={{width: 12, alignSelf: 'stretch', margin: '300px 56px 300px 0', background: meta.accent, opacity: fadeIn(frame)}} />
        <div>
          <div style={{...fadeUp(frame, fps, 0), fontSize: 30, letterSpacing: 3, textTransform: 'uppercase', color: meta.accent, fontWeight: 600}}>{meta.sectionLabel}</div>
          <div style={{...fadeUp(frame, fps, 5), fontSize: slide.title.length > 50 ? 68 : 84, fontWeight: 700, lineHeight: 1.12, marginTop: 20, maxWidth: 1450}}>{slide.title}</div>
          {slide.subtitle ? <div style={{...fadeUp(frame, fps, 10), fontSize: 40, color: C.muted, marginTop: 28}}>{slide.subtitle}</div> : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const ClosingSlide: React.FC<{slide: SlideData; meta: Meta}> = ({slide, meta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: PAD_X, right: PAD_X, top: 0, bottom: CAPTION_ZONE, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
        <div style={{...fadeUp(frame, fps, 0), fontSize: slide.title.length > 40 ? 72 : 96, fontWeight: 700, color: meta.accent, lineHeight: 1.12}}>{slide.title}</div>
        <div style={{width: 120, height: 8, background: meta.accent, margin: '40px 0', opacity: fadeIn(frame, 8)}} />
        {slide.subtitle ? <div style={{...fadeUp(frame, fps, 10), fontSize: 42, color: C.ink, maxWidth: 1400, lineHeight: 1.3}}>{slide.subtitle}</div> : null}
      </div>
    </AbsoluteFill>
  );
};

export const SlideView: React.FC<{slide: SlideData; meta: Meta}> = ({slide, meta}) => {
  switch (slide.type) {
    case 'title':
      return <TitleSlide slide={slide} meta={meta} />;
    case 'section':
      return <SectionSlide slide={slide} meta={meta} />;
    case 'closing':
      if (!slide.bullets.length) return <ClosingSlide slide={slide} meta={meta} />;
    // вопросы для обсуждения — как обычный слайд с пунктами
    // eslint-disable-next-line no-fallthrough
    default:
      return (
        <AbsoluteFill>
          <Header slide={slide} meta={meta} />
          {slide.type === 'table' && slide.table ? <TableView slide={slide} meta={meta} /> : <Bullets slide={slide} meta={meta} />}
        </AbsoluteFill>
      );
  }
};
