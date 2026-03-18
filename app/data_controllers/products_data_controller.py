from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any
from uuid import UUID
from app.models.products import Products
from app.models.product_details import ProductDetails
from app.schemas.product_schemas import (
    ProductCreate,
    ProductListingUpdate,
    ProductSummaryResponse,
    AdminProductResponse,
)
from app.exceptions import ConflictException, NotFoundException
import math


class ProductsDataController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_products(
        self, page: int = 1, size: int = 10, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get products with summary price info - User only"""

        skip = (page - 1) * size

        filters = [Products.deleted_at.is_(None)]
        if search:
            like = f"%{search}%"
            filters.append(
                or_(
                    Products.model_number.ilike(like),
                    Products.brand.ilike(like),
                    Products.series.ilike(like),
                    Products.processor.ilike(like),
                )
            )

        count_stmt = select(func.count(Products.id)).where(*filters)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        stmt = (
            select(Products)
            .options(selectinload(Products.product_details))
            .where(*filters)
            .order_by(Products.created_at.desc())
            .offset(skip)
            .limit(size)
        )
        result = await self.db.execute(stmt)
        products = result.scalars().unique().all()

        data = []
        for product in products:
            details = [d for d in product.product_details if d.deleted_at is None]
            details_sorted = sorted(details, key=lambda d: d.scraped_at)
            prices = [float(d.price) for d in details if d.price is not None]
            sources = sorted({d.source for d in details})
            first_image_url = next(
                (d.image_url for d in details_sorted if d.image_url),
                None,
            )
            data.append(
                ProductSummaryResponse(
                    id=product.id,
                    model_number=product.model_number,
                    brand=product.brand,
                    series=product.series,
                    processor=product.processor,
                    ram=product.ram,
                    storage=product.storage,
                    screen_size=product.screen_size,
                    graphic_processor=product.graphic_processor,
                    colour=product.colour,
                    min_price=min(prices) if prices else None,
                    max_price=max(prices) if prices else None,
                    sources=sources,
                    image_url=first_image_url,
                )
            )

        pages = math.ceil(total / size) if total > 0 else 0

        return {
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
            "data": data,
        }

    async def get_product_with_details(
        self, product_id: UUID
    ) -> Optional[AdminProductResponse]:
        """Get a product with listings by its ID"""

        stmt = (
            select(Products)
            .options(selectinload(Products.product_details))
            .where(and_(Products.id == product_id, Products.deleted_at.is_(None)))
        )
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            return None

        return AdminProductResponse(
            id=product.id,
            model_number=product.model_number,
            brand=product.brand,
            series=product.series,
            processor=product.processor,
            ram=product.ram,
            storage=product.storage,
            screen_size=product.screen_size,
            graphic_processor=product.graphic_processor,
            colour=product.colour,
            created_at=product.created_at,
            updated_at=product.updated_at,
            product_details=[
                detail
                for detail in product.product_details
                if detail.deleted_at is None
            ],
        )

    async def get_products_by_ids(
        self, product_ids: list[UUID]
    ) -> list[AdminProductResponse]:
        if not product_ids:
            return []

        stmt = (
            select(Products)
            .options(selectinload(Products.product_details))
            .where(Products.id.in_(product_ids), Products.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        products = result.scalars().unique().all()

        return [
            AdminProductResponse(
                id=product.id,
                model_number=product.model_number,
                brand=product.brand,
                series=product.series,
                processor=product.processor,
                ram=product.ram,
                storage=product.storage,
                screen_size=product.screen_size,
                graphic_processor=product.graphic_processor,
                colour=product.colour,
                created_at=product.created_at,
                updated_at=product.updated_at,
                product_details=[
                    detail
                    for detail in product.product_details
                    if detail.deleted_at is None
                ],
            )
            for product in products
        ]

    async def get_all_products_admin(
        self, page: int = 1, size: int = 10, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all products with listings - Admin only"""

        skip = (page - 1) * size

        filters = [Products.deleted_at.is_(None)]
        if search:
            like = f"%{search}%"
            filters.append(
                or_(
                    Products.model_number.ilike(like),
                    Products.brand.ilike(like),
                    Products.series.ilike(like),
                    Products.processor.ilike(like),
                )
            )

        count_stmt = select(func.count(Products.id)).where(*filters)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        stmt = (
            select(Products)
            .options(selectinload(Products.product_details))
            .where(*filters)
            .order_by(Products.created_at.desc())
            .offset(skip)
            .limit(size)
        )
        result = await self.db.execute(stmt)
        products = result.scalars().unique().all()

        data = [
            AdminProductResponse(
                id=product.id,
                model_number=product.model_number,
                brand=product.brand,
                series=product.series,
                processor=product.processor,
                ram=product.ram,
                storage=product.storage,
                screen_size=product.screen_size,
                graphic_processor=product.graphic_processor,
                colour=product.colour,
                created_at=product.created_at,
                updated_at=product.updated_at,
                product_details=[
                    detail
                    for detail in product.product_details
                    if detail.deleted_at is None
                ],
            )
            for product in products
        ]

        pages = math.ceil(total / size) if total > 0 else 0

        return {
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
            "data": data,
        }

    async def create_product_with_detail(self, product_data: ProductCreate) -> Products:
        """Create a new product and listing - Admin only"""
        try:
            existing_product = await self.db.execute(
                select(Products).where(
                    Products.model_number == product_data.model_number,
                    Products.deleted_at.is_(None),
                )
            )
            product = existing_product.scalar_one_or_none()

            if not product:
                product = Products(
                    model_number=product_data.model_number,
                    brand=product_data.brand,
                    series=product_data.series,
                    processor=product_data.processor,
                    ram=product_data.ram,
                    storage=product_data.storage,
                    screen_size=product_data.screen_size,
                    graphic_processor=product_data.graphic_processor,
                    colour=product_data.colour,
                )
                self.db.add(product)
                await self.db.flush()

            detail = ProductDetails(
                product_id=product.id,
                source=product_data.source,
                run_id=product_data.run_id,
                price=product_data.price,
                discount=product_data.discount,
                rating=product_data.rating,
                review_count=product_data.review_count,
                url=str(product_data.url),
                image_url=str(product_data.image_url)
                if product_data.image_url
                else None,
            )
            self.db.add(detail)

            await self.db.commit()
            await self.db.refresh(product)
            return product
        except IntegrityError:
            await self.db.rollback()
            raise ConflictException(
                "Product listing already exists for this model and source."
            )
        except Exception:
            await self.db.rollback()
            raise

    async def update_product_detail(
        self, product_id: UUID, source: str, update_data: ProductListingUpdate
    ) -> Optional[ProductDetails]:
        """Update a listing - Admin only"""
        try:
            update_dict = update_data.model_dump(exclude_unset=True)

            result = await self.db.execute(
                update(ProductDetails)
                .where(
                    and_(
                        ProductDetails.product_id == product_id,
                        ProductDetails.source == source,
                        ProductDetails.deleted_at.is_(None),
                    )
                )
                .values(**update_dict)
                .returning(ProductDetails)
            )
            detail = result.scalar_one_or_none()

            if not detail:
                await self.db.rollback()
                return None
            else:
                await self.db.commit()
                return detail
        except Exception:
            await self.db.rollback()
            raise

    async def delete_product_detail(self, product_id: UUID, source: str) -> bool:
        """Delete a listing - Admin only"""

        try:
            stmt = select(ProductDetails).where(
                and_(
                    ProductDetails.product_id == product_id,
                    ProductDetails.source == source,
                    ProductDetails.deleted_at.is_(None),
                )
            )
            result = await self.db.execute(stmt)
            detail = result.scalar_one_or_none()

            if not detail:
                raise NotFoundException("Listing not found for this product and source")

            await self.db.execute(
                update(ProductDetails)
                .where(ProductDetails.id == detail.id)
                .values(deleted_at=func.now())
            )

            await self.db.commit()
            return True

        except NotFoundException:
            raise
        except Exception:
            await self.db.rollback()
            raise

    async def delete_product(self, product_id: UUID) -> bool:
        """Delete a product - Admin only"""

        try:
            result = await self.db.execute(
                update(Products)
                .where(and_(Products.id == product_id, Products.deleted_at.is_(None)))
                .values(deleted_at=func.now())
                .returning(Products.id)
            )

            deleted_product = result.scalar_one_or_none()

            if not deleted_product:
                raise NotFoundException(
                    "Product not found. Please check the product ID and try again."
                )

            await self.db.execute(
                update(ProductDetails)
                .where(
                    and_(
                        ProductDetails.product_id == product_id,
                        ProductDetails.deleted_at.is_(None),
                    )
                )
                .values(deleted_at=func.now())
            )

            await self.db.commit()
            return True

        except NotFoundException:
            raise
        except Exception:
            await self.db.rollback()
            raise
