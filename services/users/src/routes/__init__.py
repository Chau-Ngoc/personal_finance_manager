from fastapi import APIRouter
from src.routes.all import router as all_router
from src.routes.signup import router as signup_router

router = APIRouter(prefix="/api/users", tags=["users"])
router.include_router(signup_router)
router.include_router(all_router)
