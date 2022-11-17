# [RNNoise超详细解读](https://zhuanlan.zhihu.com/p/397288851)
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20221007/image.9xxl8f6lpo0.webp)
1.  **SIGNAL MODEL**
作者提出了一种用于噪声抑制的快速算法，在降噪时需要精细调整的部分使用深度学习方法，而其他部分使用传统的DSP方法。使用的窗长为20ms，窗之间的overlap为10ms，噪声抑制的主要部分是将RNN计算出的增益作用于分辨率较低的噪声频谱包络。后面还用pitch filter进行进一步地优化。
**A. band struction**

​ 其他论文中用神经网络直接估计frequency bins需要的网络复杂度较高，从而计算量较大。为了避免此问题，作者假定频谱包络足够平坦，进而可以使用比较粗糙的分辨率。此外，并没有直接计算频谱幅度，而是对理想临界带增益（ideal critical band gains）进行估计。频带划分选择和Opus codec使用的Bark scale相同（实际上为了方便，文章作者直接使用了Opus的pitch计算代码），在低频区，每个频带最少有4个bins，并且使用的是三角频带（滤波）而非矩形频带，每个三角的峰值和其相邻三角的边界点重合。最终band的数量为22，也即网络输出为22个[ 0,1]的值。
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.6y0ig6b2mj40.webp)
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.5k63re2o06o0.webp)
**C. Feature extraction**

​ 前22个特征由22个频带能量做对数变换再做DCT变换得到，也即22个BFCC（Bark-frequency cepstral coefficients）。此外取BFCC的前六个一阶差分和二阶差分作为第23至34个特征，再将前六个基因相关度作为第35至第40个特征。最后两个特征为基音周期（pitch tracking得到的结果）和基音平稳度。因此输入特征一共有42个。

1.  **DEEP LEARNING ARCHITECTURE**

​ 神经网络的结构如下图所示，主要包括三个循环层，作用分别为VAD、噪声谱估计、噪声消除，实验表明，实验表明使用GRU网络的效果优于LSTM网络。

