# [多媒体文件格式（五）：PCM / WAV 格式](https://www.cnblogs.com/renhui/p/12148330.html)  
### 位深度  
位深度决定动态范围。采样声波时，为每个采样指定最接近原始声波振幅的振幅值。较高的位深度可提供更多可能的振幅值，产生更大的动态范围、更低的噪声基准和更高的保真度。

![](https://img2018.cnblogs.com/blog/682616/202001/682616-20200104124916045-1853047547.png)

位深度越高，提供的动态范围越大。
采样位深，音频的位深度决定动态范围。我们常见的16Bit（16比特），可以记录大概96分贝的动态范围。那么，您可以大概知道，**每一个比特大约可以记录6分贝的声音** 同理，20Bit可记录的动态范围大概就是120dB；24Bit就大概是144dB。音频位速，也叫码率，或者比特率。位速是指在一个数据流中每秒钟能通过的信息量，也可以理解为：每秒钟用多少比特的数据量去表示。96kbps的WMA音频格式的音质明显要比96kbps的MP3音质好。为什么会这样呢？因为不同的压缩算法，对数据的利用率不同而造成的差异。再举例，假如MP3压缩至48kbps以下，已经惨不忍睹，而如果是AAC音频格式，同样是48kbps的位速下，音质明显比MP3好。  
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


```cpp
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
WAV 符合 RIFF(Resource Interchange File Format) 规范，所有的WAV都由 **44字节 头文件** 和 **PCM文件** 组成，这个文件头包含语音信号的所有参数信息(声道数、采样率、量化位数、比特率....)

　　 44个字节的 头文件由 3个区块组成：

-   **RIFF chunk**：WAV文件标识
-   **Format chunk**： 声道数、采样率、量化位数、等信息
-   **Data chunk**：存放数据

　　相反的，在PCM文件头部添加44个字节的WAV文件头，就可以生成WAV格式文件

这里是一个 WAVE 文件的开头72 字节，字节显示为十六进制数字：

52 49 46 46 | 24 08 00 00 | 57 41 56 45
66 6d 74 20 | 10 00 00 00 | 01 00 02 00 
22 56 00 00 | 88 58 01 00 | 04 00 10 00
64 61 74 61 | 00 08 00 00 | 00 00 00 00 
24 17 1E F3 | 3C 13 3C 14 | 16 F9 18 F9
34 E7 23 A6 | 3C F2 24 F2 | 11 CE 1A 0D

字段解析如下图：

![](https://img2018.cnblogs.com/blog/682616/202001/682616-20200104131832991-1533022058.png)

代码如下：
```cpp
/* Created on 2016-08-15
 * Author: Zhang Binbin
 */

#ifndef WAV_H_
#define WAV_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

struct WavHeader {
    char riff[4]; // "riff"
    unsigned int size;  
    char wav[4];  // "WAVE"
    char fmt[4];  // "fmt "
    unsigned int fmt_size; // 
    unsigned short format; // 
    unsigned short channels; 
    unsigned int sample_rate; 
    unsigned int bytes_per_second; // 
    unsigned short block_size; 
    unsigned short bit;  // 
    char data[4]; // "data"
    unsigned int data_size; //
};

class WavReader {
public:
    WavReader(const char *filename) {
        FILE *fp = fopen(filename, "rb");
        if (NULL == fp) {
            perror(filename);
            exit(1);
        }
        
        WavHeader header;
        fread(&header, 1, sizeof(header), fp);
        if (header.fmt_size < 16) {
            printf("WaveData: expect PCM format data to have fmt chunk of at least size 16.\n");
            exit(1);
        }
        else if (header.fmt_size > 16) {
            int offset = 44 - 8 + header.fmt_size - 16;
            fseek(fp, offset, SEEK_SET);
            fread(header.data, 8, sizeof(char), fp);
        }
        // check "riff" "WAVE" "fmt " "data"
        // only support one sub data chunk
        num_channel_ = header.channels;
        sample_rate_ = header.sample_rate;
        bits_per_sample_ = header.bit;
        int num_data = header.data_size / (bits_per_sample_ / 8);
        data_ = new float[num_data];
        num_sample_ = num_data / num_channel_;
       
        for (int i = 0; i < num_data; i++) {
            switch (bits_per_sample_) {
                case 8: {
                    char sample;
                    fread(&sample, 1, sizeof(char), fp);
                    data_[i] = (float)sample;
                    break;
                }
                case 16: {
                    short sample;
                    fread(&sample, 1, sizeof(short), fp);
                    data_[i] = (float)sample;
                    break;
                }
                case 32: {
                    int sample;
                    fread(&sample, 1, sizeof(int), fp);
                    data_[i] = (float)sample;
                    break;
                }
                default:
                    fprintf(stderr, "unsupported quantization bits");
                    exit(1);
            }
        }
        fclose(fp);
    }

    int NumChannel() const { return num_channel_; }
    int SampleRate() const { return sample_rate_; }
    int BitsPerSample() const { return bits_per_sample_; }
    int NumSample() const { return num_sample_; }

    ~WavReader() {
        if (data_ != NULL) delete data_;
    }

    const float *Data() const { return data_; }

private:
    int num_channel_;
    int sample_rate_;
    int bits_per_sample_;
    int num_sample_; // sample points per channel
    float *data_;
};

class WavWriter {
public:
    WavWriter(const float *data, int num_sample, 
              int num_channel, int sample_rate, 
              int bits_per_sample):
        data_(data), num_sample_(num_sample), 
        num_channel_(num_channel),
        sample_rate_(sample_rate),
        bits_per_sample_(bits_per_sample) {}

    void Write(const char *filename) {
        FILE *fp = fopen(filename, "wb");
        // init char 'riff' 'WAVE' 'fmt ' 'data'
        WavHeader header;
        char wav_header[44] = {
            0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00,
            0x57, 0x41, 0x56, 0x45, 0x66, 0x6d, 0x74, 0x20,
            0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x64, 0x61, 0x74, 0x61,
            0x00, 0x00, 0x00, 0x00
        };
        memcpy(&header, wav_header, sizeof(header));
        header.channels = num_channel_;
        header.bit = bits_per_sample_;
        header.sample_rate = sample_rate_;
        header.data_size = num_sample_ * num_channel_ * (bits_per_sample_ / 8);
        header.size = sizeof(header) - 8 + header.data_size;
        header.bytes_per_second = sample_rate_ * num_channel_ * 
            (bits_per_sample_ / 8);
        header.block_size = num_channel_ * (bits_per_sample_ / 8);

        fwrite(&header, 1, sizeof(header), fp);

        for (int i = 0; i < num_sample_; i++) {
            for (int j = 0; j < num_channel_; j++) {
                switch (bits_per_sample_) {
                    case 8: {
                        char sample = (char)data_[i * num_channel_ + j];
                        fwrite(&sample, 1, sizeof(sample), fp);
                        break;
                    }
                    case 16: {
                        short sample = (short)data_[i * num_channel_ + j];
                        fwrite(&sample, 1, sizeof(sample), fp);
                        break;
                    }
                    case 32: {
                        int sample = (int)data_[i * num_channel_ + j];
                        fwrite(&sample, 1, sizeof(sample), fp);
                        break;
                    }
                }
            }
        }
        fclose(fp);
    }
private:
    const float *data_;
    int num_sample_; // total float points in data_
    int num_channel_;
    int sample_rate_;
    int bits_per_sample_;
};

#endif

```

```cpp
/* Created on 2016-08-15
 * Author: Zhang Binbin
 */

#include "wav.h"


int main(int argc, char *argv[]) {

    const char *usage = "Test wav reader and writer\n"
                        "Usage: wav-test wav_in_file wav_output_file\n";
    if (argc != 3) {
        printf(usage);
        exit(-1);
    }

    WavReader reader(argv[1]);

    WavWriter writer(reader.Data(), reader.NumSample(), reader.NumChannel(),
                     reader.SampleRate(), reader.BitsPerSample());
    writer.Write(argv[2]);
    return 0;
}
```