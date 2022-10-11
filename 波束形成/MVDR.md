MVDR中文名字叫**最小均方无畸变响应**，**最小方差无失真响应**它的精髓就体现在无畸变上。什么叫无畸变呢，就是在对感兴趣方位（声源方向）的信号无失真地输出，这意味着该算法可以直接当做语音后端算法(如ASR)的前处理过程。MVDR波束形成器的公式推导并不复杂，我们这里简单的介绍一下。MVDR由Capon于1969年提出，也称为Capon波束形成器，它的目标是对感兴趣方位的信号无失真输出的同时使波束输出的噪声方差最小。波束输出噪声方差记为

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcTCxapPSsCvtbS6aPeErGyrUCfzyq1wroiaJ82TjOsKUx8m0m8urXZ0EMNgHSnyLgbNnnN3xpccSQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

其中**w**是加权向量，**Rn**是噪声的协方差矩阵。于是MVDR可以描述为

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcTCxapPSsCvtbS6aPeErGyI4gTUOTC4vWCkVc2xgC2kjAMcT03px2uefqdicwGLuf4P9blIx92pMg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

采用拉格朗日算子，对上述有约束的优化问题进行求解，定义函数  

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/R3j7FT5mhhcTCxapPSsCvtbS6aPeErGyibFXS3TicEJd19t49TEoibya5OOnStglQbnu047ibL3cnWX7iapC7LqJvYQ/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)

对**w**求导，并令其导数为**0**有  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhcTCxapPSsCvtbS6aPeErGy3p2FeEy59ZibM6b5QRGoRoSKuAygJt5JLFTgHZ5SZryRQBnGt1xfBHg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

代入公式（2）中的约束条件得到

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhfuv2hzIfibxChkeKLDt76CWxeKAXsuC57hMfLiayyN0y3I7XCYcnhYLsXgtJOhFmUGMPUhCTfsQboA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

把公式（5）代入公式（4）解得MVDR的权重为

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhfuv2hzIfibxChkeKLDt76CWLJS4cgBzgibc5fIjJnhoPrwa3MYHU8OTAicK3dhmKVGIuibiaG3f0ricTSw/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

若噪声场为空间白噪声，那么MVDR退化成常规波束成形。公式（6）的权重计算需要知道噪声的协方差矩阵，但有时无法估计出噪声的协方差矩阵，直接使用接受数据的协方差矩阵进行计算，即  

