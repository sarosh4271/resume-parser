from resume_parser.models import ParsedResume


def test_skills_are_trimmed_and_deduplicated():
    resume = ParsedResume(skills=[" Python ", "python", "SQL", ""])
    assert resume.skills == ["Python", "SQL"]


def test_missing_sections_have_safe_defaults():
    resume = ParsedResume()
    assert resume.contact.full_name is None
    assert resume.work_experience == []
    assert resume.education == []

