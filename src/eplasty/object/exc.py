class SearchError(Exception):
    """Any problems with searches"""

class NotFound(SearchError):
    """No row found when one was expected"""

class TooManyFound(SearchError):
    """Too many rows found"""

class LifecycleError(Exception):
    """There is some problem with the current status of object"""