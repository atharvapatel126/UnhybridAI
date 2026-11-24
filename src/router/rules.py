"""Deterministic university-domain routing when Gemini is unavailable."""
import re


def fallback(query):
    text = query.lower()
    personal = bool(re.search(r"\b(my|mine|am i|do i|can i|for me|i have)\b", text))
    docs = bool(re.search(r"\b(policy|policies|rules?|regulations?|handbook|attendance|scholarship|deadline|notices?|library|borrow|backlog|exam)\b", text))
    tools = []
    scholarship_personal = "scholarship" in text and personal
    profile = bool(re.search(r"\b(gpa|profile|email|records?|department|dept|name|year|major|branch)\b", text))
    if profile or scholarship_personal:
        tools.append("get_student_profile")
    if re.search(r"\b(fees?|paid|outstanding|balance)\b", text) or scholarship_personal:
        tools.append("get_fee_status")
    if re.search(r"\b(courses?|enrollments?|enrolled|grades?|credits?)\b", text):
        tools.append("get_enrollments")
    if re.search(r"\b(department|dept)\b", text) and re.search(r"\b(average|stats|statistics|count)\b", text):
        tools = ["get_student_profile", "get_department_stats"]
    if docs and not personal:
        # A policy threshold is document evidence, not a request for someone's GPA.
        tools = []
    route = "HYBRID" if docs and tools else "UNSTRUCTURED" if docs else "STRUCTURED" if tools else "OUT_OF_SCOPE"
    return {"route": route, "sql_tools": tools, "doc_query": query if docs else "",
            "reason": "Deterministic university keyword rules.", "method": "fallback"}
