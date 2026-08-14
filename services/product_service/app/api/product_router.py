from uuid import UUID

from fastapi import APIRouter, Query, status

from app.dependencies.category_dependency import TargetCategoryDep
from app.dependencies.product_dependency import TargetProductDep, TargetProductSellerDep
from app.enums import DeleteProductMode
from app.schemas.product import GetProduct, NewProduct
from app.services.product_service import ProductService
from app.storage.postgresql.connection import SessionDep
from app.constants import EXAMPLE_UUID


router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "/{product_id}",
    response_model=GetProduct,
    summary="Get product by ID",
    description="Return a single product by its UUID.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Product not found"},
    },
)
async def get_product(target_product: TargetProductDep) -> GetProduct:
    return target_product


@router.get(
    "/",
    response_model=list[GetProduct],
    summary="List products",
    description=(
        "Return a paginated list of products. "
        "Filter by availability and/or category."
    ),
)
async def get_products(
    session: SessionDep,
    only_available: bool | None = Query(
        default=True,
        description="If true, return only available products. Set to false to include unavailable ones.",
        examples=[True],
    ),
    category_id: UUID | None = Query(
        default=None,
        description="Filter products by category UUID.",
        examples=[EXAMPLE_UUID],
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of products to return.",
        examples=[100],
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of products to skip for pagination.",
        examples=[0],
    ),
) -> list[GetProduct]:
    return await ProductService.get_products(
        session=session,
        only_available=only_available,
        category_id=category_id,
        limit=limit,
        offset=offset,
    )


@router.delete(
    "/{product_id}",
    response_model=GetProduct,
    summary="Delete product",
    description=(
        "Delete a product by ID. "
        "Use `mode=soft` to mark unavailable or `mode=delete` for permanent removal."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Product not found"},
    },
)
async def delete_product(
    session: SessionDep,
    target_product: TargetProductDep,
    mode: DeleteProductMode = Query(
        default=DeleteProductMode.SOFT,
        description="Deletion mode: `soft` marks the product unavailable, `delete` removes it permanently.",
        examples=[DeleteProductMode.SOFT],
    ),
) -> GetProduct:
    return await ProductService.delete_product(
        session=session,
        product_id=target_product.id,
        mode=mode,
    )


@router.post(
    "/",
    response_model=GetProduct,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description=(
        "Create a product in the given category. "
        "Requires query parameters `category_id` and `seller_id`."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "User is not a seller"},
        status.HTTP_404_NOT_FOUND: {"description": "Category or seller not found"},
        status.HTTP_502_BAD_GATEWAY: {"description": "User Service returned invalid data"},
    },
)
async def add_product(
    session: SessionDep,
    new_product: NewProduct,
    target_category: TargetCategoryDep,
    target_seller: TargetProductSellerDep,
) -> GetProduct:
    """
       Create a product with all the information:
       - **category_id**: each product must belong to at least one category and must exist
       - **seller_id**: each product must be sold by a seller and must exist
       - **name**: each product must have a name
       - **description**: long product description
       - **price**: required
       - **stock**: quantity must be > 0
       """
    return await ProductService.create_new_product(
        name=new_product.name,
        description=new_product.description,
        price=new_product.price,
        stock=new_product.stock,
        category_id=target_category.id,
        session=session,
        seller_id=target_seller.id,
    )
