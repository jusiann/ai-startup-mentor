class ApiError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    @staticmethod
    def bad_request(message: str):
        return ApiError(400, message)

    @staticmethod
    def unauthorized(message: str):
        return ApiError(401, message)

    @staticmethod
    def forbidden(message: str):
        return ApiError(403, message)

    @staticmethod
    def not_found(message: str):
        return ApiError(404, message)

    @staticmethod
    def conflict(message: str):
        return ApiError(409, message)
