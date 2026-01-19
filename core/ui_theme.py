"""
UI theme helpers for Streamlit pages.

Goal: Make the app look polished for demos without changing business logic.
"""

from __future__ import annotations

import streamlit as st
from PIL import Image


_CSS = r"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
  
  :root {
    --cv-bg: #0A0E1A;
    --cv-panel: #111827;
    --cv-panel-2: #0F172A;
    --cv-border: rgba(255, 255, 255, 0.1);
    --cv-text: #F3F4F6;
    --cv-muted: rgba(243, 244, 246, 0.7);
    --cv-primary: #3B82F6;
    --cv-primary-2: #60A5FA;
    --cv-primary-dark: #2563EB;
    --cv-success: #10B981;
    --cv-warning: #F59E0B;
    --cv-danger: #EF4444;
    --cv-purple: #8B5CF6;
    --cv-radius: 20px;
    --cv-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
    --cv-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
  }

  * {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  }

  /* Reduce Streamlit chrome */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header { visibility: hidden; }
  .stDeployButton { display: none; }

  /* Smooth scrolling */
  html { scroll-behavior: smooth; }

  /* Main container */
  .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1400px;
  }

  /* Enhanced Buttons */
  .stButton > button {
    border-radius: 14px !important;
    border: 1px solid var(--cv-border) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: var(--cv-shadow) !important;
    background: rgba(255,255,255,0.05) !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--cv-shadow-lg) !important;
    border-color: rgba(255,255,255,0.2) !important;
  }
  .stButton > button[kind="primary"] {
    border: none !important;
    background: linear-gradient(135deg, var(--cv-primary), var(--cv-primary-2)) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4) !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--cv-primary-dark), var(--cv-primary)) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
    transform: translateY(-2px) !important;
  }

  /* Enhanced Tabs */
  div[data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: rgba(255,255,255,0.02);
    padding: 0.4rem;
    border-radius: 16px;
    border: 1px solid var(--cv-border);
  }
  button[data-baseweb="tab"] {
    border-radius: 12px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    padding: 0.6rem 1.2rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
  }
  button[data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.05) !important;
  }
  button[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(96,165,250,0.15)) !important;
    border-color: rgba(59,130,246,0.3) !important;
    color: var(--cv-primary-2) !important;
  }

  /* Enhanced Cards */
  .cv-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid var(--cv-border);
    border-radius: var(--cv-radius);
    padding: 1.5rem 1.75rem;
    box-shadow: var(--cv-shadow);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
  }
  .cv-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--cv-shadow-lg);
    border-color: rgba(255,255,255,0.15);
  }
  .cv-card + .cv-card { margin-top: 1rem; }
  
  .cv-card-interactive {
    cursor: pointer;
  }
  .cv-card-interactive:hover {
    transform: translateY(-4px) !important;
    border-color: var(--cv-primary) !important;
  }

  /* Typography */
  .cv-title {
    font-size: 1.75rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    margin: 0 0 0.5rem 0;
    background: linear-gradient(135deg, var(--cv-text), var(--cv-muted));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .cv-subtitle {
    color: var(--cv-muted);
    margin: 0;
    font-size: 0.95rem;
    line-height: 1.6;
  }
  .cv-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cv-border), transparent);
    margin: 1.5rem 0;
  }

  /* Enhanced Badges */
  .cv-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    border: 1px solid var(--cv-border);
    background: rgba(255,255,255,0.05);
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--cv-text);
    white-space: nowrap;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    transition: all 0.2s ease;
  }
  .cv-badge:hover {
    transform: scale(1.05);
  }
  .cv-badge--success {
    border-color: rgba(16,185,129,0.4);
    background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.1));
    color: #6EE7B7;
  }
  .cv-badge--warning {
    border-color: rgba(245,158,11,0.4);
    background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.1));
    color: #FCD34D;
  }
  .cv-badge--danger {
    border-color: rgba(239,68,68,0.4);
    background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.1));
    color: #FCA5A5;
  }
  .cv-badge--info {
    border-color: rgba(59,130,246,0.4);
    background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(59,130,246,0.1));
    color: #93C5FD;
  }

  /* Enhanced Hero */
  .cv-hero {
    border-radius: 28px;
    padding: 2.5rem 2rem;
    border: 1px solid var(--cv-border);
    background:
      radial-gradient(1400px 700px at 15% 0%, rgba(59,130,246,0.4), transparent 60%),
      radial-gradient(1000px 600px at 85% 25%, rgba(139,92,246,0.25), transparent 60%),
      radial-gradient(800px 500px at 50% 100%, rgba(16,185,129,0.15), transparent 60%),
      linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    box-shadow: var(--cv-shadow-lg);
    position: relative;
    overflow: hidden;
  }
  .cv-hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 50% 50%, rgba(59,130,246,0.1), transparent 70%);
    pointer-events: none;
  }
  .cv-hero p {
    margin: 0.5rem 0 0 0;
    color: var(--cv-muted);
    font-size: 1.05rem;
    line-height: 1.7;
  }
  .cv-hero .cv-title {
    margin-bottom: 0.5rem;
    font-size: 2.25rem;
  }

  /* Form enhancements */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div > select {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--cv-border) !important;
    border-radius: 12px !important;
    color: var(--cv-text) !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.2s ease !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus,
  .stSelectbox > div > div > select:focus {
    border-color: var(--cv-primary) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
    background: rgba(255,255,255,0.08) !important;
  }

  /* Metric cards */
  [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, var(--cv-text), var(--cv-muted));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  [data-testid="stMetricLabel"] {
    color: var(--cv-muted) !important;
    font-weight: 600 !important;
  }

  /* Success/Error messages */
  .stSuccess, .stError, .stInfo, .stWarning {
    border-radius: 14px !important;
    border: 1px solid var(--cv-border) !important;
    padding: 1rem 1.25rem !important;
    box-shadow: var(--cv-shadow) !important;
  }

  /* Complaint card styling */
  .complaint-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid var(--cv-border);
    border-radius: var(--cv-radius);
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* Image container styling */
  .cv-image-container {
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    border: 1px solid var(--cv-border);
    border-radius: 16px;
    padding: 1rem;
    margin: 1rem 0;
    overflow: hidden;
    width: 100%;
    max-width: 500px;
    height: 400px;
  }

  .cv-image-container img,
  .cv-image-container [data-testid="stImage"] {
    max-width: 100%;
    max-height: 100%;
    width: auto !important;
    height: auto !important;
    object-fit: contain !important;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  }

  .cv-image-container [data-testid="stImage"] img {
    max-width: 100% !important;
    max-height: 100% !important;
    width: auto !important;
    height: auto !important;
    object-fit: contain !important;
  }

  .cv-image-small {
    max-width: 400px;
    height: 300px;
  }

  .cv-image-medium {
    max-width: 550px;
    height: 420px;
  }

  .cv-image-large {
    max-width: 700px;
    height: 550px;
  }
    box-shadow: var(--cv-shadow);
  }
  .complaint-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--cv-shadow-lg);
    border-color: rgba(59,130,246,0.3);
  }

  /* Animations */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .cv-card, .complaint-card {
    animation: fadeIn 0.4s ease-out;
  }

  /* Scrollbar styling */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  ::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.02);
  }
  ::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.15);
    border-radius: 4px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(255,255,255,0.25);
  }
