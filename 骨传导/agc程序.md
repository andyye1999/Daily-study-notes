```cpp
current_gain = 1;
ener_in = 一帧时域输入能量;
ener_out = 一帧时域输出能量;
target_gain = sqrt(ener_in/(ener_out + 0.000001));
stride = (target_gain - current_gain)/32;
for(i=0; i<L_FRAME; i++) 
	{	
		sum = current_gain*y[i];
		out_sp[i]=(short)max(min(sum, 32767.0f), -32768.0f);
		current_gain += stride;
		if( (stride>0)&&(current_gain>target_gain) ) current_gain = target_gain;
		if( (stride<0)&&(current_gain<target_gain) ) current_gain = target_gain;
	}

```
算能量，以及平滑