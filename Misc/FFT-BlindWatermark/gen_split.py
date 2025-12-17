import cv2
import numpy as np
import argparse
import os

def generate_split_spectrum(image_path):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    img = cv2.imread(image_path, 0)
    
    # FFT
    f = np.fft.fft2(img)
    
    # [模拟错误 / Simulation]
    # 使用 fftshift 导致水印分裂
    fshift = np.fft.fftshift(f) 
    
    # Log-scale
    res = 20 * np.log(np.abs(fshift) + 1e-6)

    # Normalize to 0-255 for saving
    res_norm = cv2.normalize(res, None, 0, 255, cv2.NORM_MINMAX)
    res_uint8 = np.uint8(res_norm)
    
    output_name = "split_anomaly.jpg"
    cv2.imwrite(output_name, res_uint8)
    print(f"[+] Generated anomaly image: {output_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("img", help="Original image path")
    args = parser.parse_args()
    
    generate_split_spectrum(args.img)