[toc]
## AEC   
### [ [深入浅出 WebRTC AEC（声学回声消除）](https://www.cnblogs.com/VideoCloudTech/p/14115848.html)]  
#### 回声的形成

WebRTC 架构中上下行音频信号处理流程如图 1，音频 3A 主要集中在上行的发送端对发送信号依次进行回声消除、降噪以及音量均衡（这里只讨论 AEC 的处理流程，如果是 AECM 的处理流程 ANS 会前置），AGC 会作为压限器作用在接收端对即将播放的音频信号进行限幅。

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/Ua9PWyGDDPjbeE10H7w2JiaqaR5ujiaBZibACp50OF5ITdvglTYUKPguHxVIkpVGyA1gAiaic0Wzp3MoBWbhxYePatQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

**图 1 WebRTC 中音频信号上下行处理流程框图**  
那么回声是怎么形成的呢？

如图 2 所示，A、B 两人在通信的过程中，我们有如下定义：

-   x(n): **远端参考信号**，即 A 端订阅的 B 端音频流，通常作为参考信号；
-   y(n): **回声信号**，即扬声器播放信号 x(n) 后，被麦克风采集到的信号，此时经过房间混响以及麦克风采集的信号 y(n) 已经不能等同于信号 x(n) 了, 我们记**线性叠加**的部分为 y'(n), **非线性叠加的部分**为 y''(n), y(n) = y'(n) + y''(n)；
-   s(n): 麦克风采集的近端说话人的语音信号，即我们真正想提取并发送到远端的信号；
-   v(n)：环境噪音，这部分信号会在 ANS 中被削弱；
-   d(n): **近端信号**，即麦克风采集之后，3A 之前的原始信号，可以表示为：d(n) = s(n) + y(n) + v(n)；
-   s'(n): 3A 之后的音频信号，即准备经过编码发送到对端的信号。

WebRTC 音频引擎能够拿到的已知信号只有近端信号 d(n) 和远端参考信号 x(n)。

![图 2 回声信号生成模型](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163202569-319322703.png)

如果信号经过 A 端音频引擎得到 s'(n) 信号中依然残留信号 y(n)，那么 B 端就能听到自己回声或残留的尾音（回声抑制不彻底留下的残留）。AEC 效果评估在实际情况中可以粗略分为如下几种情况（专业人员可根据应用场景、设备以及单双讲进一步细分）：

![file](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163202835-330302634.jpg)  
####  回声消除的本质  
高保真、低延时、清晰可懂是一直以来追求的目标。在我看来，回声消除，噪声抑制和声源分离同属于语音增强的范畴，如果把噪声理解为广义的噪声三者之间的关系如下图：

