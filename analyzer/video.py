import os
import tempfile
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

def _write_uploaded_to_temp(uploaded_file):
    suffix=os.path.splitext(uploaded_file.name)[-1] or ".mp4"
    tmp=tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded_file.read())
    tmp.close()
    return tmp.name

def _bgr_to_rgb(img_bgr:np.ndarray):
    return cv2.cvtColor(img_bgr,cv2.COLOR_BGR2RGB)

def _resize_max(img:np.ndarray,max_side:int=512):
    h,w=img.shape[:2]
    scale=max_side/max(h,w)
    if scale>=1.0:
        return img
    new_w,new_h=int(w*scale),int(h*scale)
    return cv2.resize(img,(new_w,new_h),interpolation=cv2.INTER_AREA)

def _to_jpeg_bytes(img_rgb:np.ndarray,quality:int=90):
    pil=Image.fromarray(img_rgb)
    buf=BytesIO()
    pil.save(buf,format="JPEG",quality=quality,optimize=True)
    return buf.getvalue()

def sample_video_frames(uploaded_file,sampling_fps:int=1,max_frames:int=64):
    """
    Save uploaded video to a temp file, sample ~sampling_fps frames (time-based),
    cap at max_frames, return frames (RGB np arrays), thumbnails (JPEG bytes), and metadata.
    """
    path=_write_uploaded_to_temp(uploaded_file)
    cap=cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError("Unable to open video. Try a different file/codec.")

    native_fps=cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    duration_sec=total_frames/native_fps if native_fps>0 and total_frames>0 else 0.0

    step=max(1,int(round(native_fps/float(sampling_fps)))) if sampling_fps>0 else 1

    frames_rgb:list[np.ndarray]=[]
    thumbs_jpg:list[bytes]=[]
    idx=0

    while True:
        ok,frame_bgr=cap.read()
        if not ok:
            break

        if idx%step==0:
            rgb=_bgr_to_rgb(frame_bgr)
            rgb_small=_resize_max(rgb,512)
            frames_rgb.append(rgb_small)
            thumbs_jpg.append(_to_jpeg_bytes(rgb_small, quality=85))
            if len(frames_rgb)>=max_frames:
                break
        idx+=1

    cap.release()

    try:
        os.remove(path)
    except Exception:
        pass

    meta=dict(
        native_fps=float(native_fps),
        total_frames=int(total_frames),
        duration_sec=float(duration_sec),
        width=int(width),
        height=int(height),
        sampling_fps=int(sampling_fps),
        sampled_count=len(frames_rgb), )
    return dict(frames=frames_rgb,thumbs=thumbs_jpg,meta=meta)