</style>
"""


def inject_global_styles() -> None:
    """Inject global CSS once per session."""
    if st.session_state.get("_cv_styles_injected"):
        return
    st.markdown(_CSS, unsafe_allow_html=True)
    st.session_state["_cv_styles_injected"] = True


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="cv-hero">
          <div class="cv-title">{title}</div>
          <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_start() -> None:
    st.markdown('<div class="cv-card">', unsafe_allow_html=True)


def card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def badge(text: str, variant: str = "info") -> str:
    variant_class = {
        "success": "cv-badge--success",
        "warning": "cv-badge--warning",
        "danger": "cv-badge--danger",
        "info": "cv-badge--info",
    }.get(variant, "cv-badge--info")
    safe_text = (text or "").replace("<", "&lt;").replace(">", "&gt;")
    return f'<span class="cv-badge {variant_class}">{safe_text}</span>'


def complaint_card_start() -> None:
    """Start a styled complaint card container"""
    st.markdown('<div class="complaint-card">', unsafe_allow_html=True)


def complaint_card_end() -> None:
    """End a complaint card container"""
    st.markdown("</div>", unsafe_allow_html=True)


def feature_card(icon: str, title: str, description: str, features: list[str]) -> None:
    """Render a feature card for landing page"""
    features_html = "".join([f'<li style="margin:0.4rem 0;">{f}</li>' for f in features])
    st.markdown(
        f"""
        <div class="cv-card cv-card-interactive">
            <div class="cv-title" style="font-size:1.35rem; margin-bottom:0.5rem;">
                {icon} {title}
            </div>
            <p class="cv-subtitle" style="margin-bottom:1rem;">{description}</p>
            <div class="cv-divider" style="margin:1rem 0;"></div>
            <ul style="margin:0; padding-left:1.2rem; color:rgba(243,244,246,0.85); line-height:1.8;">
                {features_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_image_fixed(image, caption: str = "", size: str = "medium") -> None:
    """
    Display an image in a fixed-size container with proper scaling.
    Uses base64 encoding to ensure proper CSS application.
    
    Args:
        image: PIL Image object or file path string
        caption: Text to display below the image
        size: 'small' (300px), 'medium' (400px), or 'large' (500px)
    """
    import base64
    from io import BytesIO
    
    # Size configuration
    size_config = {
        "small": {"max_width": "400px", "height": "300px"},
        "medium": {"max_width": "550px", "height": "420px"},
        "large": {"max_width": "700px", "height": "550px"}
    }
    config = size_config.get(size, size_config["medium"])
    
    # Convert PIL Image to base64
    if hasattr(image, 'save'):  # It's a PIL Image
        buffer = BytesIO()
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            rgb_image.save(buffer, format='JPEG', quality=90)
        else:
            image.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        src = f"data:image/jpeg;base64,{img_base64}"
    else:
        # It's a file path
        with open(image, 'rb') as f:
            img_base64 = base64.b64encode(f.read()).decode()
        src = f"data:image/jpeg;base64,{img_base64}"
    
    # Create HTML with inline styles for strict control
    caption_html = f'<div style="margin-top:0.75rem; color:rgba(243,244,246,0.7); font-size:0.9rem; text-align:center;">{caption}</div>' if caption else ''
    
    html_content = f'''
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1rem;
        margin: 1rem 0;
        overflow: hidden;
        max-width: {config['max_width']};
        height: {config['height']};
        margin-left: auto;
        margin-right: auto;
    ">
        <img src="{src}" style="
            max-width: 100%;
            max-height: 100%;
            width: auto;
            height: auto;
            object-fit: contain;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        " />
        {caption_html}
    </div>
    '''
    
    st.markdown(html_content, unsafe_allow_html=True)

