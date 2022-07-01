[toc]
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

# [webRTC中语音降噪模块ANS细节详解(二)](https://www.cnblogs.com/talkaudiodev/p/15358899.html)
ANS的基本处理过程如下图1：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211010165417974-1894053618.png)

                                         图1

从图1可以看出，处理过程主要分6步，具体如下：

1）  把输入的带噪信号从时域转到频域，主要包括分帧、加窗和短时傅里叶变换(STFT)等

2）  做初始噪声估计，基于估计出的噪声算先验信噪比和后验信噪比

3）  计算分类特征，这些特征包括似然比检验(LRT)、频谱平坦度和频谱差异。根据这些特征确定语音/噪声概率，从而判定当前信号是语音还是噪声。

4）  根据算出来的语音/噪声概率去更新噪声估计

5）  基于维纳滤波去噪

6）  把去噪后的信号从频域转换回时域，主要包括短时傅里叶逆变换(ISTFT)、加窗和重叠相加等。

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
## NoiseEstimation() 分位数噪声估计  
###  [语音增强原理之噪声估计](https://www.cnblogs.com/icoolmedia/p/noise_estimate.html)
### [噪声估计](https://www.jianshu.com/p/26e24bbc2358)
从代码来看，webrtc中包含了两种噪声估计方法，**一种是QBNE（Quantile Based Noise Estimation），翻译中文可以叫做分位数噪声估计**，前50帧的初始噪声估计是以分位数噪声估计为基础。噪声估计受分位数参数控制，该参数以q表示。根据初始噪声估计步骤确定的噪声估计，仅能用作促进噪声更新/估计的后续流程的初始条件。这个只用在初始噪声估计？**另一种也是采用递归的噪声最小估计方法。**
最小值控制的递归平均（MCRA）算法
　从上面的推导过程我们可以看到，MCRA算法的主要流程是：
 （1）先用最小值跟踪法获得带噪语音的最小值，它代表的是对噪声的初步估计
（2）再利用这个最小值来计算语音存在的概率p
（3）根据上式计算噪声估计的平滑因子
（4）利用递归平均来估计噪声
### [webRTC中语音降噪模块ANS细节详解(三)](https://www.cnblogs.com/talkaudiodev/p/15492190.html)
webRTC中ANS的初始噪声估计用的是分位数噪声估计法（QBNE，Quantile Based Noise Estimation），对应的论文为《Quantile Based Noise Estimation For Spectral Subtraction And Wiener Filtering》。 分位数噪声估计认为，即使是语音段，**输入信号在某些频带分量上也可能没有信号能量**，那么**将某个频带上所有语音帧的能量做一个统计，设定一个分位数值，低于分位数值的认为是噪声，高于分位数值的认为是语音**。算法大致步骤如下：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211023211535168-2047360130.jpg)
webRTC ANS在做初始估计时，**分三个阶段**，第一个阶段是前50帧，第二个阶段是51~200帧，第三个阶段是200帧以后的。50帧以后的只用分位数噪声估计法来估计噪声，而前50帧是分位数噪声估计法和噪声模型相结合，使噪声估计的更准确。先看每个阶段都有的分位数噪声估计的处理，过程如下：
1）  算出每个频点的幅度谱的自然对数值，即**对数谱**inst->lmagn，后续用lmagn表示
2）  更新分位数自然对数值(inst->lquantile，后续用lquantile表示)和概率密度值(inst->density，后续用density表示)。 共有三组lquantile和density值，每一帧有129个频点，所以lquantile和density的数组大小为387（129*3）。内存布局示意如图1：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211023211722793-325443566.jpg)

                                                图1
												

三组不同的lquantile和density的更新由inst->counter（后续用counter表示）来控制。counter数组有三个整数值，每个值控制一组。counter数组的初始值基于200（表示前200帧），将200一分为三，即为[66, 133, 200]。每处理完一帧counter值会加1，当值变为200时就会变为0。这样处理第二帧时counter值变为[67, 134, 0]，处理第三帧时counter值变为[68, 135, 1]，以此类推。当初始200帧处理完后，counter也完成了0~200的遍历。

下面看counter怎么控制lquantile和density的，对于第i组第j个频点而言，先定义变量：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211023211826293-158195432.jpg)

更新分位数：当频点对数谱lmagn[j] > lquantile[i*129 + j]时，表示lquantile偏小，需要增大，反之则需要减小。更新数学表达式如下式1

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211023211913511-379397241.jpg)                         （1）             

更新概率密度：当|lmagn[j] – lquantile[i*129+j]| < WIDTH(值为0.01)时，意味着当前的噪声估计比较准确了，因此要更新概率密度。更新的数学表达式如下式2：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211023212035588-1804529632.jpg)                                                               （2）

3）  当帧数小于200时，对最后一组（即第二组）的lquantile做自然指数运算，将其作为噪声估计值（noise[j]，每个频点一个值），可以看出每帧估出的噪声是不同的。当帧数大于等于200后，只有当counter数组里的值等于200时，才会将对应的组的lquantile做自然指数运算，将其作为噪声估计值。可以看出当帧数大于等于200后每过66帧或者67帧噪声估计值才会更新。

再看前50帧利用分位数噪声估计法与噪声模型相结合来估计初始噪声。先定义如下四个变量：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026152422278-1374180948.jpg)

需要注意的是上述4个变量定义时均没有用到前5个频点，因为i是从5开始的。再利用上面定义的变量表示白噪声（white noise）和粉红噪声（pink noise）的参数，表示如下：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211023212339116-513739321.jpg)

其中overdrive是根据设置的降噪程度而得到的一个值（在初始化中设置）。

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211115181601267-196314828.jpg)

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211023212524693-842810852.jpg)

 其中blockInd表示当前帧的index 。

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211023212610636-708142706.jpg)

