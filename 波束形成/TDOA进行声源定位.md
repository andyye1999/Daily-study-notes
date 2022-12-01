# [公众号](https://mp.weixin.qq.com/s?__biz=MzA3MjEyMjEwNA==&mid=2247484417&idx=1&sn=a416da2d9238cd863697d91dd26233e4&chksm=9f226f96a855e6808ac3d90e83f8c673d8daddc57b95a537c0a2ba547ce53307452b0940c19a&token=139302241&lang=zh_CN#rd)

时延估计进行声源定位
互相关函数

## 广义互相关函数GCC
广义互相关函数是为了减少噪声和混响在实际环境中的影响，在互功率谱域使用加权函数加权，然后经过IFFT运算后找到峰值估计时延，其流程如下图所示：

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcibXTSJ7xgCL2hqhQuZ1aQdQ8xDVy2DNOJqWFDFWJjstkXP686iblnRuE6c3CmKpWhLZqXl1casB2A/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

广义GCC计算公式为：

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcibXTSJ7xgCL2hqhQuZ1aQdEmIUP0IRQstqYicRH915B8a6mia4iciaGGmf8BQ1nJFUuTMHTsQRUCeJtw/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

其中Ψ12为频域加权函数，常用的有如下几种

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcibXTSJ7xgCL2hqhQuZ1aQd5fjuDaGLARQXNGqbAzr6HXEVCAITDhxE1VHQrABAxRdcaqacy0ibibDQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

Gx1x2(ω)为互频谱，其计算公式为：

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcibXTSJ7xgCL2hqhQuZ1aQdrhXt9UAe1lOWWBIJ7PdDM6SAnYN3c3opur0H1fKdzJ6KEMVQMEFAAg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

最后我们就可以通过式(8)估计语音信号到达两个麦克风的时延了。  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcibXTSJ7xgCL2hqhQuZ1aQdVAyVd8R1gd8ZwwF95nCiaRgJNVjZiar7iaPmCuzXST7KDHibftv5pnFAZA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

## 声源定位

### 分远场近场，大多数是远场

如果要确定出声源在二维平面内的位置坐标,都至少需要三个麦克风。对于两个麦克风的情况，我们只能计算到达角(Direction of Arrival, DOA)。在介绍如何定位估计前需要先区分下近场(near-field)和远场(far-field)，假设声速波长为λ，麦克风之间的距离为d(有的地方称为孔径，aperture)，那么声源与麦克风之间的距离r大于2d2/λ时，符合远场模型，反之则为近场模型。对于远场模型来说，声源到达麦克风阵列的波形视为平面波，如下图所示：

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhepIGZSD6HUa1UbwnxBjEHjVay1uAQWmeYgSicdImOtMmTfxibFaGWcniaTlmsiaeP5lNkZCssxu0qgTA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

此时根据麦克风阵列的几何关系，我们有  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhepIGZSD6HUa1UbwnxBjEHjdD33jhuvM5xmNF1cGrf2tsCWszqJDMMouRcxG8MxeibSyIkEsHICboQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

进而可以求出，声源相对麦克风阵列的角度  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhepIGZSD6HUa1UbwnxBjEHjNhGicVV6sn8RdGhjaibtXxKQMe0j4icVJDAESp3P3ianr3KBBatbCyiacFQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

对于近场模型来说，声源到达麦克风阵列的波形视为球面波，如下图所示：  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhepIGZSD6HUa1UbwnxBjEHjdnWbkmEG0KdAlH0PKQCo3aJeIZXhyzPTIjztHKJb2DLoHnlTQkCeYQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

近场模型需要三个麦克风，我们假设τ12，τ13分别为第二和第三个麦克风与第一个麦克风的时延，那么

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhepIGZSD6HUa1UbwnxBjEHjDiaprWvd7ME5Xt5pYxhMYPS4lVPgw9w6k2ibsBpibFrGFGI79vhfhib3gg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

根据麦克风阵列的几何关系，我们得到

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhepIGZSD6HUa1UbwnxBjEHjAzvHBWc45Lq5g8K4NZ8RiaiafV9geDKN6OzztZKMvM32Q0FhBNwu4OIg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

其中τ12，τ13通过时延估计得到，因此可以求解公式(11)到(13)的方程组，进而使用正弦定理可以得到θ2和θ3。

# 基于线性预测残差的广义互相关算法

![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20221201/image.4cpevdjwbuq0.webp)

![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20221201/image.6jpg3tq8n6o0.webp)

