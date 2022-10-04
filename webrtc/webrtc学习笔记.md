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