这样就可以利用白噪声和粉红噪声的参数来估计模型噪声了，具体如下：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026150416872-713882962.jpg)

其中当频点id小于5时，usedBin = 5, 其他情况下usedBin = 频点id。

最后根据分位数估计噪声noise和模型估计噪声parametric_noise得到最终的估计噪声了。对于每个频点j来说，表达式如下式3:

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211023212752969-192483303.jpg)                                  (3)

至此，前50帧的结合分位数噪声估计和模型噪声估计的噪声就估计出来了。这样不管是第几帧，初始噪声都能估计出来，下面根据估计出来的初始噪声来算先验信噪比和后验信噪比。
```c
// Estimate noise.
static void NoiseEstimation(NoiseSuppressionC* self,
                            float* magn,
                            float* noise) {
  size_t i, s, offset=0;
  float lmagn[HALF_ANAL_BLOCKL], delta;

  if (self->updates < END_STARTUP_LONG) {
    self->updates++;
  }

  //webRTC ANS在做初始估计时，分三个阶段，第一个阶段是前50帧，第二个阶段是51~200帧，第三个阶段是200帧以后的。
  //50帧以后的只用分位数噪声估计法来估计噪声，而前50帧是分位数噪声估计法和噪声模型相结合，使噪声估计的更准确。
  //先看每个阶段都有的分位数噪声估计的处理，过程如下：
  for (i = 0; i < self->magnLen; i++) {
	 lmagn[i] = logf(magn[i]); 
    //lmagn[i] = (float)log(magn[i]);
  }

  // Loop over simultaneous estimates.
  for (s = 0; s < SIMULT; s++) {
    offset = s * self->magnLen;

    // newquantest(...)
    for (i = 0; i < self->magnLen; i++) {
      // Compute delta.
      if (self->density[offset + i] > 1.0) {
        delta = FACTOR * 1.f / self->density[offset + i]; // 概率密度值inst->density
      } else {
        delta = FACTOR;
      }

      // Update log quantile estimate.
      if (lmagn[i] > self->lquantile[offset + i]) {
        self->lquantile[offset + i] +=
            QUANTILE * delta / (float)(self->counter[s] + 1); // self->lquantile 分位数自然对数值
      } else {
        self->lquantile[offset + i] -=
            (1.f - QUANTILE) * delta / (float)(self->counter[s] + 1);
      }

      // Update density estimate.
	  if (fabsf(lmagn[i] - self->lquantile[offset + i]) < WIDTH) {
      //if (fabs(lmagn[i] - self->lquantile[offset + i]) < WIDTH) {
        self->density[offset + i] =
            ((float)self->counter[s] * self->density[offset + i] +
             1.f / (2.f * WIDTH)) /
            (float)(self->counter[s] + 1);
      }
    }  // End loop over magnitude spectrum.

    if (self->counter[s] >= END_STARTUP_LONG) {
      self->counter[s] = 0;
      if (self->updates >= END_STARTUP_LONG) {
        for (i = 0; i < self->magnLen; i++) {
          self->quantile[i] = expf(self->lquantile[offset + i]);
		  //self->quantile[i] = (float)exp(self->lquantile[offset + i]);
        }
      }
    }

    self->counter[s]++;
  }  // End loop over simultaneous estimates.

  // Sequentially update the noise during startup.
  if (self->updates < END_STARTUP_LONG) {
    // Use the last "s" to get noise during startup that differ from zero.
    for (i = 0; i < self->magnLen; i++) {
		self->quantile[i] = expf(self->lquantile[offset + i]);
      //self->quantile[i] = (float)exp(self->lquantile[offset + i]);
    }
  }

  for (i = 0; i < self->magnLen; i++) {
    noise[i] = self->quantile[i];
  }
}
// Compute simplified noise model during startup.
  if (self->blockInd < END_STARTUP_SHORT) {
    // Estimate White noise.
    self->whiteNoiseLevel += sumMagn / self->magnLen * self->overdrive;
    // Estimate Pink noise parameters.
    tmpFloat1 = sum_log_i_square * (self->magnLen - kStartBand);
    tmpFloat1 -= (sum_log_i * sum_log_i);
    tmpFloat2 =
        (sum_log_i_square * sum_log_magn - sum_log_i * sum_log_i_log_magn);
    tmpFloat3 = tmpFloat2 / tmpFloat1;
    // Constrain the estimated spectrum to be positive.
    if (tmpFloat3 < 0.f) {
      tmpFloat3 = 0.f;
    }
    self->pinkNoiseNumerator += tmpFloat3;
    tmpFloat2 = (sum_log_i * sum_log_magn);
    tmpFloat2 -= (self->magnLen - kStartBand) * sum_log_i_log_magn;
    tmpFloat3 = tmpFloat2 / tmpFloat1;
    // Constrain the pink noise power to be in the interval [0, 1].
    if (tmpFloat3 < 0.f) {
      tmpFloat3 = 0.f;
    }
    if (tmpFloat3 > 1.f) {
      tmpFloat3 = 1.f;
    }
    self->pinkNoiseExp += tmpFloat3;

    // Calculate frequency independent parts of parametric noise estimate.
    if (self->pinkNoiseExp > 0.f) {
      // Use pink noise estimate.
      parametric_num =
          expf(self->pinkNoiseNumerator / (float)(self->blockInd + 1));
      parametric_num *= (float)(self->blockInd + 1);
      parametric_exp = self->pinkNoiseExp / (float)(self->blockInd + 1);
    }
    for (i = 0; i < self->magnLen; i++) {
      // Estimate the background noise using the white and pink noise
      // parameters.
      if (self->pinkNoiseExp == 0.f) {
        // Use white noise estimate.
        self->parametricNoise[i] = self->whiteNoiseLevel;
      } else {
        // Use pink noise estimate.
        float use_band = (float)(i < kStartBand ? kStartBand : i);
        self->parametricNoise[i] =
            parametric_num / powf(use_band, parametric_exp);
      }
      // Weight quantile noise with modeled noise.
      noise[i] *= (self->blockInd);
      tmpFloat2 =
          self->parametricNoise[i] * (END_STARTUP_SHORT - self->blockInd);
      noise[i] += (tmpFloat2 / (float)(self->blockInd + 1));
      noise[i] /= END_STARTUP_SHORT;
    }
  }
  // Compute average signal during END_STARTUP_LONG time:
  // used to normalize spectral difference measure.
  if (self->blockInd < END_STARTUP_LONG) {
    self->featureData[5] *= self->blockInd;
    self->featureData[5] += signalEnergy;
    self->featureData[5] /= (self->blockInd + 1);
  }
```


