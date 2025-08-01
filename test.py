
str1 = "111233344455"

def remove_num(s):
    result = []
    for char in s:
        if len(result) >= 2 and result[-1] == char and result[-2] == char:
            continue
        result.append(char)
    return "".join(result)

print(remove_num(str1))

import librosa
import numpy as np

audio_path=''
y,sr = librosa.load(audio_path,sr=16000)
frame_len=16000
hop_len=8000
frames = librosa.util.frame(y, frame_length=frame_len, hop_length=hop_len)
energy = np.sum(frames**2,axis=1)
print(energy.shape)