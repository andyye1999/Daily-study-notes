# webrtc学习笔记
## 整体  
[WebRTC音频处理流程概述](https://blog.csdn.net/ssdzdk/article/details/39577335?spm=1001.2014.3001.5501)  
audio_processing.h  
APM分为两个流，一个近端流，一个远端流。近端（Near-end）流是指从麦克风进入的数据；远端（Far-end）流是指接收到的数据。  
farend获得数据后主要有4个步骤的处理。
1. 判断是否是32k信号，采取相应的分频策略；
2. AEC流程，记录AEC中的farend及其相关运算；
3. AES流程，记录AES中的farend及其相关运算；
4. AGC流程，计算farend及其相关特征。  
nearend流  
其中包括七个步骤：1、分频；2、高通滤波；3、硬件音量控制；4、AEC；5、NS；6、AES；7、VAD；8、AGC；9、综合。	
[浅谈语音质量保障：如何测试 RTC 中的音频质量？](https://mp.weixin.qq.com/s?__biz=MjM5NTE0NTY3MQ==&mid=2247515282&idx=1&sn=393775bd38a5351c2d97f1586a57f160&chksm=a6fe0e3a9189872cae23cb4badefe9f42a55f622b1eaf912e8ac40756bc64a3d1f872e884366&scene=178&cur_album_id=1612237369238175753#rd)  
评估声音质量   
[WebRTC整体架构分析](http://www.yushuai.xyz/2019/10/28/4462.html)  


## AGC  
### [详解 WebRTC 高音质低延时的背后 — AGC（自动增益控制）](https://www.cnblogs.com/VideoCloudTech/p/14816786.html)    
### 样本点幅度值 **Sample** 与分贝 **dB** 之间的关系  
以 16bit 量化的音频采样点为例：**dB = 20 * log10（Sample / 32768.0）**，与 Adobe Audition 右侧纵坐标刻度一致。  分贝表示：最大值为 0 分贝（**分贝值如下图右边栏纵坐标**），一般音量到达 -3dB 已经比较大了，3 也经常设置为 AGC 目标音量。  

### 核心参数  
**目标音量 - targetLevelDbfs**：表示音量均衡结果的目标值，如设置为 1 表示输出音量的目标值为 - 1dB;
**增益能力 - compressionGaindB**：表示音频最大的增益能力，如设置为 12dB，最大可以被提升 12dB；
**压限器开关 - limiterEnable**：一般与 targetLevelDbfs 配合使用，compressionGaindB 是调节小音量的增益范围，limiter 则是对超过 targetLevelDbfs 的部分进行限制，避免数据爆音。  

### WebRTC AGC 提供了以下模式： 
kAgcModeUnchanged,   
kAgcModeAdaptiveAnalog, // 自适应模拟模式   
kAgcModeAdaptiveDigital, // 自适应数字增益模式   
kAgcModeFixedDigital // 固定数字增益模式   
### 固定数字增益模式是最核心的模式，主要有如下两个方面值得我们深入学习：  
#### 语音检测模块 WebRtcAgc_ProcessVad 的基本思想  
最传统的 VAD 会基于能量，过零率和噪声门限等指标区分语音段和无话段，WebRTC AGC 中为粗略的区分语音段提供了新的思路：  
1. 计算短时均值和方差，描述语音包络瞬时变化，能够准确反映语音的包络  
2. 计算长时均值和方差，描述信号整体缓慢的变化趋势，勾勒信号的 “重心线”，比较平滑有利于利用门限值作为检测条件  
3. 计算**标准分数**，描述短时均值与 “重心线” 的偏差，位于中心之上的部分可以认为发生语音活动的可能性极大  
4. 
#### WebRtcAgc_ProcessDigital 如何对音频数据进行增益   
根据指定的 targetLevelDbfs 和 compressionGaindB，计算增益表 gainTable  
增益表 gainTable 可以理解为对信号能量值（幅值的平方）的量化  
基于人耳的听觉曲线，AGC 中在应用增益是是分段的，一帧 160 个样本点会分为 10 段，每段 16 个样本点，因此会引入分段增益数组 gains  
根据分段增益数组 gains，右移 16 位后获得实际的增益值（**之前计算增益表和增益数组都是基于样本点能量，这里右移 16 位可以理解成找到一个整数 α，使得信号幅度值 sample 乘以 α 最接近 32768**），直接乘到输出信号上（这里的输出信号在函数开始已经被拷贝了输入信号）。  
A. 幅度值为 8000 的数据，包络 cur_level = 8000^2 = 0x3D09000，通过 WebRtcSpl_NormU32 ((uint32_t) cur_level); 计算得到前置 0 有 6 个，查表得到整数部分增益为 stt->gainTable [6] = 3，即 8000 可以大胆乘以 3 倍，之后增益倍数小于 1.0 的部分由 fracpart 决定；

B. 幅度值为 16000 的数据，包络 cur_level = 16000^2 = 0xF424000，通过 WebRtcSpl_NormU32 ((uint32_t) cur_level); 计算得到前置 0 有 4 个，查表得到整数部分增益为 stt->gainTable [4] = 2，此时会发现 16000 * 2 = 32000，之后均衡到目标音量的过程由 limiter 决定，细节这里不展开。

**简单说就是，[0, 32768] 中的任何一个数想要增益指定的分贝且结果又不超过 32768，都能在数字增益表 gainTable 中找到确定的元素满足这个要求。**
### 自适应模拟增益 - AdaptiveAnalog   
由于PC端本身也能控制增益，导致控制增益太多，容易产生爆音。因此
在固定数字增益的基础上主要有两处新增：  
1. 在数字增益之后，新增了模拟增益更新模块：**WebRtcAgc_ProcessAnalog**，会根据当前模拟增益值 **inMicLevel**（WebRTC 中将尺度映射到 0~255）等中间参数，计算下一次需要调节的模拟增益值 **outMicLevel**，并反馈给设备层。  
2. 有些设备商麦克风阵列默认设置比较小，即使将模拟增益调满采集依然很小，此时就需要数字增益补偿部分来改善：**WebRtcAgc_AddMic**，可以在原始采集的基础上再放大 **1.0~3.16** 倍，如图 4。那么，如何判断放大不够呢？上一步中模拟增益更新模块最终输出实际为 **micVol** 与最大值 **maxAnalog（255）** 之间较小的那个：  
##### 存在的问题  
1. 无语音状态下的模拟值上调行为  
2. 调整幅度过大，造成明显的声音起伏  
3. 频繁调整操作系统 API，带来不必要的性能消耗，严重的会导致线程阻塞  
4. 数字部分增益能力有限，无法与模拟增益形成互补  
5. 爆音检测不是很敏感，不能及时下调模拟增益  
6. AddMic 模块精度不够，补偿过程中存在爆音的风险爆音  
### 自适应数字增益 - AdaptiveDigital   
基于音频视频通信的娱乐、社交、在线教育等领域离不开多种多样的智能手机和平板设备，然而这些移动端并没有类似 PC 端调节模拟增益的接口。声源与设备的距离，声源音量以及硬件采集能力等因素都会影响采集音量，单纯依赖固定数字增益效果十分有限，尤其是多人会议的时候会明显感受到不同说话人的音量并不一致，听感上音量起伏较大。

为了解决这个问题，WebRTC 科学家仿照了 PC 端模拟增益调节的能力，基于模拟增益框架新增了虚拟麦克风调节模块：WebRtcAgc_VirtualMic，利用两个长度为 128 的数组：增益曲线 - kGainTableVirtualMic 和抑制曲线 - kSuppressionTableVirtualMic 来模拟 PC 端模拟增益（增益部分为单调递增的直线，抑制部分为单调递减的凹曲线），前者提供 1.0~3.0 倍的增益能力，后者提供 1.0~0.1 的下压能力。  
核心逻辑逻辑与自适应模拟增益一致：
1. 与自适应模拟增益模式一样，依然利用 WebRtcAgc_ProcessAnalog 更新 micVol  
2. 根据 micVol 在 WebRtcAgc_VirtualMic 模块中更新增益下标 gainIdx，并查表得到新的增益 gain  
3. 应用增益 gain，期间一旦检测到饱和，会逐步递减 gainIdx  
4. 增益后的数据传入 **WebRtcAgc_AddMic**，检查 micVol 是否大于最大值 **maxAnalog** 决定是否需要激活额外的补偿  
##### 存在的问题  
存在的问题与自适应模式增益相似，这里需要明确说的一个问题是数字增益自适应调节灵敏度不高，当输入音量起伏时容易出现块状拉升或压缩，用一个比较明显的例子说明：遇到大音量时需要调用压缩曲线，如果后面紧跟较小音量，会导致小音量进一步压缩，接着会调大增益，此时小音量后续如果接着跟大音量，会导致大音量爆音，需要 limiter 参与压限，对音质是存在失真的。

### 总结与优化方向  
为了更好的听感体验，AGC 算法的目标就是忽略设备采集差异，依然能够将推流端音频音量均衡到理想位置，杜绝音量小、杜绝爆音、解决多人混音后不同人声音量起伏等核心问题。  
1. 模拟增益调节，必须修复调节频繁，步长过大等问题  
2. AddMic 部分精度不够，可以提前预判，不要等到检测到爆音再回调  
3. PC 端数字增益和模拟增益模块上是相互独立的，但是效果上应该是相互补偿的  
4. AGC 对音量的均衡不应该影响 MOS，不能因为追求灵敏度放弃了 MOS    



[WebRTC AGC 流程解析](https://zhuanlan.zhihu.com/p/485032369)  
### [WebRTC中AGC模块分析（上）](http://www.yushuai.xyz/2019/08/12/4423.html)      
特别详细解释了AGC函数的各个功能
### [WebRTC中AGC模块分析（下）](http://www.yushuai.xyz/2019/08/13/4425.html)  

## NS  

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
 **噪声抑制**需要准确估计出噪声信号，其中平稳噪声可以通过语音检测判别有话端与无话端的状态来动态更新噪声信号，进而参与降噪，常用的手段是基于**谱减法**(即在原始信号的基础上减去估计出来的噪声所占的成分)的一系列改进方法，其效果依赖于对噪声信号估计的准确性。对于**非平稳噪声**，目前用的较多的就是基于递归神经网络的深度学习方法，很多 Windows 设备上都内置了基于多麦克风阵列的降噪的算法。效果上，为了保证音质，噪声抑制允许噪声残留，只要比原始信号信噪比高，噪且听觉上失真无感知即可。

  

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
## VAD  
### [WebRTC VAD模块分析](http://www.yushuai.xyz/2019/07/15/4404.html)    
WebRTC VAD将频带分为了6个子带：80Hz~250Hz，250Hz~500Hz，500Hz~1K，1K~2K，2K~3K，3K~4K，在程序里面分别对应了分别对应于feature_vector [0]，feature_vector [1]，feature_vector [2]，feature_vector [3]，feature_vector [4]，feature_vector [5]。**之所以最高为4k是因为，WebRTC在处理的时候采样率统一调整为了8kHz，所以根据奈奎斯特定理，用于的频率就是4kHz以下。**  
可以看到以1KHz为分界，向下500HZ，250Hz以及170HZ三个段，向上也有三个段，每个段是1KHz，这一频段涵盖了语音中绝大部分的信号能量，且能量越大的子带的区分度越细致。由于我国交流电标准是220V~50Hz，电源50Hz的干扰会混入麦克风采集到的数据中且物理震动也会带来影响，所以取了80Hz以上的信号。

WebRTC VAD使用的是GMM（高斯混合模型）进行分类，使Noise作为一类，Speech作为一类，两类求求后验概率，并且实时更新GMM参数。

WebRTC VAD只能工作在采样率为8000Hz的模式下，故对16kHz、32kHz、48kHz都需要进行重新采样来转换到8000Hz。目前程序仅支持8000Hz、16kHz、32kHz和48kHz。  

** 一个好的VAD特征应该具备以下特性： ** 
 -   区分能力：含噪语音和仅含噪声音频的分离度应该尽可能的大。理论上的最好效果是让语音特征和噪声特征没有交集（实际很难，因为会有相似）
-   噪声鲁棒性：背景噪声会造成语音失真，这会影响提取的特征区分能力。
1.  基于能量的特征：基于能量的方法可以将宽带语音分成各个子带，求各个子带的能量。这是因为语音在2kHz以下频带含有大量的能量，而噪声在2~4kHz及4kHz以上频带的能量往往要比在0~2kHz的能量高。这其实就是**噪声平坦度**的概念。WebRTC中基于统计模型方法利用了频谱平坦度的特征。**基于能量的方法在信噪比低于10dB的时候，语音和噪声的区分性能会大大下降。**
2.  短时能量过零率：采集到的语音信号在数字域上有正负之分。过零率等于一段时间内穿过横轴的次数与总采样点数的比值，它反映了信号变化的**快慢**，虽然是时域特征，但变化快慢在一定程度上体现了频域的信息。**过零率对低频噪声敏感，实际使用中可以过滤掉低频部分。**
3.  频域特征：通过STFT将时域信号变成频域信号，即使SNR=0的时候，一些频带的长时包络还是可以用于区分语音和噪声的。
4.  倒谱特征：能量倒谱峰值确定了语音信号的基频，也有使用MFCC特征的。
5.  基于谐波的特征：语音的一个明显特征是包含了基频F0和多个谐波频率的，即使在强噪声条件下，谐波这一特征也存在，可以使用自相关的方法找到基频所在的频点。
6.  长时特征：语音是非稳态信号，音素间的谱分布是不同的，这就导致了随着时间变化，语音统计特性也是变化的。另外，日常绝大多数噪声都是稳态的（变化较慢），如白噪声、家电噪声等，根据音频长时统计变化特征（语音变化快，日常稳态噪声变化慢）也可以区分噪声和语音。



