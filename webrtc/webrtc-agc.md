## AGC  
### [详解 WebRTC 高音质低延时的背后 — AGC（自动增益控制）](https://www.cnblogs.com/VideoCloudTech/p/14816786.html)    
### 样本点幅度值 **Sample** 与分贝 **dB** 之间的关系  
以 16bit 量化的音频采样点为例：**dB = 20 * log10（Sample / 32768.0）**，与 Adobe Audition 右侧纵坐标刻度一致。  分贝表示：最大值为 0 分贝（**分贝值如下图右边栏纵坐标**），一般音量到达 -3dB 已经比较大了，3 也经常设置为 AGC 目标音量。  
![](https://img2020.cnblogs.com/other/2200703/202105/2200703-20210527102330896-417426353.png)

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
固定数字增益模式下仅依靠核心函数 **WebRtcAgc_ProcessDigital** 对输入信号音量进行均衡，由于没有反馈机制，其信号处理流程也是极其简单，设置好参数之后信号会经过如下流程：

![](https://img2020.cnblogs.com/other/2200703/202105/2200703-20210527102331810-472805561.png)  
#### 语音检测模块 WebRtcAgc_ProcessVad 的基本思想  
最传统的 VAD 会基于能量，过零率和噪声门限等指标区分语音段和无话段，WebRTC AGC 中为粗略的区分语音段提供了新的思路：  
1. 计算短时均值和方差，描述语音包络瞬时变化，能够准确反映语音的包络  
2. 计算长时均值和方差，描述信号整体缓慢的变化趋势，勾勒信号的 “重心线”，比较平滑有利于利用门限值作为检测条件  
3. 计算**标准分数**，描述短时均值与 “重心线” 的偏差，位于中心之上的部分可以认为发生语音活动的可能性极大  
![](https://img2020.cnblogs.com/other/2200703/202105/2200703-20210527102332079-196064004.png)  
图 2 左：长短时均值与方差 右：输入与 vad 检测门限
#### WebRtcAgc_ProcessDigital 如何对音频数据进行增益  
![WebRtcAgc_ProcessDigital流程图1](https://img-blog.csdn.net/20170117162850370?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvc3NkemRr/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
![WebRtcAgc_ProcessDigital流程图2](https://img-blog.csdn.net/20170117162859734?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvc3NkemRr/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
![WebRtcAgc_ProcessDigital流程图3](https://img-blog.csdn.net/20170117162912136?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvc3NkemRr/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
第一部分首先要**计算近端信号的VAD结果**，并且**当远端信号超过10帧（100ms）**之后，使用**远端的VAD结果来修正近端VAD**，具体的修正公式如下：

![](http://tech.yushuai.xyz/wzpt/speechnotes/agcgs1.jpg)

    接着就是使用V来计算出衰减decay，其计算公式为

![](http://tech.yushuai.xyz/wzpt/speechnotes/agcgs2.jpg)

    然后接下来的具体操作在图中都有，就不再叙述。

![](http://tech.yushuai.xyz/wzpt/speechnotes/agctu32.jpg)

图3.2 ProcessDigital()函数流程图1

第二部分如图3.3中的蓝色部分。该部分**通过快、慢包络和增益计算每个子帧的增益数组gain**。首先计算**快慢包络**，如下所示
计算每1ms的最大能量作为包络env。

![](http://tech.yushuai.xyz/wzpt/speechnotes/agcgs3.jpg)


然后取两个包络的最大值作为level。最后使用对数的分段线性函数把cur_level转换成gain。对数函数的整数部分是cur_level前面0的个数，如果0越少，说明数值越大，最多是31个0，最少1个0（有符号数）。小数部分用线性差值的方法，找到gain[zeros]，gain[zeros-1]中间的量。
##### 其中gaintable
根据指定的 targetLevelDbfs 和 compressionGaindB，计算增益表 gainTable  
增益表 gainTable 可以理解为对信号能量值（幅值的平方）的量化  我们先固定 targetLevelDbfs，分别设置 compressionGaindB 为 3dB~15dB，所对应的增益表曲线如下，可以看到增益能力设置越大，曲线越高，如下图。

![](https://img2020.cnblogs.com/other/2200703/202105/2200703-20210527102332496-240002182.png)
大家可能会好奇增益表 **gainTable** 的长度为什么只有 32 呢？32 其实表示的是一个 int 型数据的 32 位（short 型数据的能量值范围为 [0, 32768^2] 可以用无符号 int 型数据表示），从高位到低位，为 1 的最高位具有最大的数量级称为整数部分 - intpart，后续数位组成小数部分称为 fracpart。因此 [0, 32768] 之间的任意一个数都对应数字增益表中的一个增益值。接下来我们讲讲如何查表并应用增益值完成音量均衡。
根据输入信号包络在增益表 gainTable 中查找增益值，并应用增益到输入信号；
就是之前函数执行到的这一步
基于人耳的听觉曲线，AGC 中在应用增益是是分段的，一帧 160 个样本点会分为 10 段，每段 16 个样本点，因此会引入分段增益数组 gains  
根据分段增益数组 gains，右移 16 位后获得实际的增益值（**之前计算增益表和增益数组都是基于样本点能量，这里右移 16 位可以理解成找到一个整数 α，使得信号幅度值 sample 乘以 α 最接近 32768**），直接乘到输出信号上（这里的输出信号在函数开始已经被拷贝了输入信号）。  
A. 幅度值为 8000 的数据，包络 cur_level = 8000^2 = 0x3D09000，通过 WebRtcSpl_NormU32 ((uint32_t) cur_level); 计算得到前置 0 有 6 个，查表得到整数部分增益为 stt->gainTable [6] = 3，即 8000 可以大胆乘以 3 倍，之后增益倍数小于 1.0 的部分由 fracpart 决定；

B. 幅度值为 16000 的数据，包络 cur_level = 16000^2 = 0xF424000，通过 WebRtcSpl_NormU32 ((uint32_t) cur_level); 计算得到前置 0 有 4 个，查表得到整数部分增益为 stt->gainTable [4] = 2，此时会发现 16000 * 2 = 32000，之后均衡到目标音量的过程由 limiter 决定，细节这里不展开。

**简单说就是，[0, 32768] 中的任何一个数想要增益指定的分贝且结果又不超过 32768，都能在数字增益表 gainTable 中找到确定的元素满足这个要求。**


第三部分如图3.3中的橘色部分，是来计算门限gate。gate意味着衰减原来的增益。gate的计算可以看成两部分，第一部分是基于快慢包络计算出的似然比，相当于快包络与慢包络能量的倍数。第二部分是近端信号的短时方差。
表达式如下：g≈−log(Cslow/Cfast)+(3.91−STDST near)
先看第一部分，这里说− l o g ( C f a s t ) 对应于zeros_fast，这个东西是快包络大的时候它值小，− l o g ( C s l o w ) 对应于zeros，这个东西是慢包络大的时候它值小。第一部分说明，fast与slow包络的距离越大，也即是出现语音的可能性越大，gain越小。
第二部分是定值减去vadNearend.stdShortTerm。无疑，语音出现可能性越大，vadNearend.stdShortTerm越大，第二部分越小，gain越小。
然后计算门限

![](http://tech.yushuai.xyz/wzpt/speechnotes/agcgs4.jpg)

在计算完gate之后，确定gate是否小于0，若小于，则gatePrevious=0，否则就平滑门限。

![](http://tech.yushuai.xyz/wzpt/speechnotes/agcgs5.jpg)

平滑后，把门限转换成gain_adj。当gate最小的时候为0（语音），gain_adj取到最大，此时不使用gainTable[0]的值作为参考；当gate最大的时候为2500（噪声），gain_adj取到最小，此时g[k+1]要取到相对于gainTable[0]的值的70%；当gate处于最大最小值之间，g[k+1]在gainTable[0]和g[k+1]确定的这条直线上移动。这一部分如图3.4所示。

![](http://tech.yushuai.xyz/wzpt/speechnotes/agctu33.jpg)

图3.3 ProcessDigital()函数流程图2

![](http://tech.yushuai.xyz/wzpt/speechnotes/agctu34.jpg)

图3.4 ProcessDigital()函数流程图3

最后一部分就是gain与语音进行处理，如图3.5所示，图中描述已经非常清楚。

![](http://tech.yushuai.xyz/wzpt/speechnotes/agctu35.jpg)



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
### [#Webrtc AGC 算法原理介绍（一）](https://blog.csdn.net/ssdzdk/article/details/52588415)