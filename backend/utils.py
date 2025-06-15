from fastapi import HTTPException, status

internal_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail={
        "success": False,
        "message": "Server internal error occured. Try again later.",
        "data": None
    }
)
