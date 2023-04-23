

因果卷积
```python
class CausalConv1d(nn.Conv1d):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.causal_padding = self.dilation[0] * (self.kernel_size[0] - 1)

    def forward(self, x):
        return self._conv_forward(F.pad(x, [self.causal_padding, 0]), self.weight, self.bias)


class CausalConvTranspose1d(nn.ConvTranspose1d):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.causal_padding = self.dilation[0] * (self.kernel_size[0] - 1) + self.output_padding[0] + 1 - self.stride[0]

    def forward(self, x, output_size=None):
        if self.padding_mode != 'zeros':
            raise ValueError('Only `zeros` padding mode is supported for ConvTranspose1d')

        assert isinstance(self.padding, tuple)
        output_padding = self._output_padding(
            x, output_size, self.stride, self.padding, self.kernel_size, self.dilation)
        return F.conv_transpose1d(
            x, self.weight, self.bias, self.stride, self.padding,
            output_padding, self.groups, self.dilation)[..., :-self.causal_padding]

```

padding 在前面  dilation跨步

# soundstream encodec的区别

在我们看来，SoundStream和Encodec之间的主要区别在于不同的鉴别器选择。对于Encodec，它只使用STFT-dicriminator，这迫使STFT-spectrogram更加真实。SoundStream使用两种类型的鉴别器，一种强制波形级别更加真实，另一种强制specrogram级别更加真实。在我们的代码中，我们采用了HIFI-GAN中的波形级别判别器和Encodec中的spectrogram级别判别器。理论上，我们认为SoundStream具有更好的性能。事实上，Google官方声音流证明了这一点, Google只需要3个码本就可以重构高质量音频. 尽管我们也可以使用3个码本来实现良好性能, 但是我们承认目前无法与Google进行比较。

对于AcademiCodec（即我们提出的新方法），旨在帮助某些生成任务。例如VALL-E、AudioLM、MusicLM、SpearTTS、IntructTTS等等。学术码本仅需要4个码本，并显着减少标记数量。一些研究人员使用了我们提出的AcademiCodec来实现VALL-E，并证明其可以获得更好的音频质量。



# 音频编码解码器(Audio Codec)

上述几个模型利用离散化的语音表征，作为模型预训练过程的一部分，虽然没有直接将这些离散化的表征作为最终的特征， 但利用这些表征增加了预训练的效率和稳定性。

那么，这些表征能否直接用于TTS呢？个人认为是不能的：

1. 上述模型只做了基于上下文预测的预训练任务，因此，表征中主要是与上下文相关的语义信息；

2. 相应地，这些表征中缺乏足够支持将特征还原为原始语音信号的声学信息。

接下来，我们将介绍另一种离散化的音频表征，这些表征来自**音频编码解码器(Audio Codec)**：

1. Audio Codec的基本任务是将一段音频压缩为向量或其他表征，并且根据这些表征可以还原音频——该任务本身类似Auto Encoder, 但有两个重点，一是需要尽可能节约中间表征的比特数，达到低资源应用的目的，二是需要尽可能忠实地还原出原本的音频；

2. 当前主流方法：

1) 同样利用离散化的codebook获得离散tokens，离散tokens对应的中间表征作为压缩后的表征；

2) 对于每个离散token，可以用一个整数(或one-hot向量，等价)表示，此时对于N大小的codebook，只需要logN的比特数即可记录，压缩效率较高。

## SoundStream

![](https://pic2.zhimg.com/80/v2-d0045fe3ec9bf633eb8242719c13f281_720w.webp)

SoundStream是目前性能较好的主流Audio Codec之一，其结构分为Encoder、Vector Quantizer、Decoder三部分：

1. Encoder / Decoder使用常规的卷积层和反卷积层，不详细介绍；

2. Vector Quantizer是该模型重点，作者提出了一种Residual Vector Quantitation, 性能提升较大：

### RVQ

1) 先考虑传统的Vector Quantitation：

a) 假设一段音频可以被压缩为S个中间编码，codebook中有N个向量，则音频可以表示为S * N个one-hot向量，消耗比特数为S * log N ;

b) 假设音频采样率24k, 每个中间表征编码320帧，则每秒有S = 24000 / 320 = 75个中间编码；

c) 假设编码后的比特率为6kbps, 对于75个中间编码，每个编码可用6000 / 75 = 80 bits;

d) 参照上面的公式，若充分利用比特率，需要N = 2^80大小的codebook，不可接受，而更小的codebook在高比特率场景又会损失性能。

2) 此时需要考虑多个codebook的设置，但多个codebook如何编码、如何高效利用资源也是一个问题

3) 为此，作者提出Residual Vector Quantitation (RVQ)：

a) 为平衡codebook大小和比特利用率，本文提出使用多个quantitation block对应多个codebook，它们之间有残差连接，重要性不同；若使用8个codebook，则每个codebook可利用10 bits, 大小为2^8=1024, 可接受；

b) 具体地，每个Block在量化时，其量化与真实表征之间的差值会传给下一个block，相当于每个block只会量化前一个block的误差；

c) 这样做的好处，一方面区分出不同block的分工和重要性，第一个block中蕴含最重要的信息（偏语义），后续block则负责精确还原语音时的细节信息；另一方面，在训练时我们可以随机sample前k个block进行训练，保证在丢弃后若干个不重要的block时，模型仍然能保持一定精度，此时模型可以在低比特率时选择性地丢弃后面的blocks，实现了对比特率的动态适应。

![](https://pic3.zhimg.com/80/v2-fcc88c6707e4586aed023415150c909e_720w.webp)

3. 除此之外，作者还引入了对抗学习，让辨别器判断还原语音与原本语音之间的区别，这里存在一个perception-distortion trade-off，即感知度和保真度的取舍：保真度越高的还原，越可能因为信息丢失而显得过度锐化，从而听起来与原始音频不同；反过来，听感相似的音频，其还原的客观相似度可能并不高。

4. 为了同时保证感知度和保真度，作者使用对抗学习loss和Mels/特征重建loss，前者用于保证听感相似，后者则用于保证客观指标相似。

## Encodec

![](https://pic3.zhimg.com/80/v2-451a05ea0bdf3a3ffc0cadc8fb51fae6_720w.webp)

一笔带过，框架很类似SoundStream，加入了之前忽略的Waveform重建loss;

值得注意的是，作者为了提高语音解码的实时性，引入了一个小的语言模型，该语言模型根据t时刻的RVQ向量，预测t+1时刻的RVQ向量，用于提前解码下一刻的语音；实验证明该模块在性能没有明显降低的情况下，提高了解码的速度，这意味着RVQ向量中也编码了一定的语音语义信息（实际上我没有看到作者对于该模块性能的实验分析，可能我或作者有所遗漏）


AAC