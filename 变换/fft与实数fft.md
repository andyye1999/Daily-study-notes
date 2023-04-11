


```cpp

void fft(float *x, float *y, short n, short sign)
{
	short i, j, k, l, m, n1, n2;
	float c, c1, e, s, s1, t, tr, ti;

	//x实部 y虚部

	for (j = i = 1; i<32; i++)
	{
		m = i; 
		j = 2 * j;
		if (j == n) break;	 //m=log2n
	}
	// 码位倒序
	for (n1 = n - 1, j = 0, i = 0; i<n1; i++)
	{
		if (i<j)  //倒位序大于自然序，将存储单元的内容互换
		{
			tr = x[j];
			ti = y[j];
			x[j] = x[i];
			y[j] = y[i];
			x[i] = tr;
			y[i] = ti;
		}
		k = n / 2;
		while (k<(j + 1))
		{
			j = j - k;
			k = k / 2;
		}
		j = j + k;
	}
	for (n1 = l = 1; l <= m; l++)  // 第一层 每一级的蝶形运算 共m=log2n级 
	{
		n1 = 2 * n1;    //第m级 2^m
		n2 = n1 / 2;    // 2^m-1
		e = 3.1415926535897932384626433832795f / n2;
		c = 1.0;
		s = 0.0;
		c1 = cos(e);
		s1 = -sign*sin(e);
		for (j = 0; j<n2; j++)   //每一组的蝶形运算     “距离”L=2^m-1  
		{
			for (i = j; i<n; i += n1)   //1个蝶形运算
			{
				k = i + n2;
				tr = c*x[k] - s*y[k];
				ti = c*y[k] + s*x[k];
				x[k] = x[i] - tr;
				y[k] = y[i] - ti;
				x[i] = x[i] + tr;
				y[i] = y[i] + ti;
			}
			t = c;
			c = c*c1 - s*s1;
			s = t*s1 + s*c1;
		}
	}
	if (sign == -1)
	{
		for (i = 0; i<n; i++) { x[i] /= n; y[i] /= n; }
	}
}
```
# [RealFFT算法铺垫](https://www.funcwj.cn/2017/05/27/realfft-1/)

