from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_idea():
    return {"message": "Idea route"}