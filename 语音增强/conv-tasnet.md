# loss
## si-snr
![](https://pic2.zhimg.com/80/v2-55feed80e523185d25267fcfb4b21391_720w.jpg)

![](https://pic3.zhimg.com/80/v2-6aafcc5d9412520d02466ee4cbc48e0a_720w.jpg)
SI-SNR 是[scale](https://so.csdn.net/so/search?q=scale&spm=1001.2101.3001.7020)-invariant source-to-noise ratio的缩写，中文翻译为尺度不变的信噪比，意思是不受信号变化影响的信噪比
![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20220920/image.19zvvnqhaiww.webp)


# [tasnet](https://blog.csdn.net/zjuPeco/article/details/106310790)

TasNet的全程是Time-domain Audio Separation Network，它是一个可以end-to-end去train的一个网络。整个网络可以认为由三个部分组成，分别是Encoder，Separator和Decoder。Encoder相当于是一个Fourier Transformer，可以吃未经处理过的mixed audio原始声音信号，然后吐出一个特征维度为512维的特征向量。Separator会吃这个特征向量，然后吐出两个mask，这两个mask再作用到encoder吐出的feature map上，得到两个separated feature map。最后还有一个decoder，decoder吃这两个feature map。吐出separated audio。

![ch3-2-1](https://img-blog.csdnimg.cn/20200524102818902.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3pqdVBlY28=,size_16,color_FFFFFF,t_70#pic_center)

# [TasNet & Conv-TasNet](https://zhuanlan.zhihu.com/p/101235440)

# [Conv-TasNet](https://blog.csdn.net/wjrenxinlei/article/details/107018571?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522163651850816780265422153%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=163651850816780265422153&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-2-107018571.pc_search_result_control_group&utm_term=Conv-TasNet&spm=1018.2226.3001.4187)
