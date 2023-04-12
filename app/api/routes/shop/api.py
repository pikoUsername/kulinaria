from fastapi import APIRouter

from . import product, seller, search, category


router = APIRouter()

router.include_router(category.router, prefix="/category")
router.include_router(search.router, prefix="/search")
router.include_router(product.router, prefix="/product")
router.include_router(seller.router, prefix="/seller")
