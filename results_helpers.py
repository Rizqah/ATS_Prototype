"""
Matching & Results Display Helpers
Visual score cards, filtering, sorting, and PDF export utilities
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# ======================================================
# MATCH SCORE VISUALIZATION
# ======================================================

def show_match_score_card(score: float, job_title: str = "", candidate_name: str = ""):
    """
    Show an enhanced match score card with visual indicators.
    
    Args:
        score: Match score (0-1)
        job_title: Job title for context
        candidate_name: Candidate name for context
    """
    score_percent = score * 100
    
    # Determine color and interpretation
    if score_percent >= 80:
        color = "#10b981"  # Green
        status = "Excellent Match"
        icon = "🟢"
        recommendation = "Strong candidate - Ready to interview"
    elif score_percent >= 60:
        color = "#f59e0b"  # Orange
        status = "Good Match"
        icon = "🟡"
        recommendation = "Good fit - Some skill gaps but trainable"
    elif score_percent >= 40:
        color = "#ef4444"  # Red
        status = "Fair Match"
        icon = "🔴"
        recommendation = "Potential - May require additional training"
    else:
        color = "#6b7280"  # Gray
        status = "Poor Match"
        icon = "⚫"
        recommendation = "Not recommended - Significant gaps"
    
    # Display header
    if candidate_name:
        st.subheader(f"📊 {candidate_name}")
    
    # Main score card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.metric("Match Score", f"{score_percent:.1f}%")
    
    with col2:
        # Create visual progress bar
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, {color} {score_percent}%, #e5e7eb {score_percent}%);
            height: 30px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin: 10px 0;
        ">
            {score_percent:.1f}%
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.write(f"**{icon} {status}**")
    
    # Recommendation
    st.info(f"💡 **Recommendation:** {recommendation}")


def show_score_breakdown(
    required_skills_match: float = 0.0,
    experience_match: float = 0.0,
    nice_to_have_match: float = 0.0,
    overall_score: float = 0.0
):
    """
    Show breakdown of match score components.
    
    Args:
        required_skills_match: Percentage of required skills matched (0-1)
        experience_match: Experience level match (0-1)
        nice_to_have_match: Nice-to-have skills match (0-1)
        overall_score: Overall match score (0-1)
    """
    st.subheader("📈 Score Breakdown")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Required Skills",
            f"{required_skills_match*100:.0f}%",
            delta="40% weight" if required_skills_match > 0 else None
        )
    
    with col2:
        st.metric(
            "Experience Level",
            f"{experience_match*100:.0f}%",
            delta="30% weight" if experience_match > 0 else None
        )
    
    with col3:
        st.metric(
            "Nice-to-Have",
            f"{nice_to_have_match*100:.0f}%",
            delta="20% weight" if nice_to_have_match > 0 else None
        )
    
    with col4:
        st.metric(
            "Overall",
            f"{overall_score*100:.1f}%",
            delta="Final Score"
        )


def show_skill_match_details(
    matched_skills: List[str],
    missing_skills: List[str],
    extra_skills: List[str] = None
):
    """
    Show detailed skill matching breakdown.
    
    Args:
        matched_skills: List of matched skills
        missing_skills: List of missing skills
        extra_skills: Additional skills from resume
    """
    st.subheader("🎯 Skill Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Matched Skills", len(matched_skills))
        if matched_skills:
            with st.expander("View matched skills"):
                for skill in matched_skills:
                    st.success(f"✅ {skill}")
    
    with col2:
        st.metric("Missing Skills", len(missing_skills))
        if missing_skills:
            with st.expander("View missing skills"):
                for skill in missing_skills:
                    st.warning(f"⚠️ {skill}")
    
    with col3:
        if extra_skills:
            st.metric("Additional Skills", len(extra_skills))
            with st.expander("View additional skills"):
                for skill in extra_skills:
                    st.info(f"➕ {skill}")


def show_improvement_suggestions(suggestions: List[str], max_items: int = 5):
    """
    Show actionable improvement suggestions.
    
    Args:
        suggestions: List of suggestion strings
        max_items: Maximum suggestions to show initially
    """
    st.subheader("💡 How to Improve Your Match")
    
    if not suggestions:
        st.info("No specific suggestions at this time.")
        return
    
    # Show summary
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{len(suggestions)} improvement opportunities identified**")
    with col2:
        st.write(f"Could improve by up to **20-30%**")
    
    # Show suggestions
    for idx, suggestion in enumerate(suggestions[:max_items], 1):
        st.markdown(f"**{idx}.** {suggestion}")
    
    # Show remaining if any
    if len(suggestions) > max_items:
        with st.expander(f"View {len(suggestions) - max_items} more suggestions"):
            for idx, suggestion in enumerate(suggestions[max_items:], max_items + 1):
                st.markdown(f"**{idx}.** {suggestion}")


# ======================================================
# RECRUITER FILTERING & SORTING
# ======================================================

def show_filter_sidebar(
    candidates_df: pd.DataFrame,
    score_column: str = "match_score"
) -> Tuple[float, float, List[str]]:
    """
    Show filtering controls in sidebar.
    
    Args:
        candidates_df: DataFrame with candidate data
        score_column: Column name for match scores
        
    Returns:
        Tuple of (min_score, max_score, selected_statuses)
    """
    st.sidebar.markdown("### 🔍 Filters")
    
    # Score range slider
    score_range = st.sidebar.slider(
        "Score Range",
        min_value=0.0,
        max_value=100.0,
        value=(0.0, 100.0),
        step=5.0,
        help="Filter candidates by match score"
    )
    
    # Status filter
    if "status" in candidates_df.columns:
        available_statuses = candidates_df["status"].unique().tolist()
        selected_statuses = st.sidebar.multiselect(
            "Application Status",
            available_statuses,
            default=available_statuses,
            help="Filter by application status"
        )
    else:
        selected_statuses = []
    
    return score_range[0], score_range[1], selected_statuses


def apply_filters(
    candidates_df: pd.DataFrame,
    min_score: float = 0.0,
    max_score: float = 100.0,
    statuses: List[str] = None,
    score_column: str = "match_score"
) -> pd.DataFrame:
    """
    Apply filters to candidates dataframe.
    
    Args:
        candidates_df: Original DataFrame
        min_score: Minimum score filter
        max_score: Maximum score filter
        statuses: List of statuses to include
        score_column: Column name for scores
        
    Returns:
        Filtered DataFrame
    """
    filtered_df = candidates_df.copy()
    
    # Apply score filter
    if score_column in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df[score_column] >= min_score) &
            (filtered_df[score_column] <= max_score)
        ]
    
    # Apply status filter
    if statuses and "status" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["status"].isin(statuses)]
    
    return filtered_df


def show_sort_options(
    sort_column: str = "match_score",
    sort_order: str = "descending"
) -> Tuple[str, str]:
    """
    Show sorting controls.
    
    Args:
        sort_column: Current sort column
        sort_order: Current sort order
        
    Returns:
        Tuple of (selected_column, selected_order)
    """
    col1, col2 = st.columns(2)
    
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ["Match Score", "Name", "Date Added", "Score (High to Low)"],
            index=0,
            help="Choose what to sort by"
        )
    
    with col2:
        sort_direction = st.selectbox(
            "Order",
            ["Descending", "Ascending"],
            index=0,
            help="Sort order"
        )
    
    return sort_by, sort_direction


def sort_candidates(
    candidates_df: pd.DataFrame,
    sort_by: str = "Match Score",
    order: str = "Descending"
) -> pd.DataFrame:
    """
    Sort candidates dataframe.
    
    Args:
        candidates_df: DataFrame to sort
        sort_by: Column to sort by
        order: Sort order (Ascending/Descending)
        
    Returns:
        Sorted DataFrame
    """
    sorted_df = candidates_df.copy()
    ascending = order == "Ascending"
    
    if sort_by == "Match Score" and "match_score" in sorted_df.columns:
        sorted_df = sorted_df.sort_values("match_score", ascending=ascending)
    elif sort_by == "Name" and "candidate_name" in sorted_df.columns:
        sorted_df = sorted_df.sort_values("candidate_name", ascending=ascending)
    elif sort_by == "Date Added" and "created_at" in sorted_df.columns:
        sorted_df = sorted_df.sort_values("created_at", ascending=ascending)
    
    return sorted_df


def show_candidates_table(
    candidates_df: pd.DataFrame,
    columns_to_show: List[str] = None
):
    """
    Display candidates in a nice table format.
    
    Args:
        candidates_df: DataFrame with candidate data
        columns_to_show: Columns to display
    """
    if candidates_df.empty:
        st.info("No candidates match the current filters.")
        return
    
    if columns_to_show:
        display_df = candidates_df[columns_to_show]
    else:
        display_df = candidates_df
    
    # Format score column if present
    if "match_score" in display_df.columns:
        display_df = display_df.copy()
        display_df["match_score"] = display_df["match_score"].apply(
            lambda x: f"{x*100:.1f}%" if isinstance(x, float) else x
        )
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ======================================================
# BATCH PROCESSING PROGRESS
# ======================================================

def show_batch_progress(current: int, total: int, current_file: str = ""):
    """
    Show batch processing progress.
    
    Args:
        current: Current file number
        total: Total files
        current_file: Name of current file being processed
    """
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        progress = current / total
        st.progress(progress)
    
    with col2:
        st.metric("Progress", f"{current}/{total}")
    
    with col3:
        st.metric("Remaining", total - current)
    
    if current_file:
        st.caption(f"📖 Processing: {current_file}")


def show_processing_stats(
    total_files: int,
    processed: int,
    succeeded: int,
    failed: int,
    elapsed_time: float = 0.0
):
    """
    Show batch processing statistics.
    
    Args:
        total_files: Total files in batch
        processed: Files processed so far
        succeeded: Successful processes
        failed: Failed processes
        elapsed_time: Time elapsed in seconds
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", total_files)
    
    with col2:
        st.metric("Processed", processed)
    
    with col3:
        st.metric("Successful", succeeded, delta=f"{(succeeded/total_files*100):.0f}%")
    
    with col4:
        st.metric("Failed", failed, delta=f"{(failed/total_files*100):.0f}%" if failed > 0 else None)
    
    if elapsed_time > 0:
        st.caption(f"⏱️ Time elapsed: {elapsed_time:.1f} seconds")


