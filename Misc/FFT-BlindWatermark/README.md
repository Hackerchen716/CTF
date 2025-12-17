# 🕵️‍♂️ Blind Watermark Quadrant Restorer
> **基于 FFT 频谱逆向思维的盲水印修复方案 / A CTF solution for FFT-shift anomalies**

![Python](https://img.shields.io/badge/Language-Python3-blue?logo=python&logoColor=white)
![Category](https://img.shields.io/badge/Category-Misc%20%2F%20Forensics-orange)
![Tech](https://img.shields.io/badge/Tech-FFT%20%26%20OpenCV-green)
![Status](https://img.shields.io/badge/Status-Solved-success)

<table>
  <tr>
    <td><strong>Title</strong></td>
    <td>[CTF/Misc] 频域盲水印的象限复原技术：基于 FFT Shift 的逆向思考</td>
  </tr>
  <tr>
    <td><strong>Date</strong></td>
    <td>2025-12-17</td>
  </tr>
  <tr>
    <td><strong>Tags</strong></td>
    <td><code>CTF</code> <code>Digital Signal Processing</code> <code>Python</code> <code>FFT</code></td>
  </tr>
  <tr>
    <td><strong>Description</strong></td>
    <td>针对单图频域盲水印题目中，因 FFT 频谱中心化导致的水印分裂问题，提出的一种基于逆向思维的象限复原方案。</td>
  </tr>
</table>

## 📝 摘要 (Abstract)
本文记录了一次 CTF 题目中的特殊案例分析。针对常规频域盲水印工具无法识别的“频谱分裂”现象，提出了一种去除中心化 (De-centering)的逆向复原思路，并提供了通用的自动化验证脚本。

---

## 0x00 问题现象 (Issue Description)

在对一道 CTF 题目样本（单张图片）进行常规的频域盲水印分析时，使用标准二维傅里叶变换（2D-FFT）处理后，频谱可视化结果呈现异常。

目标隐写信息（Flag）并非呈现预期的连续文本，而是被切割并散落在频谱图的四个角落（高频/边缘区域），造成识别困难。

![FFT Spectrum Split Anomaly](fft-spectrum-restoration/split_anomaly.jpg)


## 0x01 技术原理分析 (Technical Analysis)

**1. FFT 的频率分布特性**
在数字图像处理中，使用 `numpy.fft.fft2` 得到的原始频域矩阵，其零频率分量（DC Component）默认位于矩阵的左上角 `(0,0)` 位置。

**2. fftshift 的几何意义**
为了符合光学的中心化视觉习惯，标准流程中通常会调用 `numpy.fft.fftshift` 函数。该操作的数学本质是对角象限交换：
* 第一象限 $\leftrightarrow$ 第三象限
* 第二象限 $\leftrightarrow$ 第四象限
从而将低频分量移动至图像几何中心。

**3. 异常成因推断**
观测到的“分裂”现象表明，出题人在嵌入水印时，是直接基于原始（Raw/Unshifted）的频域矩阵进行操作的，并未进行中心化处理。
因此，解题时的标准 `fftshift` 操作反而破坏了水印的空间连续性，将其“错误地”拆分到了四角。

**Visualizing the Shift (原理图解):**

```text
+-------------------+       +-------------------+
| Q2  (High) | Q1   |       | Q3  (High) | Q4   |
|            | (Low)|       |            | (Low)|
|      RAW   |      |  ==>  |   SHIFTED  |      |
|------------+------|       |------------+------|
| Q3   (Low) | Q4   |       | Q1   (Low) | Q2   |
|            |(High)|       |            |(High)|
+-------------------+       +-------------------+
   (Origin at 0,0)           (Origin at Center)

```
## 0x02 解决方案 (Solution)

**Core Logic:**
在解密流程中Bypass（绕过） `fftshift` 操作，直接对 FFT 的原始输出进行对数变换和可视化，即可实现频谱的象限复原。

**修正后的核心算法：**


```python
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load raw image
img = cv2.imread('challenge.png', 0)

# Perform 2D FFT
f = np.fft.fft2(img)

# [CRITICAL STEP]
# Disable fftshift to maintain original quadrant alignment
# fshift = np.fft.fftshift(f)  <-- Bypassed
fshift = f 

# Log-scale transformation for visibility
res = 20 * np.log(np.abs(fshift) + 1e-6)

# Visualization
plt.imshow(res, cmap='gray')
plt.title('Restored Spectrum')
plt.axis('off')
plt.show()
```

**Result:**
修正逻辑后，Flag 文本成功在频谱中心区域重组，内容清晰可读。

![FFT Spectrum Split Anomaly](fft-spectrum-restoration/spectrum_restored.jpg)


## 0x03 自动化验证脚本 (PoC)

为了快速验证此类单图盲水印是否存在“象限分裂”问题，封装了如下通用 Python 脚本：

```python
import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

def analyze_spectrum(image_path):
    if not os.path.exists(image_path):
        print(f"[-] File not found: {image_path}")
        return

    img = cv2.imread(image_path, 0)
    
    # FFT Calculation
    f = np.fft.fft2(img)
    
    # Strategy: No Shift (Raw Spectrum)
    # Applying strictly to non-centered watermarks
    f_raw = f 
    res = 20 * np.log(np.abs(f_raw) + 1e-6)

    plt.figure(figsize=(8, 8))
    plt.imshow(res, cmap='gray')
    plt.title(f'Spectrum Analysis: {os.path.basename(image_path)}')
    plt.axis('off')
    print("[+] Rendering spectrum...")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTF FFT Spectrum Analyzer")
    parser.add_argument("img", help="Path to the challenge image")
    args = parser.parse_args()
    
    analyze_spectrum(args.img)
```
## 0x04 总结与心得 (Conclusion)

本次案例展示了 CTF Misc 类题目中典型的“工具陷阱”。在处理频域盲水印时，我们不能盲目依赖现成工具的默认行为，而需要理解算法底层的数学意义。

**核心知识点回顾 (Key Takeaways):**

1.  **现象即线索**
    当 FFT 频谱图出现“内容被切割、散落在四角”的现象时，这通常不是数据损坏，而是**坐标系定义不一致**（中心化 vs 非中心化）导致的象限错位。

2.  **逆向思维**
    标准的 `fftshift` 操作是为了符合人类视觉习惯（将低频移至中心）。如果出题者反其道而行之（直接在 Raw 频谱嵌入），解题者必须同步“去中心化”，即**禁用 `fftshift`**。

3.  **脚本化习惯**
    常规的 GUI 工具或一键脚本往往固化了 `fftshift` 流程。掌握 `numpy.fft` 的基础调用，能够让你在面对非标题目时拥有更灵活的调试能力。



---


> **"The real voyage of discovery consists not in seeking new landscapes, but in having new eyes."**
>
> — *Marcell Proust*