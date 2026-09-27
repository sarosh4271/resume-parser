"""Pydantic models for normalized resume data."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ContactInfo(BaseModel):
    full_name: str | None = Field(default=None, description="Candidate's full name.")
    email: str | None = Field(default=None, description="Email address exactly as written.")
    phone: str | None = Field(default=None, description="Phone number exactly as written.")
    location: str | None = Field(default=None, description="City, region, or country if provided.")
    linkedin_url: str | None = Field(default=None, description="LinkedIn URL if present.")
    portfolio_url: str | None = Field(default=None, description="Portfolio or personal-site URL.")


class WorkExperience(BaseModel):
    company: str | None = None
    title: str | None = None
    location: str | None = None
    start_date: str | None = Field(default=None, description="Date exactly as stated.")
    end_date: str | None = Field(default=None, description="Date or Present exactly as stated.")
    highlights: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    graduation_date: str | None = Field(default=None, description="Date exactly as stated.")
    details: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None


class ParsedResume(BaseModel):
    """Normalized resume structure produced by the parser."""

    contact: ContactInfo = Field(default_factory=ContactInfo)
    professional_summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    work_experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    parsing_notes: list[str] = Field(
        default_factory=list,
        description="Ambiguities, unreadable content, or important missing sections.",
    )

    @field_validator("skills", "certifications", "languages", mode="after")
    @classmethod
    def deduplicate_strings(cls, values: list[str]) -> list[str]:
        """Remove empty and duplicate values without changing their order."""
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            cleaned = value.strip()
            key = cleaned.casefold()
            if cleaned and key not in seen:
                seen.add(key)
                result.append(cleaned)
        return result

