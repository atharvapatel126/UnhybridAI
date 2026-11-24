"""Reproduce the four fictional source documents; no real university policy."""
from pathlib import Path
import pymupdf
from config import settings

BANNER = "SYNTHETIC - DEMO ONLY"


def _pdf(path, pages):
    with pymupdf.open() as document:
        for text in pages:
            page = document.new_page()
            page.insert_textbox(pymupdf.Rect(50, 50, 545, 790), BANNER + "\n\n" + text, fontsize=12)
        document.save(path, garbage=4, deflate=True)


def create_documents(directory=None):
    directory = Path(directory or settings.raw_docs_dir)
    directory.mkdir(parents=True, exist_ok=True)
    _pdf(directory / "Scholarship_Policy.pdf", [
        "Merit Scholarship Policy\nPublished: 2026-10-01\nEffective: 2026-10-01\n"
        "Merit scholarship eligibility requires GPA of at least 8.0, study in year 2, 3, or 4, "
        "and no outstanding current-term fees. These are the complete eligibility criteria in this demo policy.",
        "Merit Scholarship Application\nPublished: 2026-10-01\n"
        "The merit scholarship application deadline is 15 December 2026. "
        "The required application document list is not specified in this policy.",
    ])
    _pdf(directory / "Academic_Regulations.pdf", [
        "Academic Regulations\nPublished: 2026-09-01\n"
        "All students must follow the synthetic examination and course enrollment rules.",
        "Backlog Rules\nPublished: 2026-09-01\n"
        "A failed course is a backlog. A student must pass the registered repeat examination to clear it.",
        "Assessment Rules\nPublished: 2026-09-01\n"
        "Course grades are A, B, C, D, or F. An F grade indicates a failed course.",
        "Attendance Rule\nPublished: 2026-09-01\n"
        "Minimum attendance required to sit for examinations is 75 percent in each course. "
        "No attendance condonation exception is defined in these synthetic regulations.",
    ])
    (directory / "Student_Handbook.txt").write_text(
        BANNER + "\nPublished: 2026-09-05\nStudent Handbook\n"
        "Library hours are Monday through Friday, 09:00 to 17:00. "
        "Students may borrow up to three books for fourteen days. "
        "Contact the synthetic student support desk for administrative queries.", encoding="utf-8")
    (directory / "Notices_2026.txt").write_text(
        BANNER + "\nPublished: 2026-11-01\n"
        "Merit scholarship notice: the application deadline is 15 December 2026.\n\n"
        + BANNER + "\nPublished: 2026-11-15\n"
        "Conflicting merit scholarship notice: the application deadline is 20 December 2026. "
        "This notice does not state that it supersedes the previous notice or scholarship policy. "
        "The conflict requires confirmation from the university administration.", encoding="utf-8")
    return sorted(p.name for p in directory.iterdir() if p.suffix.lower() in (".pdf", ".txt"))


if __name__ == "__main__":
    print("Created synthetic documents:", ", ".join(create_documents()))
