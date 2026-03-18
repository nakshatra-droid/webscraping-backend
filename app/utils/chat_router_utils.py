import re

import ollama

ROUTER_PROMPT = """You are a query router for a laptop product search system.
Classify the user's query as either STRUCTURED or SEMANTIC.

STRUCTURED: queries that mention specific filters like price range, brand name, RAM size,
storage, processor type, screen size, rating, or discount.
SEMANTIC: general or descriptive queries like "best laptop for gaming" or
"lightweight laptop for students".

Respond with exactly one word: STRUCTURED or SEMANTIC.

Query: {question}"""

SQL_PROMPT = """
You are an expert PostgreSQL SQL generator for a laptop product search system.

Your task is to convert the user's natural language question into a safe SQL SELECT query.

DATABASE SCHEMA

products (
    id UUID,
    model_number TEXT,
    brand TEXT,
    series TEXT,
    processor TEXT,
    ram TEXT,
    storage TEXT,
    screen_size TEXT,
    graphic_processor TEXT,
    colour TEXT,
    deleted_at TIMESTAMP
)

product_details (
    id UUID,
    product_id UUID,
    source TEXT,
    price NUMERIC,
    discount NUMERIC,
    rating NUMERIC,
    review_count INTEGER,
    url TEXT,
    image_url TEXT,
    deleted_at TIMESTAMP
)

TABLE RELATIONSHIP

product_details.product_id = products.id

IMPORTANT RULES

1. ALWAYS use this JOIN

FROM products
JOIN product_details
ON product_details.product_id = products.id

2. ALWAYS filter out deleted records

products.deleted_at IS NULL
AND product_details.deleted_at IS NULL

3. TEXT SEARCH

Use case-insensitive search for text fields using ILIKE.

Example:
products.brand ILIKE '%asus%'
products.processor ILIKE '%ryzen%'
products.ram ILIKE '%16%'
products.storage ILIKE '%512%'
products.series ILIKE '%tuf%'
products.graphic_processor ILIKE '%rtx%'
products.graphic_processor ILIKE '%nvidia%'

4. PRICE FILTERING

All price filters MUST use:

product_details.price

Examples:

under 70000
→ product_details.price <= 70000

between 50000 and 80000
→ product_details.price BETWEEN 50000 AND 80000

above 60000
→ product_details.price >= 60000

NEVER use products.price (it does not exist).

5. RESULT AGGREGATION

Because the same product may exist on multiple sources,
aggregate results per product.

Use:

MIN(product_details.price) AS min_price
MAX(product_details.price) AS max_price
MAX(product_details.rating) AS max_rating
ARRAY_AGG(DISTINCT product_details.source) AS sources
ARRAY_AGG(DISTINCT product_details.url) AS urls
ARRAY_AGG(DISTINCT product_details.image_url) AS image_urls
ARRAY_AGG(DISTINCT product_details.price) AS prices

6. GROUPING

Always group by:

GROUP BY products.id

7. RESULT ORDERING

Always sort results by the cheapest available price:

ORDER BY MIN(product_details.price) ASC

8. RESULT LIMIT

Always limit results:

LIMIT 50

9. SELECT EXACTLY THESE COLUMNS

products.id,
products.model_number,
products.brand,
products.series,
products.processor,
products.ram,
products.storage,
products.screen_size,
products.graphic_processor,
products.colour,
MIN(product_details.price) AS min_price,
MAX(product_details.price) AS max_price,
MAX(product_details.rating) AS max_rating,
ARRAY_AGG(DISTINCT product_details.source) AS sources
ARRAY_AGG(DISTINCT product_details.url) AS urls,
ARRAY_AGG(DISTINCT product_details.image_url) AS image_urls,
ARRAY_AGG(DISTINCT product_details.price) AS prices

10. RETURN FORMAT

Return ONLY the raw SQL query.
Do NOT include markdown, explanation, or comments.

USER QUESTION:
{question}
"""

ALLOWED_TABLES = {"products", "product_details"}
_BLOCKED = re.compile(
    r"\b(drop|delete|update|insert|alter|truncate|create|grant|revoke|exec|execute)\b",
    re.IGNORECASE,
)


def route_query(question: str) -> str:
    """Returns 'STRUCTURED' or 'SEMANTIC'."""
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": ROUTER_PROMPT.format(question=question)}],
    )
    result = response["message"]["content"].strip().upper()
    return "STRUCTURED" if "STRUCTURED" in result else "SEMANTIC"


def generate_sql(question: str) -> str:
    """Ask the LLM to produce a SELECT SQL string for the given question."""
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": SQL_PROMPT.format(question=question)}],
    )
    sql = response["message"]["content"].strip()

    sql = (
        re.sub(r"```(?:sql)?", "", sql, flags=re.IGNORECASE).replace("```", "").strip()
    )
    return sql


def is_safe_sql(sql: str) -> bool:
    """Validate that SQL is a safe read-only SELECT on allowed tables only."""
    stripped = sql.strip()
    if not stripped.upper().startswith("SELECT"):
        return False
    if _BLOCKED.search(stripped):
        return False

    if ";" in stripped.rstrip(";"):
        return False

    table_matches = re.findall(
        r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)", stripped, re.IGNORECASE
    )
    referenced = {t for pair in table_matches for t in pair if t}
    if not referenced.issubset(ALLOWED_TABLES):
        return False
    return True
