一、安装iTerm2  
方式1官网下载：https://iterm2.com/downloads.html可视化安装  
二、配置iTerm2的主题  
1、访问 iTerm2 主题网站  
下载 zip 包并解压至本地，找到 schemes 文件夹，里面就是 iTerm2 的所有主题了  
[图片]  
2、在item2中配置导入配色和主题  
Profiles -> Colors -> Color Presets选择Import选项找到schemes文件夹里面的主题  
再次打开就有一堆主题了可选择了  

下载oh-my-zsh  
```
sudo apt install zsh -y  

#Install oh-my-zsh via curl
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
四、安装Oh-my-Zsh插件  
1、zsh-autosuggestions（需下载安装）：高亮显示所有支持的命令  
使用国内镜像的下载安装  
git clone https://gitcode.com/gh_mirrors/zs/zsh-autosuggestions.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions  
2、zsh-syntax-highlighting（需下载安装）：根据输入的历史命令进行智能提示  
使用国内镜像的下载安装  
git clone https://gitcode.com/gh_mirrors/zs/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting  
[图片]  
3、修改加入插件配置  
//打开文件  
vim ~/.zshrc//在文件中加入插件  
plugins=(git z zsh-autosuggestions zsh-syntax-highlighting)  
//第一个z插件是自带的，用于快速跳转文件 可带上//wq退出文件编辑//执行配置  
source ~/.zshrc  
https://blog.csdn.net/weixin_44904331/article/details/135651136  
https://segmentfault.com/a/1190000046097967  

item2 ssh配置密码  

https://www.cnblogs.com/mingcoder/p/18561848  

# Pip 镜像源  
```
-i https://pypi.tuna.tsinghua.edu.cn/simple   
```

# Vscode shell调试python  
```
https://zhuanlan.zhihu.com/p/677246646
https://blog.csdn.net/Defiler_Lee/article/details/134254405
https://zhuanlan.zhihu.com/p/1929911003484788223
```

# pdb调试 python  
https://www.zhihu.com/question/580713865/answer/3537650518  
https://zhuanlan.zhihu.com/p/37294138  

不要在vscode 的终端 改conda环境 容易有bug  

# vim配置  
https://blog.csdn.net/MBuger/article/details/68954053  

# Huggingface linux登录自己账号 下载测试集  
1️⃣ 获取你的 Access Token  
1. 在浏览器登录 Hugging Face  
2. 打开 Settings → Access Tokens：  
https://huggingface.co/settings/tokens  
3. 点击 Create new token：  
  - 给它一个名字，比如 server-token  
  - 选择 Read 权限（下载数据集足够用）  
4. 复制生成的 Token（形如：hf_xxxxxxxxxxxxxxxxx）  

---  
2️⃣ 在服务器登录 Hugging Face 账号  
方法一：命令行登录（推荐）  
在服务器终端运行：  
BASH  
1huggingface-cli login  
然后粘贴你刚才的 token 回车即可。  
这会在服务器用户的 ~/.huggingface/token 文件中保存登录信息，之后 任何使用 transformers / datasets 的代码都会自动带上你的身份  


# 环境变量  
export PYTHONPATH=$PWD:$PYTHONPATH  
export HF_DATASETS_CACHE=  设置hf cahce地址  

# kaldi对齐  
https://zhuanlan.zhihu.com/p/433536900  

transformer库 GenerationMixin  
https://blog.csdn.net/fydw_715/article/details/146947130  

# Tts 洗数据  
https://www.icviews.cn/semiCommunity/postDetail/11071  

# Wenet  
https://github.com/wenet-e2e/wenet/issues/2097   
Torch 支持force align https://docs.pytorch.org/audio/master/tutorials/forced_alignment_for_multilingual_data_tutorial.html ctc的  
https://github.com/wenet-e2e/wenet/issues/2094 dataset   

## 1dcnn 和 2dcnn  
语音任务里有两种使用CNN的方式，一种是2D-Conv，一种是1D-Conv：  
- 2D-Conv: 输入数据看作是深度(通道数）为1，高度为F（Fbank特征维度，idim），宽度为T（帧数）的一张图.  
- 1D-Conv: 输入数据看作是深度(通道数）为F（Fbank特征维度)，高度为1，宽度为T（帧数）的一张图.  
Kaldi中著名的TDNN就是是1D-Conv，在Wenet中采用2D-Conv来实现降采样。  
