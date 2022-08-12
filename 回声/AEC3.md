# [AEC个人学习串讲之AEC3：概述及非核心部分（上）](https://mp.weixin.qq.com/s?__biz=MzUzMDg2NTczMQ==&mid=2247484943&idx=2&sn=90da38338481c956f4718f2d09f270f7&chksm=fa4a0d23cd3d84352ca400d5f60a4d853e9e4de17b2bf5c79a39d9d6c8fb04d9de06a929376b&scene=178&cur_album_id=2094993082898317315#rd)
# **框图**

![图片](https://mmbiz.qpic.cn/mmbiz_png/6pIgP2IfBVmauEOEY1CqzMDFF5Yb76YWnuLhvs96acT9OKEgj8zGLdHJZ6qIe8XNAvF6pnGRAxH90yCjgvpqqA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

参考信号：送往时延估计、AEC的状态计算

采集信号：送往时延估计、线性滤波器、AEC的状态计算

线性滤波器使用时延对齐后的参考信号和采集信号进行处理；线性滤波器处理后的结果送往NLP模块，最终得到处理结果。