## ComputeSnr()
**后验信噪比σ是带噪语音Y与噪声N的功率比值**，**先验信噪比ρ是干净语音S与噪声N的功率比值**，表达式如下式4和5：

 ![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026145533017-1489537224.jpg)                                                                                                                            (4)

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026145555921-1759932499.jpg)                                                                                                                             (5)

其中**m表示第几帧，k表示第几个频点**，即每一个频点上都有先验SNR和后验SNR。由于**噪声N已通过分位数估计法估计出来**，而且带噪语音Y已知，因而后验SNR可以算出来。

因为

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026145656503-1066249438.jpg)

从而

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026145720044-804655305.jpg)

所以得到式6：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026145745965-569677294.jpg)                                              (6)

即**先验SNR等于后验SNR – 1**。

至于算先验SNR，用的是**判决引导法**（Decision-Directed，简称DD）。根据式5和式6可以得到式7：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026145840109-1391328590.jpg)                                                                                       (7)

对先验SNR的估算可以将上式递推化得到，具体如式8：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026145938588-842305161.jpg)                                                            (8)

这里**α为权重（或叫平滑系数），以代替上式中的1/2**。从上式看出估算当前帧的先验SNR是**基于上一帧的先验SN**R和**当前帧的后验SNR**。max()用以保证估值是**非负**的。平滑系数α取值范围为0 < α < 1，典型取值为0.98，webRTC ANS中就是用的这个值。

在具体软件实现中，WebRTC中为了减小运算load，并未严格按照定义的公式去计算，而是**采用幅度谱的比值**去计算，即式9和式10中第二个等号的右边部分。

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026150033462-757323235.jpg)                                                                                                        (9)

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026150054923-394624229.jpg)                                                                                                          (10)

算当前帧的先验SNR时，上一帧的带噪语音Y(k, m-1)是已知的，**上一帧的维纳滤波器系数的值H(k, m-1)**（即inst-smooth数组里的值）也是已知的，根据维纳滤波原理，从而**上一帧的估计出来的干净语音S(k, m-1) = H(k, m-1)Y(k, m-1)也是已知的**，所以上一帧的先验SNR计算如式11：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026150136374-1929177294.jpg)                                                 (11)

将其带入式8可得**当前帧的先验SNR**计算表达式如式12：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211026150233148-457476120.jpg)                                           (12)

这样当前帧的先验SNR和后验SNR都计算出来了，用于后面的语音噪声概率计算中。
```c
// Compute prior and post SNR based on quantile noise estimation.
// Compute DD estimate of prior SNR.
// Inputs:
//   * |magn| is the signal magnitude spectrum estimate.
//   * |noise| is the magnitude noise spectrum estimate.
// Outputs:
//   * |snrLocPrior| is the computed prior SNR.
//   * |snrLocPost| is the computed post SNR.
static void ComputeSnr(const NoiseSuppressionC* self,
                       const float* magn,
                       const float* noise,
                       float* snrLocPrior,
                       float* snrLocPost) {
  size_t i;

  for (i = 0; i < self->magnLen; i++) {
    // Previous post SNR.
    // Previous estimate: based on previous frame with gain filter.
    float previousEstimateStsa = self->magnPrevAnalyze[i] /
        (self->noisePrev[i] + 0.0001f) * self->smooth[i]; // 前一帧的后验信噪比乘维纳滤波器系数=前一帧后验信噪比 self->magnPrevAnalyze前一帧带噪语音赋值 self->noisePrev前一帧估计噪声
    // Post SNR.
    snrLocPost[i] = 0.f;
    if (magn[i] > noise[i]) {
      snrLocPost[i] = magn[i] / (noise[i] + 0.0001f) - 1.f; // 当前帧后验信噪比-1=前验信噪比
    }
    // DD estimate is sum of two terms: current estimate and previous estimate.
    // Directed decision update of snrPrior.
    snrLocPrior[i] =
        DD_PR_SNR * previousEstimateStsa + (1.f - DD_PR_SNR) * snrLocPost[i];  // 平滑公式
  }  // End of loop over frequencies.
}
```


## FFT()
先看从时域信号变成频域信号。主要步骤是分帧、加窗和做短时傅里叶变换（STFT）。分帧上面说过，10 ms一帧，每帧160个采样点。加窗的目的是避免频谱泄漏。有多种窗函数，常见的有矩形窗、三角窗、汉宁（hanning）窗和海明（hamming）窗等。语音处理中常用的是汉宁窗和海明窗。ANS中用的是汉宁窗和矩形窗混在一起的混合窗。做STFT要求点数是2的N次方，现在每帧160个点，大于160的最近的2的N次方是256，所以STFT一次处理256个点（这也是代码中256（#define ANAL_BLOCKL_MAX  256）的由来）。现在每帧160个点，需要补成256个点。一种做法是在160个点后面补零补成256个点。ANS用了一种更好的方法。用上一帧的尾部的96个点来补从而形成256个点。这样从时域信号变成频域信号的处理流程如下图2：

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211001102809941-1875069307.png)

                                                     图2

