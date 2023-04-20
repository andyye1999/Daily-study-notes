

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