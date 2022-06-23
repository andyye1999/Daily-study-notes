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