因为对256点做STFT，所以加窗的点数也是256。ANS用的是窗是汉宁和矩形混合窗。汉宁窗函数是w(n) = 0.5 * (1 + cos(2*pi*n / (N-1)))，范围是（0,1），波形如下图3。

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211001103545289-1297415478.png)

                                    图3

这个混合窗是把192（96*2）点的汉宁窗在顶点处插入64点的幅值为1的矩形窗，从而形成256（256 = 192 + 64）点的混合窗，波形如下图4。

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211001103322978-1520098678.jpg)

                                        图4

至于为什么要这么做，后面讲频域转换到时域时再说。256个点的值与相应的窗函数相乘，得到要送进STFT处理的值。STFT处理后得到256个频点的值，这些值除了第0点和第N/2点（N=256，即第128点）点是实数外，其余点都是复数，且关于第N/2点共轭对称。因为共轭对称，一个点知道了，它的对称点就可以求出来。所以STFT处理后有（N/2 + 1）个点的值。这里N=256，STFT的输出是129个点的值。这也是代码中129（#define HALF_ANAL_BLOCKL  129）的由来。得到129个频点的值后还要算每个频点的幅度谱和能量等，用于后面降噪算法，具体处理如下面代码，已给出详细的注释，就不细说了。

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211001102918293-1962742034.jpg)

在频域做完降噪处理后需要把信号从频域变回时域，即信号的重建或者合成，主要步骤是做短时傅里叶反变换（ISTFT）、加窗和重叠相加(overlap add, OLA)等，处理流程如下图5。

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211010170902634-948730435.png)

                                    图5

先做ISTFT（短时傅里叶反变换），得到256点的实数值。这256点包括上一帧的尾部的96点，即有重叠。该怎么拼接保证声音连贯呢？上面讲从时域到频域变换时用的窗是汉宁矩形混合窗，汉宁窗前半部分（头部96点）类似于做正弦操作，后半部分（尾部96点）类似于做余弦操作。重叠部分是在上一帧的尾部，加窗做的是类余弦操作，在当前帧是头部，加窗做的是类正弦操作。信号重建叠加时一般要求能量或者幅值不变，能量是幅值的平方。那些重叠的点（假设幅值为m）在上一帧中加窗时做了类余弦操作，加窗后幅值变成了m*cosθ，在当前帧中加窗时做了类正弦操作，加窗后幅值变成了m*sinθ，能量和为m2*cos2θ + m2*sin2θ, 正好等于m2(原信号的能量)，这说明只要把重叠部分相加就可以保证语音信号的连贯了。这就解释了代码中把ISTFT后的值再做一次加窗操作并把重叠部分相加的原因。具体代码见下图6。

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211001103026305-2070308426.jpg)

                                                   图6

至于矩形窗部分，幅值为1，即加窗后信号幅值不变，因而不需要做处理，直接填上就可以了。需要注意的是图6中还有一个能量缩放因子factor。它在前200帧默认为1，后续帧按如下逻辑关系得到。

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211022064054833-516584772.png)

图7给出了做完ISTFT后数据拼接的示意图。做完ISTFT后有256点数据，当前帧的头部96点数据与上一帧的尾部96点数据相加，中间64点数据不变，当前帧尾部96点数据与下一帧的头部96点数据相加，这样就能很好的拼接处连贯的语音数据了。

![](https://img2020.cnblogs.com/blog/1181527/202110/1181527-20211021224607997-774155967.jpg)

                                                  图7
```c
// Transforms the signal from time to frequency domain.
// Inputs:
//   * |time_data| is the signal in the time domain.
//   * |time_data_length| is the length of the analysis buffer.
//   * |magnitude_length| is the length of the spectrum magnitude, which equals
//     the length of both |real| and |imag| (time_data_length / 2 + 1).
// Outputs:
//   * |time_data| is the signal in the frequency domain.
//   * |real| is the real part of the frequency domain.
//   * |imag| is the imaginary part of the frequency domain.
//   * |magn| is the calculated signal magnitude in the frequency domain.
static void FFT(NoiseSuppressionC* self,
                float* time_data,
                size_t time_data_length,
                size_t magnitude_length,
                float* real,
                float* imag,
                float* magn) {
  size_t i;

  assert(magnitude_length == time_data_length / 2 + 1);

  WebRtc_rdft(time_data_length, 1, time_data, self->ip, self->wfft); // 0和1分别放的是0和N/2直流分量

  imag[0] = 0;
  real[0] = time_data[0];
  magn[0] = fabsf(real[0]) + 1.f;
  imag[magnitude_length - 1] = 0;
  real[magnitude_length - 1] = time_data[1];
  magn[magnitude_length - 1] = fabsf(real[magnitude_length - 1]) + 1.f;
  for (i = 1; i < magnitude_length - 1; ++i) {
    real[i] = time_data[2 * i];
    imag[i] = time_data[2 * i + 1];
    // Magnitude spectrum.
    magn[i] = sqrtf(real[i] * real[i] + imag[i] * imag[i]) + 1.f;
  }
}
```
```c
// Back to time domain.
  IFFT(self, real, imag, self->magnLen, self->anaLen, winData);

  // Scale factor: only do it after END_STARTUP_LONG time.
  factor = 1.f;
  if (self->gainmap == 1 && self->blockInd > END_STARTUP_LONG) {
    factor1 = 1.f;
    factor2 = 1.f;

    energy2 = Energy(winData, self->anaLen);
	gain = sqrtf(energy2 / (energy1 + 1.f));
    //gain = (float)sqrt(energy2 / (energy1 + 1.f));

    // Scaling for new version.
    if (gain > B_LIM) {
      factor1 = 1.f + 1.3f * (gain - B_LIM);
      if (gain * factor1 > 1.f) {
        factor1 = 1.f / gain;
      }
    }
    if (gain < B_LIM) {
      // Don't reduce scale too much for pause regions:
      // attenuation here should be controlled by flooring.
      if (gain <= self->denoiseBound) {
        gain = self->denoiseBound;
      }
      factor2 = 1.f - 0.3f * (B_LIM - gain);
    }
    // Combine both scales with speech/noise prob:
    // note prior (priorSpeechProb) is not frequency dependent.
    factor = self->priorSpeechProb * factor1 +
             (1.f - self->priorSpeechProb) * factor2;
  }  // Out of self->gainmap == 1.

  Windowing(self->window, winData, self->anaLen, winData);

  // Synthesis.
  for (i = 0; i < self->anaLen; i++) {
    self->syntBuf[i] += factor * winData[i];
  }
  // Read out fully processed segment.
  for (i = self->windShift; i < self->blockLen + self->windShift; i++) {
    fout[i - self->windShift] = self->syntBuf[i];
  }
  // Update synthesis buffer.
  UpdateBuffer(NULL, self->blockLen, self->anaLen, self->syntBuf);

  for (i = 0; i < self->blockLen; ++i)
    outFrame[0][i] =
        outFrame[0][i] =
                WEBRTC_SPL_SAT(32767, fout[i], (-32768));
```

## FeatureUpdate() 提取平均LRT参数、频谱差异、频谱平坦度
提取平均LRT参数、频谱差异、频谱平坦度

## ComputeSpectralFlatness() 计算频谱平坦度
计算频谱平坦度
语音比噪声的谐波多，其表现是语音频谱通常在基频和谐波中出现能量峰值，而噪声频谱则相对平坦，因此频谱平坦度可以区分语音和噪声。定义F2为频谱平坦度特征，频谱平坦度算法是**几何平均除以算术平均**，计算如式15：

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109075426732-1181935106.png)（15）
 由于![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107062736151-293875047.png)不太方便计算，软件实现时**先取对数，变成加法运算，加法算好后再取指数从而得到几何平均**，具体如下，令

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109074839031-1752090376.png)
 所以

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107062911158-1514485627.png)

