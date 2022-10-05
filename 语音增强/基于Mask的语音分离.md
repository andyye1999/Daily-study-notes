# [基于Mask的语音分离](https://mp.weixin.qq.com/s?__biz=MzA3MjEyMjEwNA==&mid=2247484164&idx=1&sn=f0f59a10fa04f02228bbba381348e66c&chksm=9f226893a855e185aab5b0abcf6c8c11802fe0b8d97b22c89222d533cf32c6498fa8587a4e77&scene=21#wechat_redirect)
-   理想二值掩蔽（Ideal Binary Mask，IBM）中的分离任务就成为了一个二分类问题。这类方法根据听觉感知特性，把音频信号分成不同的子带，根据每个时频单元上的信噪比，把对应的时频单元的能量设为0（噪音占主导的情况下）或者保持原样（目标语音占主导的情况下）
    
-   理想比值掩蔽（Ideal Ratio Mask, IRM），它同样对每个时频单元进行计算，但不同于IBM的“非零即一”，IRM中会计算语音信号和噪音之间的能量比，得到介于0到1之间的一个数，然后据此改变时频单元的能量大小。IRM是对IBM的演进，反映了各个时频单元上对噪声的抑制程度，可以进一步提高分离后语音的质量和可懂度。
**理想二值掩蔽**（Ideal Binary Mask, IBM）和**理想比值掩蔽**（Ideal Ratio Mask, IRM）。IBM的计算公式如下：

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhfibutZMG97NbCicvib6oUne9bg3cFpRCKqOdLALu0ZeddNSbaKbvSFq3wtuibkJoiczdHcaiaGVSYorAMA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

其中LC为阈值，一般取0，SNR计算公式为：  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhfibutZMG97NbCicvib6oUne9bkHVd5wOKu8VfrQmMNeHVmyeFw6THSWpEuMRtlkicvGqJDSIBq2qqJlg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

IRM为一个[0-1]的值,计算公式为：  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhfibutZMG97NbCicvib6oUne9bKralIYDE5iaKZ7DPhTnncn7V14iaajoicH19LPYR4WUpJMNu6uVeTxyRw/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

其中β为可调节尺度因子，一般取0.5。

理想二值掩蔽阨陉陂降阩解决语音增强（分离）问题。理想二值掩蔽，其中掩蔽广泛
用于图像处理之中，具体到语音增强领域是指对选定的时频区域进行遮挡
以控制要处理的区域，二值则是对每个时频点量化的精度非阰即阱，理想二
值掩蔽的含义则是根据纯净语音和噪声之间的能量关系，将语音能量占主
导的时频点标记为阱，噪声能量占主导的时频点标记为阰，由此得到一个滤
波器，对带噪特征进行滤波，在语音时频稀疏性假设下留下的即使语音成
分

理想比值掩蔽阨陉陒降阩、相位敏感掩蔽阨限陓降阩等训练目标也明显受到了传统语音增
强统计模型的影响，这类掩蔽估计由于其定义也不再能被视为分类问题阨而
同样是回归问题阩。这类掩蔽本质上是在设计某种意义上最优的滤波器，毕
竟，回顾陉陂降的介绍阐陉陂降的含义正是根据每个时频点上语音和噪声之间的能
量关系，将语音能量占主导的时频点标记为阱，噪声能量占主导的时频点标
记为阰阑中阐主导阑二字充满了不安全感。一个极端的例子是，在极低信噪比情
况下陉陂降会出现非常多的阰值导致理想掩蔽的滤波结果的语音质量和可懂度
都会十分糟糕。陉陒降将陉陂降的硬分类变成了一种软分类，每个时频点的滤波
器系数定义为语音能量和语音噪声二者能量之和的比值。熟悉传统语音增强
算法的读者不难发现，这个定义和频域维纳滤波算法尽管并不相同但还是十
分相像。

从训练目标角度将上述两大类工作分别
定义为基于掩蔽mask和基于谱映射mapping的算法用于分
类，这种分类方式得到了广泛地接受。