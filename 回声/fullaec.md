fullaec.m的流程解释


[![](https://dqhplhzz2008-1251830035.cos.ap-guangzhou.myqcloud.com/2021/08/20210808152151653-498x1024.png)](https://dqhplhzz2008-1251830035.cos.ap-guangzhou.myqcloud.com/2021/08/20210808152151653.png)


# 线性滤波

上图红色虚线框的部分为线性滤波器处理部分。需要解释的有以下几点：

1.  为什么计算有多少块的时候Nb=floor(NN/N)-M？

答：NN是音频总长度，N是每块的长度。NN/N得到音频有多少块（因为可能为非整数，所以向上取整）。但是因为每次进来都是一块，只有满到底16块了第一个大块才被填满，因此可以看做是第一次进来16块，然后下次进来了一块这才被看做是真正的第一次开始，所以总数里面要减去那刚开始进来的16块，即floor(NN/N)-M。


[![](https://dqhplhzz2008-1251830035.cos.ap-guangzhou.myqcloud.com/2021/08/20210808152322583-1024x488.png)](https://dqhplhzz2008-1251830035.cos.ap-guangzhou.myqcloud.com/2021/08/20210808152322583.png)

2.  为何要将新的64点xk与旧的64点xo组成xx？

答：结合在一起是重叠保留法，将循环卷积转变为线性卷积。两个离散序列的FFT变换结果直接相乘是循环卷积，而我们需要线性卷积。【仍需要进一步理解和google】

3.  对上图中黑框框住的红色虚线框说明

yfk是对估计的16个块的频谱按列求和，得到的就是最近16块（时间）的远端频谱估计信息，yfk就是最终估计的回声在频域的结果。这样做的好处就是，近端麦克风采集到的信号里只要有这16块（时间）包含的远端信号，就都可以进行消除。这个16块包含了多长时间呢？若采样率fs=16k，则就是16*(64/16000)=0.064s=64ms的数据（每个块是4ms）。也就是说，只要近端采集到的信号里面的回声滞后扬声器64ms以内，就都是可以消除的。

# 线性滤波器系数更新

对各个上标的解释：

1.  补0是为了保证能做128点的FFT变换，并且补0并不会影响FFT频率值的结果。
2.  归一化计算结果实际上是：

$$Ek2=\frac{E(n)}{p(n)}$$

3.  第一步是对Ek2的幅值进行处理得到absEf：若Ek2的幅值大于threshold，则取Ek2的幅值，否则为threshold。将第一步和第二步结合起来，实际上每个点的物理意义就是将Ek2的振幅与门限比较，若比门限小则取该点为1，如果比门限大则该点值为门限值/振幅（因为振幅比门限大，所以值范围为0~1）。由于第二步进行了除以操作，所以第三步实际上是这样一个操作：如果该点的值比门限大，则取门限；如果该点的值比门限小，则保持不变。这样做的好处是降低滤波器系数更新过于快导致滤波器发散的风险。
4.  实际得到的结果就是（为了方便理解，以时域形式）

$$mEk=\frac{\mu E(n)}{p(n)}$$

5.  这一步实际上是将65*1的矩阵数据复制出另外15份，得到一个65*16的矩阵，每一列的结果其实是一样的，然后再与远端信号XFm（65*16），第一列是最新的一个块，其他的都是过去15个时间段的块）相乘，实际上得到的就是
    

$$\frac{X(n)\mu E(n)}{p(n)}$$

6.  求解IFFT后得到IFPP，将IFPP的后64点置零再变换到频域得到FPH，这样操作是为了避免线性卷积变成循环卷积。

# 一个分析部分

```
     if mod(kk, 10*mult) == 0
        WFbEn = sum(real(WFb.*conj(WFb)));
        %WFbEn = sum(abs(WFb));
        [tmp, dIdx] = max(WFbEn);

        WFbD = sum(abs(WFb(:, dIdx)),2);
        %WFbD = WFbD / (mean(WFbD) + 1e-10);
        WFbD = min(max(WFbD, 0.5), 4);
     end
    dIdxV(kk) = dIdx;%第dIdx块能量最强，代表近端对应的那个远端参考信号就是这个块
```

暂时无法在文档外展示此内容
![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.3x591lpnewo0.webp)

这一部分实际并没有用到，是在plot性能分析的时候用到的。所以为了节省性能也为了稳定，并不是每一次都更新，而是每10给块更新一次。WFb就是线性滤波器更新出来的系数矩阵的频域表示，我们首先计算权重矩阵中每个点的功率，然后按列求和（把每一列加起来），得到WFEn，然后寻找WFEn中的最大值为tmp和它对应的下标为dldx。这个时候，在计算权重最大的那个块的列，对其按行求和，得到的就是65*1的矩阵，然后对其进行继续更新，若值小于0.5则为0.5，若值大于4则为4，然后就更新出来了WFbD，将didx保存在didxV的第kk个值（didxV是Nb+1行、1列的矩阵）。

# 非线性处理

非线性处理的主要思想：

WebRTC是利用信号之间的频域相干性c（0<=c<=1）来衡量误差信号中残留回声的大小的。首先计算麦克风输入的近端信号d(n)与误差信号e(n)的频域相干性cde【实际上e(n)就是理想情况下我们去除回声后的纯近端语音信号，但是实际上还会有一些残留回声，因此可以简单地把cde当作残留回声在误差信号中的占有比例。假设线性阶段正常运行，cde越接近于1，说明近端信号和误差信号相似性越高，越不需要对误差信号做控制；相反，cde越小，越需要对误差信号做抑制。】。另外还会计算近端信号d(n)和远端信号x(n)之间的频域相关性cxd，令c'xd=1-cxd，c'xd越大，说明回声残留越小，越不需要一直；c'xd越小，说明回声残留越大，越需要抑制。由cxd和c'xd做进一步的处理操作，计算出每个频带相应的抑制因子sγ(k)。将抑制因子与误差信号对应的频带相乘，从而实现残留回声的抑制。

暂时无法在文档外展示此内容
![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.4hy62bc8fg20.webp)
下面回到matlab代码里面。由于非线性处理部分较长，所以一部分一部分来讲述。

第一部分是FFT变换到平均相干性的计算。

首先将ekfb与上次的误差组合成新的ee，即ee=[eo;ekfb]，然后对ee、xx、dd都要进行先加窗再做FFT变换得到ef、xf、df。这里加窗目的显而易见，就是为了减少频谱泄露，提高频谱的分辨率。

然后将xf存放在xfwm的第一列，df存放在dfm第一列。然后把dldx（即“一个分析部分”里面计算出来的权重矩阵能量最大的那块的索引值）指向的那一列赋值给xf，**这样从xfwm矩阵里把真正要处理的近端信号对应的远端参考信号获取到。**

```
xfwm(:,1) = xf;
xf = xfwm(:,dIdx);
dfm(:,1) = df;
```

然后计算功率谱，它们都是65*1的矩阵。

```
Se = gamma*Se + (1-gamma)*real(ef.*conj(ef));
Sd = gamma*Sd + (1-gamma)*real(df.*conj(df));
Sx = gamma*Sx + (1 - gamma)*real(xf.*conj(xf));
```

然后计算误差信号和近端输入信号（包括感兴趣信号和回声）的互功率谱Sed、远端参考信号和近端输入信号的互功率谱Sxd。

```
 Sxd = gamma*Sxd + (1 - gamma)*xf.*conj(df);
 Sed = gamma*Sed + (1-gamma)*ef.*conj(df);
```

然后计算误差信号和近端信号的相关性cohed，远端信号和近端信号相关性cohxd。cohxd越小，表示回声越小，cohxd越大，表示回声越大。

然后计算cohed在echoBandRange范围内的平均相干性。之所以是在这个范围内的，是考虑到回声主要集中在较低的频带，且人耳实际到高频带感知有限，所以对于高频带我们不拿来计算，节省计算量。将计算结果保存在cohedAvg，表征这是第kk个块的情况。cohedAvg是一个（Nb+1）*1的向量。

```
 cohed = real(Sed.*conj(Sed))./(Se.*Sd + 1e-10);
 cohedAvg(kk) = mean(cohed(echoBandRange));
 cohxd = real(Sxd.*conj(Sxd))./(Sx.*Sd + 1e-10);
```

在《实时语音处理实践指南》的解析中，没有对cohxd做进一步处理，但是在我所参考的代码里面对其进行了进一步处理，即

```
 cohxd(2:end) = filter(freqSm, [1 -(1-freqSm)], cohxd(2:end));
 cohxd(end:2) = filter(freqSm, [1 -(1-freqSm)], cohxd(end:2));
 cohxdAvg(kk) = mean(cohxd(echoBandRange));
```

感觉这像做了一个高通+低通滤波器？滤波器为：

H(z)=0.56/(1+0.44z-1)

然后依旧是求解了在感兴趣频带的cohxd的平均值，保存在了cohxdAvg。cohxdAvg和cohedAvg貌似后面没使用？

暂时无法在文档外展示此内容
![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.15m8szi4tulc.webp)

然后继续往下。

首先寻找1-cohxd和cohed中对应每个元素的最小值，存入hnled。1-cohxd的值越大，说明回声越小，否则回声越大。cohed的值越大，说明回声越小，否则回声越大。【此处应该是假设d里面包括感兴趣的信号s】。该值越大，说明回声在对应频率分量上越小，该频率分量越不需要抑制回声。之所以取两者判断，也是为了最大可能消除回声。

```
hnled = min(1 - cohxd, cohed);
```

然后对1-cohxd(echoBnadRange)和Sx进行升序排列。然后计算1-cohxd(echoBandRange)的均值。这里计算出来的结果hnlSortQ其实表示了远端和近端不相关性的平均值（因为cohxd表示的是相关性，所以1-cohxd是不相关性）。值越大，相关性越差，实际上回声越小。然后在感兴趣频带对hnled进行升序排序。

```
[hnlSort,hnlSortIdx] = sort(1-cohxd(echoBandRange));
[xSort, xSortIdx] = sort(Sx);
hnlSortQ = mean(1 - cohxd(echoBandRange));
[hnlSort2, hnlSortIdx2] = sort(hnled(echoBandRange));
```

我们从hnled中取两个值，一个值是取在排序后的后四分之三的地方的一个值，记为hnlPrefAvg；另一个是排序后二分之一的地方的值，即为hnlPrefAvgLow。

```
hnlQuant = 0.75;
hnlQuantLow = 0.5;
qldx = floor(hnlQuant*length(hnlSort2));
qldxLow = floor(hnlQuantLow*length(hnlSort2));
hnlPrefAvg = hnlSort2(qldx);
hnlPrefAvgLow = hnlSort2(qldxLow);
```

接下来我们就要判断是否要进行残余回声的抑制了，这里依据了两个条件：其一是cohedMean，即误差信号与近端信号的相关性，它们越相关（即值越大），说明越不需要抑制回声；其二是hnlSortQ，即近端信号和远端参考信号的非相关性，它们越不相关（即值越大），说明越不需要抑制回声。这里cohedMean的门限值为0.98，hnlSortQ为0.9，说明WebRTC的开发人员宁可牺牲一部分双讲效果，也不愿意接受回声残留。所以可以说这个算法是抑制回声较好，但是双讲可能效果较差。若都大于门限值，则不需要抑制回声，suppState=0；否则若cohedMean<0.95或hnlSortQ<0.8，则需要进行抑制，suppState=1，若为其他情况，则按照上一帧的选择来进行。

```
if cohedMean > 0.98 && hnlSortQ >0.9
    suppState = 0;
elseif cohedMean <0.95 | hnlSortQ < 0.8
    suppState = 1;
end
```

cohxdLocalMin的初始值为1，代表远端和近端完全不相关，这里会判断计算得到的远端和近端不相关性hnlSortQ是否小于前一次不相关，如果hnlSortQ小于前一次且小于0.75，则更新一次cohxdLocalMin：

```
if hnlSortQ < cohxdLocalMin & hnlSortQ <0.75
    cohxdLocalMin =hnlSortQ;
end
```

如果cohxdLocalMin=1，要么说明远端和近端完全不相关，要么就是cohxdLocalMin没有更新，既然非相关性非常大，则说明有回声的概率很小，那么使用较小的ocrd(over-drivend）值和较大的hnled(65*1)值，这样做是为了当回升路径接近于0时，避免发生抑制，例如耳机通话场景。

```
if cohxdLocalMin == 1
    ovrd = 3;
    hnled = 1-cohxd;
    hnlPrefAvg = hnlSortQ;
    hnlPrefAvgLow = hnlSortQ;
end
```

另外，如果suppState==0，则认为不需要进行回声抑制，cohedMean和hnlSortQ都接近于1，这种情况下，hnled的值也接近于1。

```
if suppState == 0:
    hnled = cohed;
    hnlPrefAvg = cohedMean;
    hnlPrefAvgLow =cohedMean;
end
```

暂时无法在文档外展示此内容
![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.21t9imziprk0.webp)
计算完hnled，接下来开始计算ovrd。

hnlLocalMin是对hnlPrefAvgLow的最小值跟踪，其初始值为1，在满足了下面判断条件下，实际上就是发现了更小的值（并且这个最小值符合条件），就会对其更新，然后将hnlNewMin设置为1，hnlMinCtr重新置0。

设置hnlNewMin为1其实更接近于一个bool值，他其实是指有没有更新hnlLocalMin，hnlMinCtr其实更类似于一个计数器，当hnlNewMin=1（也就是更新了之后），往下走就会更新hnlMinCtr=2，若此时下一个循环过来了没有更新hnlPrefAvg，则实际满足了hnlNewMin=1且计数的hnlMinCtr=2，这个时候就开始更新抑制等级ovrd。

```
if hnlPrefAvgLow < hnlLocalMin & hnlPrefAvgLow < 0.6
    hnlLocalMin = hnlPrefAvgLow;
    hnlMin = hnlPrefAvgLow;
    hnlNewMin = 1;
    hnlMinCtr = 0;
end

if hnlNewMin == 1:
    hnlMinCtr = hnlMinCtr + 1;
end
if hnlMinCtr == 2:
    hnlNewMin = 0;
    hnlMinCtr = 0;
    ovrd = max(log(0.00000001)/log(hnlMin +1e-10),3);
end
```

这里更新的ovrd最小值为3。

除了hnlLocalMin是对hnlPrefAvgLow的最小值跟踪外，cohxdLocalMin是对hnlSort的最小值跟踪。这里为了防止值大于1，对其进行了处理。

```
hnlLocalMin = min(hnlLocalMin + 0.0008/mult, 1);
cohxdLocalMin = min(cohxdLocalMin + 0.0004/mult, 1);
```

最后平滑更新ovrdSm。

```
if ovrd < ovrdSm
    ovrdSm = 0.99*ovrdSm + 0.01*ovrd;
else
    ovrdSm = 0.9*ovrdSm + 0.1*ovrd;
end
```

暂时无法在文档外展示此内容
![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.5fwlkdzah2w0.webp)

接下来是进行发散处理。

首先对Se和Sd（分别是误差信号的功率谱和近端信号的功率谱）按行求和，得到误差信号的能量ekEn和近端信号的能量dkEn。然后进行发酸处理。如果divergeState为0，期望误差能量大于近端能量，则用df（近端信号频谱）更新ef（误差信号频谱），并将发散处理装divergeState置为1，否则继续往下走。如果divergeState为1，则判断近端信号能量是否大于误差信号能量的1.05倍，若是则将divergeState置为0，否则用df（近端信号频谱）更新ef（误差信号频谱），divergeState仍为1。

```
ekEn = sum(Se);
dkEn = sum(Sd);
if divergeState == 0
    if ekEn > dkEn
        ef = df;
        divergeState = 1;
    end
else
    if ekEn*1.05 < dkEn
        divergeState = 0;
    else
        ef = df;
    end
end
```

如果误差信号比近端信号大约13dB（差不多误差能量大于近端能量的19.95倍），则认为此时滤波器已经发散了，就要重新更新滤波器，即将滤波器系数WFb置为全零矩阵。

```
if ekEn > dkEn*19.95
    WFb=zeros(N+1,M); % Block-based FD NLMS
end
```

如果滤波器系数每发散，或者已经将WFb置零了之后，就需要将相应的能量存放在相应的向量中，将hnlLocalMin/cohxdLocalMin/hnlMin等保存在相应向量中。

```
ekEnV(kk) = ekEn;
dkEnV(kk) = dkEn;
hnlLocalMinV(kk) = hnlLocalMin;
cohxdLocalMinV(kk) = cohxdLocalMin;
hnlMinV(kk) = hnlMin;
```

暂时无法在文档外展示此内容
![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.ztw7lp7xy5s.webp)

接下来开始平滑滤波器系数及抑制指数，计算NLP的权重了。

首先使用权重曲线weight平滑hnled。wegiht是一个频率在较低的时候值很低，随着频率点变大值变大的曲线（如下图所示）。我们用hnlPrefAvg和hnled对应频点的较小值来更新这一次的hnled，更新后的值乘上weight，更新之前的值（上一次）乘1-weight的和来作为最终的hnled。结合weight的曲线我们发现，更新的时候存在这样一个现象：频率越高的点，使用本次更新的hnled的值的占比越大；频率越低的点，使用上一次的值平滑的结果占比越大。


![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.bzae2q18igo.webp)

```
aggFact = 0.3;
wCurve = [0; aggrFact*sqrt(linspace(0,1,N))' + 0.1];
weight = wCurve;
hnled = weight.*min(hnlPrefAvg, hnled) + (1 - weight).*hnled;
```

接下来利用ovrdSm来生成od，实际上是ovrdSm*(1+sqrt(x))，其中x是0~1之间等分65份的线性分布。od用来更新hnld的幂指数。

```
od = ovrdSm *sqrt(linspace(0,1,N+1))' + 1;
sshift = ones(N+1,1);
hnled = hnled.^(od.*sshift);
```

最后就是hnl系数与误差信号的频谱点乘，在时域相当于卷积，也就是将误差信号通过这样一个滤波器最后得到NLP处理后的感兴趣信号。最后存储一些有关的变量值。

```
hnl=hnled;
ef = ef.*(hnl);
```

```
ovrdV(kk) = ovrdSm;
hnledAvg(kk) = 1-mean(1-cohed(echoBandRange));
hnlxdAvg(kk) = 1-mean(cohxd(echoBandRange));
hnlSortQV(kk) = hnlPrefAvgLow;
hnlPrefAvgV(kk) = hnlPrefAvg;
```

暂时无法在文档外展示此内容

![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.3urain2timo0.webp)

至此，整个aec的主要流程已经结束。后面就是舒适噪声的生成和将频域信号经过IFFT和重叠相加变回时域信号，然后切到下一帧进行处理，直到所有音频处理完成。