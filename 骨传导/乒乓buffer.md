
```c
  	*p_air_in++ = scale_factor_3 * Right_Channel_In2;  	
	Left_Channel_Out1 = (*p_send_out++)/scale_factor_4;
	
	if(FRM_LEN2*2+air_in<=p_air_in)
	{
    	p_send_out = send_out;
    	p_air_in = air_in;
    	data_ok = FRM_LEN2;
	}
	if(FRM_LEN2+air_in==p_air_in)
	{
	    data_ok = 0;
	}



for (i = 0; i < FRM_LEN2; i++) in_f32[i] = air_in[data_ok + i];
send_out[data_ok+i]=air_in[data_ok+i];

```