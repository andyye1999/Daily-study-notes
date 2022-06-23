# IIR滤波器代码
```cpp
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define PI 3.1415926535
#define ORD2 5
#define NUM 20000
// a是分母系数 b是分子系数
const double b[ORD2] = { 0.009974726636333, -0.03833394460209,     0.05676259683, -0.03833394460209,
   0.009974726636333 };
const double a[ORD2] = { 1,   -3.849826046791,    5.688203849557,   -3.816962873623,
	 0.9830011607069 };

int main()
{
	long i, k;
	double vv, x[ORD2], y[ORD2];
	FILE* fq, * fr;

	for (k = 0; k < ORD2; k++) x[k] = y[k] = 0;

	fopen_s(&fq, "work1.txt", "r");//读方波 100000点数，幅值为10000
	fopen_s(&fr, "work2.txt", "w");//写滤出的正弦波
	//IIR滤波器
	for (i = 0; i < NUM; i++)
	{
		for (k = ORD2 - 1; k > 0; k--) y[k] = y[k - 1];
		for (k = ORD2 - 1; k > 0; k--) x[k] = x[k - 1];
		fscanf_s(fq, "%lf", &x[0]);
		for (vv = x[0] * b[0], k = 1; k < ORD2; k++) vv += x[k] * b[k] - y[k] * a[k];
		y[0] = vv;

		fprintf(fr, "%d\n", (short)vv);
	}
	fclose(fr);
	fclose(fq);
}
```
a是分母系数 b是分子系数,用matlab中的工具箱生成的
ORD2是滤波器系数


# FIR滤波器代码
```cpp
#define H1_TRUE_ORD 18
const double A[H1_TRUE_ORD] = {
	0.06438408701907, -0.02519421477958,  0.04155370049251, -0.04324502214555,
	0.06668137412364, -0.07960309326041,   0.1270708646786,   -0.204569835881,
	 0.6403536044635,   0.6403536044635,   -0.204569835881,   0.1270708646786,
   -0.07960309326041,  0.06668137412364, -0.04324502214555,  0.04155370049251,
   -0.02519421477958,  0.06438408701907
};
int main()
{
	if (fread(&vi, sizeof(Word16), 1L, f_x) != 1L)  break;
	//求d(n)
	//相当于FIR滤波器，右移一位，新的赋值到x[0]
	for (i = H1_TRUE_ORD - 1; i > 0; i--) 
	{
		x_dn[i] = x_dn[i - 1];
	}
	x_dn[0] = vi;
	for (d_n = i = 0; i < H1_TRUE_ORD; i++) 
	{
		d_n = d_n + A[i] * x_dn[i];
	}
}
```

# 区别
IIR优点：取得非常好的通带与阻带衰减，还可得到准确的通带与阻带的bian'yua