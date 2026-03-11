# Color palette
COLORS = {
    "primary": "#00D4FF",       # Cyan accent
    "secondary": "#7B2FFF",     # Purple accent
    "accent": "#FF6B6B",        # Coral for alerts
    "success": "#00E676",       # Green
    "warning": "#FFD93D",       # Yellow
    "background": "#0A0E17",    # Deep dark blue
    "surface": "#12161F",       # Card background
    "surface_light": "#1A1F2E", # Elevated surface
    "border": "#2A3142",        # Subtle borders
    "text": "#F8FAFC",          # Primary text
    "text_muted": "#94A3B8",    # Secondary text
}

def get_global_styles():
    return """
<style>
    /* ===== IMPORT FONTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ===== ROOT VARIABLES ===== */
    :root {
        --primary: #00D4FF;
        --secondary: #7B2FFF;
        --accent: #FF6B6B;
        --success: #00E676;
        --warning: #FFD93D;
        --bg-dark: #0A0E17;
        --surface: #12161F;
        --surface-light: #1A1F2E;
        --border: #2A3142;
        --text: #F8FAFC;
        --text-muted: #94A3B8;
        --gradient-primary: linear-gradient(135deg, #00D4FF 0%, #7B2FFF 100%);
        --gradient-accent: linear-gradient(135deg, #FF6B6B 0%, #FFD93D 100%);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.4);
        --shadow-glow: 0 0 30px rgba(0, 212, 255, 0.15);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }

    /* ===== GLOBAL STYLES ===== */
    .stApp {
        background: var(--bg-dark);
    }

    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }

    /* ===== TYPOGRAPHY ===== */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }

    code, pre, .stCode {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ===== CUSTOM HEADER ===== */
    .quantlab-header {
        text-align: center;
        padding: 3rem 0 2rem;
        margin-bottom: 2rem;
    }

    .quantlab-logo {
        font-size: 3.5rem;
        font-weight: 700;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
    }

    .quantlab-tagline {
        font-size: 1.1rem;
        color: var(--text-muted);
        font-weight: 400;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* ===== GLASSMORPHISM CARDS ===== */
    .glass-card {
        background: linear-gradient(135deg, rgba(26, 31, 46, 0.8) 0%, rgba(18, 22, 31, 0.9) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 0.75rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-sm);
    }

    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: rgba(0, 212, 255, 0.2);
    }

    .glass-card-accent {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(123, 47, 255, 0.05) 100%);
        border-left: 3px solid var(--primary);
    }

    /* ===== FEATURE CARDS ===== */
    .feature-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 2rem;
        height: 100%;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .feature-card:hover {
        border-color: var(--primary);
        transform: translateY(-4px);
        box-shadow: var(--shadow-glow);
    }

    .feature-card:hover::before {
        opacity: 1;
    }

    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }

    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.75rem;
    }

    .feature-desc {
        color: var(--text-muted);
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* ===== METRICS ===== */
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        transition: all 0.3s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-sm);
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: var(--text) !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
    }

    /* ===== STAT CARD ===== */
    .stat-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        border-color: var(--primary);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
    }

    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stat-label {
        color: var(--text-muted);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.5rem;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: var(--bg-dark) !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.02em;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.4) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        box-shadow: none !important;
    }

    .stButton > button[kind="secondary"]:hover {
        border-color: var(--primary) !important;
        color: var(--primary) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text) !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2) !important;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--surface) 0%, var(--bg-dark) 100%);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] .block-container {
        padding: 2rem 1.5rem;
    }

    .sidebar-header {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 1.5rem 0 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border);
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface);
        border-radius: var(--radius-md);
        padding: 0.25rem;
        gap: 0.25rem;
        border: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-sm);
        color: var(--text-muted);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text);
        background: var(--surface-light);
    }

    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary) !important;
        color: var(--bg-dark) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        font-weight: 500;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--primary);
    }

    /* ===== DATAFRAMES ===== */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        overflow: hidden;
    }

    .stDataFrame thead th {
        background: var(--surface) !important;
        color: var(--text) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--primary) !important;
    }

    .stDataFrame tbody tr:hover {
        background: var(--surface-light) !important;
    }

    /* ===== ALERTS/CALLOUTS ===== */
    .stAlert {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        border-left: 4px solid var(--primary) !important;
    }

    .stSuccess {
        border-left-color: var(--success) !important;
    }

    .stWarning {
        border-left-color: var(--warning) !important;
    }

    .stError {
        border-left-color: var(--accent) !important;
    }

    /* ===== DIVIDER ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 2rem 0;
    }

    /* ===== SLIDERS ===== */
    .stSlider > div > div > div > div {
        background: var(--gradient-primary) !important;
    }

    .stSlider > div > div > div > div > div {
        background: var(--text) !important;
        border: 2px solid var(--primary) !important;
    }

    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div > div > div {
        background: var(--gradient-primary) !important;
    }

    /* ===== CHECKBOX/RADIO ===== */
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p,
    .stRadio > label > div[data-testid="stMarkdownContainer"] > p {
        color: var(--text);
    }

    /* ===== SPINNER ===== */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }

    /* ===== TOOLTIPS ===== */
    [data-baseweb="tooltip"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }

    /* ===== ANIMATIONS ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-fade-in {
        animation: fadeIn 0.5s ease forwards;
    }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); }
        50% { box-shadow: 0 0 40px rgba(0, 212, 255, 0.4); }
    }

    .pulse-glow {
        animation: pulse-glow 2s ease-in-out infinite;
    }

    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }

        .quantlab-logo {
            font-size: 2.5rem;
        }

        .stat-value {
            font-size: 2rem;
        }
    }
</style>
"""


def inject_styles():
    import streamlit as st
    st.markdown(get_global_styles(), unsafe_allow_html=True)


def create_stat_card(value: str, label: str, icon: str = "") -> str:
    return f"""
    <div class="stat-card">
        <div class="stat-value">{icon}{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """


# SVG icons for feature cards
ICONS = {
    "pricing": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22,7 13.5,15.5 8.5,10.5 2,17"/><polyline points="16,7 22,7 22,13"/></svg>',
    "portfolio": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>',
    "chain": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    "forecast": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>',
}


def create_feature_card(icon_key: str, title: str, description: str) -> str:
    icon_svg = ICONS.get(icon_key, '')
    return f"""
    <div class="feature-card">
        <span class="feature-icon" style="color: var(--primary);">{icon_svg}</span>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    """


def create_glass_card(content: str, accent: bool = False) -> str:
    accent_class = " glass-card-accent" if accent else ""
    return f'<div class="glass-card{accent_class}">{content}</div>'
