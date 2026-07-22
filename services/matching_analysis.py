"""Deterministic, role-agnostic requirement evidence for matching UIs."""

import re
from collections import Counter
from typing import Dict, List


STOPWORDS = {
    "about", "after", "also", "and", "are", "based", "been", "being", "build", "company",
    "advisor", "candidate", "excellent", "experience", "from", "have", "into", "job", "junior",
    "looking", "manager", "must", "our", "required", "role", "senior", "specialist", "strong", "team",
    "that", "the", "their", "them", "they", "this", "using", "what", "when",
    "where", "which", "will", "with", "work", "working", "years", "you", "your",
}

KNOWN_REQUIREMENTS = [
    "account management", "accounts payable", "accounts receivable", "active listening", "agile",
    "analytics", "applicant tracking systems", "audit", "budgeting", "business development",
    "change management", "clinical care", "communication", "compliance", "conflict resolution",
    "content marketing", "contract management", "crm", "customer service", "data analysis",
    "data protection", "digital marketing", "employee engagement", "employee relations", "excel",
    "financial modelling", "forecasting", "graphql", "health and safety", "hris", "javascript",
    "leadership", "learning and development", "machine learning", "marketing strategy", "negotiation",
    "node.js", "performance management", "power bi", "presentation", "project management", "python",
    "react", "recruitment", "reporting", "rest api", "risk management", "salesforce", "seo",
    "social media", "sql", "stakeholder management", "talent acquisition", "testing", "typescript",
    "user research", "wcag", "workforce planning",
]


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9+#./ -]", " ", value.lower())).strip()


def extract_job_requirements(job_description: str, limit: int = 16) -> List[str]:
    """Extract explicit domain terms plus useful keywords from an arbitrary JD."""
    clean_jd = _clean(job_description)
    found = [term for term in KNOWN_REQUIREMENTS if re.search(rf"\b{re.escape(term)}\b", clean_jd)]

    bullet_text = " ".join(
        line for line in job_description.splitlines()
        if re.match(r"^\s*[-*\u2022]", line) or re.search(r"\b(required|requirements|experience|knowledge|proficien|skilled)\b", line, re.I)
    )
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.]{2,}\b", bullet_text or job_description)
    counts = Counter(token.lower() for token in tokens if token.lower() not in STOPWORDS)
    for token, _ in counts.most_common(30):
        if token not in found and not any(token in phrase.split() for phrase in found) and len(token) > 3:
            found.append(token)
        if len(found) >= limit:
            break
    return found[:limit]


def analyse_role_fit(job_description: str, candidate_text: str) -> Dict:
    requirements = extract_job_requirements(job_description)
    resume = _clean(candidate_text)
    matched = [item for item in requirements if re.search(rf"\b{re.escape(item)}\b", resume)]
    missing = [item for item in requirements if item not in matched]
    evidence_score = round((len(matched) / len(requirements)) * 100) if requirements else 0
    suggestions = [
        {
            "requirement": item.title() if item.islower() else item,
            "advice": f"Add truthful evidence of {item}: name the project or responsibility, your actions, and a measurable outcome.",
        }
        for item in missing[:6]
    ]
    return {
        "requirements": requirements,
        "matched_requirements": matched,
        "missing_requirements": missing,
        "bonus_skills": [],
        "evidence_score": evidence_score,
        "suggestions": suggestions,
    }
