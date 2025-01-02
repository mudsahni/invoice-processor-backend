from enum import Enum


class ParsingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    DELETED = "deleted"
    DRAFT = "draft"
    REJECTED = "rejected"
    REVERTED = "reverted"
    REVIEW = "review"
    REVISION = "revision"
    SUBMITTED = "submitted"
