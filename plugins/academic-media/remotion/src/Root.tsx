import React from 'react';
import {Composition} from 'remotion';
import {LectureVideo} from './LectureVideo';
import {DEMO} from './demo';
import {FPS, H, W} from './theme';
import type {LectureProps} from './types';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="LectureVideo"
    component={LectureVideo}
    width={W}
    height={H}
    fps={FPS}
    durationInFrames={DEMO.totalFrames}
    defaultProps={DEMO}
    calculateMetadata={({props}: {props: LectureProps}) => ({durationInFrames: Math.max(1, props.totalFrames)})}
  />
);
