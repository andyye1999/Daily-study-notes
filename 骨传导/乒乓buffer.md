
```c
  	*p_air_in++ = scale_factor_3 * Right_Channel_In2;  	
	Left_Channel_Out1 = (*p_send_out++)/scale_factor_4;
	*p_bone_send_in++ = scale_factor_1 * Left_Channel_In2;
	if(FRM_LEN2*2+air_in<=p_air_in)
	{
    	p_send_out = send_out;
    	p_bone_send_in = bone_send_in; // 将指针指向最初数组的头部 相当于pairin读满了
    	p_air_in = air_in;
    	data_ok = FRM_LEN2;
	}
	if(FRM_LEN2+air_in==p_air_in) // 读一半了
	{
	    data_ok = 0;
	}


if (0 <= data_ok)
{
	for (i = 0; i < FRM_LEN2; i++) in_f32[i] = air_in[data_ok + i];
	send_out[data_ok+i]=air_in[data_ok+i];
	
	
	data_ok = -1;

}



```