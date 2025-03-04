from enum import Enum


class ProfileErrorCode(str, Enum):
    """Error codes specific to the profiles domain"""
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    PROFILE_CREATION_FAILED = "PROFILE_CREATION_FAILED"
    PROFILE_UPDATE_FAILED = "PROFILE_UPDATE_FAILED"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS" 