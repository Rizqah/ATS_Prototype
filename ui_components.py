"""
UI Components & Utilities
Reusable components for consistent UX across the application
"""

import streamlit as st
from typing import Optional, List
import time

# ======================================================
# TOAST NOTIFICATIONS
# ======================================================

def show_success_toast(message: str):
    """Show a success toast notification."""
    st.success(f"✅ {message}")


def show_error_toast(message: str):
    """Show an error toast notification with user-friendly formatting."""
    st.error(f"❌ {message}")


def show_warning_toast(message: str):
    """Show a warning toast notification."""
    st.warning(f"⚠️ {message}")


def show_info_toast(message: str):
    """Show an info toast notification."""
    st.info(f"ℹ️ {message}")


# ======================================================
# LOADING STATES & SPINNERS
# ======================================================

def show_loading_spinner(message: str = "Processing..."):
    """
    Show a loading spinner with descriptive message.
    
    Usage:
        with st.spinner(show_loading_spinner("Analyzing resume...")):
            # Long running operation
    """
    return st.spinner(f"⏳ {message}")


def show_processing_steps(steps: List[str]):
    """
    Show a multi-step processing indicator.
    
    Args:
        steps: List of step descriptions
        
    Example:
        show_processing_steps([
            "Extracting text from PDF",
            "Analyzing content structure",
            "Generating match score"
        ])
    """
    for i, step in enumerate(steps, 1):
        st.write(f"**Step {i}/{len(steps)}:** {step}")
        time.sleep(0.3)  # Brief pause for UX


# ======================================================
# CONFIRMATION DIALOGS
# ======================================================

def confirm_logout() -> bool:
    """
    Show logout confirmation dialog.
    
    Returns:
        True if user confirms, False otherwise
    """
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚪 Yes, Logout", use_container_width=True):
            return True
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            return False
    
    return False


def confirm_delete(item_name: str = "this item") -> bool:
    """
    Show delete confirmation dialog.
    
    Args:
        item_name: Name of the item being deleted
        
    Returns:
        True if user confirms, False otherwise
    """
    st.warning(f"⚠️ Are you sure you want to delete {item_name}? This cannot be undone.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Yes, Delete", use_container_width=True, type="primary"):
            return True
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            return False
    
    return False


# ======================================================
# USER-FRIENDLY ERROR MESSAGES
# ======================================================

ERROR_MESSAGES = {
    "file_not_pdf": "Invalid file format. Please upload a PDF file.",
    "file_empty": "The file appears to be empty. Please check the file and try again.",
    "file_too_large": "File size exceeds the limit (max 10 MB). Please use a smaller file.",
    "text_extraction_failed": "Unable to extract text from the PDF. Make sure it's not a scanned image.",
    "invalid_resume": "The document doesn't appear to be a resume. Please check and try again.",
    "invalid_jd": "The job description is too short. Please provide at least 50 characters.",
    "api_error": "Service temporarily unavailable. Please try again in a few moments.",
    "invalid_email": "Please enter a valid email address.",
    "password_mismatch": "The passwords do not match.",
    "email_exists": "This email is already registered. Please use a different email.",
    "invalid_credentials": "Email or password is incorrect.",
    "profile_incomplete": "Please complete your profile before proceeding.",
    "no_data": "No data available. Please check your input and try again.",
}


def show_error(error_key: str, custom_message: Optional[str] = None):
    """
    Show a user-friendly error message.
    
    Args:
        error_key: Key from ERROR_MESSAGES dict
        custom_message: Optional custom message to override default
    """
    message = custom_message or ERROR_MESSAGES.get(error_key, "An error occurred. Please try again.")
    show_error_toast(message)


# ======================================================
# DRAG & DROP FILE UPLOAD
# ======================================================

def show_file_upload_area(
    label: str = "Upload File",
    file_type: str = "pdf",
    help_text: Optional[str] = None,
    key: Optional[str] = None
):
    """
    Show a file upload area with drag-and-drop support.
    
    Args:
        label: Upload field label
        file_type: File type to accept (pdf, docx, txt, etc.)
        help_text: Help text to display
        key: Streamlit key for the uploader
        
    Returns:
        Uploaded file object or None
    """
    if help_text is None:
        help_text = f"Drag and drop your {file_type.upper()} file or click to browse"
    
    uploaded_file = st.file_uploader(
        label,
        type=[file_type],
        help=help_text,
        key=key
    )
    
    return uploaded_file


# ======================================================
# NAVIGATION COMPONENTS
# ======================================================

