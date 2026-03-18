from sqlalchemy.dialects.postgresql import ENUM

listing_source_enum = ENUM(
    "AMAZON",
    "FLIPKART",
    name="listing_source",
    create_type=True,
)

embedding_status_enum = ENUM(
    "PENDING",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    name="embedding_status",
    create_type=True,
)

activity_type_enum = ENUM(
    "FIELD_MISSING",
    "PRODUCT_NOT_FOUND",
    "REDIRECTED",
    "ALREADY_EXIST",
    name="activity_type_enum",
    create_type=True,
)

user_role_enum = ENUM(
    "ADMIN",
    "USER",
    name="user_role",
    create_type=True,
)
