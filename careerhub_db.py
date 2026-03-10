import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st
import hashlib

# ======================================================
# FILE-BASED STORAGE SETUP
# ======================================================

DATA_DIR = "careerhub_data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")
WORK_EXP_FILE = os.path.join(DATA_DIR, "work_experience.json")
ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, "achievements.json")
SKILLS_FILE = os.path.join(DATA_DIR, "skills.json")
CVS_FILE = os.path.join(DATA_DIR, "generated_cvs.json")
USAGE_FILE = os.path.join(DATA_DIR, "usage_tracking.json")

def init_data_dir():
    """Initialize data directory and files."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Initialize all JSON files if they don't exist
    files = [USERS_FILE, PROFILES_FILE, WORK_EXP_FILE, ACHIEVEMENTS_FILE, 
             SKILLS_FILE, CVS_FILE, USAGE_FILE]
    
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump({}, f)

init_data_dir()

def load_json(filepath: str) -> dict:
    """Load JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(filepath: str, data: dict):
    """Save JSON file safely."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# ======================================================
# AUTHENTICATION FUNCTIONS
# ======================================================

def hash_password(password: str) -> str:
    """Hash password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def sign_up(email: str, password: str) -> dict:
    """Sign up a new user."""
    try:
        users = load_json(USERS_FILE)
        
        if email in users:
            return {"success": False, "error": "Email already registered"}
        
        users[email] = {
            "email": email,
            "password_hash": hash_password(password),
            "created_at": datetime.now().isoformat()
        }
        
        save_json(USERS_FILE, users)
        
        # Create profile for new user
        create_or_get_profile(email)
        
        return {"success": True, "user": email}
    except Exception as e:
        return {"success": False, "error": str(e)}

def sign_in(email: str, password: str) -> dict:
    """Sign in a user."""
    try:
        users = load_json(USERS_FILE)
        
        if email not in users:
            return {"success": False, "error": "Email not found"}
        
        if users[email]["password_hash"] != hash_password(password):
            return {"success": False, "error": "Incorrect password"}
        
        return {"success": True, "user": email}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ======================================================
# PROFILE FUNCTIONS
# ======================================================