算出F2后还要做一个平滑处理。
就128个频率点可分成4个频带（低带，中低频带，中高频带，高频），每个频带32个频点。对于**噪声Flatness偏大且为常数**，而**对于语音，计算出的数量则偏小且为变量**。  
根据上面的公式，**如果接近于1，则是噪声**，（**噪声的幅度谱趋于平坦**），二对于**语音**，**上面的N次根是对乘积结果进行N次缩小，相比于分母部分，缩小的数量级是倍数的，所以语音的平坦度较小，是趋近于0的**	。
```c
// Compute spectral flatness on input spectrum.
// |magnIn| is the magnitude spectrum.
// Spectral flatness is returned in self->featureData[0].
static void ComputeSpectralFlatness(NoiseSuppressionC* self,
                                    const float* magnIn) {
  size_t i;
  size_t shiftLP = 1;  // Option to remove first bin(s) from spectral measures.
  float avgSpectralFlatnessNum, avgSpectralFlatnessDen, spectralTmp;

  // Compute spectral measures.
  // For flatness.
  avgSpectralFlatnessNum = 0.0;
  avgSpectralFlatnessDen = self->sumMagn;
  // 跳过第一个频点，即直流频点Den是denominator（分母）的缩写，avgSpectralFlatnessDen是上述公式分母计算用到的
  for (i = 0; i < shiftLP; i++) {
    avgSpectralFlatnessDen -= magnIn[i];
  }
  // Compute log of ratio of the geometric to arithmetic mean: check for log(0)
  // case.
  for (i = shiftLP; i < self->magnLen; i++) {
    if (magnIn[i] > 0.0) {
		avgSpectralFlatnessNum += logf(magnIn[i]);
      //avgSpectralFlatnessNum += (float)log(magnIn[i]);
    } else {
      self->featureData[0] -= SPECT_FL_TAVG * self->featureData[0]; // TVAG是time-average的缩写，对于能量出现异常的处理。利用前一次平坦度直接取平均返回。
      return;
    }
  }
  // Normalize.
  avgSpectralFlatnessDen = avgSpectralFlatnessDen / self->magnLen;
  avgSpectralFlatnessNum = avgSpectralFlatnessNum / self->magnLen; // 频谱平坦度算法是几何平均除以算术平均 几何平均为了方便计算，先取对数变成求和再变回指数运算

  // Ratio and inverse log: check for case of log(0).
  spectralTmp = expf(avgSpectralFlatnessNum) / avgSpectralFlatnessDen;
  //spectralTmp = (float)exp(avgSpectralFlatnessNum) / avgSpectralFlatnessDen;

  // Time-avg update of spectral flatness feature.
  self->featureData[0] += SPECT_FL_TAVG * (spectralTmp - self->featureData[0]); // 平滑处理
  // Done with flatness feature.
}
```

## ComputeSpectralDifference() 计算频谱差异度
计算频谱差异度噪声频谱比语音频谱更稳定，因此，假设噪声频谱体形状在任何给定阶段都倾向于保持相同，  
此特征用于测量输入频谱与噪声频谱形状的偏差。
先定义五个变量：avgMagn/varMagn （magnitude的均值和方差均值）和avgPause/varPause（conservative noise spectrum的均值和方差均值），以及covMagnPause（magn和pause的协方差均值）
![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109075219055-67712467.png)
定义F3为频谱模板差异度特征，表达式如式16：
 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109075329448-184303205.png)                        (16)

