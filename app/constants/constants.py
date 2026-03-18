class DataBaseConstants:
    """Database connection and pooling constants"""

    ECHO = False
    FUTURE = True
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 1800
    POOL_PRE_PING = True


class Roles:
    """User roles in the system"""

    ADMIN = "ADMIN"
    USER = "USER"


class SeedAdminConstants:
    """Default admin user constants for seeding the database"""

    USERNAME = "admin"
    PASSWORD = "admin1"
    ROLE = Roles.ADMIN


class PaginationConstants:
    DEFAULT_PAGE = 1
    DEFAULT_SIZE = 10
    MAX_SIZE = 100


class ListingSources:
    """Supported marketplace sources"""

    AMAZON = "AMAZON"
    FLIPKART = "FLIPKART"


class PublicRoutes:
    """Public routes that do not require authentication"""

    ROUTES = [
        "/",
        "/db-test",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/docs",
        "/openapi.json",
        "/ui/login",
        "/ui/admin/dashboard",
        "/ui/user/dashboard",
    ]


class EmbeddingRunStatus:
    """Status of the embedding process"""

    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EmbeddingStatus:
    """Status of product embeddings"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ChatConstants:
    """Constants related to chat functionality"""

    TOP_K_RESULTS = 5
    MIN_RELEVANCE_SCORE = 20.0


class ActivityTypes:
    """Types of activities for logging"""

    REDIRECTED = "REDIRECTED"
    PRODUCT_NOT_FOUND = "PRODUCT_NOT_FOUND"
    FIELD_MISSING = "FIELD_MISSING"
    ALREADY_EXIST = "ALREADY_EXIST"
