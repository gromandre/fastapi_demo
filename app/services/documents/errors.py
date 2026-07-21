class DocumentServiceError(Exception):
    """Base error for document operations."""


class UnsupportedDocumentTypeError(DocumentServiceError):
    pass


class EmptyDocumentError(DocumentServiceError):
    pass


class DocumentNotFoundError(DocumentServiceError):
    pass


class DocumentTextNotFoundError(DocumentServiceError):
    pass


class StorageUnavailableError(DocumentServiceError):
    pass


class DocumentPersistenceError(DocumentServiceError):
    pass


class TaskBrokerUnavailableError(DocumentServiceError):
    pass
