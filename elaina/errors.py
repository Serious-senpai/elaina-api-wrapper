class HTTPException(Exception):
    """Exception raised when fetching the data failed"""

    def __init__(self, status: int) -> None:
        super().__init__(f"HTTP response status code {status}")