![图片](https://mmbiz.qpic.cn/mmbiz_png/Ua9PWyGDDPhqkfIDaRE39RTa1dTXjmxuJCk6wAaSxZn90jEQTVOWrSCoBCktrcVqgicZBJuG0VxeExwluoa1HfQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1 "image.png")  
 **噪声抑制**需要准确估计出噪声信号，其中平稳噪声可以通过语音检测判别有话端与无话端的状态来动态更新噪声信号，进而参与降噪，常用的手段是基于**谱减法**(即在原始信号的基础上减去估计出来的噪声所占的成分)的一系列改进方法，其效果依赖于对噪声信号估计的准确性。对于**非平稳噪声**，目前用的较多的就是基于**递归神经网络的深度学习方法**，很多 Windows 设备上都内置了基于多麦克风阵列的降噪的算法。效果上，为了保证音质，噪声抑制允许噪声残留，只要比原始信号信噪比高，噪且听觉上失真无感知即可。

  

**单声道的声源分离**技术起源于传说中的鸡尾酒会效应，是指人的一种听力选择能力，在这种情况下，注意力集中在某一个人的谈话之中而忽略背景中其他的对话或噪音。该效应揭示了人类听觉系统中令人惊奇的能力，即我们可以在噪声中谈话。科学家们一直在致力于用技术手段从单声道录音中分离出各种成分，一直以来的难点，随着机器学习技术的应用，使得该技术慢慢变成了可能，但是较高的计算复杂度等原因，距离 RTC 这种低延时系统中的商用还是有一些距离。

  

噪声抑制与声源分离都是单源输入，只需要近端采集信号即可，傲娇的回声消除需要同时输入近端信号与远端参考信号。有同学会问已知了远端参考信号，为什么不能用噪声抑制方法处理呢，**直接从频域减掉远端信号的频谱不就可以了吗？**  
![图片](https://mmbiz.qpic.cn/mmbiz_png/Ua9PWyGDDPjbeE10H7w2JiaqaR5ujiaBZibzrJzXgbY532XDFlHn7oNelN1ycibIG5bp8nV4w0AmuBF33LaOljicnyg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

  

上图中第一行为近端信号 s(n)，已经混合了近端人声和扬声器播放出来的远端信号，黄色框中已经标出对齐之后的远端信号，其语音表达的内容一致，**但是频谱和幅度(明显经过扬声器放大之后声音能量很高)均不一致**，意思就是：**参考的远端信号**与**扬声器播放出来的远端信号**已经是“貌合神离”了，与降噪的方法相结合也是不错的思路，但是直接套用降噪的方法显然会造成回声残留与双讲部分严重的抑制。接下来，我们来看看 WebRTC 科学家是怎么做的吧。
####  信号处理流程  
WebRTC AEC 算法包含了**延时调整策略，线性回声估计，非线性回声抑制 3 个部分**。回声消除本质上更像是音源分离，我们期望从混合的近端信号中消除不需要的远端信号，保留近端人声发送到远端，但是 WebRTC 工程师们更倾向于将两个人交流的过程理解为一问一答的交替说话，存在远近端同时连续说话的情况并不多（**即保单讲轻双讲**）。

因此只需要区分远近端说话区域就可以通过一些手段消除绝大多数远端回声，至于双讲恢复能力 WebRTC AEC 算法提供了 {kAecNlpConservative, kAecNlpModerate, kAecNlpAggressive} 3 个模式，由低到高依次代表不同的抑制程度，远近端信号处理流程如图 4：

![图 4 WebRTC AEC 算法结构框图](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163203463-2029556461.png)

**NLMS 自适应算法**（上图中橙色部分）的运用旨在尽可能地消除信号 d(n) 中的**线性部分回声**，而残留的**非线性回声信号会在非线性滤波**（上图中紫色部分）部分中被消除，这两个模块是 Webrtc AEC 的核心模块。模块前后依赖，现实场景中远端信号 x(n) 由扬声器播放出来在被麦克风采集的过程中，同时包含了回声 y(n) 与近端信号 x(n) 的线性叠加和非线性叠加：**需要消除线性回声的目的**是为了**增大近端信号 X(ω) 与滤波结果 E(ω) 之间的差异，计算相干性时差异就越大（近端信号接近 1，而远端信号部分越接近 0），更容易通过门限直接区分近端帧与远端帧。** **非线性滤波部分**中只需要根据检测的**帧类型，调节抑制系数，滤波消除回声即可**。下面我们结合实例分析这套架构中的线性部分与非线性部分。
####  线性滤波
线性回声 y'(n) 可以理解为是远端参考信号 x(n) 经过房间冲击响应之后的结果，线性滤波的本质也就是在估计一组滤波器使得 y'(n) 尽可能的等于 x(n)，通过统计滤波器组的最大幅值位置 index 找到与之对齐远端信号帧，该帧数据会参与相干性计算等后续模块。

需要注意的是，如果 index 在滤波器阶数两端疯狂试探，只能说明当前给到线性部分的远近端延时较小或过大，此时滤波器效果是不稳定的，需要借助固定延时调整或大延时调整使 index 处于一个比较理想的位置。线性部分算法是可以看作是一个固定步长的 NLMS 算法，具体细节大家可以结合源码走读，本节重点讲解线型滤波在整个框架中的作用。

从个人理解来看，线性部分的目的就是最大程度的消除线性回声，为远近端帧判别的时候，最大程度地保证了信号之间的相干值( 0~1 之间，值越大相干性越大)的可靠性。

我们记消除线性回声之后的信号为估计的回声信号 e(n)，e(n) = s(n) + y''(n) + v(n)，其中 y''(n) 为非线性回声信号，记 y'(n) 为线性回声，y(n) = y'(n) + y''(n)。相干性的计算 （Matlab代码）：

```matlab
% WebRtcAec_UpdateCoherenceSpectra →_→ UpdateCoherenceSpectra
Sd = Sd * ptrGCoh(1) + abs(wined_fft_near) .* abs(wined_fft_near)*ptrGCoh(2);
Se = Se * ptrGCoh(1) + abs(wined_fft_echo) .* abs(wined_fft_echo)*ptrGCoh(2);
Sx = Sx * ptrGCoh(1) + max(abs(wined_fft_far) .* abs(wined_fft_far),ones(N+1,1)*MinFarendPSD)*ptrGCoh(2);
Sde = Sde * ptrGCoh(1) + (wined_fft_near .* conj(wined_fft_echo)) *ptrGCoh(2);
Sxd = Sxd * ptrGCoh(1) + (wined_fft_near .* conj(wined_fft_far)) *ptrGCoh(2);     

% WebRtcAec_ComputeCoherence →_→ ComputeCoherence
cohde = (abs(Sde).*abs(Sde))./(Sd.*Se + 1.0e-10);
cohdx = (abs(Sxd).*abs(Sxd))./(Sx.*Sd + 1.0e-10);
```

-   **两个实验**
    

（1）计算近端信号 d(n) 与远端参考信号 x(n) 的相关性 cohdx，理论上远端回声信号的相干性应该更接近 0（为了方便后续对比，WebRTC 做了反向处理: 1 - cohdx），如图 5(a)，第一行为计算近端信号 d(n)，第二行为远端参考信号 x(n)，第三行为二者相干性曲线: 1 - cohdx，会发现回声部分相干值有明显起伏，最大值有0.7，近端部分整体接近 1.0，但是有持续波动，如果想通过一条固定的门限去区分远近端帧，会存在不同程度的误判，反映到听感上就是回声（远端判断成近端）或丢字（近端判断为远端）。

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/Ua9PWyGDDPjbeE10H7w2JiaqaR5ujiaBZibgd4d14EdibDHxudicmdC7bjcLlcr0ia6csH3Ks9uhuqLCmnQRqs8CkQLg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

<center> **(a) 近端信号与远端参考信号的相干性** </center>  

![图片](https://mmbiz.qpic.cn/mmbiz_png/Ua9PWyGDDPjbeE10H7w2JiaqaR5ujiaBZibDibZVFro43FPvySMG5xCbGlHymfyvHabyzBDOibT9UEuodwsprKw5icxA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

<center> **(b) 近端信号与估计的回声信号的相干性**</center>  

<center>** 图 5 信号的相干性** </center>  

（2）计算近端信号 d(n) 与估计的回声信号 e(n) 的相干性，如图 5(b)，第二行为估计的回声信号 e(n)，第三行为二者相干性 cohde，很明显近端的部分几乎全部逼近 1.0，WebRTC 用比较严格的门限（>=0.98）即可将区分绝大部分近端帧，且误判的概率比较小，WebRTC 工程师设置如此严格的门限想必是宁可牺牲一部分双讲效果，也不愿意接受回声残留。  

  

从图 5 可以体会到，线性滤波之后可以进一步凸显远端参考信号 x(n) 与估计的回声信号 e(n) 的差异，从而提高远近端帧状态的判决的可靠性。
-   **存在的问题与改进**
    

理想情况下，远端信号从扬声器播放出来没有非线性失真，那么 e(n) = s(n) + v(n)，但实际情况下 e(n)与d(n) 很像，只是远端区域有一些幅度上的变化，说明 WebRTC AEC **线性部分在这个 case 中表现不佳**，如图 6(a) 从频谱看低频段明显削弱，但中高频部分几乎没变。而利用**变步长的双滤波器结构的结果**会非常明显，如图 6(b) 所示无论是时域波形和频谱与近端信号 x(n) 都有很大差异，目前** aec3 和 speex** 中都采用这种结构，可见 WebRTC AEC 中线性部分还有很大的优化空间。

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/Ua9PWyGDDPjbeE10H7w2JiaqaR5ujiaBZibicic8ltJTfDFQ4wKzOGDjbxhSRM3rCGGu6D23QF9jhia4ibQsVK6pInjGg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

**(a) WebRTC AEC 线性部分输出**   

![图片](https://mmbiz.qpic.cn/mmbiz_png/Ua9PWyGDDPjbeE10H7w2JiaqaR5ujiaBZibicehrjXiaWbsXS5wZm1tiboqcCjlOsibN7tJEkrPj9912lzDVXjian5R6eg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

 **(b) 改进的线性部分输出**

**图 6 近端信号与估计的回声信号的对比**  
**如何衡量改进的线性部分效果？**

这里我们对比了现有的固定步长的 NLMS 和变步长的 NLMS，近端信号 d(n) 为加混响的远端参考信号 x(n) +  近端语音信号 s(n)。理论上 NLMS 在处理这种纯线性叠加的信号时，可以不用非线性部分出马，直接干掉远端回声信号。图 7(a) 第一行为近端信号 d(n)，第二列为远端参考信号 x(n)，线性部分输出结果，黄色框中为远端信号。WebRTC AEC 中采用固定步长的 NLMS 算法收敛较慢，有些许回声残留。但是变步长的 NLMS 收敛较快，回声抑制相对好一些，如图 7(b)。

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/Ua9PWyGDDPjbeE10H7w2JiaqaR5ujiaBZibnxRPO80iabSLyuEkHIPds7gNqicxhJutJm3S3m49WDvia6vwHLjhUQj7A/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

**（a）固定步长的 NLMS**  

![图片](https://mmbiz.qpic.cn/mmbiz_png/Ua9PWyGDDPjbeE10H7w2JiaqaR5ujiaBZib9CexhZjsfz3EIn9ylFPr2N7ibvxusVeuKLA5CDDhWcxkJvnUeF82jJA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

**（b） 变步长的 NLMS**  

     **图 7 两种 NLMS 算法的效果对比**  
	 线性滤波器参数设置

```cpp
#define FRAME_LEN 80
#define PART_LEN 64
enum { kExtendedNumPartitions = 32 };
static const int kNormalNumPartitions = 12;
```

FRAME_LEN 为每次传给音频 3A 模块的数据的长度，默认为** 80 个采样点**，由于 WebRTC AEC 采用了** 128 点 FFT**，内部拼帧逻辑会取出 **PART_LEN = 64 个样本点**与**前一帧剩余数据连接成128点做 FFT**，**剩余的 16 点遗留到下一次**，因此实际每次处理 PART_LEN 个样本点   16k采样率（4ms 数据）。

默认滤波器阶数仅为 kNormalNumPartitions = 12 个，能够覆盖的数据范围为 kNormalNumPartitions * 4ms = 48ms，如果打开扩展滤波器模式(设置 extended_filter_enabled为true)，覆盖数据范围为 kNormalNumPartitions * 4ms = 132ms。随着芯片处理能力的提升，默认会打开这个扩展滤波器模式，甚至扩展为更高的阶数，以此来应对市面上绝大多数的移动设备。另外，线性滤波器虽然不具备调整延时的能力，但可以通过估计的 index 衡量当前信号的延时状态，范围为 [0, kNormalNumPartitions]，如果 index 处于作用域两端，说明真实延时过小或过大，会影响线性回声估计的效果，严重的会带来回声，此时需要结合固定延时与大延时检测来修正。	
#### 非线性滤波

非线性部分一共做了两件事，就是想尽千方百计干掉远端信号。

**(1) 根据线性部分提供的估计的回声信号，计算信号间的相干性，判别远近端帧状态。**

**(2) 调整抑制系数，计算非线性滤波参数。**

非线性滤波抑制系数为 hNl，大致表征着估计的回声信号 e(n) 中，期望的近端成分与残留的非线性回声信号 y''(n) 在不同频带上的能量比，hNl 是与相干值是一致的，范围是 [0，1.0]，通过图 5(b) 可以看出需要消除的远端部分幅度值也普遍在 0.5 左右，如果直接使用 hNl 滤波会导致大量的回声残留。

因此 WebRTC 工程师对 hNl 做了如下尺度变换，over_drive 与 nlp_mode 相关，代表不同的抑制激进程度，drive_curve 是一条单调递增的凸曲线，范围 [1.0, 2.0]。由于中高频的尾音在听感上比较明显，所以他们设计了这样的抑制曲线来抑制高频尾音。我们记尺度变换的 α = over_drive_scaling * drive_curve，如果设置 nlp_mode = kAecNlpAggressive，α 大约会在 30 左右。  

如果当前帧为近端帧（即 echo_state = false），假设第 k 个频带 hNl(k) = 0.99994 ，hNl(k) = hNl(k)^α = 0.99994 ^ 30 = 0.9982，即使滤波后的损失听感上几乎无感知。如图 8(a)，hNl 经过 α 调制之后，幅值依然很接近 1.0。

如果当前帧为远端帧（即 echo_state = true），假设第 k 个频带 hNl(k) = 0.6676 ，hNl(k) = hNl(k)^α = 0.6676 ^ 30 = 5.4386e-06，滤波后远端能量小到基本听不到了。如图 8(b)，hNl 经过 α 调制之后，基本接近 0。

![（a）近端帧对应的抑制系数](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163204850-769490395.png)

![（b）远端帧对应的抑制系数](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163205013-1835270388.png)

图 8 远近端信号抑制系数在调制前后的变化

经过如上对比，为了保证经过调制之后近端期望信号失真最小，远端回声可以被抑制到不可听，WebRTC AEC 才在远近端帧状态判断的的模块中设置了如此严格的门限。

另外，调整系数 α 过于严格的情况下会带来双讲的抑制，如图 9 第 1 行，近端说话人声音明显丢失，通过调整 α 后得以恢复，如第 2 行所示。因此如果在 WebRTC AEC 现有策略上优化 α 估计，可以缓解双讲抑制严重的问题。

![图 9 双讲效果](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163205211-1030552581.png)  
####  延时调整策略

回声消除的效果与**远近端数据延时强相关**，调整不当会带来算法不可用的风险。在远近端数据进入线性部分之前，一定要**保证延时在设计的滤波器阶数范围内**，不然**延时过大超出了线性滤波器估计的范围**或**调整过当导致远近端非因果**都会造成无法收敛的回声。先科普两个问题：  
##### （1）为什么会存在延时？	

首先近端信号 d(n) 中的回声是扬声器播放远端参考 x(n)，又被麦克风采集到的形成的，也就意味着在近端数据还未采集进来之前，远端数据缓冲区中已经躺着 N 帧 x(n)了，这个天然的延时可以约等于音频信号从准备渲染到被麦克风采集到的时间，不同设备这个延时是不等的。苹果设备延时较小，基本在 120ms 左右，Android 设备普遍在 200ms 左右，低端机型上会有 300ms 左右甚至以上。
##### （2）远近端非因果为什么会导致回声？

从（1）中可以认为，正常情况下当前帧近端信号为了找到与之对齐的远端信号，必须在远端缓冲区沿着写指针向前查找。如果此时设备采集丢数据，远端数据会迅速消耗，导致新来的近端帧在向前查找时，已经找不到与之对齐的远端参考帧了，会导致后续各模块工作异常。如图 10(a) 表示正常延时情况，(b) 表示非因果。

**非因果就是远端参考信号落后于近端信号**

![（a）远近端正常延时](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163205420-340788594.png)

![（b）远近端非因果](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163205646-1709962344.png)

图10 正常远近端延时与非因果  
WebRTC AEC 中的延时调整策略关键而且复杂，涉及到**固定延时调整，大延时检测，以及线性滤波器延时估计**。三者的关系如下：

① **固定延时调整**只会发生在开始 AEC 算法开始处理之前，而且仅调整一次。如会议盒子等固定的硬件设备延时基本是固定的，可以通过直接减去固定的延时的方法缩小延时估计范围，使之快速来到滤波器覆盖的延时范围之内。  
下面结合代码来看看固定延时的调整过程：  
```cpp
int32_t WebRtcAec_Process(void* aecInst,
const float* const* nearend,
size_t num_bands,
float* const* out,
size_t nrOfSamples,
int16_t reported_delay_ms,
int32_t skew);
```

WebRtcAec_Process 接口如上，**参数 reported_delay_ms 为当前设备需要调整延时的目标值**。如某 Android 设备固定延时为 400ms 左右，400ms 已经超出滤波器覆盖的延时范围，至少需要调整 300ms 延时，才能满足回声消除没有回声的要求。固定延时调整在 WebRTC AEC 算法开始之初仅作用一次：

```rust
if (self->startup_phase) {
    int startup_size_ms = reported_delay_ms < kFixedDelayMs ? kFixedDelayMs : reported_delay_ms;
    int target_delay = startup_size_ms * self->rate_factor * 8;
    int overhead_elements = (WebRtcAec_system_delay_aliyun(self->aec) - target_delay) / PART_LEN;
    printf("[audio] target_delay = %d, startup_size_ms = %d, self->rate_factor = %d, sysdelay = %d, overhead_elements = %d\n", target_delay, startup_size_ms, self->rate_factor, WebRtcAec_system_delay(self->aec), overhead_elements);
    WebRtcAec_AdjustFarendBufferSizeAndSystemDelay_aliyun(self->aec,  overhead_elements);
self->startup_phase = 0;
  }
```

**为什么 target_delay 是这么计算？** 
**没看懂**
int target_delay = startup_size_ms * self->rate_factor * 8;  
startup_size_ms 其实就是设置下去的 reported_delay_ms，这一步将计算时间毫秒转化为样本点数。16000hz 采样中，10ms 表示 160 个样本点，因此 target_delay 实际就是需要调整的目标样本点数（aecpc->rate_factor = aecpc->splitSampFreq / 8000 = 2）。

我们用 330ms 延时的数据测试：  
如果设置默认延时为 240ms，overhead_elements 第一次被调整了 -60 个 block，**相当于一个block长度 PART_LEN = 64 个样本点 即4ms** 负值表示向前查找，正好为 60 * 4 = 240ms，之后线性滤波器固定 index = 24，表示 24 * 4 = 96ms 延时，二者之和约等于 330ms。日志打印如下：

![file](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163205822-452311395.png)

② 大延时检测是基于远近端数据相似性在远端大缓存中查找最相似的帧的过程，其算法原理有点类似音频指纹中特征匹配的思想。大延时调整的能力是对固定延时调整与线型滤波器能力的补充，使用它的时候需要比较慎重，需要控制调整的频率，以及控制造成非因果的风险。

WebRTC AEC 算法中开辟了可存储 250 个 block 大缓冲区，**每个 block 的长度 PART_LEN = 64 个样本点**，能够保存最新的 1s 的数据，这也是理论上的大延时能够估计的范围，绝对够用了。

```cpp
static const size_t kBufferSizeBlocks = 250;
buffer_ = WebRtc_CreateBuffer(kBufferSizeBlocks, sizeof(float) * PART_LEN);
aec->delay_agnostic_enabled = 1;
```

我们用 610ms 延时的数据测试(启用大延时调整需要设置 delay_agnostic_enabled = 1)：  
我们还是设置默认延时为 240ms，刚开始还是调整了 -60 个 block，随后大延时调整接入之后有调整了 -88 个 block，一共调整(60 + 88) * 4 = 592ms，之后线性滤波器固定 index = 4，表示最后剩余延时剩余 16ms，符合预期。

![file](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163205998-1216114321.png)

![file](https://img2020.cnblogs.com/other/2200703/202012/2200703-20201210163206152-1781028975.png)

③ 线性滤波器延时估计是固定延时调整和大延时调整之后，滤波器对当前远近端延时的最直接反馈。前两者调整不当会造成延时过小甚至非因果，或延时过大超出滤波器覆盖能力，导致无法收敛的回声。因此前两者在调整的过程中需要结合滤波器的能力，确保剩余延时在滤波器能够覆盖的范围之内，即使延时小范围抖动，线性部分也能自适应调整。

#### 总结与优化方向

WebRTC AEC 存在的问题：

（1）**线性部分收敛时间较慢**，**固定步长的 NLMS 算法**对线性部分回声的估计欠佳；  
（2）线性部分滤波器阶数默认为 32 阶，默认覆盖延时 132ms，**对移动端延时较大设备支持不是很好**，**大延时检测部分介入较慢**，且存在误调导致非因果回声的风险；  
（3）基于**相干性的帧状态依赖严格的固定门限**，存在一定程度的误判，如果再去指导非线性部分抑制系数的调节，会带来比较严重的**双讲抑制**。

优化的方向：  
（1）算法上可以通过学习** speex 和 AEC3** 的线性部分，改善当前线性滤波效果；  
（2）算法上可以**优化延时调整策略**，工程上可以**新增参数配置下发等**工程手段解决一些设备的延时问题；  
（3）另外，有一些新的思路也是值得我们尝试的，如开头提到的，既然回声也可以是视为噪声，那么能否用降噪的思路做回声消除呢，答案是可以的。


# [声学回声消除(Acoustic Echo Cancellation)原理与实现](https://www.cnblogs.com/LXP-Never/p/11703440.html)  
## 声学回声

　　在麦克风与扬声器互相作用影响的双工通信系统中极易产生声学回声。如下图所示

远端讲话者-->远端麦克风-->通话网络---->近端扬声器--->近端麦克风-->通话网络-->远端扬声器--->远端麦克风--->远端电话-->近端电话---->......就这样无限循环，

**详细讲解：**远端讲话者的声音被远端麦克风采集并传入通信设备，经过无线或有线传输之后达到近端的通信设备，并通过近端扬声器播放，这个声音又会被近端麦克风采集形成声学回声，经传输又返回到远端的通信设备，并通过远端扬声器播放出来，从而远端讲话者就听到了自己的回声。

![](https://img2020.cnblogs.com/blog/1433301/202012/1433301-20201230073644218-653313392.png)

声学回声产生原理

**远端语音信号**：被远端麦克风采集的信号（说话人语音），也等于近端扬声器播放的语音，也称为参考语音

![](https://img2020.cnblogs.com/blog/1433301/202012/1433301-20201215115722027-201641617.png)

**近端语音信号**：近端说话人语音信号  

![](https://img2020.cnblogs.com/blog/1433301/202012/1433301-20201215120343507-1033301706.png)

**近端麦克风接收的语音信号**：近端扬声器播放的声音**+**在房间多径反射的语音**+**近端说话人的语音

![](https://img2020.cnblogs.com/blog/1433301/202012/1433301-20201215120233108-2069676962.png)

**远端混合回声信号**：整个对话过程中，近端麦克风接收到的信号有近端说话人语音信号和近端扬声器播放的远端说话人语音，这样叠加的语音信号通过传输线路传到远端扬声器播放导致远端人听到自己刚刚检测出的语音信号，即所谓的回声。

![](https://img2020.cnblogs.com/blog/1433301/202012/1433301-20201215120047497-168758559.png)
声学回声信号根据传输途径的差别可以分别**直接回声**信号和**间接回声**信号。

-   **直接回声（线性回声）**：近端扬声器将语音信号播放出来后，被近端麦克风直接采集后得到的回声；直接回声不受环境的印象，与扬声器到麦克风的距离及位置有很大的关系，因此直接回声是一种**线性信号**。
-   **间接回声（非线性回声）**：近端扬声器将语音信号播放出来后，语音信号经过复杂多变的墙面反射后由近端麦克风采集；间接回声的大小与房间环境、物品摆放以及墙面吸引系数等等因素有关，因此间接回声是一种**非线性信号**。
-   一个完整的回声消除系统，包含以下几个模块：

1.  **时延估计（Time Delay Estimation, TDE）** 模块
2.  **(线性)回声消除（Linear **Acoustic**  Echo Cancellation, AEC）** 模块
3.  **双讲检测（Double-Talk Detect, DTD）** 模块
4.  **非线性残余声学回声抑制（Residual Acoustic Echo Suppression, RAES）** 模块

![](https://img2020.cnblogs.com/blog/1433301/202104/1433301-20210410112425375-883346308.jpg)

滤波器有**两种状态**：

-   **滤波**：y^(n)=x(n)∗w^(n)，e(n)=d(n)−y^(n)
-   **自适应滤波器系数更新(NLMS)**：w^(n+1)=w^(n)+μe(n)x(n)xT(n)x(n)

自适应滤波器有**三种工作模式**（通过DTD双讲检测）：

-   **远端语音存在，近端语音不存在**：滤波、自适应滤波器系数更新
-   **远端语音存在，近端语音存在**：滤波
-   **远端语音不存在**：什么都不用做  
-   > 使用**自适应滤波算法**调整滤波器的权值向量，**估计一个近似的回声路径**来逼近真实回声路径，从而得到**估计的回声信号**，并在纯净语音和回声的混合信号中除去此信号来实现回声的消除。

![](https://img2020.cnblogs.com/blog/1433301/202104/1433301-20210410144224272-493817801.jpg)

 AEC的基本原理

　　x(n)为远端语音，经过未知的回声路径w(n)得到远端回声语音y(n)=x(n)∗w(n)，再加上近端语音s(n)，得到期望信号d(n)=y(n)+s(n)。x(n)通过自适应滤波器w^(n)得到估计的回声信号y^(n)，并与期望信号d(n)相减得到误差信号e(n)=d(n)−y^(n)，误差信号的值越小说明自适应滤波算法所估计的回声路径就越接近实际的回声路径。

　　滤波器采用特定的自适应算法不停地调整权值向量，使估计的回声路径w^(n)逐渐趋近于真实回声路径w(n)。显然，在 AEC 问题中，**自适应滤波器的选择**对回声消除的性能好坏起着十分关键的作用。接下来将介绍几种解决 AEC 问题的经典自适应滤波算法。	
  ## FLMS(频域LMS)

不论是webRTC还是speex开源的AEC算法都是基于频域来做的。**之所以放在频域而非时域实现的主要原因实时性**，在16kHz采样率的情况下，屋子里的回声持续时间长达0.1~0.5秒（多次反射），这就要求**自适应滤波器的抽头数达到8000之多**，工程上在考虑到计算量和延迟因素时基本都选择在频域实现。 FLMS（Fast LMS）的基本思想是将时域块LMS放到频域来计算。利用FFT算法在频域上完成滤波器系数的自适应。快速卷积算法用重叠相加法和重叠存储法。重叠相加法是将长序列分成大小相等的短片段，分别对各个端片段做FFT变换，再将变换重叠的部分相加构成最终FFT结果，重叠存储法在分段时，各个短的段之间存在重叠，对各个段进行FFT变换，最后将FFT变换得结果直接相加即得最终变换结果。当块的大小和权值个数相等时，运算效率达到最高。

![aec](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/aec.79h9ujhlh680.webp)

# [WebRTC AEC 流程解析](https://juejin.cn/post/7105607322604404767)
## I. Introduction

回声消除的简单原理前面已经有介绍过了，可以有参考[解析自适应滤波回声消除](https://link.juejin.cn?target=https%3A%2F%2Flink.zhihu.com%2F%3Ftarget%3Dhttp%253A%2F%2Fmp.weixin.qq.com%2Fs%253F__biz%253DMzA3MjEyMjEwNA%253D%253D%2526mid%253D2247484312%2526idx%253D1%2526sn%253Dafa00c2fb91f72bdfd73fc99f0efede0%2526chksm%253D9f22680fa855e119cdc2fc2c6a4ddb646bf2adff27010a6c0c16383b687c0104fc3d9561c0ef%2526scene%253D21%2523wechat_redirect "https://link.zhihu.com/?target=http%3A//mp.weixin.qq.com/s%3F__biz%3DMzA3MjEyMjEwNA%3D%3D%26mid%3D2247484312%26idx%3D1%26sn%3Dafa00c2fb91f72bdfd73fc99f0efede0%26chksm%3D9f22680fa855e119cdc2fc2c6a4ddb646bf2adff27010a6c0c16383b687c0104fc3d9561c0ef%26scene%3D21%23wechat_redirect")和[基于卡尔曼滤波器的回声消除算法](https://link.juejin.cn?target=https%3A%2F%2Flink.zhihu.com%2F%3Ftarget%3Dhttp%253A%2F%2Fmp.weixin.qq.com%2Fs%253F__biz%253DMzA3MjEyMjEwNA%253D%253D%2526mid%253D2247484999%2526idx%253D1%2526sn%253D4bad80ad016cae43b0adcead513e28f6%2526chksm%253D9f226dd0a855e4c6fd0af54380225f1269e9760043d9c4ff15880d623c25f223ccc3e864db35%2526scene%253D21%2523wechat_redirect "https://link.zhihu.com/?target=http%3A//mp.weixin.qq.com/s%3F__biz%3DMzA3MjEyMjEwNA%3D%3D%26mid%3D2247484999%26idx%3D1%26sn%3D4bad80ad016cae43b0adcead513e28f6%26chksm%3D9f226dd0a855e4c6fd0af54380225f1269e9760043d9c4ff15880d623c25f223ccc3e864db35%26scene%3D21%23wechat_redirect")。WebRTC AEC的时延估计使用了频域自相关的方法。线性部分采用了分块频域自适应滤波器(Partitioned Block Frequency Domain Adaptive Filter, PBFDAF)，这个滤波器在Speex中称为分块频域波器（Multidelayblock frequency Filter，MDF）, 其实它们原理是一样的。有所不同的是Speex的AEC使用了两个滤波器(前景滤波器和背景滤波器)因此其线性回声消除部分性能更好一点，但是AEC3也引入了两个滤波器，这里就不展开讲了后面有机会再介绍。最后通过计算近端信号、误差信号和远端信号的频域相关性来进行的非线性处理（NonLinearProcessing, NLP）。

WebRTC AEC的流程和其他算法类似，首先我们要create一个实例。

```arduino
int32_t WebRtcAec_Create(void** aecInst)
```
在上面这个函数中我们创建AEC的实例和重采样的实例。

```java
int WebRtcAec_CreateAec(AecCore** aecInst) 
int WebRtcAec_CreateResampler(void** resampInst)
复制代码
```

在WebRtcAec_CreateAec中会开辟一些buffer，包括近端/远端/输出/延迟估计等。值得一提的是，WebRTC AEC的buffer结构体定义如下，我们可以发现除了数据之外还有一些记录位置的变量。

```arduino
struct RingBuffer {
  size_t read_pos;
  size_t write_pos;
  size_t element_count;
  size_t element_size;
  enum Wrap rw_wrap;
  char* data;
};
复制代码
```

其中近端和输出的buffer大小一样(FRAME_LEN:80, PART_LEN:64)

```ini
aec->nearFrBuf = WebRtc_CreateBuffer(FRAME_LEN + PART_LEN, sizeof(int16_t));
aec->outFrBuf = WebRtc_CreateBuffer(FRAME_LEN + PART_LEN, sizeof(int16_t));
复制代码
```

远端buffer要大一点(kBufSizePartitions:250, PART_LEN1:64+1)

```ini
aec->far_buf = WebRtc_CreateBuffer(kBufSizePartitions, sizeof(float) * 2 * PART_LEN1);
aec->far_buf_windowed = WebRtc_CreateBuffer(kBufSizePartitions, sizeof(float) * 2 * PART_LEN1);
复制代码
```

有关时延估计的内容也会在这里初始化。

```arduino
void* WebRtc_CreateDelayEstimatorFarend(int spectrum_size, int history_size) 
void* WebRtc_CreateDelayEstimator(void* farend_handle, int lookahead)
复制代码
```

接下来是初始化，这里有两个采样率一个是原始的采样率，另一个是重采样后的采样率。原始采样率只支持8k/16k/32kHz, 重采样的采样率为1—96kHz。

```arduino
int32_t WebRtcAec_Init(void* aecInst, int32_t sampFreq, int32_t scSampFreq)
复制代码
```

在下面这个函数会根据原始采样率设置对应参数，并初始WebRtcAec_Create开辟的各种buffer空间和各种参数变量以及FFT计算的初始化。

```scss
WebRtcAec_InitAec(AecCore* aec, int sampFreq)
复制代码
```

由于涉及到重采样，需要初始化重采样相关内容，可以发现重采样在WebRTC多个算法中均有出现。

```java
int WebRtcAec_InitResampler(void* resampInst, int deviceSampleRateHz)
复制代码
```

最后是参数设定，WebRTC AEC的配置结构体如下

```arduino
typedef struct {
  int16_t nlpMode;      // default kAecNlpModerate
  int16_t skewMode;     // default kAecFalse
  int16_t metricsMode;  // default kAecFalse
  int delay_logging;    // default kAecFalse
} AecConfig;
复制代码
```

在初始化过程中，它们被默认配置为如下参数

```ini
  aecConfig.nlpMode = kAecNlpModerate;
  aecConfig.skewMode = kAecFalse;
  aecConfig.metricsMode = kAecFalse;
  aecConfig.delay_logging = kAecFalse;
复制代码
```

可以通过WebRtcAec_set_config来设定各种参数。

```arduino
int WebRtcAec_set_config(void* handle, AecConfig config)
复制代码
```

在处理每一帧时，WebRTC AEC会首先把远端信号放入buffer中

```arduino
int32_t WebRtcAec_BufferFarend(void* aecInst,
                               const int16_t* farend,
                               int16_t nrOfSamples)
复制代码
```

如果需要重采样，会在这个函数内部调用重采样函数，aec的重采样非常简单直接线形插值处理，并没有接镜像抑制滤波器。这里的skew好像是对44.1 and 44 kHz 这种奇葩采样率的时钟补偿（更细节可以参考[4]）。

```arduino
void WebRtcAec_ResampleLinear(void* resampInst,
                              const short* inspeech,
                              int size,
                              float skew,
                              short* outspeech,
                              int* size_out)
复制代码
```

当far end的buffer有足够多的数据时，进行FFT计算，这里会计算两次，一次是加窗的一次是不加窗的，窗函数带来的影响可以参考[分帧，加窗和DFT](https://link.juejin.cn?target=https%3A%2F%2Flink.zhihu.com%2F%3Ftarget%3Dhttp%253A%2F%2Fmp.weixin.qq.com%2Fs%253F__biz%253DMzA3MjEyMjEwNA%253D%253D%2526mid%253D2247484741%2526idx%253D1%2526sn%253D1e3ebd6d9a0da6879433bf795677006e%2526chksm%253D9f226ed2a855e7c430c53d22b8bd781fde59d6e4760376fcb94708bd8295199a1100971d754a%2526scene%253D21%2523wechat_redirect "https://link.zhihu.com/?target=http%3A//mp.weixin.qq.com/s%3F__biz%3DMzA3MjEyMjEwNA%3D%3D%26mid%3D2247484741%26idx%3D1%26sn%3D1e3ebd6d9a0da6879433bf795677006e%26chksm%3D9f226ed2a855e7c430c53d22b8bd781fde59d6e4760376fcb94708bd8295199a1100971d754a%26scene%3D21%23wechat_redirect")。

```arduino
void WebRtcAec_BufferFarendPartition(AecCore* aec, const float* farend)
复制代码
```

## II. Delay Estimation

在软件层面由于各种原因会导致麦克风收到的近端信号与网络传输的远端信号并不是对齐的，当近端信号和远端信号的延迟较大时就不得不使用较长的线性滤波器来处理，这无疑增加了计算量。如果我们能将近端信号和远端信号对齐，那么就可以减少滤波器的系数从而减少算法开销。

然后运行处理函数,其中msInSndCardBuf就是声卡实际输入和输出之间的时间差，即本地音频和消去参考音频之间的错位时间。对于8kHz和16kHz采样率的音频数据在使用时可以不管高频部分，只需要传入低频数据即可，但是对大于32kHz采样率的数据就必须通过滤波接口将数据分为高频和低频传入这就是nearend和nearendH的作用。

```arduino
int32_t WebRtcAec_Process(void* aecInst,
                          const int16_t* nearend,
                          const int16_t* nearendH,
                          int16_t* out,
                          int16_t* outH,
                          int16_t nrOfSamples,
                          int16_t msInSndCardBuf,
                          int32_t skew)
复制代码
```

首先要进行一些判断，确定函数输入的参数是有效的，然后会根据这个变量的值extended_filter_enabled来确定是否使用extend模式，两种模式划分数目以及处理方式都有所不同。

```ini
enum {
  kExtendedNumPartitions = 32
};
static const int kNormalNumPartitions = 12;
复制代码
```

如果使用extended模式需要人为设定延时(reported_delay_ms)

```arduino
static void ProcessExtended(aecpc_t* self,
                            const int16_t* near,
                            const int16_t* near_high,
                            int16_t* out,
                            int16_t* out_high,
                            int16_t num_samples,
                            int16_t reported_delay_ms,
                            int32_t skew) 
复制代码
```

将延时转为采样点数后移动远端buffer指针，然后对delay进行筛选和过滤。

```java
int WebRtcAec_MoveFarReadPtr(AecCore* aec, int elements)
static void EstBufDelayExtended(aecpc_t* self)
复制代码
```

如果使用normal模式

```arduino
static int ProcessNormal(aecpc_t* aecpc,
                         const int16_t* nearend,
                         const int16_t* nearendH,
                         int16_t* out,
                         int16_t* outH,
                         int16_t nrOfSamples,
                         int16_t msInSndCardBuf,
                         int32_t skew)
复制代码
```

会有一个startup_phase的过程，当系统延迟处于稳定状态后，这个过程结束，AEC才会生效。AEC生效后首先进行对时延估计buffer, delay进行筛选和过滤。

```arduino
static void EstBufDelayNormal(aecpc_t* aecpc) 
复制代码
```

接着就进入AEC的处理环节

```arduino
void WebRtcAec_ProcessFrame(AecCore* aec,
                            const short* nearend,
                            const short* nearendH,
                            int knownDelay,
                            int16_t* out,
                            int16_t* outH)
复制代码
```

代码里面有很明确的注释，解释了AEC核心步骤

```vbnet
   For each frame the process is as follows:
   1) If the system_delay indicates on being too small for processing a
      frame we stuff the buffer with enough data for 10 ms.
   2) Adjust the buffer to the system delay, by moving the read pointer.
   3) TODO(bjornv): Investigate if we need to add this:
      If we can't move read pointer due to buffer size limitations we
      flush/stuff the buffer.
   4) Process as many partitions as possible.
   5) Update the |system_delay| with respect to a full frame of FRAME_LEN
      samples. Even though we will have data left to process (we work with
      partitions) we consider updating a whole frame, since that's the
      amount of data we input and output in audio_processing.
   6) Update the outputs.
复制代码
```

我们直接看处理模块，即步骤4

```java
static void ProcessBlock(AecCore* aec)
复制代码
```

首先记住这三个变量分别是近端信号、远端信号和误差信号。

```css
d[PART_LEN], y[PART_LEN], e[PART_LEN]
复制代码
```

第一步会进行舒适噪声的噪声功率谱估计和平滑，接着就是延迟估计了。
** 我们那个项目在dsp上可以不用延时估计，在代码中找到将那段注释掉
```cpp
if (aec->delay_logging_enabled) {
    int delay_estimate = 0;
    /*if (WebRtc_AddFarSpectrumFloat(
            aec->delay_estimator_farend, abs_far_spectrum, PART_LEN1) == 0) {
      delay_estimate = WebRtc_DelayEstimatorProcessFloat(
          aec->delay_estimator, abs_near_spectrum, PART_LEN1);
      if (delay_estimate >= 0) {
        // Update delay estimate buffer.
        aec->delay_histogram[delay_estimate]++;
      }
    }*/  将上面那段注释，相当于延时为0
  }
```

```java
int WebRtc_DelayEstimatorProcessFloat(void* handle,
                                      float* near_spectrum,
                                      int spectrum_size)
复制代码
```

其算法原理如下表所示,

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/80bbc4cc35444f6cb07667fd18a37c30~tplv-k3u1fbpfcp-zoom-in-crop-mark:3024:0:0:0.awebp)​

首先根据远端信号和近端信号的功率谱计算子带振幅与阈值之间的关系得到二元谱，这样便得到了远端和近端信号二值化的频谱。

```arduino
static uint32_t BinarySpectrumFloat(float* spectrum,
                                    SpectrumType* threshold_spectrum,
                                    int* threshold_initialized)
复制代码
```

然后通过求解两者的按位异或值，选择相似度最高的候选远端信号并计算对应的延时。

```arduino
int WebRtc_ProcessBinarySpectrum(BinaryDelayEstimator* self,
                                 uint32_t binary_near_spectrum) 
复制代码
```

## III. PBFDAF

接下来就是NLMS的部分了，其整体流程如下图所示：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8eb363bd03f04165aef2fd652a23646b~tplv-k3u1fbpfcp-zoom-in-crop-mark:3024:0:0:0.awebp)​

PBFDAF的每一步都可以在上图中找到对应的流程，首先实现远端频域滤波，然后对结果进行IFFT运算，缩放后减去近端信号得到时域误差

```java
static void FilterFar(AecCore* aec, float yf[2][PART_LEN1])
复制代码
```

接着对误差信号进行FFT变换并归一化误差信号

```java
static void ScaleErrorSignal(AecCore* aec, float ef[2][PART_LEN1])
复制代码
```

最后经过了FFT/IFFT，把一半数值置零等操作，在频域更新滤波器权重。

```java
static void FilterAdaptation(AecCore* aec, float* fft, float ef[2][PART_LEN1])
复制代码
```

## IV. NLP

NLMS是线性滤波器并不能消除所有的回声，因为回声的路径不一定是非线性的，因此需要非线性处理来消除这些残余的回声，其基本原理就是信号的频域相干性：近端信号和误差信号的相似度高则不需要进行处理，远端信号和近端信号相似度高则需要进行处理，其中非线性体现在处理是使用指数衰减。WebRTC AEC的NLP处理在这个函数中

```java
static void NonLinearProcessing(AecCore* aec, short* output, short* outputH)
复制代码
```

首先计算近端远端误差信号的功率谱，然后计算他们的互功率谱，从而计算近端-误差子带相干性、远端-近端子带相干性。接着得出平均相干性，估计回声状态，计算抑制因子然后进行非线性处理。

```arduino
static void OverdriveAndSuppress(AecCore* aec,
                                 float hNl[PART_LEN1],
                                 const float hNlFb,
                                 float efw[2][PART_LEN1])
复制代码
```

最后加上舒适噪声后进行IFFT，然后overlap and add得到最终的输出。

```arduino
static void ComfortNoise(AecCore* aec,
                         float efw[2][PART_LEN1],
                         complex_t* comfortNoiseHband,
                         const float* noisePow,
                         const float* lambda)
```

  
# 论文总结
## 时延估计
WebRTC 中AEC 的延时对齐算法用的是Bastiaan 等人的一篇专利，这个算法复
杂度低，稳定性好，是十分经典的算法。
传统的延时估计都直接或间接的利用互相关函数，这种算法主要有三个缺点。
(1) 计算复杂度较高，尤其是当延时较大的时候，算法需在较宽的范围内进行搜索；
(2) 当远端信号和回声之间不是线性关系，即回声路径受到非线性干扰时，算法的
准确性降低；
(3) 若系统时延是变化的，算法很难在旧的延迟和新的延迟间进行决策。
Bastiaan 的专利可以在很大程度上解决上述问题，它的方案是基于参考信号和接收
信号间联合概率的概念，并以此建立测量时间延迟的函数。在这一方案中，可以使用任
何合适的量来度量参考信号和接收信号，比如瞬时能量或平均能量。
实际中，需设置阈值对信号进行量化，
超过这个阈值时，将信号**量化**为1，表示信号强度较高；低于这个阈值时，量化为0，
表示信号强度较低。这样，远端信号和近端信号有四种可能的共现量化值：(0,0),(0,1),(1,0)
和(1,1)。其中，(0,1)表示远端信号强度较低而近端信号强度较高；(0,0)表示两端信号强
度都较低；(1,1)表示两端信号强度都较高。类似的数值对可以在两端同时测量，也可以
将一端经过一定时延后再测量。
现在单独考虑数值对(1,0)。假设远端信号和近端信号之间没有延迟，则表示远端信
号强度较高、近端信号强度较低的数值对(1,0)不可能出现，因为远端信号传过来的回声
会提高近端信号的强度。在实际环境中，这意味着(1,0)共现的概率很低。现在假设两端
信号之间延迟为D，D为一个非零常数，此时同时对两端信号进行测量，则很有可能出
现(1,0)。然而，有理由认为，**如果对两端信号进行延时补偿，当补偿值为D或一个接近
D的值时，(1,0)共现的概率会大大降低；** 如果**补偿值与D相差较大，则(1,0)共现的概率
会增加**。这样，通过统计不同延时下(1,0)共现的次数，就可以比较准确的找到时延。这
个算法，最简单的方案就是**找出(1,0)共现概率最低的时延**，将其作为真正时延。考虑实
际环境的复杂性，为了使算法有更好的性能，可以考虑其他的数值对的共现概率。
在单独考虑了数值对(1,0)之后，可以进一步优化算法。尽管每个数值对出现的频率
并不确定，但是可以依据经验为每一个数值对分配一个权重。比如上述讨论的情况，合
理的做法是，为数值对(0,0),(0,1)和(1,1)分配权重1，而为数值对(1,0)分配权重0，然后
将其保存在一个表格中。定义一系列合理的候选延迟后，选择其中一个候选延迟，将二
进制流按照此延迟对齐，然后计算出各类数值对，并从表格中读出相应权重进行求和。
这样，每个候选延迟都对应一个权重和，对权重和求平均，其值最小的则为最优延迟。
对每一个信号值和每个时间间隔计算周期图，在时间间隔Tp中，x(n)的周期图是非负的实数矢量𝜺𝑝=(𝜀1,𝑝,𝜀2,𝑝,𝜀3,𝑝….𝜀𝑄,𝑝)，其值计算如下：
𝜀𝑞,𝑝= ∫|∫𝑒−𝑗2𝜋𝑓𝑛𝑥(𝑛)𝑤(𝑛)𝑑𝑛𝑇𝑝|2𝑑𝑓𝐹𝑞
其中w(n)是汉宁窗。同样地，d(n)的周期图是𝝀𝑝=(𝜆1,𝑝,𝜆2,𝑝,𝜆3,𝑝….𝜆𝑄,𝑝)，其值计算如下： 
𝜆𝑞,𝑝= ∫|∫𝑒−𝑗2𝜋𝑓𝑛𝑑(𝑛)𝑤(𝑛)𝑑𝑛𝑇𝑝|2𝑑𝑓
对于远端参考信号值，使用固定阈值𝜀̃1，𝜀̃2，…，𝜀̃
𝑄其每个值表示信号功率的周期图的平均值，则每个周期图被量化为二进制矢量𝑿𝑝=(𝑋1,𝑝,…,𝑋𝑄,𝑝)，其中：
𝑋𝑞,𝑝 = {1 𝑖𝑓 𝜀𝑞,𝑝 ≥ 𝜀̃𝑞
			0 𝜀𝑞,𝑝 < 𝜀̃
同样地，对近端语音信号值使用阈值
缓冲区将远端参考信号和近端语音信号的二进制矢量收集到二进制矩阵𝑿=(𝑋1,…,𝑋𝐾+𝐷𝑚)和𝑫=(𝐷1,…,𝐷𝐾)中，用于最优候选延迟𝐷𝑒𝑙𝑎𝑦𝑚的计算。
设M个候选延迟𝐷𝑒𝑙𝑎𝑦1<𝐷𝑒𝑙𝑎𝑦2<⋯<𝐷𝑒𝑙𝑎𝑦𝑀，其每个值表示为连续的时刻的距离的倍数，即延迟单位。通过缓冲区收集的二进制矩阵，对每个候选延迟计算平均代价。
对于第q个量、第m个候选延迟和在K个时刻内的平均代价，计算如下： Δ𝑞,𝑚=1𝐾Σ𝑝𝑒𝑛𝑎𝑙𝑡𝑦(𝑋𝑞,𝑘+𝐷𝑒𝑙𝑎𝑦𝑚,𝐷𝑞,𝑘)
在所有候选延迟的平均代价计算完成后，按照下式进行加权和计算： Δ𝑚=Σ𝐶𝑞Δ𝑞,𝑚𝑄𝑞
其中系数𝐶1，𝐶2，…，𝐶𝑞优选地反应每个量的重要性。在生成加权和Δ1，Δ2 ，…，Δ𝑚之后，对应候选延迟𝐷𝑒𝑙𝑎𝑦1，𝐷𝑒𝑙𝑎𝑦2，…，𝐷𝑒𝑙𝑎𝑦𝑀当中的最小的值，将是最好的估计𝐷𝑒𝑙𝑎𝑦𝑀。
## 非线性处理NLP
算法的**第一部分**是判断滤波器是否处于“发散”状态。当滤波器收敛良好时，由于
误差信号E(l,k)是将近端信号中的回声滤除后得到的，所以它的能量应该小于近端信号
的能量；**而当误差信号的能量大于近端信号的能量时，就说明误差信号失真严重**，自适
应滤波器系数发生**明显偏移，称之为“发散”状态**。
为了判断滤波器是否属于“发散”状态，需要计算近端信号和误差信号的**功率谱密
度**。精确的计算功率谱需要信号无限长时间上的集中平均，但在实际计算时，不可避免
的要进行信号截断，为了使功率谱估计的结果尽可能准确，采用**指数平滑**的方式，将当
前块的结果与前一块的结果进行平滑，定义平滑系数为S λ ，近端信号d(n)的频域表示
为D，则第l 个近端块PSD 的计算公式如下：
远端信号、误差信号的PSD 都可按照类似的方式进行计算。不同的是，在计算远
端信号时，为防止数值的不稳定性，一般为其设置一个阈值15 ，则远端信号的 PSD
需按示(4.13)进行修正。max（）
得到近端信号和误差信号的PSD 后，就可以判断滤波器是否属于“发散”状态。
如果信号满足式(4.14)，一般则认为滤波器“发散”。
$\left\|\boldsymbol{S D}_{E_{l} E_{l}}\right\|_{1}>\left\|\boldsymbol{S D}_{\boldsymbol{D}_{l} D_{t}}\right\|_{1}$
此时通过强制设置l l E  D ，可以逆转滤波器的发散，当信号满足公式(4.15)时，认为滤
波器退出“发散”状态。式中0  为比例系数，一般 1.05 
$\sigma_{0}\left\|\boldsymbol{S} \boldsymbol{D}_{E_{l} E_{l}}\right\|_{1}<\left\|\boldsymbol{S} \boldsymbol{D}_{\boldsymbol{D}_{l} \boldsymbol{D}_{l}}\right\|_{1}$
实际应用中，WebRTC 还考虑了“强发散”状态，即误差信号的能量远大于近端信
号，一般通过下式度量。比例系数一般 19.95  。
$\left\|\boldsymbol{S} \boldsymbol{D}_{E_{l} E_{l}}\right\|_{1}>\sigma_{1}\left\|\boldsymbol{S} \boldsymbol{D}_{D_{l} D_{l}}\right\|_{1}$
此时将滤波器系数置0 以清除过大误差。
算法的**第二部分**是根据残留回声的量计算出抑制因子de c ，从而去除残留回声。计
算抑制因子主要利用近端信号和误差信号的互功率谱密度，互功率谱密度的计算方法与
“自”功率谱密度相似：
$\boldsymbol{S} \boldsymbol{D}_{D_{l} E_{l}}=\lambda_{S} \boldsymbol{S} \boldsymbol{D}_{D_{l-1} E_{l-1}}+\left(1-\lambda_{S}\right) \boldsymbol{D}_{l} \boldsymbol{E}_{l}^{*}$
则抑制因子的计算如下所示：
$c_{d e}=\frac{S D_{D_{l} E_{l}} S D_{D_{l} E_{l}}^{*}}{S D_{D_{l} D_{l}} S D_{E_{l} E_{l}}}$
c 满足0<$c_{d e}$  <1，它可以表征残留回声在误差信号中所占的比例，**残留回声越小，
则$c_{d e}$越接近于1**。这样，如果自适应滤波阶段，回声消除的比较干净，则 $c_{d e}$ ，也就
是说，不需要再对误差信号进行回声抑制；**如果残留回声较大，则$c_{d e}$的值较小**，可以
通过$c_{d e}$对残留回声进行抑制。经过NLP 阶段后的输出信号表示如下：

$\boldsymbol{E}_{l}^{\prime}=\boldsymbol{E}_{l} \boldsymbol{c}_{d e}$
实际中的处理更加复杂，计算抑制因
子时，通常还要考虑远端信号和近端信号间的互功率谱密度，同时针对不同情况，还会
做出多种合理的修正。

在NLMS 自适应调节阶段，为了防止归一化误差信号的频谱过大，此处增加一个门
限值，正常设为6 2 10  ，超过门限值则将门限值赋给归一化误差频域信号。当采样频率
为8kHz 时，步长stepsize 设为0.6，16kHz 和32kHz 采样频率下步长设为0.5。计算误
差信号和近端信号的互相关记为cohde，远端信号和近端信号的互相关记为cohxd，取
1-cohxd 和cohde 的最小值为hNlDe，取hNlDe 的平均值为hNlDeAvg 来决定利用维纳
滤波消除残留回声的增益大小。
当误差能量seSum 大于近端能量sdSum 时，就将近端信号频谱赋值给误差信号频
谱，并将发散标志位divergeState 置1，如果seSum 的1.05 倍小于sdSum 时，则将
divergeState 置0，如果seSum 大于sdSum 的19.95 倍时，将权重系数矩阵置0。平滑滤波器系数和抑制系数共同作用来更新最终hNl 滤波器系数。最终将频域误差信号通过该
滤波器，接着使用重叠相加法恢复成时域信号，整体后移进行下一块迭代。

![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220524/image.5wwy2yyud140.webp)