同频谱平坦度一样，最后也要做一个平滑。
```c
// Compute the difference measure between input spectrum and a template/learned
// noise spectrum.
// |magnIn| is the input spectrum.
// The reference/template spectrum is self->magnAvgPause[i].
// Returns (normalized) spectral difference in self->featureData[4].
static void ComputeSpectralDifference(NoiseSuppressionC* self,
                                      const float* magnIn) {
  // avgDiffNormMagn = var(magnIn) - cov(magnIn, magnAvgPause)^2 /
  // var(magnAvgPause)
  size_t i;
  float avgPause, avgMagn, covMagnPause, varPause, varMagn, avgDiffNormMagn;
  // avgMagn/varMagn （magnitude的均值和方差均值）avgPause/varPause（conservative noise spectrum的均值和方差均值）covMagnPause（magn和pause的协方差均值）

  avgPause = 0.0;
  avgMagn = self->sumMagn;
  // Compute average quantities.
  for (i = 0; i < self->magnLen; i++) {
    // Conservative smooth noise spectrum from pause frames.
    avgPause += self->magnAvgPause[i];
  }
  avgPause /= self->magnLen;
  avgMagn /= self->magnLen;

  covMagnPause = 0.0;
  varPause = 0.0;
  varMagn = 0.0;
  // Compute variance and covariance quantities.
  for (i = 0; i < self->magnLen; i++) {
    covMagnPause += (magnIn[i] - avgMagn) * (self->magnAvgPause[i] - avgPause);
    varPause +=
        (self->magnAvgPause[i] - avgPause) * (self->magnAvgPause[i] - avgPause);
    varMagn += (magnIn[i] - avgMagn) * (magnIn[i] - avgMagn);
  }
  covMagnPause /= self->magnLen;
  varPause /= self->magnLen;
  varMagn /= self->magnLen;
  // Update of average magnitude spectrum.
  self->featureData[6] += self->signalEnergy;

  avgDiffNormMagn =
      varMagn - (covMagnPause * covMagnPause) / (varPause + 0.0001f);
  // Normalize and compute time-avg update of difference feature.
  avgDiffNormMagn = avgDiffNormMagn / (self->featureData[5] + 0.0001f); // 归一化
  //avgDiffNormMagn = (float)(avgDiffNormMagn / (self->featureData[5] + 0.0001f));
  self->featureData[4] +=
      SPECT_DIFF_TAVG * (avgDiffNormMagn - self->featureData[4]);
}
```

## FeatureParameterExtraction() 提取特征阈值 没怎么看懂
## SpeechNoiseProb()  语音噪声概率更新
先看怎么算带噪语音和特征条件下的语音概率。其中会用到先前算好的先验SNR和后验SNR，也会用到特征条件下的语音概率，从而涉及到怎么算特征条件下的语音概率，有了特征条件下的语音概率后结合先前算好的先验SNR和后验SNR带噪语音和特征条件下的语音概率就好算了。

1，  带噪语音和特征条件下的语音概率

令H1(k, m)表示第m帧的第k个频点上是语音状态，表示H0(k, m)第m帧的第k个频点上是噪声状态，Y(k,m)表示第m帧的第k个频点上的幅度谱，{F}表示特征集合。为方便书写，简写为H1、H0、Y和F。P(H1 | Y F)表示在带噪语音和特征条件下是语音的概率，其他类推。因为只有语音和噪声两种类型，所以有式1和2（P(•)表示概率）：

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106185152291-1103843288.png)                               (1)

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106185212963-1899964678.png)                                 (2)

对式1展开得式3：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106185312736-447260115.png)                      (3)

因为

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106185440421-204389775.png)

所以得到式4：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106185539678-2028041838.png)               （4）

还可得到式5：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106185615095-981335249.png)                                   （5）

在带噪语音和特征条件下是语音的概率为P(H1 | YF) ，把式4和5带入得到式6:

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106185822148-3609393.png)                                               (6)

在式2中，令P(H1 | F) = q(k, m)，这里简计为q，则P(H0| F) = 1 – q。

再令Δ(k, m) =  ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106190040870-1151076009.png)为似然比， 所以得到式7:

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106190133669-1129573766.png)                                                                   (7)

看怎么求似然比。这里会用到复高斯分布，先了解一下什么是复高斯分布。假设实随机高斯变量x和y的均值分别为mx与my，方差为σ2，则x的概率密度函数为

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106190447191-345974959.png)

y的概率密度函数为

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106190552593-1527722853.png)

若x与y相互独立，则x与y的联合概率密度函数为

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106190704174-550130182.png)

定义 z = x + iy，则z为复高斯随机变量。求z的均值和方差如下(E(•)表示期望)：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106190759474-2097967274.png)

对于干净语音和噪声来说，转换到频域后是复数，一般假设服从零均值的复高斯分布，所以

 mz= 0， 从而 mx + imy= 0，所以 mx = 0，my = 0。

把mx = 0，my = 0以及σ2 z = 2σ2带入，得到

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106191327276-783745371.png)

这就是干净语音和噪声的概率密度函数。

在H0下（即噪声下），Y(k,m) = N(k,m)，由于噪声服从均值为0的复高斯分布，可得f(Y | H0)为与噪声有相同方差的高斯分布，所以在噪声条件下带噪语音的条件概率密度函数表示如式8:

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106220443611-765148300.png)                                        (8)

在H1下（即语音下），Y(k,m) = S(k,m) + N(k,m)，由于语音和噪声均服从均值为0的复高斯分布，以及S(k,m)和N(k,m)相互独立，可得f(Y | H1)也为高斯分布，方差为语音和噪声的方差和，所以在语音条件下带噪语音的条件概率密度函数表示如式9:

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106220620735-1117982664.png)         (9)

所以

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106220739691-2102375079.png)

软件实现时同计算先后验信噪比一样，用幅值代替能量，从而

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106220905285-1273937198.png)

用上篇（[webRTC中语音降噪模块ANS细节详解(三)](https://www.cnblogs.com/talkaudiodev/p/15492190.html)）计算出的先验信噪比和后验信噪比表示就可以写成式10：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106221102484-186019613.png)                                 （10）

为方便计算，对似然比取自然对数得到式11：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106221438609-1601881132.png)                       (11)

