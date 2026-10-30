import {interpolate, spring} from 'remotion';

export const fadeUp = (frame: number, fps: number, at = 0, dist = 24) => {
  const p = spring({frame: frame - at, fps, config: {damping: 200}, durationInFrames: 14});
  return {opacity: p, transform: `translateY(${interpolate(p, [0, 1], [dist, 0])}px)`};
};

export const fadeIn = (frame: number, at = 0, len = 10) =>
  interpolate(frame, [at, at + len], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
