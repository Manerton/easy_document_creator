def ResponseModel(data, message):
    return {
        "data": [data],
        "status_code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "status_code": code,
        "message": message
    }
