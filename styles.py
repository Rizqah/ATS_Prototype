"""
Global CSS Stylesheet
Consistent styling and responsive design across the application
"""

GLOBAL_CSS = """
<style>
/* ========================================================
   ROOT VARIABLES & GENERAL STYLING
   ======================================================== */

:root {
    --color-primary: #60a5fa;      /* Blue */
    --color-success: #10b981;      /* Green */
    --color-danger: #ef4444;       /* Red */
    --color-warning: #f59e0b;      /* Orange */
    --color-bg-dark: #0f172a;      /* Slate 900 */
    --color-bg-light: #1e293b;     /* Slate 800 */
    --color-text-light: #e2e8f0;   /* Slate 200 */
    --color-text-muted: #94a3b8;   /* Slate 400 */
    --color-border: #334155;       /* Slate 700 */
}

* {
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--color-bg-dark);
    color: var(--color-text-light);
}

/* ========================================================
   STREAMLIT OVERRIDES
   ======================================================== */

.stAppHeader {
    display: none;
}

.stMainBlockContainer {
    padding-top: 2rem;
}

/* ========================================================
   BUTTONS - CONSISTENT STYLING
   ======================================================== */

button {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

[data-testid="stBaseButton-primary"] > button {
    background: linear-gradient(90deg, #60a5fa, #34d399) !important;
    border: none !important;
    color: white !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
}

[data-testid="stBaseButton-primary"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(96, 165, 250, 0.3) !important;
}

[data-testid="stBaseButton-secondary"] > button {
    background: var(--color-bg-light) !important;
    border: 2px solid var(--color-border) !important;
    color: var(--color-text-light) !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
}

[data-testid="stBaseButton-secondary"] > button:hover {
    border-color: var(--color-primary) !important;
    transform: translateY(-2px);
}

/* ========================================================
   TEXT ELEMENTS
   ======================================================== */

h1 {
    color: var(--color-primary);
    margin-bottom: 1rem !important;
    font-weight: 800 !important;
}

h2 {
    color: var(--color-text-light);
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
    font-weight: 700 !important;
}

h3 {
    color: var(--color-text-light);
    font-weight: 700 !important;
}

p {
    color: var(--color-text-muted);
    line-height: 1.6;
    font-weight: 500;
}

a {
    color: var(--color-primary);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* ========================================================
   FORM ELEMENTS
   ======================================================== */

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select {
    background-color: var(--color-bg-light) !important;
    border: 2px solid var(--color-border) !important;
    border-radius: 8px !important;
    color: var(--color-text-light) !important;
    padding: 10px 12px !important;
    font-size: 0.95rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
    border-color: var(--color-primary) !important;
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1) !important;
}

/* ========================================================
   ALERTS & NOTIFICATIONS
   ======================================================== */

[data-testid="stAlert"] {
    border-radius: 8px !important;
    border-left: 4px solid !important;
    padding: 15px !important;
    background: var(--color-bg-light) !important;
}

[data-testid="stAlert"] > div {
    color: var(--color-text-light) !important;
}

/* Success */
[data-testid="stAlert"] > div > div > .e1f1d6gp0:contains("✅") {
    border-left-color: var(--color-success) !important;
}

/* Error */
[data-testid="stAlert"] > div > div > .e1f1d6gp0:contains("❌") {
    border-left-color: var(--color-danger) !important;
}

/* Warning */
[data-testid="stAlert"] > div > div > .e1f1d6gp0:contains("⚠️") {
    border-left-color: var(--color-warning) !important;
}

/* Info */
[data-testid="stAlert"] > div > div > .e1f1d6gp0:contains("ℹ️") {
    border-left-color: var(--color-primary) !important;
}

/* ========================================================
   CARDS & CONTAINERS
   ======================================================== */

.card {
    background: var(--color-bg-light);
    border: 2px solid var(--color-border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
}

.card:hover {
    border-color: var(--color-primary);
    box-shadow: 0 10px 30px rgba(96, 165, 250, 0.1);
}

.card-elevated {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 2px solid var(--color-border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

/* ========================================================
   SIDEBAR
   ======================================================== */

[data-testid="stSidebar"] {
    background: var(--color-bg-light);
}

[data-testid="stSidebar"] > div {
    background: var(--color-bg-light);
}

/* ========================================================
   TABLES
   ======================================================== */

[data-testid="stDataFrame"] {
    background: var(--color-bg-light) !important;
}

[data-testid="stDataFrame"] th {
    background: var(--color-primary) !important;
    color: white !important;
}

/* ========================================================
   PROGRESS BAR
   ======================================================== */

[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, #60a5fa, #34d399) !important;
}

/* ========================================================
   DIVIDER
   ======================================================== */

hr {
    border-color: var(--color-border) !important;
}

/* ========================================================
   RESPONSIVE DESIGN
   ======================================================== */

/* Tablets */
@media (max-width: 768px) {
    h1 {
        font-size: 2rem !important;
    }

    h2 {
        font-size: 1.5rem !important;
    }

    .stColumn {
        min-width: 100% !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
}

/* Mobile */
@media (max-width: 480px) {
    body {
        font-size: 0.95rem;
    }

    h1 {
        font-size: 1.5rem !important;
    }

    h2 {
        font-size: 1.2rem !important;
    }

    .stButton > button {
        padding: 10px 16px !important;
        font-size: 0.9rem !important;
    }

    [data-testid="stColumn"] {
        flex-wrap: wrap;
    }

    .cta-container {
        flex-direction: column !important;
    }

    .cta-card {
        min-width: 100% !important;
    }

    .features {
        grid-template-columns: 1fr !important;
    }
}

/* ========================================================
   UTILITIES
   ======================================================== */

.text-center {
    text-align: center;
}

.text-muted {
    color: var(--color-text-muted);
}

.mt-0 { margin-top: 0 !important; }
.mt-1 { margin-top: 0.5rem !important; }
.mt-2 { margin-top: 1rem !important; }
.mt-3 { margin-top: 1.5rem !important; }
.mt-4 { margin-top: 2rem !important; }

.mb-0 { margin-bottom: 0 !important; }
.mb-1 { margin-bottom: 0.5rem !important; }
.mb-2 { margin-bottom: 1rem !important; }
.mb-3 { margin-bottom: 1.5rem !important; }
.mb-4 { margin-bottom: 2rem !important; }

.p-2 { padding: 1rem !important; }
.p-3 { padding: 1.5rem !important; }
.p-4 { padding: 2rem !important; }

.rounded { border-radius: 8px !important; }
.rounded-lg { border-radius: 12px !important; }
.rounded-xl { border-radius: 16px !important; }

.shadow { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important; }
.shadow-md { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important; }
.shadow-lg { box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1) !important; }

/* ========================================================
   ANIMATIONS
   ======================================================== */

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.animate-fade-in {
    animation: fadeIn 0.5s ease-out;
}

.animate-slide-in {
    animation: slideInRight 0.5s ease-out;
}

.animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

</style>
"""


def inject_global_css():
    """Inject global CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
