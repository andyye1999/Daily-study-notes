# 自适应滤波
[[FDAF自适应滤波器算法综述]]
[[FXLMS]]
# webrtc
[[webrtc_ns]]
[[webrtc-aec]]

# 降噪

[[语音增强理论与实践]]

# 深度学习

[[基于深度学习的语音增强概述]]

# 波束形成

[[MVDR]]
[[GSC]]

# 骨导项目

## 频域RLS

[[频域RLS]]

## 谱线增强

对每帧每个频段计算能量，算自相关和互相关
然后根据VAD结果为语音和相关性（互相关/自相关）大，采用快步长进行参考麦的能量平滑
找到前12个较大的能量，将剩余的比第12个小的所有频点能量相加取平均
将它除以每个频点能量开根号，与主麦信号相乘

```cpp
// Spectral line enhancement.
	for (ref_avg = 0, j = 1; j < FFT_LEN / 2; j++)
	{
		ener_ref[j] = ref_dat_buf[2 * j] * ref_dat_buf[2 * j] + ref_dat_buf[2 * j + 1] * ref_dat_buf[2 * j + 1];
		ref_avg += ener_ref[j] / (FFT_LEN / 2);
		ener_send[j] = send_dat_buf[2 * j] * send_dat_buf[2 * j] + send_dat_buf[2 * j + 1] * send_dat_buf[2 * j + 1];
	}
	for (corr_ref_ref = corr_send_send = corr_ref_send = 0, j = 1; j < FFT_LEN / 2; j++)
	{
		corr_ref_ref += ener_ref[j] * ener_ref[j];
		corr_send_send += ener_send[j] * ener_send[j];
		corr_ref_send += ener_ref[j] * ener_send[j];
	}
	if ((corr_ref_send*corr_ref_send > corr_ref_ref*corr_send_send*0.9f) && (TRUE == send_update_flag))
	{
		alpha = FAST_STEP_SIZE;
	}
	else
	{
		alpha = SLOW_STEP_SIZE;
	}
	for (vv = 1.0f - alpha, j = 1; j < FFT_LEN / 2; j++)
	{
		st->ener_ref_aver[j] = max(vv * st->ener_ref_aver[j] + alpha * ener_ref[j], INE);
	}
	st->send_frame_cnt = min(st->send_frame_cnt + 1, 64);
	if (1 == st->sle_flag)
	{
		for (i = 0; i < 100; i++) hist[i] = 0;
		for (j = 1; j < FFT_LEN / 2; j++)
		{
			vv = 10 * (float)log10(1.0 + st->ener_ref_aver[j]);// 直方图，统计前12个较大的能量
			hist[(Word16)vv]++;
		}
		for (freq_num = 0, i = 99; i > 0; i--)
		{
			freq_num += hist[i];
			if (freq_num > 12) break;//找到第12个
		}
		vv = (float)pow(10, i / 10.0);//反推回能量
		for (aver_level = freq_num = 0, j = 1; j < FFT_LEN / 2; j++)
		{
			if (st->ener_ref_aver[j] < vv)
			{
				aver_level += st->ener_ref_aver[j];
				freq_num++;
			}
		}
		if (freq_num == 0)
		{
			freq_num = FFT_LEN / 2 - 1;
			for (aver_level = 0, j = 1; j < FFT_LEN / 2; j++) aver_level += st->ener_ref_aver[j];
		}
		aver_level /= freq_num;
		for (i = 1; i < FFT_LEN / 2; i++)
		{
			vv = (float)sqrt(aver_level / st->ener_ref_aver[i]);
			if (vv > 1.0f) vv = 1.0f;
			vv = (float)sqrt(vv);
			vv = (float)sqrt(vv);
			send_dat_buf[2 * i] *= vv;
			send_dat_buf[2 * i + 1] *= vv;
		}
	}
```


## 硬件

### 改进webrtc aec

fft换成自己的
不能轻易使用malloc，dsp容易溢出
nlp中步长的判决简单化

### 定点化



# 阵列

[[阵列软著总结]]
