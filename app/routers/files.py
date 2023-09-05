from fastapi import APIRouter, Depends
from starlette.responses import FileResponse

from dependencies import get_current_active_user

router = APIRouter(
    prefix="/file",
    tags=["file"],
    dependencies=[Depends(get_current_active_user)]
)


@router.get("/{file_name}", response_class=FileResponse)
async def get_file(file_name: str):
    return f'docs/{file_name}'
