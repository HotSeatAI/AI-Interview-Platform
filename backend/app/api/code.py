from fastapi import APIRouter, Request, Response

from app.core.rate_limiter import limiter
from app.schemas.code import (
    CodeRunRequest,
    CodeRunResponse,
)
from app.services.execution_service import (
    CodeExecutionService,
)

router = APIRouter(
    prefix="/code",
    tags=["Code Execution"],
)

execution_service = CodeExecutionService()


@router.post(
    "/run",
    response_model=CodeRunResponse,
)
@limiter.limit("15/minute")
def run_code(
    request: Request,
    response: Response,
    payload: CodeRunRequest,
):

    return execution_service.run_code(
        payload
    )