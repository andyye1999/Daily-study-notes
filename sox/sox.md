``` shell
sox $wav_path -t raw -r 16k -b 16 -e signed-integer $raw_pcm_path remix $c  
```

```shell
sox -t raw -c 3 -r 16k -b 16 -e signed-integer $wav_path -t raw -r 16k -b 16 -e signed-integer $raw_pcm_path remix $c
```

```shell
cat run.sh | while read line; do
  echo $line
done | xargs -P 20 -i sh -c {}
``` 