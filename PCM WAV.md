# [多媒体文件格式（五）：PCM / WAV 格式](https://www.cnblogs.com/renhui/p/12148330.html)  
### 位深度  
位深度决定动态范围。采样声波时，为每个采样指定最接近原始声波振幅的振幅值。较高的位深度可提供更多可能的振幅值，产生更大的动态范围、更低的噪声基准和更高的保真度。

![](https://img2018.cnblogs.com/blog/682616/202001/682616-20200104124916045-1853047547.png)

位深度越高，提供的动态范围越大。
采样位深，音频的位深度决定动态范围。我们常见的16Bit（16比特），可以记录大概96分贝的动态范围。那么，您可以大概知道，** 每一个比特大约可以记录6分贝的声音。** 同理，20Bit可记录的动态范围大概就是120dB；24Bit就大概是144dB。音频位速，也叫码率，或者比特率。位速是指在一个数据流中每秒钟能通过的信息量，也可以理解为：每秒钟用多少比特的数据量去表示。96kbps的WMA音频格式的音质明显要比96kbps的MP3音质好。为什么会这样呢？因为不同的压缩算法，对数据的利用率不同而造成的差异。再举例，假如MP3压缩至48kbps以下，已经惨不忍睹，而如果是AAC音频格式，同样是48kbps的位速下，音质明显比MP3好。  
### PCM音频数据存储方式

如果是单声道的文件，采样数据按时间的先后顺序依次存入。如果是单声道的音频文件，采样数据按时间的先后顺序依次存入（也可能采用 LRLRLR 方式存储，只是另一个声道的数据为 0）。

如果是双声道的话通常按照 LRLRLR 的方式存储，存储的时候还和机器的大小端有关。（关于字节序大小端的相关内容可参考《[字节序问题之大小端模式讲解](https://www.cnblogs.com/renhui/p/13600572.html)》进行了解）

PCM的存储方式为小端模式，存储Data数据排列如下图所示：

![](https://img2018.cnblogs.com/blog/682616/202001/682616-20200104112313716-290297915.png)  
##  WAV

WAV 是 Microsoft 和 IBM 为 PC 开发的一种声音文件格式，它符合 RIFF（Resource Interchange File Format）文件规范，用于保存 Windows 平台的音频信息资源，被 Windows 平台及其应用程序所广泛支持。WAVE 文件通常只是一个具有单个 “WAVE” 块的 RIFF 文件，该块由两个子块（”fmt” 子数据块和 ”data” 子数据块），它的格式如下图所示：

![](https://img2018.cnblogs.com/blog/682616/202001/682616-20200104131622902-1855086338.png)  
**WAV 格式定义**

该格式的实质就是在 PCM 文件的前面加了一个文件头，每个字段的的含义如下：


```
typedef struct {
    char          ChunkID[4]; //内容为"RIFF"
    unsigned long ChunkSize;  //存储文件的字节数（不包含ChunkID和ChunkSize这8个字节）
    char          Format[4];  //内容为"WAVE“
} WAVE_HEADER;
 
typedef struct {
   char           Subchunk1ID[4]; //内容为"fmt"
   unsigned long  Subchunk1Size;  //存储该子块的字节数（不含前面的Subchunk1ID和Subchunk1Size这8个字节）
   unsigned short AudioFormat;    //存储音频文件的编码格式，例如若为PCM则其存储值为1。
   unsigned short NumChannels;    //声道数，单声道(Mono)值为1，双声道(Stereo)值为2，等等
   unsigned long  SampleRate;     //采样率，如8k，44.1k等
   unsigned long  ByteRate;       //每秒存储的bit数，其值 = SampleRate * NumChannels * BitsPerSample / 8
   unsigned short BlockAlign;     //块对齐大小，其值 = NumChannels * BitsPerSample / 8
   unsigned short BitsPerSample;  //每个采样点的bit数，一般为8,16,32等。
} WAVE_FMT;
 
typedef struct {
   char          Subchunk2ID[4]; //内容为“data”
   unsigned long Subchunk2Size;  //接下来的正式的数据部分的字节数，其值 = NumSamples * NumChannels * BitsPerSample / 8
} WAVE_DATA;

```

**WAV 文件头解析**

这里是一个 WAVE 文件的开头 72 字节，字节显示为十六进制数字：

52 49 46 46 | 24 08 00 00 | 57 41 56 45
66 6d 74 20 | 10 00 00 00 | 01 00 02 00 
22 56 00 00 | 88 58 01 00 | 04 00 10 00
64 61 74 61 | 00 08 00 00 | 00 00 00 00 
24 17 1E F3 | 3C 13 3C 14 | 16 F9 18 F9
34 E7 23 A6 | 3C F2 24 F2 | 11 CE 1A 0D

字段解析如下图：

![](https://img2018.cnblogs.com/blog/682616/202001/682616-20200104131832991-1533022058.png)