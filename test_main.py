"""Tests for main.py.

We're checking specifically for core correctness, reproducibility/determinism, missing research data, messy real-world data,
data integrity, preventing misleading research outputs, and distinguishing real inconsistencies from harmless formatting differences.
"""

from itertools import permutations
import unittest

from main import NumberingError, Study, number_studies


def study(
    identifier: int,
    *,
    reference_id: int = 10,
    year: int | None = 2001,
    position: int = 0,
    title: str = "Study",
    authors: str = "Author",
) -> Study:
    """Create a valid Study with convenient defaults."""
    return Study(
        assignment_id=identifier,
        summary_id=identifier + 100,
        reference_id=reference_id,
        position=position,
        year=year,
        title=title,
        authors=authors,
    )


class NumberStudiesTests(unittest.TestCase):

    def test_empty_input_returns_empty_result(self) -> None:
        """Empty research data should produce an empty result."""
        result = number_studies([])

        self.assertEqual(result.ordered_assignment_ids, ())
        self.assertEqual(result.summary_numbers, {})
        self.assertEqual(result.references, {})

    def test_numbers_and_groups_shared_references(self) -> None:
        """Multiple summaries can point to the same publication."""
        result = number_studies(
            [
                study(2, position=2),
                study(1, position=1),
                study(
                    3,
                    reference_id=20,
                    year=2015,
                    title="Later Study",
                ),
            ]
        )

        self.assertEqual(
            result.ordered_assignment_ids,
            (1, 2, 3),
        )

        self.assertEqual(
            result.summary_numbers,
            {
                101: 1,
                102: 2,
                103: 3,
            },
        )

        self.assertEqual(
            result.references,
            {
                10: (1, 2),
                20: (3,),
            },
        )

    def test_input_order_does_not_change_result(self) -> None:
        """The same research data should always produce the same numbering."""
        rows = [
            study(1),
            study(2, position=1),
            study(
                3,
                reference_id=20,
                year=2015,
                title="Later Study",
            ),
        ]

        expected = number_studies(rows)

        for order in permutations(rows):
            with self.subTest(order=[item.assignment_id for item in order]):
                self.assertEqual(
                    number_studies(list(order)),
                    expected,
                )

    def test_known_years_sort_before_unknown_years(self) -> None:
        """Missing publication years should have predictable behaviour."""
        result = number_studies(
            [
                study(
                    1,
                    reference_id=10,
                    year=None,
                    title="Unknown Year",
                ),
                study(
                    2,
                    reference_id=20,
                    year=2024,
                    title="Known Year",
                ),
            ]
        )

        self.assertEqual(
            result.ordered_assignment_ids,
            (2, 1),
        )

    def test_year_takes_priority_over_saved_position(self) -> None:
        """Chronological ordering should come before local position."""
        older = study(
            1,
            reference_id=10,
            year=2001,
            position=99,
            title="Older Study",
        )

        newer = study(
            2,
            reference_id=20,
            year=2020,
            position=0,
            title="Newer Study",
        )

        result = number_studies([newer, older])

        self.assertEqual(
            result.ordered_assignment_ids,
            (1, 2),
        )

    def test_text_is_normalised_for_ordering(self) -> None:
        """Case and surrounding whitespace should not affect ordering."""
        result = number_studies(
            [
                study(
                    3,
                    reference_id=30,
                    title=" beta ",
                    authors="Author",
                ),
                study(
                    2,
                    reference_id=20,
                    title="ALPHA",
                    authors="Z Author",
                ),
                study(
                    1,
                    reference_id=10,
                    title=" alpha ",
                    authors=" A Author ",
                ),
            ]
        )

        self.assertEqual(
            result.ordered_assignment_ids,
            (1, 2, 3),
        )

    def test_position_and_assignment_id_break_ties(self) -> None:
        """Stable tie-breakers ensure deterministic numbering."""
        result = number_studies(
            [
                study(3, position=2),
                study(2, position=1),
                study(1, position=1),
            ]
        )

        self.assertEqual(
            result.ordered_assignment_ids,
            (1, 2, 3),
        )

    def test_duplicate_assignment_id_is_rejected(self) -> None:
        """A saved assignment must have a unique ID."""
        first = study(1)

        duplicate = Study(
            assignment_id=1,
            summary_id=102,
            reference_id=20,
            position=0,
            year=2002,
            title="Another Study",
            authors="Another Author",
        )

        with self.assertRaisesRegex(
            NumberingError,
            "Duplicate assignment ID",
        ):
            number_studies([first, duplicate])

    def test_duplicate_summary_id_is_rejected(self) -> None:
        """Each research summary must have a unique ID."""
        first = study(1)

        duplicate = Study(
            assignment_id=2,
            summary_id=101,
            reference_id=20,
            position=0,
            year=2002,
            title="Another Study",
            authors="Another Author",
        )

        with self.assertRaisesRegex(
            NumberingError,
            "Duplicate summary ID",
        ):
            number_studies([first, duplicate])

    def test_conflicting_reference_metadata_is_rejected(self) -> None:
        """One reference ID must not describe two different publications."""
        first = study(
            1,
            reference_id=10,
            year=2020,
            title="Study A",
            authors="Researcher",
        )

        conflicting = study(
            2,
            reference_id=10,
            year=2020,
            title="Different Study",
            authors="Researcher",
        )

        with self.assertRaisesRegex(
            NumberingError,
            "Conflicting metadata",
        ):
            number_studies([first, conflicting])

    def test_equivalent_reference_metadata_is_allowed(self) -> None:
        """Harmless formatting differences should not create a conflict."""
        first = study(
            1,
            reference_id=10,
            title=" A Study ",
            authors=" A Researcher ",
        )

        second = study(
            2,
            reference_id=10,
            title="a study",
            authors="a researcher",
            position=1,
        )

        result = number_studies([first, second])

        self.assertEqual(
            result.references,
            {
                10: (1, 2),
            },
        )

    def test_different_reference_ids_are_not_merged(self) -> None:
        """Matching metadata does not mean two reference IDs are identical."""
        result = number_studies(
            [
                study(1, reference_id=10),
                study(2, reference_id=20, position=1),
            ]
        )

        self.assertEqual(
            result.references,
            {
                10: (1,),
                20: (2,),
            },
        )


if __name__ == "__main__":
    unittest.main()
Ï
