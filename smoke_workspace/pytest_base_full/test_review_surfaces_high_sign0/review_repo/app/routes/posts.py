from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post('/publish')
def publish_post():
    try:
        return {'ok': True}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
