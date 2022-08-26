# [基于Mask的语音分离](https://mp.weixin.qq.com/s?__biz=MzA3MjEyMjEwNA==&mid=2247484164&idx=1&sn=f0f59a10fa04f02228bbba381348e66c&chksm=9f226893a855e185aab5b0abcf6c8c11802fe0b8d97b22c89222d533cf32c6498fa8587a4e77&scene=21#wechat_redirect)
-   理想二值掩蔽（Ideal Binary Mask，IBM）中的分离任务就成为了一个二分类问题。这类方法根据听觉感知特性，把音频信号分成不同的子带，根据每个时频单元上的信噪比，把对应的时频单元的能量设为0（噪音占主导的情况下）或者保持原样（目标语音占主导的情况下）
    
-   理想比值掩蔽（Ideal Ratio Mask, IRM），它同样对每个时频单元进行计算，但不同于IBM的“非零即一”，IRM中会计算语音信号和噪音之间的能量比，得到介于0到1之间的一个数，然后据此改变时频单元的能量大小。IRM是对IBM的演进，反映了各个时频单元上对噪声的抑制程度，可以进一步提高分离后语音的质量和可懂度。