![图片](https://mmbiz.qpic.cn/mmbiz_png/R3j7FT5mhhfuv2hzIfibxChkeKLDt76CWNOGgTZmSsgITUzFK6DdSATFvdE8bzmKFcnRiatrJOdlHtmsp8kCPBMQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

有的地方称上式的波束形成器为最小功率无失真响应（Minimum Power Distortionless Response, MPDR）。MVDR的效果依赖于导向矢量和数据接受协方差矩阵精确与否，在理想环境下能够抑制干扰，最大程度提升信干噪比。

### [nvdr](https://www.funcwj.cn/2020/01/13/intro-on-se-and-ss/)

信号模型上远场条件下相比单通道要更加复杂，需要考虑声源位置，信号传播，干扰噪声，房间混响等因素。一般的，麦克风<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>i</mi>
  <mo>&#x2208;</mo>
  <mo fence="false" stretchy="false">{</mo>
  <mn>0</mn>
  <mo>,</mo>
  <mo>&#x22EF;</mo>
  <mo>,</mo>
  <mi>M</mi>
  <mo>&#x2212;</mo>
  <mn>1</mn>
  <mo fence="false" stretchy="false">}</mo>
</math>处接收到的信号yi可以建模为：<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <mtable displaystyle="true">
    <mlabeledtr>
      <mtd id="mjx-eqn:23">
        <mtext>(23)</mtext>
      </mtd>
      <mtd>
        <mtable displaystyle="true" columnalign="right left" columnspacing="0em" rowspacing="3pt">
          <mtr>
            <mtd>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">y</mi>
                </mrow>
                <mi>i</mi>
              </msub>
            </mtd>
            <mtd>
              <mi></mi>
              <mo>=</mo>
              <munder>
                <mo data-mjx-texclass="OP">&#x2211;</mo>
                <mrow data-mjx-texclass="ORD">
                  <mi>j</mi>
                </mrow>
              </munder>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">x</mi>
                </mrow>
                <mrow data-mjx-texclass="ORD">
                  <mi>i</mi>
                  <mi>j</mi>
                </mrow>
              </msub>
              <mo>+</mo>
              <mrow data-mjx-texclass="ORD">
                <mi mathvariant="bold">n</mi>
              </mrow>
            </mtd>
          </mtr>
          <mtr>
            <mtd></mtd>
            <mtd>
              <mi></mi>
              <mo>=</mo>
              <munder>
                <mo data-mjx-texclass="OP">&#x2211;</mo>
                <mrow data-mjx-texclass="ORD">
                  <mi>j</mi>
                </mrow>
              </munder>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">r</mi>
                </mrow>
                <mrow data-mjx-texclass="ORD">
                  <mi>i</mi>
                  <mi>j</mi>
                </mrow>
              </msub>
              <mo>&#x2217;</mo>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">s</mi>
                </mrow>
                <mi>j</mi>
              </msub>
              <mo>+</mo>
              <munder>
                <mo data-mjx-texclass="OP">&#x2211;</mo>
                <mi>k</mi>
              </munder>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">r</mi>
                </mrow>
                <mrow data-mjx-texclass="ORD">
                  <mi>i</mi>
                  <mi>k</mi>
                </mrow>
              </msub>
              <mo>&#x2217;</mo>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">n</mi>
                </mrow>
                <mi>k</mi>
              </msub>
              <mo>+</mo>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">n</mi>
                </mrow>
                <mi>i</mi>
              </msub>
              <mo>,</mo>
            </mtd>
          </mtr>
        </mtable>
      </mtd>
    </mlabeledtr>
  </mtable>
</math>
其中<math xmlns="http://www.w3.org/1998/Math/MathML">
  <msub>
    <mrow data-mjx-texclass="ORD">
      <mi mathvariant="bold">x</mi>
    </mrow>
    <mrow data-mjx-texclass="ORD">
      <mi>i</mi>
      <mi>j</mi>
    </mrow>
  </msub>
  <mo>=</mo>
  <msub>
    <mrow data-mjx-texclass="ORD">
      <mi mathvariant="bold">r</mi>
    </mrow>
    <mrow data-mjx-texclass="ORD">
      <mi>i</mi>
      <mi>j</mi>
    </mrow>
  </msub>
  <mo>&#x2217;</mo>
  <msub>
    <mrow data-mjx-texclass="ORD">
      <mi mathvariant="bold">s</mi>
    </mrow>
    <mi>j</mi>
  </msub>
  <mo>,</mo>
  <mi>j</mi>
  <mo>&#x2208;</mo>
  <mo fence="false" stretchy="false">{</mo>
  <mn>0</mn>
  <mo>,</mo>
  <mo>&#x22EF;</mo>
  <mo>,</mo>
  <mi>C</mi>
  <mo>&#x2212;</mo>
  <mn>1</mn>
  <mo fence="false" stretchy="false">}</mo>
</math> <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>C</mi>
</math>表示说话人个数，∗表示卷积操作，<math xmlns="http://www.w3.org/1998/Math/MathML">
  <msub>
    <mrow data-mjx-texclass="ORD">
      <mi mathvariant="bold">r</mi>
    </mrow>
    <mrow data-mjx-texclass="ORD">
      <mi>i</mi>
      <mi>j</mi>
    </mrow>
  </msub>
  <mo>,</mo>
  <msub>
    <mrow data-mjx-texclass="ORD">
      <mi mathvariant="bold">r</mi>
    </mrow>
    <mrow data-mjx-texclass="ORD">
      <mi>i</mi>
      <mi>k</mi>
    </mrow>
  </msub>
</math> 分别为声源j和定向噪声k到麦克风i处的传输函数，ni表示麦克风i处的环境噪声。可以使用STFT将上式在频域表示为：
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <mtable displaystyle="true">
    <mlabeledtr>
      <mtd id="mjx-eqn:24">
        <mtext>(24)</mtext>
      </mtd>
      <mtd>
        <mtable displaystyle="true" columnalign="right left" columnspacing="0em" rowspacing="3pt">
          <mtr>
            <mtd>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">y</mi>
                </mrow>
                <mrow data-mjx-texclass="ORD">
                  <mi>i</mi>
                  <mo>,</mo>
                  <mi>f</mi>
                </mrow>
              </msub>
            </mtd>
            <mtd>
              <mi></mi>
              <mo>=</mo>
              <munder>
                <mo data-mjx-texclass="OP">&#x2211;</mo>
                <mi>j</mi>
              </munder>
              <msub>
                <mi>r</mi>
                <mrow data-mjx-texclass="ORD">
                  <mi>i</mi>
                  <mi>j</mi>
                  <mo>,</mo>
                  <mi>f</mi>
                </mrow>
              </msub>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">s</mi>
                </mrow>
                <mrow data-mjx-texclass="ORD">
                  <mi>j</mi>
                  <mo>,</mo>
                  <mi>f</mi>
                </mrow>
              </msub>
              <mo>+</mo>
              <munder>
                <mo data-mjx-texclass="OP">&#x2211;</mo>
                <mi>k</mi>
              </munder>
              <msub>
                <mi>r</mi>
                <mrow data-mjx-texclass="ORD">
                  <mi>i</mi>
                  <mi>k</mi>
                  <mo>,</mo>
                  <mi>f</mi>
                </mrow>
              </msub>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">n</mi>
                </mrow>
                <mrow data-mjx-texclass="ORD">
                  <mi>k</mi>
                  <mo>,</mo>
                  <mi>f</mi>
                </mrow>
              </msub>
              <mo>+</mo>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">n</mi>
                </mrow>
                <mrow data-mjx-texclass="ORD">
                  <mi>i</mi>
                  <mo>,</mo>
                  <mi>f</mi>
                </mrow>
              </msub>
            </mtd>
          </mtr>
          <mtr>
            <mtd></mtd>
            <mtd>
              <mi></mi>
              <mo>=</mo>
              <munder>
                <mo data-mjx-texclass="OP">&#x2211;</mo>
                <mi>j</mi>
              </munder>
              <msub>
                <mi>r</mi>
                <mrow data-mjx-texclass="ORD">
                  <mi>i</mi>
                  <mi>j</mi>
                  <mo>,</mo>
                  <mi>f</mi>
                </mrow>
              </msub>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">s</mi>
                </mrow>
                <mrow data-mjx-texclass="ORD">
                  <mi>j</mi>
                  <mo>,</mo>
                  <mi>f</mi>
                </mrow>
              </msub>
              <mo>+</mo>
              <msub>
                <mrow data-mjx-texclass="ORD">
                  <mi mathvariant="bold">n</mi>
                </mrow>
                <mrow data-mjx-texclass="ORD">
                  <mi>f</mi>
                </mrow>
              </msub>
              <mo>.</mo>
            </mtd>
          </mtr>
        </mtable>
      </mtd>
    </mlabeledtr>
  </mtable>
</math>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <msub>
    <mrow data-mjx-texclass="ORD">
      <mi mathvariant="bold">y</mi>
    </mrow>
    <mrow data-mjx-texclass="ORD">
      <mi>i</mi>
      <mo>,</mo>
      <mi>f</mi>
    </mrow>
  </msub>
  <mo>,</mo>
  <msub>
    <mrow data-mjx-texclass="ORD">
      <mi mathvariant="bold">s</mi>
    </mrow>
    <mrow data-mjx-texclass="ORD">
      <mi>j</mi>
      <mo>,</mo>
      <mi>f</mi>
    </mrow>
  </msub>
  <mo>,</mo>
  <msub>
    <mrow data-mjx-texclass="ORD">
      <mi mathvariant="bold">n</mi>
    </mrow>
    <mi>f</mi>
  </msub>
  <mo>&#x2208;</mo>
  <msup>
    <mrow data-mjx-texclass="ORD">
      <mi mathvariant="double-struck">C</mi>
    </mrow>
    <mrow data-mjx-texclass="ORD">
      <mi>T</mi>
    </mrow>
  </msup>
</math>     
  
f表示频率索引。在信号处理中，通常习惯以yt,f=[y0,tf,⋯,yM−1,tf]为一个独立的观测向量，上式还可以重写为：
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <mtable displaystyle="true">
    <mlabeledtr>
      <mtd id="mjx-eqn:25">
        <mtext>(25)</mtext>
      </mtd>
      <mtd>
        <msub>
          <mrow data-mjx-texclass="ORD">
            <mi mathvariant="bold">y</mi>
          </mrow>
          <mrow data-mjx-texclass="ORD">
            <mi>t</mi>
            <mo>,</mo>
            <mi>f</mi>
          </mrow>
        </msub>
        <mo>=</mo>
        <munder>
          <mo data-mjx-texclass="OP">&#x2211;</mo>
          <mi>j</mi>
        </munder>
        <msub>
          <mrow data-mjx-texclass="ORD">
            <mi mathvariant="bold">r</mi>
          </mrow>
          <mrow data-mjx-texclass="ORD">
            <mi>j</mi>
            <mo>,</mo>
            <mi>f</mi>
          </mrow>
        </msub>
        <mo>&#x22C5;</mo>
        <msub>
          <mi>s</mi>
          <mrow data-mjx-texclass="ORD">
            <mi>j</mi>
            <mo>,</mo>
            <mi>t</mi>
            <mi>f</mi>
          </mrow>
        </msub>
        <mo>+</mo>
        <msub>
          <mrow data-mjx-texclass="ORD">
            <mi mathvariant="bold">n</mi>
          </mrow>
          <mrow data-mjx-texclass="ORD">
            <mi>t</mi>
            <mo>,</mo>
            <mi>f</mi>
          </mrow>
        </msub>
        <mo>,</mo>
      </mtd>
    </mlabeledtr>
  </mtable>
</math>




