import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

def solve_spectrum(image_path):
    if not os.path.exists(image_path):
        print(f"Error: 文件 {image_path} 不存在")
        return

    # 1. 读取灰度图
    img = cv2.imread(image_path, 0)
    if img is None:
        print("Error: 无法读取图片")
        return

    # 2. 傅里叶变换 (FFT)
    f = np.fft.fft2(img)

    # -------------------------------------------------
    # [关键点 / Key Logic]
    # 标准操作通常包含 fftshift 将低频移至中心。
    # 但针对“象限分裂”的盲水印，我们需要注释掉这行，
    # 直接使用原始的 FFT 结果来还原拼图。
    # -------------------------------------------------
    # fshift = np.fft.fftshift(f)  # Standard method (Disabled)
    fshift = f                     # CTF Solution method

    # 3. 对数变换增强显示 (Log-scale)
    res = 20 * np.log(np.abs(fshift) + 1e-6)

    # 4. 显示结果
    plt.figure(figsize=(10, 6))
    plt.imshow(res, cmap='gray')
    plt.title('Restored Spectrum (No Shift)')
    plt.axis('off')
    
    print("[+] Spectrum restored. Displaying window...")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTF Tool: FFT Spectrum Restorer")
    parser.add_argument("img", help="Path to the challenge image")
    args = parser.parse_args()
    
    solve_spectrum(args.img)