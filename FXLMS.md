# [主动降噪(Active Noise Control)](https://www.cnblogs.com/LXP-Never/p/11683944.html)
实际应用中，ANC降噪对2KHZ以下的信号噪声降噪效果比较好，**对高频噪声降噪效果很差**。原因为高频信号波长短，对相位偏差也比较敏感，导致ANC对高频噪声降噪效果差。**一般高频噪声可以被耳机物理的遮蔽屏蔽掉**，这种降噪被称为被动降噪。
上图是ANC系统的原理图，一共三层，用虚线分隔。最上一层primary path是从ref mic到error mic的声学通道，响应函数用P(z)P(z)表示；中间一层是模拟通道，其中secondary path是adaptive filter输出到返回残差的通路，包括DAC、reconstruction filter、power amplifier、speaker播放、再采集、pre-amplifier、anti-aliasing filter、ADC；最下一层是数字通路，其中adaptive filter不断调整滤波器权系数来削减残差，直到收敛。最常用的方案是用FIR滤波器结合LMS算法来实现adaptive filter。简化上图2，得到下图  
![](https://img2018.cnblogs.com/blog/1433301/201910/1433301-20191016152008229-1095148480.png)
再来说图3。这里adaptive filter输出后还要经过S(z)才去和desire output比较，S(z)会引起instability，用文献的话说，“the error signal is not correctly ‘aligned’ in time with the reference signal”，破坏了LMS的收敛性。一种有效的方法是FXLMS（Filtered-X LMS），也就让x(n)经过Sˆ(z)再输入给LMS 模块， S^(z)是S(z)的估计。FXLMS的objective：  
e2(n)=(d(n)−s(n)∗[wT(n)x(n)])2

所以gradient=−2e(n)s(n)∗x(n)，其中$s(n)$未知，用其estimate近似，所以FXLMS的更新公式是

w(n+1)=w(n)+μe(n)x′(n)
其中x′(n)=s^(n)∗x(n)


1. ANC为什么只针对2kHz以下的低频噪音？  
　　一方面，耳机的物理隔音方式（被动降噪）可以有效阻挡高频噪音，没必要用ANC降高频噪声。另一方面，**低频噪声波长较长，可以承受一定的相位延迟**，**而高频噪声波长短，对相位偏差敏感**，因此ANC消高频噪声并不理想。  
2. 当electronic delay比primary delay大时，算法性能大大下降如何理解？  
　　P(z)延时小，S(z)延时大，比如P(z)=z-1, S(z)=z-2，只有当W(z)=z才能满足要求，**非因果**，unreachable。  
3. Feedforward ANC、narrow-band feedforward ANC、feedback ANC有什么区别？  
　　Feedforwad结构有一个ref mic和一个error mic，分别采集外部噪音和内部残差信号。feedback结构只有一个error mic，由error mic和adaptive filter output生成reference signal。  
　　Broad-band feedforward就是上面所述结构，而narrow-band结构中，noise source会产生某个signal触发signal generator，signal generator再生成reference signal送给adaptive filter。只适用于消除periodic noise。  
　　Feedback ANC由于只有error mic，用error mic来恢复feedforward结构中ref mic采集的信号，通路不满足因果约束，因此只消除predictable noise components，即窄带周期性噪声。需要注意的是，feedforward如果不满足因果约束，即electronic delay比主通道acoustic delay长的话，也只能消除窄带周期性噪声。  
　　另外还有一种Hybrid ANC的结构，同时包含feedforward和feedback结构，主要的优点是可以节省自适应滤波器的阶数。
  
  
[英文](http://www.geocities.ws/ranjit_raphael/FXLMS.html)
[# 关于主动降噪耳机，你想知道的一切（一）](https://mp.weixin.qq.com/s/iS0bz8w9qrKCrQIO2PFN6Q)