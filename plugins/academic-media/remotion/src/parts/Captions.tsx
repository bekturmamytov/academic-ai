import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeIn} from './anim';
import type {Cue} from '../types';

export const Captions: React.FC<{cues: Cue[]}> = ({cues}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const cue = cues.find((c) => t >= c.start && t < c.end);
  if (!cue) return null;
  const opacity = fadeIn(frame, Math.round(cue.start * fps), 4);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 56, display: 'flex', justifyContent: 'center', opacity}}>
      <div
        style={{
          maxWidth: 1480, padding: '14px 30px', borderRadius: 10, background: 'rgba(20, 24, 30, 0.84)',
          color: '#FFFFFF', fontSize: 38, lineHeight: 1.32, textAlign: 'center', fontWeight: 400,
        }}
      >
        {cue.text}
      </div>
    </div>
  );
};
