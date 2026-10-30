import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeIn, fadeUp} from './anim';
import {C, PAD_X, tint} from '../theme';
import type {Meta} from '../types';

const titleSize = (s: string) => (s.length > 70 ? 64 : s.length > 45 ? 76 : 88);

export const Intro: React.FC<{meta: Meta}> = ({meta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 28, background: meta.accent}} />
      <div style={{position: 'absolute', left: PAD_X + 20, right: PAD_X, top: 0, bottom: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
        {meta.course ? (
          <div style={{...fadeUp(frame, fps, 0), fontSize: 32, letterSpacing: 3, textTransform: 'uppercase', color: C.muted, fontWeight: 600}}>
            {meta.course}
          </div>
        ) : null}
        <div style={{...fadeUp(frame, fps, 6), fontSize: titleSize(meta.title), fontWeight: 700, lineHeight: 1.12, marginTop: 28, maxWidth: 1500}}>
          {meta.title}
        </div>
        <div style={{width: 140, height: 8, background: meta.accent, marginTop: 40, opacity: fadeIn(frame, 12)}} />
        {meta.topic ? (
          <div style={{...fadeUp(frame, fps, 14), fontSize: 40, color: meta.accent, marginTop: 36, fontWeight: 600}}>{meta.topic}</div>
        ) : null}
        {meta.partLabel ? (
          <div style={{...fadeUp(frame, fps, 18), marginTop: 28}}>
            <span style={{fontSize: 30, padding: '8px 20px', borderRadius: 8, background: tint(meta.accent, 0.1), color: meta.accent, fontWeight: 600}}>
              {meta.partLabel}
            </span>
          </div>
        ) : null}
        {meta.teacher ? (
          <div style={{...fadeUp(frame, fps, 22), fontSize: 36, color: C.ink, marginTop: 72}}>{meta.teacher}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

export const Outro: React.FC<{meta: Meta}> = ({meta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: tint(meta.accent, 0.06), alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
      <div style={{...fadeUp(frame, fps, 0), fontSize: 76, fontWeight: 700, color: meta.accent}}>{meta.endLabel}</div>
      <div style={{width: 120, height: 8, background: meta.accent, margin: '44px 0', opacity: fadeIn(frame, 8)}} />
      <div style={{...fadeUp(frame, fps, 10), fontSize: 36, color: C.ink, maxWidth: 1500}}>
        {[meta.course, meta.title].filter(Boolean).join(' · ')}
      </div>
      {meta.teacher ? <div style={{...fadeUp(frame, fps, 16), fontSize: 32, color: C.muted, marginTop: 20}}>{meta.teacher}</div> : null}
    </AbsoluteFill>
  );
};
