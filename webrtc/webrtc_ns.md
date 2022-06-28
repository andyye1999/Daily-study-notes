# [webrtc_ns](https://cxymm.net/article/godloveyuxu/73657931)
所以对噪声的估计准确性是至关重要的，噪声估计的越准得到的结果就越好，由此又多出来几种估计噪声的方法。

1. 基于VAD检测的噪声估计，VAD对Y进行检测，如果检测没有语音，则认为噪声，这是对噪声的一种估计方法。

2.基于全局幅度谱最小原理，该估计认为幅度谱最小的情况必然对应没有语音的时候。

3.还有基于矩阵奇异值分解原理估计噪声的。

webRTC没有采用上述的方法，而是对**似然比**（VAD检测时就用了该方法）函数进行改进，将多个语音/噪声分类特征合并到一个模型中形成一个多特征综合概率密度函数，对输入的每帧频谱进行分析。其可以有效抑制风扇/办公设备等噪声。

其抑制过程如下：

**对接收到的每一帧带噪语音信号，以对该帧的初始噪声估计为前提，定义语音概率函数，测量每一帧带噪信号的分类特征，使用测量出来的分类特征，计算每一帧基于多特征的语音概率，在对计算出的语音概率进行动态因子（信号分类特征和阈值参数）加权，根据计算出的每帧基于特征的语音概率，修改多帧中每一帧的语音概率函数，以及使用修改后每帧语音概率函数，更新每帧中的初始噪声（连续多帧中每一帧的分位数噪声）估计。**

基于特征的语音概率函数通过使用映射函数（sigmoid/tanh又称S函数，在神经元分类算法中常用为种子函数）将每帧的信号分类特征映射到一个概率值而得出的。

分类特征包括：随时间变化的平局似然比，频谱平坦度测量以及频谱模板差异测量。频谱模板差异测量以输入信号频谱与模板噪声频谱的对比为基础。

  

信号分析：包括缓冲、加窗和离散傅立叶变换(DFT) 的预处理步骤

噪声估计和过滤包括：初始噪声估计、后验和先验SNR的判决引导(DD)更新、语音/噪声可能性测定，可能性测定是基于似然比(LR)因子进行的，而似然比是使用后验和先验SNR，以及语音概率密度函数(HF)模型 (如高斯、拉普拉斯算子、伽马、超高斯等)，还有根据特征建模、噪声估计更新并应用维纳增益滤波器确定的概率而确定的。

信号合成：离散傅立叶逆变换、缩放和窗口合成。

  

初始噪声估计是以分位数噪声估计为基础。噪声估计受分位数参数控制，该参数以q表示。根据初始噪声估计步骤确定的噪声估计，仅能用作促进噪声更新/估计的后续流程的初始条件。

# [Webrtc NS模块算法](https://www.likecs.com/show-203316256.html "Webrtc NS模块算法")  
算法的主要函数调用关系如下：
```cpp
1、初始化模块
//设置特征提取参数
set_feature_extraction_parameters()
//特征参数提取
FeatureParameterExtraction()
//初始化状态
WebRtcNs_InitCore()
//改变噪声抑制方法的激增性
WebRtcNs_set_policy_core()
2、分析模块
//噪声抑制分析模块
WebRtcNs_AnalyzeCore()
//更新数据缓冲
UpdateBuffer()
//计算缓冲区的能量
Energy()
//窗缓冲区
Windowing()
//将信号从时域变换到频域
FFT()
//噪声估计
NoiseEstimation()
//计算信噪比
ComputeSnr()
//特征值更新(主要是谱差和平坦度)
FeatureUpdate()
//计算谱平坦度
ComputeSpectralFlatness()
 //计算谱差异
ComputeSpectralDifference()
//计算语音/噪声概率
SpeechNoiseProb()
//更新噪声估计
UpdateNoiseEstimate()
//计算缓冲区的能量
Energy()
//窗缓冲区
Windowing()
3、处理模块
//噪声抑制处理模块
WebRtcNs_ProcessCore()
//更新数据缓冲
UpdateBuffer()
//计算缓冲区的能量
Energy()
/ /窗缓冲区
Windowing()
//将信号从时域变换到频域
FFT()
//估计先验信噪比判决定向和计算基于DD的维纳滤波器
ComputeDdBasedWienerFilter()
//将信号从频率变换到时域
IFFT()
//窗缓冲区
Windowing()
//更新数据缓冲
UpdateBuffer()
```
## WebRtcNs_InitCore() 
```cpp
// We only support 10ms frames.
  if (fs == 8000) {
    self->blockLen = 80;  //帧的点数
    self->anaLen = 128;  //FFT点数
    self->window = kBlocks80w128;
  } else {
    self->blockLen = 160;
    self->anaLen = 256;
    self->window = kBlocks160w256;
  }
  self->magnLen = self->anaLen / 2 + 1;  // Number of frequency bins.
  // 频带数
```
## set_feature_extraction_parameters()
设置了特征提取使用到的参数，当前WebRTC噪声抑制算法使用了LRT特征/频谱平坦度和频谱差异度三个指标，没有使用频谱熵和频谱方差这两个特征。
# [Processing of WebRTC noise suppression](http://www.yushuai.xyz/2019/07/01/4396.html)  
## NoiseEstimation() 噪声估计  
###  [语音增强原理之噪声估计](https://www.cnblogs.com/icoolmedia/p/noise_estimate.html)
### [噪声估计](https://www.jianshu.com/p/26e24bbc2358)

## WebRtcNs_AnalyzeCore()
计算信噪比函数之前的部分分别是：
1.对输入的时域帧数据进行加窗、FFT变换。
2.然后计算能量，若能量为0，返回；否则继续往下。
3.然后计算新的能量和幅度。
4.使用分位数噪声估计进行初始噪声估计。
5.然后取前50个帧，计算得到高斯白噪声、粉红噪声模型，联合白噪声、粉红噪声模型，得到建模的混合噪声模型。
在噪声抑制模块WebrtcAnalyzeCore中，输入信号经过时频变换后分成三路信号，分别对这三路信号进行计算频谱平坦度、计算信噪比、计算频谱差异。最后将这三个相应的特征值输入到语音/噪声概率更新模板中。该模块具体的流程图以及功能介绍如下：

![Webrtc NS模块算法](https://www.likecs.com/default/index/img?u=aHR0cHM6Ly9waWFuc2hlbi5jb20vaW1hZ2VzLzYzOS9iN2E0YmNhNGRlOGM4YmYwYWE0ZDNhM2FiMTExMmQyZi5wbmc= "Webrtc NS模块算法")
