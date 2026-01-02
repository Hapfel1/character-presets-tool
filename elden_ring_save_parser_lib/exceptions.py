"""Custom exceptions for elden-ring-save-parser-lib"""


class SaveFileError(Exception):
    """Base exception for save file errors"""
    pass


class CorruptedSaveError(SaveFileError):
    """Save file is corrupted and cannot be parsed"""
    pass


class UnsupportedVersionError(SaveFileError):
    """Save file version is not supported"""
    pass


class ChecksumMismatchError(SaveFileError):
    """Checksum validation failed"""
    pass
