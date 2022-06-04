# webrtc学习笔记
## 整体  

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
#### WebRtcAgc_ProcessDigital 如何对音频数据进行增益  
### 自适应模拟增益 - AdaptiveAnalog  
### 自适应数字增益 - AdaptiveDigital  
### 总结与优化方向
[WebRTC AGC 流程解析](https://zhuanlan.zhihu.com/p/485032369)  
[WebRTC中AGC模块分析（上）](http://www.yushuai.xyz/2019/08/12/4423.html)    
[WebRTC中AGC模块分析（下）](http://www.yushuai.xyz/2019/08/13/4425.html)  

## NS  

## AEC  

