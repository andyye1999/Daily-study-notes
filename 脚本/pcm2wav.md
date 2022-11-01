```shell
#!/bin/bash 
for noisy_wav_filepath in ./*.pcm; do  
    filename=$(basename "$noisy_wav_filepath")
    pcmname="${filename%.*}"
    wavename="${pcmname}.wav"
    b=${noisy_wav_filepath##*/}
    #noisy_wav_filepath="./${fileid}.wav"
    sox -t raw -c 1 -e signed-integer -b 16 -r 8000 ${filename} ${wavename}
    echo "genereated ${wavename}"
done
```
