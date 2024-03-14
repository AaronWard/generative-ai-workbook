from melo.api import TTS

# import unidic
# print(unidic.DICDIR)
# import unidic_lite
# unidic_lite.download()


# import MeCab

# # Specify the paths directly
# dic_path = "/Users/award40/anaconda3/envs/melotts/lib/python3.9/site-packages/unidic_lite/dicdir"
# mecabrc_path = "/Users/award40/anaconda3/envs/melotts/lib/python3.9/site-packages/unidic_lite/dicdir/mecabrc"

# # Initialize MeCab with specified dictionary and mecabrc paths
# tagger = MeCab.Tagger(f"-d {dic_path} -r {mecabrc_path}")

# Speed is adjustable
speed = 1.0

# CPU is sufficient for real-time inference.
# You can set it manually to 'cpu' or 'cuda' or 'cuda:0' or 'mps'
# device = 'auto' # Will automatically use GPU if available
device = 'mps' # Will automatically use GPU if available

# English 
text = "This is an example of AI voice generation, cool huh?"
model = TTS(language='EN', device=device)
speaker_ids = model.hps.data.spk2id

# American accent
output_path = '_output/en-us.wav'
model.tts_to_file(text, speaker_ids['EN-US'], output_path, speed=speed)

# British accent
output_path = '_output/en-br.wav'
model.tts_to_file(text, speaker_ids['EN-BR'], output_path, speed=speed)

# Indian accent
output_path = '_output/en-india.wav'
model.tts_to_file(text, speaker_ids['EN_INDIA'], output_path, speed=speed)

# Australian accent
output_path = '_output/en-au.wav'
model.tts_to_file(text, speaker_ids['EN-AU'], output_path, speed=speed)

# Default accent
output_path = '_output/en-default.wav'
model.tts_to_file(text, speaker_ids['EN-Default'], output_path, speed=speed)

