#  [Overlap-add & Overlap-save method](https://zhuanlan.zhihu.com/p/480320394)    
利用圆周卷积与线性卷积的关系，在频域通过FFT是快速计算卷积的方法之一。但当参与卷积的序列长度相差较多，如常见的音频系统，输入序列通常是麦克风拾取到的数据，输入序列长度会很长，此时需要对另外一个序列补较多的零再进行计算，计算效率通常很低，同时还会引入较长的处理延时。为了利用快速卷积法的优越性，可将较长的输入序列x（n）进行分段，再通过频域FFT快速卷积算法得到子序列的卷积结果，最后按照相应的规则将子序列的卷积结果拼接起来，就可以得到最终的线性卷积结果。一般按照分段的规则可以将上述方法分为两类，即OLA和OLS。
## OLA  
![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.6k0dk95c2b40.webp)   
移位L，舍去后M-1个点
## OLS  
![image](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/image.4o7qzb51tdk0.webp)  
与OLA不同的是，OLS选取的分割长度为L+M-1
然后丢弃其前M-1点，保留剩余L点的数值