软件实现时，没有严格按照这个表达式来，而是用2ρ(k, m)代替了ρ(k, m)， 用（1+ σ(k, m)）代替了σ(k, m)。所以式11变成了式12:

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211106221528910-365140838.png)        (12)

为了防止帧间频变导致似然比波动较大，对似然比进行了平滑，并将式12带入得到表达式13（![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107062112975-1850100980.png)为平滑系数）：

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211108215507225-685902851.png)       （13）

ln(Δ(k,m))能算出，取自然指数就算出Δ(k,m)了。回看在带噪语音和特征条件下算语音的概率如式7：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107062302846-1275586631.png)

Δ(k,m)已算出，只要再算出q(q = P(H1 | F) ，特征条件下是语音的概率)，就可算出在带噪语音和特征条件下的语音概率了。下面看怎么算在特征条件下语音的概率。

2， 特征条件下的语音概率

webRTC用到的特征有似然比检验（Likelihood Rate Test, LRT）均值、频谱平坦度（Spectral Flatness）和频谱模板差异度（Spectral Difference）。先看这些特征，然后看怎么算在这些特征条件下的语音概率。

1） LRT均值特征

似然比Δ(k,m)上面已算出，定义F1为LRT均值特征，如下式14:

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211108215948997-1059255066.png)                 （14）

N为频点数，当采样率为16k HZ时，N = 129，下同。

2） 频谱平坦度特征

语音比噪声的谐波多，其表现是语音频谱通常在基频和谐波中出现能量峰值，而噪声频谱则相对平坦，因此频谱平坦度可以区分语音和噪声。定义F2为频谱平坦度特征，频谱平坦度算法是几何平均除以算术平均，计算如式15：

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109075426732-1181935106.png)                                                        （15）       

由于![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107062736151-293875047.png)不太方便计算，软件实现时先取对数，变成加法运算，加法算好后再取指数从而得到几何平均，具体如下，令

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109074839031-1752090376.png)

所以

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107062911158-1514485627.png)

算出F2后还要做一个平滑处理。

3）频谱模板差异度特征

先定义五个变量：avgMagn/varMagn （magnitude的均值和方差均值）和avgPause/varPause（conservative noise spectrum的均值和方差均值），以及covMagnPause（magn和pause的协方差均值）

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109075219055-67712467.png)

定义F3为频谱模板差异度特征，表达式如式16：

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109075329448-184303205.png)                        (16)

同频谱平坦度一样，最后也要做一个平滑。

三个特征得到后，特征条件下的语音概率P(H1 | F)或者q(k, m)的更新模型可用式17表示：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107063252318-162113190.png)                                     (17)

其中β为平滑系数，M(F)为映射函数，宜用非线性函数，如人工智能(AI)中常用做激活函数的S函数(sigmoid)和双曲正切(tanh)等，因为它们都把函数的取值范围压在了(0, 1)或者(-1, 1)范围内。映射函数根据特征、阈值和宽度参数，将频点划分为语音（M接近1）或者噪声（M接近0）。WebRTC中用的是tanh。这里简单说一下tanh，它的定义式如下：

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109075712742-1803687161.png)

可以证明它的取值范围是（-1, 1）, 并且是单调递增的。tanh的波形图如下图：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107063614129-610989976.png)

实现中M(F) = 0.5 * [tanh(ω*|F - T|) + 1.0]，因为tanh的取值范围是（-1, 1），所以M(F)的取值范围是（0，1）。这里F表示特征，T是阈值，参数ω代表映射函数的形状和宽度。当有多个特征后，每个特征都有一定的权重，这时q(k, m)的更新模型变为式18:

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107063809965-471110475.png)        (18)

再回看在带噪语音和特征条件下算语音的概率如式7：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107063904582-515739947.png)

似然比Δ(k,m)已求出，特征(F1/F2/F3)条件下语音的概率q(k, m)也求出，在带噪语音和特征条件下算语音的概率P(H1 | YF)就算出来了，代码如下：

![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107064130357-1577821000.png)

q = inst->priorSpeechProb， Δ = inst->logLrtTimeAvg

根据代码，

 ![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211109075944797-1981506766.png)

