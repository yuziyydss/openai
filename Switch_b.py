import fitz  # PyMuPDF
from PIL import Image

doc = fitz.open("123.pdf")
for page_num in range(len(doc)):
    pix = doc[page_num].get_pixmap(dpi=300)  # 转成高分辨率图片
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # 颜色反转
    inverted = Image.eval(img, lambda x: 255 - x)

    # 转灰度再二值化
    bw = inverted.convert("L").point(lambda x: 0 if x < 128 else 255, "1")

    bw.save(f"page_{page_num+1}.png")

# 如果要合并回 PDF：
bw_images = [Image.open(f"page_{i+1}.png") for i in range(len(doc))]
bw_images[0].save("output.pdf", save_all=True, append_images=bw_images[1:])