![](https://pic2.zhimg.com/80/v2-13cd25e3f5ec9b54483c205d908b5ce9_720w.jpg)
## 整体计算流程分析

![](https://pic1.zhimg.com/80/v2-a3261d752d239079944f315e935c42e4_720w.jpg)
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.6enaeddup200.webp)
### Pitch analysis

![](https://pic3.zhimg.com/80/v2-9a5eb698e033096bb9a453d95cfff0de_720w.jpg)

语音频谱示意图

​ 上图为一段语音（带噪）的频谱图，如果我们分析对其分析会发现人声有很明显的共振特征（图中高亮条状即为共振峰），这是由于声带振动所产生的。在很短的时间内，声带振动的频率是比较平稳的，也即有一个稳定的基频，pitch analysis的目的就是寻找该基频。因为基频的存在，语音的时域信号在很短的时间窗口内可以认为是有周期性的。如下图所示，对于一条语音，将红线部分放大便得到下面的时域图，可以看出信号在短时间内有很强的周期性。我们将某一个峰值对应的index记为index 0，将其下一个峰值记为index 1，音高追踪（pitch analysis/ pitch tracking）的目的便是得到两个index的差值。

​

![](https://pic2.zhimg.com/80/v2-a74a393f982c2b0a35af3c0c79394e5d_720w.jpg)
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.5mosflnwxpg0.webp)
![](https://pic4.zhimg.com/80/v2-c8ca089d5cf6b1e90c297a7be97ae44b_720w.jpg)
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.19fsr9vdno00.webp)
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.1hw8zdryx8ow.webp)
### 整体流程

![](https://pic3.zhimg.com/80/v2-2edef6416482194bcbe4d6768abbb31e_720w.jpg)

pitch tracking(analysis)流程图

​ 上图为音高追踪的整体流程，首先进行低通滤波和降采样操作，接着对数据求自相关，利用平方最小法进行线性预测分析（LPC analysis）得到线性预测系数（LPC cofficient），将之作用于低通滤波后的信号便得到了LPC残差（residual），此残差便是计算得到的声带原始激励信号。对残差求自相关，然后利用周期检测函数求出index值。
### Feature extraction

​ 特征提取是rnnoise流程中很关键的的一步，送入RNN的数据便是通过这一步获得的，整个特征提取数据流动如下图所示。帧移为10ms，使用采样率为48kHz的音频时，每一帧的新数据长度变为480，即下图中的in，将其与上一次输入的480个点数据拼接得到长度为960的数据，此为一帧。对其做长度为960的傅里叶变换并取前481（代码中此值记作FREQ_SIZE）点数据得到 X。Ex则是利用X求出的22个频带的能量。
![](https://pic4.zhimg.com/80/v2-dfa96f204465e4dc799cb4d70c2d7813_720w.jpg)
### 数据p

​ 上图中有一段长度为1728的数据名为pitch_buf，每次有新数据in进入时，都对其进行更新。对于某一帧数据进行基音追踪得到index，则p=pitch_buf[1728 - WINDOW_SIZE - index : 1728 - WINDOW_SIZE - index]，其中WINDOW_SIZE=960)。即p为长度为960的数据，其最后一个数据为pitch_buf的第1728 - index个数据。同理对p进行傅里叶变换并取FREQ_SIZE个点得到P。
### 频带能量计算
![](https://pic4.zhimg.com/80/v2-3851def9824ddc97bc521ded122a1047_720w.jpg)

三角滤波器组示意图

![](https://pic1.zhimg.com/80/v2-95594725a8cf1f82569d79dbdad435a4_720w.jpg)
如图所示，上面的图展示了完整的22个三角滤波器，下面是前面若干个滤波器放大后的结果。对于每个频带，滤波时，将滤波器的所有点（图中用小圆圈表示）与频域数据x 或 p) 的对应部分的模长平方相乘相加即可，也即论文中的 Eb=wbXk2，同时由上图可以看出，每个滤波器的中间点和上一个滤波器的右端及下一个滤波器的左端对应同一个频点。**此外还需要注意的是，第一个滤波器和最后一个滤波器只有三角形的一半，因而计算这两个频带的能量时需要乘以2。**
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.78n1mhx5llw0.webp)
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.54954l45ivw0.webp)
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.6p1jtibpsow0.webp)
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.77wk3kzbdbk0.webp)
![](https://pic3.zhimg.com/80/v2-e1cc5e4746fac49b35d163e37c361f26_720w.jpg)
## 一些值得注意的问题

### 1. 高频数据消失

![](https://pic3.zhimg.com/80/v2-abf1c65377912fe324953cff4d93990e_720w.jpg)

原带噪语音频谱图

![](https://pic2.zhimg.com/80/v2-712206d63fa53275d5d7548174731189_720w.jpg)

经rnnoise降噪后语音频谱图

​ 如上图所示为某含噪语音频谱及其经过rnnoise降噪后的频谱，在实现降噪的同时，可以看出上面高频区域的数据完全消失，可能的原因如下：观察三角滤波器的图我们不难发现，其最右边的滤波器的频点也只是到了400左右，远远未达到480，因此这后面的高频区域没有被三角滤波器所覆盖。最终的增益插值后，在该部分也全部为0，因而乘以增益后，该部分的频谱即为绝对的0，即为图片所呈现的样子。
# [RNNoise: Learning Noise Suppression（深度学习噪声抑制）（1）](https://blog.csdn.net/dakeboy/article/details/88039977)
![RNN框架](https://img-blog.csdnimg.cn/20190228180603678.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2Rha2Vib3k=,size_16,color_FFFFFF,t_70)
RNNoise使用门控循环单元（GRU），因为它在此任务上执行得比LSTM略好，并且需要更少的资源（CPU和权重的存储容量）。与简单的循环单元相比，GRU有两个额外的门。复位门决定是否将当前状态（记忆）用于计算新状态，而更新门决定当前状态将根据新输入改变多少。这个更新门（关闭时）使得GRU可以长时间地记住信息，这是GRU（和LSTM）比简单的循环单元执行得更好的原因。

![神经网络经典框架](https://img-blog.csdnimg.cn/20190228181058564.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2Rha2Vib3k=,size_16,color_FFFFFF,t_70)
上图将简单的循环单元与GRU进行比较。区别在于GRU的r和z门，这使得有可能学习更长期的模式。两者都是基于整个层的先前状态和输入计算的软开关（0到1之间的值），具有S形激活功能。当更新门z在左边时，状态可以在很长一段时间内保持恒定，直到一个条件使z转向右边。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190228181142758.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2Rha2Vib3k=,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190228181231865.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2Rha2Vib3k=,size_16,color_FFFFFF,t_70)
计算频带增益的优点：首先，它使模型变得非常简单，只需要很少的频带计算。第二，不会产生所谓的音乐噪声伪影（musical noise artifacts），因为在周围被衰减的同时只有单音调能通过。这些伪影在噪声中很常见且很难处理，频带足够宽时，要么让整个频带通过，要么剪掉。**第三个优点来自于如何优化模型。由于增益总是在0和1之间，所以简单地使用S形激活函数（其输出也在0和1之间）来计算它们确保计算方法的正确**，比如不在一开始就引入认为噪声。
分频段计算的缺点是在没有语音的足够分辨率时不能在基频谐波之间很细致的抑制噪声。但是这并不是那么重要，因为可以通过额外的手段来处理，**比如使用一个类似于语音编码增强的后滤波方法：使用梳状滤波器在一个基频周期(pitch period)内消除间谐波噪声(inter-harmonic noise)。**
由于我们计算的输出是基于22个频段的，所以输入频率分辨率更高是没有意义的，因此我们使用相同的22个子带将频谱信息提供给神经网络。**因为音频具有很大的动态范围，所以计算能量的log而不是直接传送能量值**。更进一步，我们使用**这个对数值进行DCT对特征进行去相关。所得到的数据是基于Bark量表的倒谱，其与语音识别中非常常用的梅尔倒谱系数（MFCC）密切相关。**
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190228181459157.png)  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190228181504198.png)
频带结构
纯粹的RNN模型处理8khz语音，计算增益使用了6144个隐藏单元，大概1000万个权重
对于20ms的48khz语音需要400个输出。
使用一个较粗的范围尺度比按照频率尺度计算更有效。选取了音频编码较常使用的bark scale
Ex的计算：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190228181543273.png)
求平方和，并做一次指数平滑，每个频带的增益：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190228181606386.png)
Ex是clean speech，Es是noisy信号，频率尺度的插值增益：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190228181650168.png)
## 训练数据
与语音识别常见的不同，我们选择不将倒谱平均归一化应用于特征，并保留代表能量的第一个倒谱系数。 因此，我们必须确保数据包括所有现实级别的音频。 我们还对音频应用随机滤波器，使系统对各种麦克风频率响应（通常由倒谱均值归一化处理）具有鲁棒性。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190228181810587.png)
Pitch filtering
由于我们的频带的频率分辨率不足，无法滤除音调谐波之间的噪声，所以我们使用基本的信号处理。 这是混合方式的另一部分。当有相同变量的多个测量值时，提高精度（降低噪声）的最简单方法就是计算平均值。显然，只是计算相邻音频样本的平均值不是我们想要的，因为它会导致低通滤波。然而，当信号是周期性的（例如语音）时，我们可以计算由基频周期偏移的采样的平均值。引入梳状滤波器，使基频谐波通过，同时衰减它们之间的频率这是含有噪声的部分。为了避免信号失真，梳状滤波器被独立地应用于每个频带，并且其滤波器强度取决于基频相关性和神经网络计算的频带增益。
我们目前使用FIR滤波器进行pitch filtering，但也可以使用IIR滤波器，如果强度太高，则会导致更高的失真风险，从而产生较大的噪声衰减。
# [RNNoise: Learning Noise Suppression（深度学习噪声抑制）（2）](https://blog.csdn.net/dakeboy/article/details/88065399)
RNNoise分为三层嵌入式网络，由全连接层，GRU网络构成
包含了215个units
4个hidden layers
Largest：96 units

