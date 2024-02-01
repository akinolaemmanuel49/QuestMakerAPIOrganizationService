class DatabaseError(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


class DocumentNotFoundError(DatabaseError):
    def __init__(self, detail: str = 'Document not found') -> None:
        super().__init__(detail)


class DuplicateKeyError(DatabaseError):
    def __init__(self, detail: str = 'Duplicate key violation') -> None:
        super().__init__(detail)


class ValidationError(DatabaseError):
    def __init__(self, detail: str = 'Validation error') -> None:
        super().__init__(detail)
