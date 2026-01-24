from email.mime import image
import streamlit as st
from PIL import Image
from backend import (
    zoom_image,
    enhance_image,
    make_ken_burns_video,
    adjust_brightness,
    adjust_contrast,
    adjust_sharpness,
    preset_portrait,
    preset_night,
    preset_vintage
)

import io


st.set_page_config(
    page_title="Photo Editor & Enhancer",
    layout="wide"
)

st.markdown(
    """
    <h1 style="text-align:center;">📸 Photo Editor & Enhancer</h1>
    <p style="text-align:center; color: gray;">
    Zoom • Enhance • Presets • Photo → Video
    </p>
    """,
    unsafe_allow_html=True
)

uploaded = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png"]
)

# ✅ EVERYTHING BELOW MUST BE INSIDE THIS
if uploaded:
    img = Image.open(uploaded).convert("RGB")

    # -----------------------
    # Original
    # -----------------------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(img, use_container_width=True)

    # -----------------------
    # Zoom
    # -----------------------
    st.subheader("🔍 Zoom")
    zoom_type = st.radio("Zoom type", ["Zoom In", "Zoom Out"], horizontal=True)
    zoom_factor = st.slider("Zoom factor", 1.1, 2.0, 1.2, 0.1)

    if st.button("Apply Zoom"):
        scale = zoom_factor if zoom_type == "Zoom In" else 1 / zoom_factor
        zoomed = zoom_image(img, scale)

        with col2:
            st.subheader("Zoomed")
            st.image(zoomed, use_container_width=True)

    st.divider()

    # -----------------------
    # Enhance
    # -----------------------
    st.subheader("✨ Enhance Quality")

    if st.button("Enhance Image"):
        with st.spinner("Enhancing image..."):
            @st.cache_data(show_spinner=False)
            def cached_enhance(image):
                return enhance_image(image)

            enhanced = cached_enhance(img)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(img, use_container_width=True)
        with col2:
            st.subheader("Enhanced")
            st.image(enhanced, use_container_width=True)

    st.divider()

    # -----------------------
    # Manual Adjustments
    # -----------------------
    st.subheader("🎚 Manual Adjustments")

    brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
    contrast   = st.slider("Contrast",   0.5, 2.0, 1.0, 0.1)
    sharpness  = st.slider("Sharpness",  0.5, 3.0, 1.0, 0.1)

    edited = adjust_brightness(img, brightness)
    edited = adjust_contrast(edited, contrast)
    edited = adjust_sharpness(edited, sharpness)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(img, use_container_width=True)
    with col2:
        st.subheader("Edited (Live)")
        st.image(edited, use_container_width=True)

    st.divider()

    # -----------------------
    # Preset Filters
    # ----------------------
    st.subheader("🎨 Preset Filters")
    preset = st.radio(
    "Choose a preset",
    ["None", "Portrait", "Night", "Vintage"],
    horizontal=True
    )

    preset_img = edited.copy()

    if preset == "Portrait":
        preset_img = preset_portrait(preset_img)
    elif preset == "Night":
        preset_img = preset_night(preset_img)
    elif preset == "Vintage":
        preset_img = preset_vintage(preset_img)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Before Preset")
        st.image(edited, use_container_width=True)
    with col2:
        st.subheader("After Preset")
        st.image(preset_img, use_container_width=True)
    # IMPORTANT: overwrite edited image
    edited = preset_img

    #------------------------
    #Before / After Comparison
    #------------------------
    st.subheader("🆚 Before / After Comparison")

    compare_value = st.slider(
        "Drag to compare",
        min_value=0,
        max_value=100,
        value=50
    )

    # Resize images to same size
    orig = img.copy()
    edit = edited.copy()

    width, height = orig.size
    cut = int((compare_value / 100) * width)

    # Create comparison image
    comparison = Image.new("RGB", (width, height))
    comparison.paste(orig.crop((0, 0, cut, height)), (0, 0))
    comparison.paste(edit.crop((cut, 0, width, height)), (cut, 0))

    st.image(comparison, use_container_width=True)
    st.divider()

    #-----------------------
    #Download Edited Image
    #-----------------------
    
    st.subheader("⬇️ Download Edited Image")

    buf = io.BytesIO()
    edited.save(buf, format="JPEG", quality=95)
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Image",
        data=byte_im,
        file_name="edited_photo.jpg",
        mime="image/jpeg"
    )
    st.divider()



    # -----------------------
    # Photo to Video
    # -----------------------
    st.subheader("🎞 Photo → Video (Ken Burns)")

    duration = st.slider("Video duration (seconds)", 2, 8, 4)
    fps = st.selectbox("FPS", [15, 24, 25, 30], index=2)

    if st.button("Create Video"):
        with st.spinner("Rendering video..."):
            @st.cache_data(show_spinner=False)
            def cached_video(image, duration, fps):
                return make_ken_burns_video(image, duration, fps)

            video_path = cached_video(img, duration, fps)

        st.video(video_path)