def create_or_get_profile(user_email: str, full_name: str = "") -> dict:
    """Create profile if doesn't exist, or get existing."""
    try:
        profiles = load_json(PROFILES_FILE)
        
        if user_email in profiles:
            return {"success": True, "profile": profiles[user_email]}
        
        # Create new profile
        new_profile = {
            "user_email": user_email,
            "full_name": full_name,
            "email": "",
            "phone": "",
            "location": "",
            "professional_summary": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        profiles[user_email] = new_profile
        save_json(PROFILES_FILE, profiles)
        
        return {"success": True, "profile": new_profile}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_profile(user_email: str, data: dict) -> dict:
    """Update user profile."""
    try:
        profiles = load_json(PROFILES_FILE)
        
        if user_email not in profiles:
            return {"success": False, "error": "Profile not found"}
        
        data["updated_at"] = datetime.now().isoformat()
        profiles[user_email].update(data)
        
        save_json(PROFILES_FILE, profiles)
        return {"success": True, "profile": profiles[user_email]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_profile(user_email: str) -> dict:
    """Get profile details."""
    try:
        profiles = load_json(PROFILES_FILE)
        
        if user_email not in profiles:
            return {"success": False, "error": "Profile not found"}
        
        return {"success": True, "profile": profiles[user_email]}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ======================================================
# WORK EXPERIENCE FUNCTIONS
# ======================================================

def add_work_experience(user_email: str, company: str, position: str, start_date: str,
                       end_date: str, current_job: bool, description: str) -> dict:
    """Add work experience."""
    try:
        exp_data = load_json(WORK_EXP_FILE)
        
        if user_email not in exp_data:
            exp_data[user_email] = {}
        
        exp_id = f"exp_{datetime.now().timestamp()}"
        
        exp_data[user_email][exp_id] = {
            "id": exp_id,
            "user_email": user_email,
            "company": company,
            "position": position,
            "start_date": start_date,
            "end_date": end_date if not current_job else None,
            "current_job": current_job,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        save_json(WORK_EXP_FILE, exp_data)
        return {"success": True, "experience": exp_data[user_email][exp_id]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_work_experience(user_email: str) -> dict:
    """Get all work experience for a user."""
    try:
        exp_data = load_json(WORK_EXP_FILE)
        
        if user_email not in exp_data:
            return {"success": True, "experiences": []}
        
        experiences = list(exp_data[user_email].values())
        experiences.sort(key=lambda x: x['start_date'], reverse=True)
        
        return {"success": True, "experiences": experiences}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_work_experience(user_email: str, exp_id: str, data: dict) -> dict:
    """Update work experience."""
    try:
        exp_data = load_json(WORK_EXP_FILE)
        
        if user_email not in exp_data or exp_id not in exp_data[user_email]:
            return {"success": False, "error": "Experience not found"}
        
        exp_data[user_email][exp_id].update(data)
        save_json(WORK_EXP_FILE, exp_data)
        
        return {"success": True, "experience": exp_data[user_email][exp_id]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_work_experience(user_email: str, exp_id: str) -> dict:
    """Delete work experience."""
    try:
        exp_data = load_json(WORK_EXP_FILE)
        
        if user_email in exp_data and exp_id in exp_data[user_email]:
            del exp_data[user_email][exp_id]
            save_json(WORK_EXP_FILE, exp_data)
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ======================================================
# ACHIEVEMENTS FUNCTIONS
# ======================================================

def add_achievement(exp_id: str, achievement: str, metric: str = "") -> dict:
    """Add achievement to work experience."""
    try:
        ach_data = load_json(ACHIEVEMENTS_FILE)
        
        if exp_id not in ach_data:
            ach_data[exp_id] = {}
        
        ach_id = f"ach_{datetime.now().timestamp()}"
        
        ach_data[exp_id][ach_id] = {
            "id": ach_id,
            "work_experience_id": exp_id,
            "achievement": achievement,
            "metric": metric,
            "created_at": datetime.now().isoformat()
        }
        
        save_json(ACHIEVEMENTS_FILE, ach_data)
        return {"success": True, "achievement": ach_data[exp_id][ach_id]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_achievements(exp_id: str) -> dict:
    """Get all achievements for work experience."""
    try:
        ach_data = load_json(ACHIEVEMENTS_FILE)
        
        if exp_id not in ach_data:
            return {"success": True, "achievements": []}
        
        achievements = list(ach_data[exp_id].values())
        return {"success": True, "achievements": achievements}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_achievement(exp_id: str, ach_id: str) -> dict:
    """Delete achievement."""
    try:
        ach_data = load_json(ACHIEVEMENTS_FILE)
        
        if exp_id in ach_data and ach_id in ach_data[exp_id]:
            del ach_data[exp_id][ach_id]
            save_json(ACHIEVEMENTS_FILE, ach_data)
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ======================================================
# SKILLS FUNCTIONS
# ======================================================

def add_skill(user_email: str, skill_name: str, proficiency: str) -> dict:
    """Add skill to profile."""
    try:
        skills_data = load_json(SKILLS_FILE)
        
        if user_email not in skills_data:
            skills_data[user_email] = {}
        
        skill_id = f"skill_{datetime.now().timestamp()}"
        
        skills_data[user_email][skill_id] = {
            "id": skill_id,
            "user_email": user_email,
            "skill_name": skill_name,
            "proficiency": proficiency,
            "created_at": datetime.now().isoformat()
        }
        
        save_json(SKILLS_FILE, skills_data)
        return {"success": True, "skill": skills_data[user_email][skill_id]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_skills(user_email: str) -> dict:
    """Get all skills for user."""
    try:
        skills_data = load_json(SKILLS_FILE)
        
        if user_email not in skills_data:
            return {"success": True, "skills": []}
        
        skills = list(skills_data[user_email].values())
        return {"success": True, "skills": skills}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_skill(user_email: str, skill_id: str) -> dict:
    """Delete skill."""
    try:
        skills_data = load_json(SKILLS_FILE)
        
        if user_email in skills_data and skill_id in skills_data[user_email]:
            del skills_data[user_email][skill_id]
            save_json(SKILLS_FILE, skills_data)
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ======================================================
# CV STORAGE FUNCTIONS
# ======================================================

def save_generated_cv(user_email, job_title, match_score, cv_content, job_description) -> dict:
    """Save generated CV to storage."""
    try:
        cvs_data = load_json(CVS_FILE)
        
        if user_email not in cvs_data:
            cvs_data[user_email] = {}
        
        cv_id = f"cv_{datetime.now().timestamp()}"
        
        cvs_data[user_email][cv_id] = {
            "id": cv_id,
            "user_email": user_email,
            "job_title": job_title,
            "match_score": match_score,
            "cv_content": cv_content,
            "job_description": job_description,
            "application_status": "Draft",
            "created_at": datetime.now().isoformat()
        }
        
        save_json(CVS_FILE, cvs_data)
        
        # Increment CV count
        increment_cv_count(user_email)
        
        return {"success": True, "cv": cvs_data[user_email][cv_id]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_generated_cvs(user_email: str) -> dict:
    """Get all generated CVs for user."""
    try:
        cvs_data = load_json(CVS_FILE)
        
        if user_email not in cvs_data:
            return {"success": True, "cvs": []}
        
        cvs = list(cvs_data[user_email].values())
        cvs.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {"success": True, "cvs": cvs}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_cv_status(user_email: str, cv_id: str, status: str) -> dict:
    """Update CV application status."""
    try:
        cvs_data = load_json(CVS_FILE)
        
        if user_email not in cvs_data or cv_id not in cvs_data[user_email]:
            return {"success": False, "error": "CV not found"}
        
        cvs_data[user_email][cv_id]["application_status"] = status
        save_json(CVS_FILE, cvs_data)
        
        return {"success": True, "cv": cvs_data[user_email][cv_id]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_cv(user_email: str, cv_id: str) -> dict:
    """Delete generated CV."""
    try:
        cvs_data = load_json(CVS_FILE)
        
        if user_email in cvs_data and cv_id in cvs_data[user_email]:
            del cvs_data[user_email][cv_id]
            save_json(CVS_FILE, cvs_data)
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ======================================================
# USAGE TRACKING FUNCTIONS
# ======================================================

def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")

def check_cv_limit(user_email: str) -> dict:
    """Check if user has reached CV generation limit."""
    try:
        usage_data = load_json(USAGE_FILE)
        current_month = get_current_month()
        
        user_key = f"{user_email}_{current_month}"
        
        if user_key not in usage_data:
            usage_data[user_key] = {
                "user_email": user_email,
                "month": current_month,
                "cvs_generated": 0,
                "tier": "free"
            }
            save_json(USAGE_FILE, usage_data)
        
        usage = usage_data[user_key]
        tier = usage["tier"]
        limit = 20 if tier == "free" else float('inf')
        limit_reached = usage["cvs_generated"] >= limit
        
        return {
            "success": True,
            "limit_reached": limit_reached,
            "cvs_generated": usage["cvs_generated"],
            "limit": limit,
            "tier": tier
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def increment_cv_count(user_email: str) -> dict:
    """Increment CV generation count for current month."""
    try:
        usage_data = load_json(USAGE_FILE)
        current_month = get_current_month()
        user_key = f"{user_email}_{current_month}"
        
        if user_key in usage_data:
            usage_data[user_key]["cvs_generated"] += 1
            save_json(USAGE_FILE, usage_data)
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}