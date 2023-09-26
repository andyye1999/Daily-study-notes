# 自适应滤波
[[FDAF自适应滤波器算法综述]]
[[FXLMS]]
# webrtc
[[webrtc_ns]]  NS的算法原理
[[webrtc-aec]]  NLP

# 降噪

[[语音增强理论与实践]]

# Rnnoise

[[RNNoise]]

# 带宽扩展及AIcodec

[[深度学习骨导映射]]

# 深度学习

[[基于深度学习的语音增强概述]]

# 波束形成

[[MVDR]]
[[GSC]]


# 近期反馈


目前硬件在做防爆测试 软件在调优
公司过来人 有几个问题 
第一 输出能量问题 声音小 
第二 噪声更新慢？不应该 
第三 也会外加恒玄内置的算法 
第四 算力剩余？ 
第五 高信噪比下语音损失大

# 骨导项目



## 音色

[[语音转换]]



**LSF怎么算的**


[[带宽扩展#LSF系数]]
## VAD

[[语音活动检测模块]]

## 频域RLS

[[频域RLS]]
**噪声段用快步长，语音段用慢步长**
**这里面有程序和原理，一定要看！！！**

**时域N阶的RLS在频域实现，等效于N个一阶的频域RLS**

Background noise reduction 和 Statistical noise reduction 区别是前者是在VAD判决为噪声时

## 谱线增强

对每帧每个频段计算能量，算自相关和互相关
然后根据VAD结果为语音和相关性（互相关/自相关）大，采用快步长进行参考麦的能量平滑
找到前12个较大的参考麦能量，将剩余的比第12个小的所有频点能量相加取平均
将它除以每个频点能量（参考麦）开根号，与主麦信号相乘

代码在BCE工程中  md中删除了，防止保密协议

```cpp
for (i = 0; i < 100; i++) list[i] = 0;
		for (j = 1; j < fftpoint / 2; j++)
		{
			tmp = 10 * (float)log10(1.0 + st->refenergyaverage[j]);
			list[(Word16)tmp]++; 
		}
		for (num = 0, i = 99; i > 0; i--)
		{
			num += list[i];
			if (num > 12) break; 
		}
		tmp = (float)pow(10, i / 10.0); 
		for (energaverage = num = 0, j = 1; j < fftpoint / 2; j++)
		{
			if (st->refenergyaverage[j] < tmp)
			{
				energaverage += st->refenergyaverage[j];
				num++;
			}
		}
		if (num == 0)
		{
			num = fftpoint / 2 - 1;
			for (energaverage = 0, j = 1; j < FFT_LEN / 2; j++) energaverage += st->refenergyaverage[j];
		}
		energaverage /= freq_num;
		for (i = 1; i < fftpoint / 2; i++)
		{
			tmp = (float)sqrt(energaverage / st->refenergyaverage[i]);
			if (tmp > 1.0f) tmp = 1.0f;
			tmp = (float)sqrt(tmp);
			input[2 * i] *= tmp;
			input[2 * i + 1] *= tmp;
		}
```

为什么直方图用log，因为为了使容器的容量小，语音波动大，转换成db后波动小

## 硬件


### 简化webrtc aec

fft换成自己的，我们的fft跟原来的相比，需要除以64.不知道为什么 因为我们的FFT本身就是是真正的FFT/64的 128点FFT是除以64  256点FFT是除以128
不能轻易使用malloc，dsp容易溢出，将它们事先放进结构体中，这样直接占用栈空间
nlp中步长的判决简单化

NLMS滤波器采用10阶系数 也是10个block  原来webrtc是12阶


分块的BLOCK_LEN为64
每次读取160点，缓存为64+160+160+384点采样值
远端信号进行FFT后缓存20个128点FFT值

后面采用先RLS再非线性处理

# 回声的NLP

[[webrtc-aec#非线性处理NLP]]

简单就是指数平滑计算近端信号和误差信号的自相关（功率谱） 如果误差信号大于近端信号，则滤波器发散，将误差信号等于近端信号，如果特别大，则直接将滤波器系数置0

之后计算抑制因子，同过互相关除以自相关，得到

### 定点化

[[定点化#神经网络权重的定点化]]

#### 四舍五入
统计降噪的定点化FFT中+16384的目的是  在进行右移的同时，因为运算结果是向下取整的，为了避免因为右移造成的精度损失，所以在每个数的末尾加上一个偏移量，即16384L，以便获得一个更精确的结果。相当于+0.5 为了四舍五入 得到更高精度 **尤其是像自适应滤波器或者FFT这种循环迭代**的定点化  这么做的目的是为了使运算结果四舍五入为最接近的整数，以保证运算结果的精度。

webrtc的NSX中fft定点化inst->stages = inst->order 80点->128FFt 为7 160点->256FFT 为8
FFT的定点化之后的Q值为(norm-stages)

窗函数或者查表的数组浮点为1时，定点为32767，不是32768，调试经验 

#### log函数 查表法以及小数和整数

log函数怎么实现看那个定点化文档的PDF，最后有详细解释
log10(x) = log10(2) *  log2(x)

frac的计算方法是将magn(i)左移zeros位，然后将结果的31位取出来，再右移23位，这样就得到了magn(i)的分数部分。最后，frac的值被用来查表，得到log2(magn(i))的分数部分的值。

```c
// lmagn(i)=log(magn(i))=log(2)*log2(magn(i))
  // magn is in Q(-stages), and the real lmagn values are:
  // real_lmagn(i)=log(magn(i)*2^stages)=log(magn(i))+log(2^stages)
  // lmagn in Q8
zeros = WebRtcSpl_NormU32((uint32_t)magn[i]);
      frac = (int16_t)((((uint32_t)magn[i] << zeros)
                              & 0x7FFFFFFF) >> 23);
      // log2(magn(i))
      assert(frac < 256);
      log2 = (int16_t)(((31 - zeros) << 8)
                             + WebRtcNsx_kLogTableFrac[frac]);
      // log2(magn(i))*log(2)
      lmagn[i] = (int16_t)WEBRTC_SPL_MUL_16_16_RSFT(log2, log2_const, 15);
      // + log(2^stages)
      lmagn[i] += logval;
      frac的计算方法是将magn(i)左移zeros位，然后将结果的31位取出来，再右移23位，这样就得到了magn(i)的分数部分。最后，frac的值被用来查表，得到log2(magn(i))的分数部分的值。
```


![image](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230410/image.tesssc4czc0.webp)

#### basicop
用电脑去模拟指令集，芯片是恒玄2500，arm指令集。32位分为高16位低16位
basic_op.c 这个文件中有以下几种函数：

add、sub、abs_s、shl、shr等，用于对16位整数进行加减、绝对值、左移、右移等运算。
L_add、L_sub、L_abs、L_shl、L_shr等，用于对32位整数进行加减、绝对值、左移、右移等运算。
mult、round等，用于对16位整数进行乘法和四舍五入运算，并返回16位整数。
L_mult等，用于对16位整数进行乘法运算，并返回32位整数。
mac_r、msu_r等，用于对两个16位整数进行乘累加或乘累减运算，并返回16位整数。
L_mac、L_msu等，用于对两个16位整数进行乘累加或乘累减运算，并返回32位整数

mpy32_16 相当于32位乘16位数再右移15位
mpy32_32 相当于32位乘32位数再右移31位
div_s 除法 将分母取norm 上面的1再右移norm位 得到结果是Q15的数 函数的分子必须小于分母

DIV_32类似，32位的除法
除法转换为乘法，但Qzhi还是按除法算，即除法后的Q 是 之前的Q减去分母norm之前的Q值

长时平滑agc定点化函数
平方根[[平方根]]   牛顿迭代法，二分法

### 恒玄

[[恒玄2500]]

DSP的晶振  450MHz  内存总共5Mbits  内存占用多大 恒玄2700 什么芯片Cortex-M55 占用多大内存

## 后置滤波

基音滤波 仿照rnnoise 和编解码器中的后置滤波，因为音色增强中求了基音周期了，看rnnoise中的后置滤波模块[[RNNoise#[RNNoise超详细解读](https://zhuanlan.zhihu.com/p/397288851)]]

后置滤波在CELP等编码器中很常见，但却在语音增强方面没有引入。
在percepnet中，引入了FIR的梳状滤波器。系数由神经网络进行计算

尝试后置滤波，有效果的，共振峰间隙之间降噪

# 阵列

[[阵列软著总结]]

[[环形麦克风阵列]]

# 指标

每个项目的指标

恒玄2700 时延9mm

电力 103db环境 降噪前 3db 降噪后 提高个25db

PESQ? 

音色的统计指标？ PESQ STOI LSD 语音识别错误率 主观mos  分段噪声比、分段干扰比、语音失真度
算力指标RTF 运算所需时间除以音频长度

## 延时
恒玄2700 时延9mm

回声的延时 60ms

帧长160

## 音色指标
音色：
LSD：2.37 HLSD: 2.5
SISDR:4.5 不知道为什么这么低
PESQ:原始1.608 补偿：2.021
STOI: 原始0.68 补偿 0.851

## BWE
BWE：
SISDR: 18 LSD:1.8 HLSD:3.12

用频域的比时域的在实时效果时稳定很多  
时域的在处理帧与帧之间会出现问题
频域模型： [(31条消息) DPCRN: Dual-Path Convolution Recurrent Network for Single Channel Speech Enhancement---论文翻译_我和代码有个约会.的博客-CSDN博客](https://blog.csdn.net/caixiaobaideye/article/details/118958325)  DPCRN
PESQ:3.43 STOI:0.98 SI-SDR17.33 LSD: 1.63 HLSD:2.54


## OPUS
DPCRN修复
opus SI_SDR: 2.5799457628579643, LSD: 4.999016284942627, LSD_high: 8.153860092163086 PESQ: 2.217040777206421, STOI: 0.9297654788366524
处理后 SI_SDR: 4.046725547297675, LSD: 2.107752561569214, LSD_high: 2.413111448287964, PESQ: 2.760394811630249, STOI: 0.9432520335999617

音色网络参数量 0.08M  flops 8.1M
DPCRN网络参数量 0.64M flops 3463.75M
