import {Config} from '@remotion/cli/config';

// H.264 + yuv420p открываются везде: Moodle, YouTube, PowerPoint, телефоны.
Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(20);