# ======================================================
# PDF EXPORT UTILITIES
# ======================================================

def export_match_report_to_pdf(
    candidate_name: str,
    match_score: float,
    job_title: str,
    matched_skills: List[str],
    missing_skills: List[str],
    suggestions: List[str],
    timestamp: str = None
) -> Optional[bytes]:
    """
    Generate a PDF report of match analysis.
    
    Args:
        candidate_name: Name of candidate
        match_score: Match score (0-1)
        job_title: Job title being matched against
        matched_skills: List of matched skills
        missing_skills: List of missing skills
        suggestions: List of improvement suggestions
        timestamp: Report timestamp
        
    Returns:
        PDF bytes or None if failed
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        import io
        
        # Create PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#60a5fa'),
            spaceAfter=30,
            alignment=1
        )
        
        # Title
        story.append(Paragraph("TrueFit Match Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Header info
        header_data = [
            ["Candidate Name", candidate_name],
            ["Position", job_title],
            ["Match Score", f"{match_score*100:.1f}%"],
            ["Report Date", timestamp or datetime.now().strftime("%Y-%m-%d %H:%M")]
        ]
        
        header_table = Table(header_data, colWidths=[2*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Matched Skills
        story.append(Paragraph("Matched Skills", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        if matched_skills:
            for skill in matched_skills[:10]:
                story.append(Paragraph(f"✓ {skill}", styles['Normal']))
        else:
            story.append(Paragraph("No matched skills", styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Missing Skills
        story.append(Paragraph("Skills to Develop", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        if missing_skills:
            for skill in missing_skills[:10]:
                story.append(Paragraph(f"• {skill}", styles['Normal']))
        else:
            story.append(Paragraph("No critical skills missing", styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Suggestions
        if suggestions:
            story.append(Paragraph("Improvement Suggestions", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for i, suggestion in enumerate(suggestions[:5], 1):
                story.append(Paragraph(f"{i}. {suggestion}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None


def download_match_report_button(
    candidate_name: str,
    match_score: float,
    job_title: str,
    matched_skills: List[str],
    missing_skills: List[str],
    suggestions: List[str]
):
    """
    Show a download button for match report PDF.
    
    Args:
        candidate_name: Candidate name
        match_score: Match score
        job_title: Job title
        matched_skills: Matched skills list
        missing_skills: Missing skills list
        suggestions: Suggestions list
    """
    pdf_bytes = export_match_report_to_pdf(
        candidate_name,
        match_score,
        job_title,
        matched_skills,
        missing_skills,
        suggestions
    )
    
    if pdf_bytes:
        st.download_button(
            label="📥 Download Report (PDF)",
            data=pdf_bytes,
            file_name=f"match_report_{candidate_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )


# ======================================================
# CANDIDATE COMPARISON
# ======================================================

def show_candidate_comparison(
    candidates: List[Dict],
    comparison_fields: List[str] = None
):
    """
    Show side-by-side candidate comparison.
    
    Args:
        candidates: List of candidate dictionaries
        comparison_fields: Fields to compare
    """
    if len(candidates) < 2:
        st.info("Select at least 2 candidates to compare")
        return
    
    if comparison_fields is None:
        comparison_fields = ["name", "match_score", "experience", "skills_count"]
    
    # Create comparison table
    comparison_data = {
        field: [candidate.get(field, "N/A") for candidate in candidates]
        for field in comparison_fields
    }
    
    comparison_df = pd.DataFrame(comparison_data, index=[c.get("name", "Unknown") for c in candidates])
    
    st.dataframe(comparison_df, use_container_width=True)