def show_top_navigation(current_page: str = ""):
    """
    Show a persistent top navigation bar.
    
    Args:
        current_page: Name of current page to highlight
    """
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.4rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    nav_pages = [
        ("Dashboard", "pages/04_careerhub_dashboard.py"),
        ("Profile", "pages/05_careerhub_profile.py"),
        ("Generate CV", "pages/06_careerhub_cv_generator.py"),
        ("CV Tracker", "pages/07_careerhub_tracker.py"),
        ("CV Match", "pages/08_careerhub_cv_matcher.py"),
    ]

    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.markdown("### ✨ TrueFit")
    with top_right:
        if st.session_state.get("user_email"):
            st.caption(st.session_state.user_email)

    nav_cols = st.columns(len(nav_pages) + 1)
    for idx, (label, page_path) in enumerate(nav_pages):
        button_type = "primary" if current_page == label else "secondary"
        with nav_cols[idx]:
            if st.button(label, key=f"nav_{label}_{current_page}", use_container_width=True, type=button_type):
                st.switch_page(page_path)

    with nav_cols[len(nav_pages)]:
        if hasattr(st, "popover"):
            with st.popover("👤", use_container_width=True):
                if st.button("👤 Profile", key=f"acct_profile_{current_page}", use_container_width=True):
                    st.switch_page("pages/05_careerhub_profile.py")
                if st.button("⚙️ Settings", key=f"acct_settings_{current_page}", use_container_width=True):
                    st.switch_page("pages/11_security_settings.py")
                if st.button("❓ Help & FAQ", key=f"acct_help_{current_page}", use_container_width=True):
                    st.switch_page("pages/10_help_faq.py")
                if st.button("🚪 Logout", key=f"acct_logout_{current_page}", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.user_email = None
                    st.session_state.user_role = None
                    st.switch_page("pages/03_careerhub_auth.py")
        else:
            if st.button("🚪 Logout", key=f"acct_logout_fallback_{current_page}", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_email = None
                st.session_state.user_role = None
                st.switch_page("pages/03_careerhub_auth.py")

    st.divider()


def show_breadcrumbs(breadcrumb_list: List[str]):
    """
    Show breadcrumb navigation.
    
    Args:
        breadcrumb_list: List of breadcrumb items (e.g., ["Home", "Profile", "Edit"])
    """
    breadcrumb_text = " / ".join(breadcrumb_list)
    st.caption(f"📍 {breadcrumb_text}")


# ======================================================
# PROGRESS INDICATORS
# ======================================================

def show_progress_bar(current: int, total: int, label: str = "Progress"):
    """
    Show a progress bar with percentage.
    
    Args:
        current: Current progress value
        total: Total value
        label: Label for the progress bar
    """
    percentage = min(current / total, 1.0) if total > 0 else 0
    st.progress(percentage, text=f"{label}: {percentage*100:.0f}%")


def show_step_progress(current_step: int, total_steps: int, steps_list: List[str]):
    """
    Show step-by-step progress with labels.
    
    Args:
        current_step: Current step number (1-indexed)
        total_steps: Total number of steps
        steps_list: List of step names
    """
    col_containers = st.columns(total_steps)
    
    for i, (col, step) in enumerate(zip(col_containers, steps_list)):
        with col:
            step_num = i + 1
            if step_num < current_step:
                status = "✅"
            elif step_num == current_step:
                status = "🔄"
            else:
                status = f"{step_num}"
            
            st.markdown(f"<p style='text-align: center;'>{status}</p>", unsafe_allow_html=True)
            st.caption(f"<p style='text-align: center; font-size: 0.8em;'>{step}</p>", unsafe_allow_html=True)


# ======================================================
# EMPTY STATES
# ======================================================

def show_empty_state(
    icon: str = "📭",
    title: str = "No Data",
    description: str = "Nothing to display",
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
):
    """
    Show a helpful empty state message.
    
    Args:
        icon: Emoji icon to display
        title: Title of empty state
        description: Description text
        action_label: Label for CTA button
        action_callback: Callback function for button
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.write("")
        st.markdown(f"<h2 style='text-align: center;'>{icon}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #94a3b8;'>{description}</p>", unsafe_allow_html=True)
        
        if action_label and action_callback:
            st.write("")
            if st.button(action_label, use_container_width=True, type="primary"):
                action_callback()


# ======================================================
# FORM HELPERS
# ======================================================

def show_required_marker():
    """Show a red asterisk for required fields."""
    st.markdown("<span style='color: red;'>*</span>", unsafe_allow_html=True)


def save_form_draft(form_key: str, data: dict):
    """
    Auto-save form draft to session state.
    
    Args:
        form_key: Unique key for the form
        data: Form data to save
    """
    if f"draft_{form_key}" not in st.session_state:
        st.session_state[f"draft_{form_key}"] = data
    else:
        st.session_state[f"draft_{form_key}"].update(data)


def load_form_draft(form_key: str) -> dict:
    """
    Load form draft from session state.
    
    Args:
        form_key: Unique key for the form
        
    Returns:
        Form data dict or empty dict if no draft
    """
    return st.session_state.get(f"draft_{form_key}", {})


# ======================================================
# METRIC CARDS
# ======================================================

def show_metric_card(label: str, value: str, icon: str = ""):
    """
    Show a styled metric card.
    
    Args:
        label: Metric label
        value: Metric value
        icon: Emoji icon
    """
    st.markdown(f"""
    <div style='
        background: #1e293b;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #60a5fa;
        margin-bottom: 10px;
    '>
        <p style='margin: 0; color: #94a3b8; font-size: 0.9em;'>{icon} {label}</p>
        <h3 style='margin: 5px 0 0 0; color: #e2e8f0; font-size: 1.8em;'>{value}</h3>
    </div>
    """, unsafe_allow_html=True)


# ======================================================
# CONSISTENT BUTTON STYLES
# ======================================================

def button_primary(label: str, key: Optional[str] = None, **kwargs) -> bool:
    """Primary button (blue/green gradient)."""
    return st.button(
        label,
        key=key,
        use_container_width=kwargs.get("use_container_width", False),
        type="primary",
        **{k: v for k, v in kwargs.items() if k != "use_container_width"}
    )


def button_secondary(label: str, key: Optional[str] = None, **kwargs) -> bool:
    """Secondary button (neutral)."""
    return st.button(
        label,
        key=key,
        use_container_width=kwargs.get("use_container_width", False),
        **{k: v for k, v in kwargs.items() if k != "use_container_width"}
    )


def button_danger(label: str, key: Optional[str] = None, **kwargs) -> bool:
    """Danger button (red)."""
    return st.button(
        label,
        key=key,
        use_container_width=kwargs.get("use_container_width", False),
        **{k: v for k, v in kwargs.items() if k != "use_container_width"}
    )
