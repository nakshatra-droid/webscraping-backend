from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct, text
from app.models.product_details import ProductDetails
from app.models.products import Products
from app.models.product_embeddings import ProductEmbeddings
from app.constants.constants import ChatConstants


class ChatDataController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_products(
        self,
        query_vector: list[float],
        filters: dict,
        top_k: int,
    ) -> list[dict]:
        """
        Run a pgvector product search on product embeddings,

        :params:
            query_vector: Encoded query embedding as a list of floats.
            filters:      Dict with optional keys: price_max, price_min, rating_min.
            top_k:        Maximum number of results to return.

        :returns:
            List of product dicts ready to be sent to the client.
        """

        score_expr = (
            -ProductEmbeddings.embedding.max_inner_product(query_vector)
        ).label("score")

        stmt = (
            select(
                Products,
                func.min(ProductDetails.price).label("min_price"),
                func.max(ProductDetails.price).label("max_price"),
                func.max(ProductDetails.rating).label("max_rating"),
                func.array_agg(distinct(ProductDetails.source)).label("sources"),
                score_expr,
            )
            .join(ProductEmbeddings, ProductEmbeddings.product_id == Products.id)
            .join(ProductDetails, ProductDetails.product_id == Products.id)
            .where(
                Products.deleted_at.is_(None),
                ProductDetails.deleted_at.is_(None),
            )
            .group_by(Products.id, ProductEmbeddings.embedding)
        )

        if "price_max" in filters:
            stmt = stmt.having(func.min(ProductDetails.price) <= filters["price_max"])
        if "price_min" in filters:
            stmt = stmt.having(func.min(ProductDetails.price) >= filters["price_min"])
        if "rating_min" in filters:
            stmt = stmt.having(func.max(ProductDetails.rating) >= filters["rating_min"])
        if "discount_min" in filters:
            stmt = stmt.having(
                func.max(ProductDetails.discount) >= filters["discount_min"]
            )

        stmt = stmt.order_by(
            ProductEmbeddings.embedding.max_inner_product(query_vector)
        ).limit(top_k)

        result = await self.db.execute(stmt)
        rows = result.all()

        matched = [
            (product, min_price, max_price, max_rating, sources, score)
            for product, min_price, max_price, max_rating, sources, score in rows
            if score >= ChatConstants.MIN_RELEVANCE_SCORE
        ]

        if filters.get("sort_by_rating"):
            matched.sort(
                key=lambda r: float(r[3]) if r[3] is not None else 0.0,
                reverse=True,
            )
        elif filters.get("sort_by_price_asc"):
            matched.sort(
                key=lambda r: float(r[1]) if r[1] is not None else float("inf")
            )

        results = []
        for product, min_price, max_price, max_rating, sources, score in matched:
            # Fetch all listings for this product
            listings = await self.db.execute(
                select(
                    ProductDetails.source,
                    ProductDetails.url,
                    ProductDetails.image_url,
                    ProductDetails.price,
                ).where(
                    ProductDetails.product_id == product.id,
                    ProductDetails.deleted_at.is_(None),
                )
            )
            listings = listings.all()
            sources_arr = [
                {
                    "source": src,
                    "url": url,
                    "price": float(price) if price is not None else None,
                }
                for src, url, _, price in listings
            ]
            # Pick first available image_url
            image_url = None
            for _, _, img, _ in listings:
                if img:
                    image_url = img
                    break
            results.append(
                {
                    "id": str(product.id),
                    "model_number": product.model_number,
                    "brand": product.brand,
                    "series": product.series,
                    "processor": product.processor,
                    "ram": product.ram,
                    "storage": product.storage,
                    "screen_size": product.screen_size,
                    "graphic_processor": product.graphic_processor,
                    "colour": product.colour,
                    "min_price": float(min_price) if min_price is not None else None,
                    "max_price": float(max_price) if max_price is not None else None,
                    "rating": float(max_rating) if max_rating is not None else None,
                    "sources": sources_arr,
                    "image_url": image_url,
                }
            )
        return results

    async def run_structured_sql(self, sql: str) -> list[dict]:
        """
        Execute a validated SQL query and return results in the same shape
        as search_products().
        """
        result = await self.db.execute(text(sql))
        rows = result.mappings().all()
        results = []
        for row in rows:
            
            sources_arr = []
            sources = row.get("sources", [])
            urls = row.get("urls", [])
            image_urls = row.get("image_urls", [])
            prices = row.get("prices", []) if "prices" in row else []
            if sources and urls and prices and len(sources) == len(urls) == len(prices):
                sources_arr = [
                    {
                        "source": src,
                        "url": url,
                        "price": float(price) if price is not None else None,
                    }
                    for src, url, price in zip(sources, urls, prices)
                ]
            elif sources and urls and len(sources) == len(urls):
                sources_arr = [
                    {"source": src, "url": url, "price": None}
                    for src, url in zip(sources, urls)
                ]
            else:
                sources_arr = [
                    {"source": src, "url": None, "price": None} for src in sources
                ]
            # Pick first available image_url
            image_url = None
            for img in image_urls:
                if img:
                    image_url = img
                    break
            results.append(
                {
                    "id": str(row["id"]),
                    "model_number": row["model_number"],
                    "brand": row["brand"],
                    "series": row["series"],
                    "processor": row["processor"],
                    "ram": row["ram"],
                    "storage": row["storage"],
                    "screen_size": row["screen_size"],
                    "graphic_processor": row["graphic_processor"],
                    "colour": row["colour"],
                    "min_price": float(row["min_price"])
                    if row["min_price"] is not None
                    else None,
                    "max_price": float(row["max_price"])
                    if row["max_price"] is not None
                    else None,
                    "rating": float(row["max_rating"])
                    if row["max_rating"] is not None
                    else None,
                    "sources": sources_arr,
                    "image_url": image_url,
                }
            )
        return results
