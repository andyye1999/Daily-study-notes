# MVDR

MVDR中文名字叫**最小均方无畸变响应**，**最小方差无失真响应**它的精髓就体现在无畸变上。什么叫无畸变呢，就是在对感兴趣方位（声源方向）的信号无失真地输出，这意味着该算法可以直接当做语音后端算法(如ASR)的前处理过程。MVDR波束形成器的公式推导并不复杂，我们这里简单的介绍一下。MVDR由Capon于1969年提出，也称为Capon波束形成器，它的目标是对感兴趣方位的信号无失真输出的同时使波束输出的噪声方差最小。波束输出噪声方差记为

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcTCxapPSsCvtbS6aPeErGyrUCfzyq1wroiaJ82TjOsKUx8m0m8urXZ0EMNgHSnyLgbNnnN3xpccSQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

其中**w**是加权向量，**Rn**是噪声的协方差矩阵。于是MVDR可以描述为

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcTCxapPSsCvtbS6aPeErGyI4gTUOTC4vWCkVc2xgC2kjAMcT03px2uefqdicwGLuf4P9blIx92pMg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

采用拉格朗日算子，对上述有约束的优化问题进行求解，定义函数  

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/R3j7FT5mhhcTCxapPSsCvtbS6aPeErGyibFXS3TicEJd19t49TEoibya5OOnStglQbnu047ibL3cnWX7iapC7LqJvYQ/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)

对**w**求导，并令其导数为**0**有  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcTCxapPSsCvtbS6aPeErGy3p2FeEy59ZibM6b5QRGoRoSKuAygJt5JLFTgHZ5SZryRQBnGt1xfBHg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

代入公式（2）中的约束条件得到

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhfuv2hzIfibxChkeKLDt76CWxeKAXsuC57hMfLiayyN0y3I7XCYcnhYLsXgtJOhFmUGMPUhCTfsQboA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

把公式（5）代入公式（4）解得MVDR的权重为

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhfuv2hzIfibxChkeKLDt76CWLJS4cgBzgibc5fIjJnhoPrwa3MYHU8OTAicK3dhmKVGIuibiaG3f0ricTSw/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

若噪声场为空间白噪声，那么MVDR退化成常规波束成形。公式（6）的权重计算需要知道噪声的协方差矩阵，但有时无法估计出噪声的协方差矩阵，直接使用接受数据的协方差矩阵进行计算，即  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhfuv2hzIfibxChkeKLDt76CWNOGgTZmSsgITUzFK6DdSATFvdE8bzmKFcnRiatrJOdlHtmsp8kCPBMQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

有的地方称上式的波束形成器为最小功率无失真响应（Minimum Power Distortionless Response, MPDR）。MVDR的效果依赖于导向矢量和数据接受协方差矩阵精确与否，在理想环境下能够抑制干扰，最大程度提升信干噪比。

### [mvdr](https://www.funcwj.cn/2020/01/13/intro-on-se-and-ss/)

