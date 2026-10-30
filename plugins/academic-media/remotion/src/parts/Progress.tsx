import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';

export const Progress: React.FC<{from: number; to: number; accent: string}> = ({from, to, accent}) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  const w = interpolate(frame, [from, to], [0, 100], {extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', left: 0, bottom: 0, height: 6, width: `${w}%`, background: accent, opacity: 0.85}} />;
};
