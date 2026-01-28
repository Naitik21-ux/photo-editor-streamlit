from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import cv2
import os
import tempfile

def pil_to_cv2(pil_img):
    arr = np.array(pil_img.convert("RGB"))
    return arr[:, :, ::-1].copy()

def cv2_to_pil(cv_img):
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)

def zoom_image(pil_img, scale):
    w, h = pil_img.size
    new_w, new_h = int(w * scale), int(h * scale)
    resized = pil_img.resize((new_w, new_h), Image.LANCZOS)

    if scale > 1:
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        return resized.crop((left, top, left + w, top + h))
    else:
        bg = Image.new("RGB", (w, h), (0, 0, 0))
        bg.paste(resized, ((w - new_w) // 2, (h - new_h) // 2))
        return bg

def enhance_image(pil_img):
    img = pil_img.filter(ImageFilter.UnsharpMask(radius=2, percent=150))
    cv_img = pil_to_cv2(img)
    den = cv2.fastNlMeansDenoisingColored(cv_img, None, 10, 10, 7, 21)
    return cv2_to_pil(den)

def make_ken_burns_video(pil_img, duration=4, fps=25):
    frames = int(duration * fps)
    w, h = pil_img.size
    cv_img = pil_to_cv2(pil_img)

    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    path = tmp.name
    tmp.close()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (w, h))

    if not writer.isOpened():
        raise RuntimeError("VideoWriter failed to open")

    for i in range(frames):
        scale = 1.0 + 0.2 * (i / frames)
        cw, ch = int(w / scale), int(h / scale)
        x, y = (w - cw) // 2, (h - ch) // 2

        frame = cv_img[y:y+ch, x:x+cw]
        frame = cv2.resize(frame, (w, h))
        writer.write(frame)

    writer.release()

    with open(path, "rb") as f:
        video_bytes = f.read()

    os.remove(path)
    return video_bytes


    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    path = tmp.name
    tmp.close()

    writer = cv2.VideoWriter(
        path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    for i in range(frames):
        scale = 1 + 0.2 * (i / frames)
        cw, ch = int(w / scale), int(h / scale)
        x, y = (w - cw) // 2, (h - ch) // 2
        frame = cv_img[y:y+ch, x:x+cw]
        frame = cv2.resize(frame, (w, h))
        writer.write(frame)

    writer.release()
    return path

def adjust_brightness(img, factor):
    return ImageEnhance.Brightness(img).enhance(factor)

def adjust_contrast(img, factor):
    return ImageEnhance.Contrast(img).enhance(factor)

def adjust_sharpness(img, factor):
    return ImageEnhance.Sharpness(img).enhance(factor)

def preset_portrait(img):
    img = adjust_brightness(img, 1.1)
    img = adjust_contrast(img, 1.15)
    img = adjust_sharpness(img, 1.4)
    return img

def preset_night(img):
    img = adjust_brightness(img, 1.3)
    img = adjust_contrast(img, 1.25)
    return img

def preset_vintage(img):
    img = adjust_brightness(img, 0.95)
    img = adjust_contrast(img, 0.85)
    img = adjust_sharpness(img, 0.9)
    return img