GRU VS LSTM
GRU容易执行去噪任务，需要更少的计算资源，较少参数，训练快
RNN可以对时间序列建模，而噪声抑制需要在时域获得良好的噪声估计。很长时间以来，RNN的能力受到很大的限制，因为它们长期不能保存信息，并且由于当通过时间反向传播时涉及的梯度下降过程是非常低效的（消失的梯度问题）。门控单元（LSTM和GRU）解决了简单RNN不能长期保存信息和梯度消失的问题。与简单RNN相比，GRU有两个额外的门。复位门决定是否将状态（记忆）用于计算新状态，而更新门决定状态将根据新输入改变多少。当更新门关闭时，GRU可以长时间地记住信息。
# [深度学习降噪方案-RNNoise源码解析 - 特征提取](https://blog.csdn.net/danteLiujie/article/details/102799038)
## denoise 训练
![](https://img-blog.csdnimg.cn/20191029143324447.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2RhbnRlTGl1amll,size_16,color_FFFFFF,t_70)
## 特征提取
![](https://img-blog.csdnimg.cn/20191029143324529.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2RhbnRlTGl1amll,size_16,color_FFFFFF,t_70)

# [深度学习降噪方案-RNNoise简介和环境配置](https://blog.csdn.net/danteLiujie/article/details/102769905)
![](https://img-blog.csdnimg.cn/20191027185115916.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2RhbnRlTGl1amll,size_16,color_FFFFFF,t_70)

# 量化
RNNoise 采用8bit量化，具体操作是将权重和偏执限制在-0.5到+0.5之间
这样写data.c时乘以256取整 可以char类型量化 另外在c语言dense中 out应该除以256