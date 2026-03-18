import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config.config import Config
from app.data_controllers.user_data_controller import UserDataController
from app.schemas.user_schemas import UserCreate
from app.constants.constants import SeedAdminConstants
from app.utils.jwt_utils import JWTUtils


async def seed_admin():
    """Seed an admin user into the database."""

    engine = create_async_engine(
        url=Config.DATABASE_URL,
        echo=True,
    )

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            user_controller = UserDataController(session)

            existing_admin = await user_controller.get_user_by_username(
                SeedAdminConstants.USERNAME
            )
            if existing_admin:
                print("Admin user already exists!")
                return

            admin_data = UserCreate(
                username=SeedAdminConstants.USERNAME,
                password=SeedAdminConstants.PASSWORD,
                role=SeedAdminConstants.ROLE,
            )

            hashed_password = JWTUtils.get_password_hash(admin_data.password)
            admin_user = await user_controller.create_user(admin_data, hashed_password)

            print("Admin user created successfully!")
            print(f"Username: {admin_user.username}")
            print(f"Role: {admin_user.role}")
            print(f"ID: {admin_user.id}")

        except Exception as e:
            print(f"Error seeding admin: {e}")
            await session.rollback()
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(seed_admin())
