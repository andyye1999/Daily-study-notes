# [DCCRN:Deep Complex Convolution Recurrent Network for Phase-Aware Speech Enhancement](https://blog.csdn.net/aidanmo/article/details/122186728)
## 1.1 Related work
作为一个有监督学习问题，我们可以通过在时频域（TF-domain）和时域（time-domain）下对嘈杂语音进行增强。基于时域的方法又可以进一步划分为直接回归方法[2, 3]和自适应前端方法[4-6]两个类别。前者直接学习从语音噪声混合波形到目标语音的回归函数，无需显式的信号前端，通常使用某种形式的一维卷积神经网络 (Conv1d)实现。后者通常采用卷积编码-解码器和U-Net网络架构，时域信号作为输入和输出，实现类似于短时傅里叶变换和逆变换过程。然后在编码器和解码器之间插入语音增强网络，通常使用具有时间建模能力的TCN（temporal convolutional network）[4, 7]架构和LSTM（long-short term memory）架构[8]。

另一个主流的方法是在时频域方法[9-13]，该类方法认为经过STFT变换得到的TF表示能够令语音和噪声的精细结构更加容易分离。CRN方法【14】是一项近期的工作，通过CED提取高级特征(high-level)，以更好的进行带噪语音分离。CED方法能够处理复值谱和实值谱。复值频谱图可以分解为极坐标下的幅度谱和相位谱，或者笛卡尔坐标系下的实部和虚部。很长一段时间里，研究人员普遍认为相位是难以训练估计的，因此研究工作大多聚焦于幅度谱估计中[15-17]，忽略的相位信息估计，通过估计出的幅度和带噪语音的相位信息进行语音重建，该方法限制了网络的性能上限。

基于时频域方法的训练目标主要可以分为两类：masking-based target和mapping-based target。前者描述了语音和背景噪声之间的时频关系。后者对应纯净语音的频谱表示。在基于掩码的方法中，理想二值掩蔽（IBM）【20】， 理想比值掩蔽（IRM）【10】和频谱幅度掩蔽（SMM）【21】仅仅用到了干净语音和混合语音的幅度信息，没用使用相位信息。相反，phase-sensitive mask（PSM）【22】是第一个利用相位信息进行相位估计的掩蔽训练目标。之后，提出了复数比值掩蔽（CRM）【23】，该方法同时增强实部和虚部，实现完美的重建纯净语音。论文[24]提出的CRN方法，使用一个encoder 和两个decoders，通过复值频谱映射(CSM)同时估计混合语音信号的实部和虚部。CRM和CSM方法用到了语音的全部信息，理论上可以达到最佳性能。

最近DCUNET方法【25】集成了深度复数网络和u-net网络的优势，直接处理复值频谱。该网络模型的训练目标为CRM，使用SI-SNR损失函数进行网络模型优化，虽然该方法实现了SOTA性能，但由于使用了多层卷积网络，使得模型的复杂度较高，训练效率低。
## 2. The DCCRN [Model](https://so.csdn.net/so/search?q=Model&spm=1001.2101.3001.7020)
CRN 模型【14】是一种典型的CED架构网络，在编码器和解码器之间，插入两层的LSTM。这里的LSTM层用于对时序依赖进行建模。encoder部分包含五个Conv2d blocks，用于从输入特征中提取高级特征，或者降低分辨率。decoder部分，通过对称设计，重构低分辨率特征。二维卷积块中包含卷积和反卷积层，batch normalization和激活函数层。encoder和decoder对应层之间通过skip-connection相连。

论文【24】在CRN的基础上，进一步提出了一个encoder 和两个decoder 的网络架构。对复值STFT频谱的实部和虚部分别进行建模。相比于仅仅对幅度信息进行建模的方法，【24】的网络性能有了非常明显的提升。但是DCCRN将实部和虚部作为输入的两个通道，依然采用实值卷积进行运算，没有考虑复数的乘法规则，因此网络可以在没有先验知识的情况下学习实部和虚部。本文提出的DCCRN使用复数CNN，复数batch normalization和复数LSTM对CRN方法进行改进。具体而言，复数模块通过对复数乘法进行模拟，可以实现对幅度和相位的关系进行建模。

![在这里插入图片描述](https://img-blog.csdnimg.cn/26229d1d2efe4f579a77a549947194e3.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBAQWlkYW5tb21v,size_20,color_FFFFFF,t_70,g_se,x_16)
2.2 Encoder and decoder with complex network
![在这里插入图片描述](https://img-blog.csdnimg.cn/55a1466fdf664fb4a43effd2c6910a59.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBAQWlkYW5tb21v,size_20,color_FFFFFF,t_70,g_se,x_16)