![image](https://cdn.jsdelivr.net/gh/andyye1999/image-hosting@master/20221011/image.5s0w5jkm9ic0.webp)


### [Overview of Beamformer](https://www.funcwj.cn/2017/11/11/overview-of-beamformer/)


这张图MVDR的公式错了。看上面那个
![QQ截图20221011203113](https://cdn.jsdelivr.net/gh/andyye1999/image-hosting@master/20221011/QQ截图20221011203113.5p0397nrs7s0.webp)


# 编程

## 归一化

协方差  向量乘以其共轭转置
噪声协方差矩阵编程时归一化，矩阵除以矩阵的迹（对角线之和）

## 求逆

![image](https://cdn.jsdelivr.net/gh/andyye1999/image-hosting@master/20230307/image.4d7fjzr4hlc0.webp)

![image](https://cdn.jsdelivr.net/gh/andyye1999/image-hosting@master/20230307/image.6kc3e2y5p700.webp)

矩阵加上一个小单位矩阵 

## 矩阵的逆变成思想

一个矩阵求逆的函数，其实现方法是高斯-约旦消元法（Gaussian-Jordan elimination），基本思路是通过初等矩阵的左乘，将原矩阵变为一个单位矩阵，这个过程中左乘的初等矩阵相当于把原矩阵的每一行都变为对角线元素为 $1$，其余元素为 $0$ 的矩阵。

具体实现步骤：

首先判断输入矩阵是否是方阵，如果不是则无法求逆。

创建一个和输入矩阵大小一致的矩阵，用于存储求逆结果。同时将这个矩阵初始化为单位矩阵，即对角线元素为 $1$，其余元素为 $0$。

为了避免修改原始矩阵，将输入矩阵拷贝到临时矩阵中。

对于每一行 $i$，选取对角线元素的绝对值最大的列 $c$，然后把第 $c$ 列所在的行变为对角线元素为 $1$，其余元素为 $0$ 的矩阵，同时在输出矩阵中对应的行做相应的变换，这个过程通过消元和代入得到，详见代码。

如果有一行 $i$ 的对角线元素的绝对值为 $0$，则说明输入矩阵是奇异矩阵，无法求逆，返回 false。

重复上述过程直到处理完所有行。

返回 true，表示求逆成功，输出矩阵即为原矩阵的逆。

## 复数矩阵的逆

C = A + iB
inv(C) = inv(A+B * inv(A) * B) - i inv(A)*B*inv(A+B* inv(A) * B)
两种证明方式
正着推
Sure, I will show you how to derive the formula for the inverse of a complex matrix C = A + iB. Here are the steps:

1.  To find the inverse of C, we need to solve the equation CC^-1 = I, where I is the identity matrix.
2.  We can write C^-1 as X + iY, where X and Y are real matrices. Then, we have (A + iB)(X + iY) = I.
3.  Expanding the product and equating the real and imaginary parts, we get AX - BY = I and AY + BX = 0.
4. AX = I + BY. X = inv(A)(I + BY). X = inv(A) + inv(A)BY.
5. inv(A) + inv(A)BY = inv(A - BY), we get X = inv(A - BY).
6.  Solving for X and Y, we get X = inv(A - BY) and Y = -inv(A)Binv(A - BY).
7.  Substituting X and Y into C^-1, we get C^-1 = inv(A - BY) - i inv(A)Binv(A - BY).
8.  Using the property that inv(A - BY) = inv(A + B*inv(A)_B), we get C^-1 = inv(A + B_inv(A)_B) - i inv(A)Binv(A + B_inv(A)*B).

反着推
To prove that `inv(C) = inv(A+B*inv(A)*B) - i inv(A)*B*inv(A+B*inv(A)*B)` for complex matrices C = A + iB, we'll proceed as follows:

First, let's define the matrix D as:

```
D = A + B * inv(A) * B
```

Then, we can express C in terms of D as:

```
C = A + iB = D + i(B - B * inv(A) * A)
```

We can observe that D is Hermitian (conjugate transpose is equal to itself), which implies that it is invertible.

Therefore, we can rewrite `inv(C)` as:

```
inv(C) = inv(D + i(B - B * inv(A) * A))
```

Now, let's use the formula for the inverse of a sum of two matrices:

```
inv(D + E) = inv(D) - inv(D) * E * inv(D + E)
```

where `E = i(B - B * inv(A) * A)`. This gives us:

```
inv(C) = inv(D) - inv(D) * i(B - B * inv(A) * A) * inv(D + i(B - B * inv(A) * A))
```

Next, let's simplify the expression `inv(D+iE)` using the Sherman-Morrison formula:

```
inv(D + E) = inv(D) - inv(D) * E * inv(D + E) 
           = inv(D) - inv(D)* E * (I + inv(E) * D) * inv(D)
           = inv(D) - inv(D) * (E * inv(D) + inv(E)) * inv(D)
```

where `I` is the identity matrix.

Using this formula with E = i(B - B \* inv(A) \* A) and D=A+B\*inv(A)\*B, we have

```
inv(D+iE) = inv(A + B*inv(A)*B + iB - iB*inv(A)*(A + B*inv(A)*B + iB))^(-1)
          = inv(A + B*inv(A)*B + iB - i^2*B*inv(A)*(A + B*inv(A)*B + iB))^(-1)
          = inv(A + B*inv(A)*B + iB + B*inv(A)*(iB/(A + B*inv(A)*B + iB)))^(-1)
          = inv(A + B*inv(A)*B + iB) - B*inv(A)/(A + B*inv(A)*B + iB) * i
```

Substituting the result into the previous equation, we get:

```
inv(C) = inv(D) - inv(D) * i(B - B * inv(A) * A) * [inv(A + B*inv(A)*B + iB) - B*inv(A)/(A + B*inv(A)*B + iB) * i]          
```

Multiplying out the expression in brackets and rearranging the terms, we obtain:

```
inv(C) = inv(A+B*inv(A)*B) - i*inv(A)*B*inv(A+B*inv(A)*B)
```

Therefore, `inv(C) = inv(A+B*inv(A)*B) - i inv(A)*B*inv(A+B*inv(A)*B)` holds for any complex matrices C = A + iB.




