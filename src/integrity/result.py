from dataclasses import dataclass


@dataclass
class IntegrityResult:
    """
    Result of archive integrity verification.
    """

    valid: bool
    model: str
    checked_files: int
    failed_files: list