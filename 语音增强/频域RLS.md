
平滑处理，相当于**IIR形式** rab 互相关 raa 自相关 其中参考信号d(n)相当于bone_buf
RLS自适应滤波器的输入信号x(n)为air_buf参考麦信号 e(n)=d(n)-h(n)*x(n)  即e(n)=bone(n)-h(n)*air(n)  h(n)为RLS滤波器系数   
RLS中 h(n)迭代公式为 Rm(n)^-1 x Dm(n) 其中Rm(n)为x(n)的自相关函数 Dm(n)为x(n)与d(n)的互相关函数 
在频域是矩阵乘法 矩阵的逆 在频域就是向量相乘和相除 
vv和1-vv 是递归加权的功率谱求法 可以看作IIR滤波器形式
互相关rab= a的转置乘b (Re(a) - jIm(a))*(Re(b) + jIm(b)) 将得到的数虚部和实部分开就是下面的式子 自相关也一样，乘完发现没有虚部了   

递推公式中自相关求逆，在频域就是除法

RLS 在频域上不是N * N了 是1 * 1

代码注释在20220515文件夹内

```c
st->rab[2 * j] = vv * st->rab[2 * j] + alpha * (x[2 * j] * d[2 * j] + x[2 * j + 1] * d[2 * j + 1]);
		st->rab[2 * j + 1] = vv * st->rab[2 * j + 1] + alpha * (-x[2 * j + 1] * d[2 * j] + x[2 * j] * d[2 * j + 1]);
		st->raa[j] = vv * st->raa[j] + alpha * (x[2 * j] * x[2 * j] + x[2 * j + 1] * x[2 * j + 1]);

		err[2 * j] = d[2 * j] - (x[2 * j] * st->rab[2 * j] - x[2 * j + 1] * st->rab[2 * j + 1]) / st->raa[j];   // ���ƹ�ʽ����������棬��Ƶ����ǳ���
		err[2 * j + 1] = d[2 * j + 1] - (x[2 * j + 1] * st->rab[2 * j] + x[2 * j] * st->rab[2 * j + 1]) / st->raa[j];
```

![IMG_3137(20220621-195527)](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/IMG_3137(20220621-195527).3f8ibl5jf120.webp)


![IMG_3136](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/IMG_3136.4h06ez76mx0.webp)


![IMG_3025](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/IMG_3025.72t7ux5sarg0.webp)



![IMG_3026](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/IMG_3026.1ptp2u0i8ds0.webp)


![IMG_3027](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/IMG_3027.48cglv2c9ci0.webp)
![IMG_3029](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/IMG_3029.3x7t7f4cxdi0.webp)
![IMG_3028](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/IMG_3028.3fqtmw8xnfg0.webp)

![AE0E54241100BB3C821748615CFC06AE](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20221029/AE0E54241100BB3C821748615CFC06AE.7d1v8hyup5c0.webp)


![IMG_3016](https://raw.githubusercontent.com/andyye1999/image-hosting/master/20220524/IMG_3016.6gesqckjen80.webp)


# 陈老师找到的书籍


![IMG_20230627_165532](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230627/IMG_20230627_165532.vajk3svv4ao.webp)


# 基于线性卷积的频域LMS自适应算法 FLMS

![IMG_20230627_165817](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230627/IMG_20230627_165817.69bhbquku600.webp)


![IMG_20230627_165823](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230627/IMG_20230627_165823.67vl9m9s7eo0.webp)


![IMG_20230627_165850](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230627/IMG_20230627_165850.5k4byt4yy340.webp)


![IMG_20230627_165854](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230627/IMG_20230627_165854.10axgfm7hc1c.webp)

# 频域RLS 退化为一阶时的算法

![IMG_20230627_165910](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230627/IMG_20230627_165910.6d9kc1c1a1c0.webp)


![IMG_20230627_165916](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230627/IMG_20230627_165916.wsp58x62m34.webp)


![IMG_20230627_165948](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230627/IMG_20230627_165948.5qlowytz2w80.webp)



![IMG_20230627_165952](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230627/IMG_20230627_165952.4wl5bysxwya0.webp)