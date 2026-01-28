import streamlit as st
from PIL import Image
from backend import (
    zoom_image,
    enhance_image,
    make_ken_burns_video,
    adjust_brightness,
    adjust_contrast,
    adjust_sharpness
)

# -----------------------
# Page Config
# -----------------------
st.set_page_config(
    page_title="Photo Editor & Enhancer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# Hero Section
# -----------------------
st.markdown("""
<style>
.hero {
    text-align: center;
    padding: 2.5rem 1rem;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 800;
}
.hero p {
    font-size: 1.2rem;
    color: #9aa0a6;
}
</style>

<div class="hero">
    <h1>📸 Photo Editor & Enhancer</h1>
    <p>Zoom • Enhance • Presets • Adjustments • Photo → Video</p>
</div>
""", unsafe_allow_html=True)

# -----------------------
# Upload Image
# -----------------------
uploaded = st.file_uploader(
    "📤 Upload an image",
    type=["jpg", "jpeg", "png"]
)

if not uploaded:
    st.info("⬆ Upload an image to start editing")
    st.stop()

img = Image.open(uploaded).convert("RGB")
edited = img.copy()

# -----------------------
# Sidebar Controls
# -----------------------
st.sidebar.header("🛠 Editing Tools")

# --- Zoom ---
st.sidebar.subheader("🔍 Zoom")
zoom_type = st.sidebar.radio("Zoom type", ["None", "Zoom In", "Zoom Out"])
zoom_factor = st.sidebar.slider("Zoom factor", 1.1, 2.0, 1.2, 0.1)

if zoom_type != "None":
    scale = zoom_factor if zoom_type == "Zoom In" else 1 / zoom_factor
    edited = zoom_image(edited, scale)

# --- Enhance ---
st.sidebar.subheader("✨ Enhance")
if st.sidebar.button("Enhance Quality"):
    with st.spinner("Enhancing image..."):
        edited = enhance_image(edited)

# --- Presets ---
st.sidebar.subheader("🎨 Presets")
preset = st.sidebar.selectbox(
    "Choose preset",
    ["None", "Portrait", "Vivid", "Vintage", "Black & White"]
)

if preset == "Portrait":
    edited = adjust_brightness(edited, 1.1)
    edited = adjust_contrast(edited, 1.2)
    edited = adjust_sharpness(edited, 1.3)

elif preset == "Vivid":
    edited = adjust_brightness(edited, 1.2)
    edited = adjust_contrast(edited, 1.4)

elif preset == "Vintage":
    edited = adjust_brightness(edited, 0.9)
    edited = adjust_contrast(edited, 0.9)

elif preset == "Black & White":
    edited = edited.convert("L").convert("RGB")

# --- Manual Adjustments ---
st.sidebar.subheader("🎚 Manual Adjustments")

brightness = st.sidebar.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
contrast   = st.sidebar.slider("Contrast",   0.5, 2.0, 1.0, 0.1)
sharpness  = st.sidebar.slider("Sharpness",  0.5, 3.0, 1.0, 0.1)

edited = adjust_brightness(edited, brightness)
edited = adjust_contrast(edited, contrast)
edited = adjust_sharpness(edited, sharpness)

# -----------------------
# Before / After Display
# -----------------------
st.markdown("## 🖼 Before & After")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Original")
    st.image(img, use_container_width=True)

with col2:
    st.subheader("Edited")
    st.image(edited, use_container_width=True)

# -----------------------
# Download Button
# -----------------------
st.download_button(
    "⬇ Download Edited Image",
    data=edited.tobytes(),
    file_name="edited_image.jpg",
    mime="image/jpeg"
)

st.divider()

# -----------------------
# Photo → Video
# -----------------------
st.markdown("## 🎞 Photo → Video (Ken Burns Effect)")

duration = st.slider("Video duration (seconds)", 2, 8, 4)
fps = st.selectbox("FPS", [15, 24, 25, 30], index=2)

if st.button("🎬 Generate Video"):
    with st.spinner("Rendering video..."):
        video_bytes = make_ken_burns_video(img, duration, fps)
    st.video(video_bytes)

