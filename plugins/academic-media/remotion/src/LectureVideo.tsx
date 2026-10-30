import React from 'react';
import {AbsoluteFill, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import './fonts';
import {Captions} from './parts/Captions';
import {Intro, Outro} from './parts/Cards';
import {Progress} from './parts/Progress';
import {SlideView} from './parts/SlideView';
import {C, FONT} from './theme';
import type {LectureProps} from './types';

export const LectureVideo: React.FC<LectureProps> = ({meta, intro, outro, slides, cues, totalFrames}) => {
  const {fps} = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);
  const outroFrom = Math.max(0, totalFrames - f(outro));
  return (
    <AbsoluteFill style={{background: C.bg, color: C.ink, fontFamily: FONT}}>
      <Sequence durationInFrames={f(intro)} name="Заставка">
        <Intro meta={meta} />
      </Sequence>
      {slides.map((s) => {
        const from = f(s.start);
        return (
          <Sequence key={s.n} from={from} durationInFrames={Math.max(1, f(s.start + s.duration) - from)} name={`Слайд ${s.n}`}>
            <SlideView slide={s} meta={meta} />
            {s.audio ? (
              <Sequence from={f(s.audioOffset)} layout="none">
                <Audio src={staticFile(s.audio)} />
              </Sequence>
            ) : null}
          </Sequence>
        );
      })}
      <Sequence from={outroFrom} name="Концовка">
        <Outro meta={meta} />
      </Sequence>
      <Captions cues={cues} />
      <Progress from={f(intro)} to={outroFrom} accent={meta.accent} />
    </AbsoluteFill>
  );
};
