"""Simplified sample adapted from research software I previously worked on."""

"""Number research study (publications) summaries and group shared references."""

from dataclasses import dataclass

# Plus other imports...


class NumberingError(ValueError):
    """Raised when study data is inconsistent."""

    # Custom exception for invalid data, e.g., duplicate IDs or conflicting metadata


@dataclass(frozen=True)
class Study:
    """A research summary and its associated bibliographic reference."""

    assignment_id: int
    summary_id: int
    reference_id: int
    position: int
    year: int | None
    title: str
    authors: str


@dataclass(frozen=True)
class NumberingResult:
    """The final numbering and grouped bibliography references."""

    ordered_assignment_ids: tuple[int, ...]
    summary_numbers: dict[int, int]
    references: dict[int, tuple[int, ...]]


def validate_studies(studies: list[Study]) -> None:
    """Validate IDs and ensure shared references have consistent metadata."""

    assignment_ids = set()
    summary_ids = set()

    # Stores the expected metadata for each canonical reference.
    reference_metadata = {}

    for study in studies:

        # Each saved assignment and summary must be uniquely identifiable.
        if study.assignment_id in assignment_ids:
            raise NumberingError(f"Duplicate assignment ID: {study.assignment_id}")

        if study.summary_id in summary_ids:
            raise NumberingError(f"Duplicate summary ID: {study.summary_id}")

        # Normalise text so differences in case or surrounding whitespace
        # do not make equivalent bibliographic records appear different.
        metadata = (
            study.year,
            study.title.strip().lower(),
            study.authors.strip().lower(),
        )

        # The same reference ID should always describe the same paper.
        if study.reference_id in reference_metadata:
            if reference_metadata[study.reference_id] != metadata:
                raise NumberingError(
                    f"Conflicting metadata for reference {study.reference_id}"
                )
        else:
            reference_metadata[study.reference_id] = metadata

        assignment_ids.add(study.assignment_id)
        summary_ids.add(study.summary_id)


def number_studies(studies: list[Study]) -> NumberingResult:
    """Return deterministic numbering and grouped bibliographic references."""

    # Fail early if the underlying research data is inconsistent.
    validate_studies(studies)

    # Explicit ordering makes the result reproducible and independent
    # of the order in which records were supplied by a file or database.
    ordered = sorted(
        studies,
        key=lambda study: (
            study.year is None,  # Known years before missing years.
            study.year or 0,  # Chronological order.
            study.title.strip().lower(),  # Normalised title.
            study.authors.strip().lower(),  # Normalised authors.
            study.position,  # Preserve intended local order.
            study.assignment_id,  # Final deterministic tie-breaker.
        ),
    )

    # Maps each research summary to its final citation number.
    summary_numbers = {}

    # Multiple summaries may refer to the same underlying paper.
    references = {}

    for number, study in enumerate(ordered, start=1):
        summary_numbers[study.summary_id] = number

        # Keep one reference entry while retaining every summary number
        # associated with that paper.
        references.setdefault(study.reference_id, []).append(number)

    return NumberingResult(
        ordered_assignment_ids=tuple(study.assignment_id for study in ordered),
        summary_numbers=summary_numbers,
        references={
            reference_id: tuple(numbers) for reference_id, numbers in references.items()
        },
    )


# .
# .
# .
# (more code...)
# .
# .
# .
Ï