```c
void c_fft(float* bone_buf, short isign)
{
	short i, j, k, ii, jj, kk, ji, kj;
	float ftmp, re7, im7;

	/* Rearrange the input array in bit reversed order */
	for (i = j = 0; i < FFT_LEN - 2; i += 2)
	{
		if (j > i)
		{
			ftmp = bone_buf[i];
			bone_buf[i] = bone_buf[j];
			bone_buf[j] = ftmp;

			ftmp = bone_buf[i + 1];
			bone_buf[i + 1] = bone_buf[j + 1];
			bone_buf[j + 1] = ftmp;
		}
		k = FFT_LEN / 2;
		while (j >= k)
		{
			j -= k;
			k >>= 1;
		}
		j += k;
	}

	/* The FFT part */
	if (isign == 1)
	{
		for (i = 0; i < NUM_STAGE; i++) //i is stage counter
		{
			jj = 2 << i;	//FFT size
			kk = 4 << i;	//2*FFT size
			ii = (short)(FFT_LEN >> 1 >> i);	//2*number of FFT's

			for (j = 0; j < jj; j += 2) //j is sample counter
			{
				ji = j * ii;  //ji is phase table index
				for (k = j; k < FFT_LEN; k += kk) //k is butterfly top
				{
					kj = k + jj; //kj is butterfly bottom

					// Butterfly computations
					re7 = bone_buf[kj] * (float)phs_tbl[ji] - bone_buf[kj + 1] * (float)phs_tbl[ji + 1];
					im7 = bone_buf[kj + 1] * (float)phs_tbl[ji] + bone_buf[kj] * (float)phs_tbl[ji + 1];
					bone_buf[kj] = (bone_buf[k] - re7) / 2;
					bone_buf[kj + 1] = (bone_buf[k + 1] - im7) / 2;
					bone_buf[k] = (bone_buf[k] + re7) / 2;
					bone_buf[k + 1] = (bone_buf[k + 1] + im7) / 2;
				}
			}
		}
	}
	else //The IFFT part
	{
		for (i = 0; i < NUM_STAGE; i++) //i is stage counter
		{
			jj = 2 << i;	//FFT size
			kk = 4 << i;	//2*FFT size
			ii = (short)(FFT_LEN >> 1 >> i);	//2*number of FFT's

			for (j = 0; j < jj; j += 2) //j is sample counter
			{
				ji = j * ii;	//ji is phase table index
				for (k = j; k < FFT_LEN; k += kk) //k is butterfly top
				{
					kj = k + jj;				//kj is butterfly bottom

					//Butterfly computations
					re7 = bone_buf[kj] * (float)phs_tbl[ji] + bone_buf[kj + 1] * (float)phs_tbl[ji + 1];
					im7 = bone_buf[kj + 1] * (float)phs_tbl[ji] - bone_buf[kj] * (float)phs_tbl[ji + 1];
					bone_buf[kj] = bone_buf[k] - re7;
					bone_buf[kj + 1] = bone_buf[k + 1] - im7;
					bone_buf[k] = bone_buf[k] + re7;
					bone_buf[k + 1] = bone_buf[k + 1] + im7;
				}
			}
		}
	}
}

void r_fft(float* bone_buf, short isign)
{
	int	i, j;
	float re8, im8, re9, im9;

	/* The FFT part */
	if (isign == 1)
	{
		/* Perform the complex FFT */
		c_fft(bone_buf, isign);

		/* First, handle the DC and foldover frequencies */
		/* X(0) and X(N/2) */
		re8 = bone_buf[0];
		re9 = bone_buf[1];
		bone_buf[0] = re8 + re9;
		bone_buf[1] = re8 - re9;

		/* Now, handle the remaining positive frequencies */
		for (i = 2; i <= FFT_LEN / 2; i += 2)
		{
			j = FFT_LEN - i;
			re8 = bone_buf[i] + bone_buf[j];
			im8 = bone_buf[i + 1] - bone_buf[j + 1];
			re9 = bone_buf[i + 1] + bone_buf[j + 1];
			im9 = bone_buf[j] - bone_buf[i];

			bone_buf[i] = (re8 + (float)phs_tbl[i] * re9 - (float)phs_tbl[i + 1] * im9) / 2;
			bone_buf[i + 1] = (im8 + (float)phs_tbl[i] * im9 + (float)phs_tbl[i + 1] * re9) / 2;
			bone_buf[j] = (re8 + (float)phs_tbl[j] * re9 + (float)phs_tbl[j + 1] * im9) / 2;
			bone_buf[j + 1] = (-im8 - (float)phs_tbl[j] * im9 + (float)phs_tbl[j + 1] * re9) / 2;
		}
	}
	else /* The IFFT part */
	{
		/* First, handle the DC and foldover frequencies */

		re8 = bone_buf[0];
		re9 = bone_buf[1];
		bone_buf[0] = (re8 + re9) / 2;
		bone_buf[1] = (re8 - re9) / 2;

		/* Now, handle the remaining positive frequencies */
		for (i = 2; i <= FFT_LEN / 2; i += 2)
		{
			j = FFT_LEN - i;
			re8 = bone_buf[i] + bone_buf[j];
			im8 = bone_buf[i + 1] - bone_buf[j + 1];
			re9 = -bone_buf[i + 1] - bone_buf[j + 1];
			im9 = -bone_buf[j] + bone_buf[i];

			bone_buf[i] = (re8 + (float)phs_tbl[i] * re9 + (float)phs_tbl[i + 1] * im9) / 2;
			bone_buf[i + 1] = (im8 + (float)phs_tbl[i] * im9 - (float)phs_tbl[i + 1] * re9) / 2;
			bone_buf[j] = (re8 + (float)phs_tbl[j] * re9 - (float)phs_tbl[j + 1] * im9) / 2;
			bone_buf[j + 1] = (-im8 - (float)phs_tbl[j] * im9 - (float)phs_tbl[j + 1] * re9) / 2;
		}
		/* Perform the complex IFFT */
		c_fft(bone_buf, isign);
	}
}
```
# [RealFFT算法实现](https://www.funcwj.cn/2017/05/28/realfft-2/)


![image](https://cdn.staticaly.com/gh/andyye1999/image-hosting@master/20230108/image.6xx5xnne3x00.webp)

![image](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/image.71gks8ztr780.webp)


# IFFT程序实现


![99114626071eab5a921974c54807ee5](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230411/99114626071eab5a921974c54807ee5.rebwb1vz200.webp)