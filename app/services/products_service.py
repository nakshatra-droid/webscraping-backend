from sqlalchemy.ext.asyncio import AsyncSession
from app.data_controllers.products_data_controller import ProductsDataController
from app.schemas.product_schemas import (
    ProductCreate,
    ProductListingUpdate,
    AdminProductResponse,
)
from typing import Dict, Any, Optional
from uuid import UUID
from app.exceptions import NotFoundException, ValidationException
from app.utils.validations_utils import ValidationsUtils


class ProductsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.controller = ProductsDataController(db)

    # User APIs
    async def get_products(
        self, page: int = 1, size: int = 10, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get products with summary pricing - User only"""

        return await self.controller.get_products(page=page, size=size, search=search)

    async def get_product_by_id(self, product_id: UUID) -> AdminProductResponse:
        """Get a specific product with listings by its ID - User only"""

        product = await self.controller.get_product_with_details(product_id)
        if not product:
            raise NotFoundException(
                "Product not found. Please check the product ID and try again."
            )
        return product

    async def get_products_by_ids(
        self, product_ids: list[UUID]
    ) -> list[AdminProductResponse]:
        """Get products by ID list - User only"""

        return await self.controller.get_products_by_ids(product_ids)

    # Admin APIs
    async def get_all_products_admin(
        self, page: int = 1, size: int = 10, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all products with listings - Admin only"""

        return await self.controller.get_all_products_admin(
            page=page, size=size, search=search
        )

    async def get_product_with_details_admin(
        self, product_id: UUID
    ) -> AdminProductResponse:
        """Get a specific product with listings by its ID - Admin only"""

        product = await self.controller.get_product_with_details(product_id)
        if not product:
            raise NotFoundException(
                "Product not found. Please check the product ID and try again."
            )
        return product

    async def create_product_with_detail(
        self, product_data: ProductCreate
    ) -> AdminProductResponse:
        """Create a new product with a listing - Admin only"""

        if not ValidationsUtils.validate_source(source=product_data.source):
            raise ValidationException("Invalid source given for product creation")

        product = await self.controller.create_product_with_detail(product_data)
        return await self.get_product_with_details_admin(product.id)

    async def update_product_detail(
        self, product_id: UUID, source: str, update_data: ProductListingUpdate
    ) -> AdminProductResponse:
        """Update product listing for a specific source - Admin only"""

        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            raise ValidationException("No update data provided")

        if not ValidationsUtils.validate_source(source=source):
            raise ValidationException("Invalid source given for update")

        detail = await self.controller.update_product_detail(
            product_id, source, update_data
        )
        if not detail:
            raise NotFoundException(
                "Listing not found. Please check the product ID and source and try again."
            )
        return await self.get_product_with_details_admin(product_id)

    async def delete_product_detail(self, product_id: UUID, source: str) -> bool:
        """Delete product listing for a specific source - Admin only"""

        if not ValidationsUtils.validate_source(source=source):
            raise ValidationException("Invalid source given for deletion")

        return await self.controller.delete_product_detail(product_id, source)

    async def delete_product(self, product_id: UUID) -> bool:
        """Delete a specific product by its ID - Admin only"""

        return await self.controller.delete_product(product_id)
