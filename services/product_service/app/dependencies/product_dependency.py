from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import NoResultFound
from pydantic import ValidationError

from app.schemas.product import GetProduct, GetSeller
from app.services.product_service import ProductService
from app.storage.postgresql.connection import SessionDep
from app.storage.postgresql.repositories.product_repository import ProductRepository
from app.messaging.rabbitMQ.publishers.UserServicePublisher import UserServicePublisher


async def get_target_product(
    product_id: Annotated[UUID, Path(description="Product ID")],
    session: SessionDep,
) -> GetProduct:
    """Validate product_id and load the product from the database."""
    try:
        product_orm = await ProductRepository.get_product_by_id(
            session=session,
            product_id=product_id,
        )
        return ProductService._to_get_product(product_orm)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Cannot get product by id={product_id}: "
                f"{type(e).__name__} - {e}"
            )
        )


TargetProductDep = Annotated[GetProduct, Depends(get_target_product)]


async def get_target_product_seller(
    seller_id: Annotated[UUID, Query(description="Seller ID")],
) -> GetSeller:
    """Validate seller_id and load the seller from the User Service."""
    try:
        seller = await UserServicePublisher.publish_user_request(
            user_id=seller_id,
            required_role="seller",
        )
        if seller.get("detail") == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={seller_id} not found",
            )

        if seller.get("detail") == f"User have not role seller":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with id={seller_id} is not a seller",
            )
        
        return GetSeller.model_validate(seller["user"])
    
    except HTTPException as e:
        raise e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error validating seller from User Service: {type(e).__name__} - {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting seller from User Service: {type(e).__name__} - {e}",
        )


TargetProductSellerDep = Annotated[GetSeller, Depends(get_target_product_seller)]
