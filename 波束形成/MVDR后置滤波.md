# Zelinski

假设噪声与语音不相关，每个通道噪声功率谱相等，每个通道噪声不相关
Zelinski 维纳后置滤波器会存在**低频去噪能力不足，有残留噪声的问 题**

# mccowan

## 噪声场分析

常用的描述噪声场特性的方法是使用复相关函数。“复杂相干函数”是用于表征噪声场的一种常见测量方式。其中，相干函数可以用于测量两个离散点处信号之间的相关性，并在一定程度上进行归一化处理。这里所说的“复杂相干函数”在阵列处理中非常有用，既可用于算法开发（如超指向波束形成），也可用于理论噪声场下的阵列性能分析。此外，交叉谱密度是衡量两个随机过程之间互相关性的统计量，它和对称自相关函数之间的关系可以用Wiener-Khinchin定理来描述。

# MVDR后置滤波

mvdr + zelinski postfilter
mvdr + mccowan postfilter
mvdr + lefkim postfilter
mvdr + stsa postfilter 
mvdr + log-stsa postfilter

![image](https://cdn.jsdelivr.net/gh/andyye1999/image-hosting@master/20221201/image.xjharf7cw40.webp)


![image](https://cdn.jsdelivr.net/gh/andyye1999/image-hosting@master/20221201/image.3rj3rsjxzyu0.webp)

![image](https://cdn.jsdelivr.net/gh/andyye1999/image-hosting@master/20221201/image.21o574xamy5c.webp)


![image](https://cdn.jsdelivr.net/gh/andyye1999/image-hosting@master/20221201/image.3gb0b0tvq8c0.webp)

噪声相关性如果较大，会出现欠估计。如果噪声相关性较小，会出现过估计。
Zelinski将噪声场假定为非相干噪声场，但是实际场景中如办公室，商场，汽车 为散射场 
低频具有较高的相关性

## 噪声场


![image](https://cdn.jsdelivr.net/gh/andyye1999/image-hosting@master/20221201/image.4u5m30xq5li0.webp)

# Lefkin

和硕士论文里类似 改进 我写的程序中加入matlab版本中的gamma 调整了中高频的alpha 使得中高频失真没之前严重

# _least-squares_post-filtering

谷歌的一篇文章 

之前的滤波器噪声源考虑的少，噪声通常包括多种成分，如扩散噪声、白噪声和点源干扰等。其中，扩散噪声是指来自环境的均匀分布的噪声，如空气中的风声、车辆行驶时的路面摩擦声等；白噪声是指功率谱密度在所有频率上都相等的随机信号，如电子设备中的热噪声、天线接收器中的热噪声等；点源干扰是指来自单个点源（如人说话或音乐演奏）的干扰信号。

之前滤波器只考虑包含漫反射噪声（diffuse noise），而没有点源干扰（point interferer）和加性白噪声（additive white noise）。

# 结果


低信噪比下中高频比MVDR后单通道降噪效果好，但低频部分不行