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

## VAD  
### [WebRTC VAD模块分析](http://www.yushuai.xyz/2019/07/15/4404.html)    
WebRTC VAD将频带分为了6个子带：80Hz~250Hz，250Hz~500Hz，500Hz~1K，1K~2K，2K~3K，3K~4K，在程序里面分别对应了分别对应于feature_vector [0]，feature_vector [1]，feature_vector [2]，feature_vector [3]，feature_vector [4]，feature_vector [5]。**之所以最高为4k是因为，WebRTC在处理的时候采样率统一调整为了8kHz，所以根据奈奎斯特定理，用于的频率就是4kHz以下。**  
可以看到以1KHz为分界，向下500HZ，250Hz以及170HZ三个段，向上也有三个段，每个段是1KHz，这一频段涵盖了语音中绝大部分的信号能量，且能量越大的子带的区分度越细致。由于我国交流电标准是220V~50Hz，电源50Hz的干扰会混入麦克风采集到的数据中且物理震动也会带来影响，所以取了80Hz以上的信号。

WebRTC VAD使用的是GMM（高斯混合模型）进行分类，使Noise作为一类，Speech作为一类，两类求求后验概率，并且实时更新GMM参数。

WebRTC VAD只能工作在采样率为8000Hz的模式下，故对16kHz、32kHz、48kHz都需要进行重新采样来转换到8000Hz。目前程序仅支持8000Hz、16kHz、32kHz和48kHz。



