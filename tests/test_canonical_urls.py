from scripts.check_canonical_urls import (
    CANONICAL_OWNER,
    CANONICAL_REPO,
    SLUG_PATTERN,
    non_canonical_references,
)


def test_repository_uses_only_the_canonical_owner() -> None:
    assert non_canonical_references() == []


def test_pattern_flags_a_foreign_owner() -> None:
    sample = "see https://github.com/" + "someone-else" + "/" + CANONICAL_REPO + " here"
    match = SLUG_PATTERN.search(sample)
    assert match is not None
    assert match.group(1) != CANONICAL_OWNER


def test_pattern_accepts_the_canonical_owner() -> None:
    sample = "https://github.com/" + CANONICAL_OWNER + "/" + CANONICAL_REPO
    match = SLUG_PATTERN.search(sample)
    assert match is not None
    assert match.group(1) == CANONICAL_OWNER


def test_pattern_recognizes_the_redirected_historical_name() -> None:
    sample = "https://github.com/" + CANONICAL_OWNER + "/" + "lumen-quantum/blob/main/README.md"
    match = SLUG_PATTERN.search(sample)
    assert match is not None
    assert match.group(2) != CANONICAL_REPO


def test_pattern_does_not_flag_other_repository_names() -> None:
    assert SLUG_PATTERN.search("https://github.com/example/quantum-models-tools") is None