所以语音概率![](https://img2020.cnblogs.com/blog/1181527/202111/1181527-20211107064526195-601058188.png)，跟式7是一致的。 

P(H1 | YF)求出，在带噪语音和特征条件下噪声的概率P(H0 | YF) = 1 - P(H1 | YF) 也就求出来了。
```c
// Compute speech/noise probability.
// Speech/noise probability is returned in |probSpeechFinal|.
// |magn| is the input magnitude spectrum.
// |noise| is the noise spectrum.
// |snrLocPrior| is the prior SNR for each frequency.
// |snrLocPost| is the post SNR for each frequency.
static void SpeechNoiseProb(NoiseSuppressionC* self,
                            float* probSpeechFinal,
                            const float* snrLocPrior,
                            const float* snrLocPost) {
  size_t i;
  int sgnMap;
  float invLrt, gainPrior, indPrior;
  float logLrtTimeAvgKsum, besselTmp;
  float indicator0, indicator1, indicator2;
  float tmpFloat1, tmpFloat2;
  float weightIndPrior0, weightIndPrior1, weightIndPrior2;
  float threshPrior0, threshPrior1, threshPrior2;
  float widthPrior, widthPrior0, widthPrior1, widthPrior2;

  widthPrior0 = WIDTH_PR_MAP;
  // Width for pause region: lower range, so increase width in tanh map.
  widthPrior1 = 2.f * WIDTH_PR_MAP;
  widthPrior2 = 2.f * WIDTH_PR_MAP;  // For spectral-difference measure.

  // Threshold parameters for features.
  threshPrior0 = self->priorModelPars[0];
  threshPrior1 = self->priorModelPars[1];
  threshPrior2 = self->priorModelPars[3];

  // Sign for flatness feature.
  sgnMap = (int)(self->priorModelPars[2]);

  // Weight parameters for features.
  weightIndPrior0 = self->priorModelPars[4];
  weightIndPrior1 = self->priorModelPars[5];
  weightIndPrior2 = self->priorModelPars[6];

  // Compute feature based on average LR factor.
  // This is the average over all frequencies of the smooth log LRT.
  logLrtTimeAvgKsum = 0.0;  
  for (i = 0; i < self->magnLen; i++) {
    tmpFloat1 = 1.f + 2.f * snrLocPrior[i];
    tmpFloat2 = 2.f * snrLocPrior[i] / (tmpFloat1 + 0.0001f);
    besselTmp = (snrLocPost[i] + 1.f) * tmpFloat2;
    self->logLrtTimeAvg[i] +=
        LRT_TAVG * (besselTmp - logf(tmpFloat1) - self->logLrtTimeAvg[i]);  // self->logLrtTimeAvg 经过时间平滑处理的似然比因子LR  Δ 
		//LRT_TAVG * (besselTmp - (float)log(tmpFloat1) - self->logLrtTimeAvg[i]);
    logLrtTimeAvgKsum += self->logLrtTimeAvg[i];
  }
   logLrtTimeAvgKsum = logLrtTimeAvgKsum / (self->magnLen);  // logLrtTimeAvgKsum经过时间平滑处理的似然比因子的几何平均数
  //logLrtTimeAvgKsum = (float)logLrtTimeAvgKsum / (self->magnLen);
  self->featureData[3] = logLrtTimeAvgKsum;
  // Done with computation of LR factor.

  // Compute the indicator functions.
  // Average LRT feature.
  widthPrior = widthPrior0;
  // Use larger width in tanh map for pause regions.
  if (logLrtTimeAvgKsum < threshPrior0) {
    widthPrior = widthPrior1;
  }
  // Compute indicator function: sigmoid map.
  indicator0 =
      0.5f *
	  (tanhf(widthPrior * (logLrtTimeAvgKsum - threshPrior0)) + 1.f);  // LRT均值再处理
      //((float)tanh(widthPrior * (logLrtTimeAvgKsum - threshPrior0)) + 1.f);

  // Spectral flatness feature.
  tmpFloat1 = self->featureData[0];
  widthPrior = widthPrior0;
  // Use larger width in tanh map for pause regions.
  if (sgnMap == 1 && (tmpFloat1 > threshPrior1)) {
    widthPrior = widthPrior1;
  }
  if (sgnMap == -1 && (tmpFloat1 < threshPrior1)) {
    widthPrior = widthPrior1;
  }
  // Compute indicator function: sigmoid map.
  indicator1 =
      0.5f *
	  (tanhf((float) sgnMap * widthPrior * (threshPrior1 - tmpFloat1))+
     // ((float)tanh((float)sgnMap * widthPrior * (threshPrior1 - tmpFloat1)) +
       1.f);

  // For template spectrum-difference.
  tmpFloat1 = self->featureData[4];
  widthPrior = widthPrior0;
  // Use larger width in tanh map for pause regions.
  if (tmpFloat1 < threshPrior2) {
    widthPrior = widthPrior2;
  }
  // Compute indicator function: sigmoid map.
  indicator2 =
  0.5f * (tanhf(widthPrior * (tmpFloat1 - threshPrior2)) + 1.f);
      //0.5f * ((float)tanh(widthPrior * (tmpFloat1 - threshPrior2)) + 1.f);

  // Combine the indicator function with the feature weights.
  indPrior = weightIndPrior0 * indicator0 + weightIndPrior1 * indicator1 +
             weightIndPrior2 * indicator2;
  // Done with computing indicator function.

  // Compute the prior probability.
  self->priorSpeechProb += PRIOR_UPDATE * (indPrior - self->priorSpeechProb);  // q = inst->priorSpeechProb
  // Make sure probabilities are within range: keep floor to 0.01.
  if (self->priorSpeechProb > 1.f) {
    self->priorSpeechProb = 1.f;
  }
  if (self->priorSpeechProb < 0.01f) {
    self->priorSpeechProb = 0.01f;
  }

  // Final speech probability: combine prior model with LR factor:.
  gainPrior = (1.f - self->priorSpeechProb) / (self->priorSpeechProb + 0.0001f);
  for (i = 0; i < self->magnLen; i++) {
            invLrt = expf(-self->logLrtTimeAvg[i]);
        invLrt = gainPrior * invLrt;
	//invLrt = (float)exp(-self->logLrtTimeAvg[i]);
    //invLrt = (float)gainPrior * invLrt;
    probSpeechFinal[i] = 1.f / (1.f + invLrt);
  }
}
```

## UpdateNoiseEstimate() 噪声估计更新

## WebRtcNs_AnalyzeCore()
计算信噪比函数之前的部分分别是：
1.对输入的时域帧数据进行加窗、FFT变换。
2.然后计算能量，若能量为0，返回；否则继续往下。
3.然后计算新的能量和幅度。
4.使用分位数噪声估计进行初始噪声估计。
5.然后取前50个帧，计算得到高斯白噪声、粉红噪声模型，联合白噪声、粉红噪声模型，得到建模的混合噪声模型。
在噪声抑制模块WebrtcAnalyzeCore中，输入信号经过时频变换后分成三路信号，分别对这三路信号进行计算频谱平坦度、计算信噪比、计算频谱差异。最后将这三个相应的特征值输入到语音/噪声概率更新模板中。该模块具体的流程图以及功能介绍如下：

![Webrtc NS模块算法](https://www.likecs.com/default/index/img?u=aHR0cHM6Ly9waWFuc2hlbi5jb20vaW1hZ2VzLzYzOS9iN2E0YmNhNGRlOGM4YmYwYWE0ZDNhM2FiMTExMmQyZi5wbmc= "Webrtc NS模块算法")
