

## Installation

```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

bash ./models/download-ggml-model.sh base.en
Downloading ggml model base.en from 'https://huggingface.co/ggerganov/whisper.cpp' ...
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1210  100  1210    0     0   5535      0 --:--:-- --:--:-- --:--:--  5525
100  141M  100  141M    0     0  7525k      0  0:00:19  0:00:19 --:--:-- 7922k
Done! Model 'base.en' saved in '/Users/award40/Desktop/personal/github/generative-ai-workbook/learning/whisper/whisper.cpp/models/ggml-base.en.bin'
You can now use it like this:

$ ./main -m /Users/award40/Desktop/personal/github/generative-ai-workbook/learning/whisper/whisper.cpp/models/ggml-base.en.bin -f samples/jfk.wav

```


## Fix kHz issue: 

```bash
ffmpeg -i /Users/award40/Desktop/personal/github/generative-ai-workbook/learning/whisper/figure.wav -ar 16000 -ac 1 -c:a pcm_s16le /Users/award40/Desktop/personal/github/generative-ai-workbook/learning/whisper/figure_fixed.wav
```

## Running the model
```bash
./main -m models/ggml-base.en.bin -f /Users/award40/Desktop/personal/github/generative-ai-workbook/learning/whisper/figure_fixed.wav
```


```md
[00:00:00.000 --> 00:00:10.000]   [music]
[00:00:10.000 --> 00:00:12.000]   Hey figure one, what do you see right now?
[00:00:12.000 --> 00:00:22.000]   I see a red apple on a plate in the center of the table, a drying rack with cups and a plate
[00:00:22.000 --> 00:00:25.000]   and you standing nearby with your hand on the table.
[00:00:25.000 --> 00:00:27.000]   Great, can I have something to eat?
[00:00:27.000 --> 00:00:31.000]   [music]
[00:00:31.000 --> 00:00:33.000]   Sure thing.
[00:00:33.000 --> 00:00:39.000]   [music]
[00:00:39.000 --> 00:00:45.000]   Great, can you explain why you did what you just did while you pick up this trash?
[00:00:45.000 --> 00:00:49.000]   [music]
[00:00:49.000 --> 00:00:56.000]   On it, so I gave you the apple because it's the only edible item I could provide you with from the table.
[00:00:56.000 --> 00:01:02.000]   [music]
[00:01:02.000 --> 00:01:08.000]   Great, so based on the scene right now, where do you think the dish is in front of you go next?
[00:01:08.000 --> 00:01:13.000]   [music]
[00:01:13.000 --> 00:01:19.000]   The dishes on the table like that plate and cup are likely to go into the drying rack next.
[00:01:19.000 --> 00:01:21.000]   Great, can you put them there?
[00:01:21.000 --> 00:01:25.000]   [music]
[00:01:25.000 --> 00:01:27.000]   Of course.
[00:01:27.000 --> 00:01:37.000]   [music]
[00:01:37.000 --> 00:01:42.000]   [music]
[00:01:42.000 --> 00:01:45.000]   All right, so how do you think you did?
[00:01:45.000 --> 00:01:48.000]   [music]
[00:01:48.000 --> 00:01:53.000]   I think I did pretty well. The apple found its new owner, the trash is gone,
[00:01:53.000 --> 00:01:57.000]   and the tableware is right where it belongs.
[00:01:57.000 --> 00:01:59.000]   I agree. Thanks, figure one.
[00:01:59.000 --> 00:02:01.000]   [music]
[00:02:01.000 --> 00:02:05.000]   You're welcome. If there's anything else you need help with, just let me know.
[00:02:05.000 --> 00:02:32.000]   [music]
[00:02:32.000 --> 00:02:42.000]   [BLANK_AUDIO]
```