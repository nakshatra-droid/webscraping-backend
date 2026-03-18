from app.data_controllers.dashboard_data_controller import DashboardDataController
from sqlalchemy.ext.asyncio import AsyncSession


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self):
        stats = await DashboardDataController(self.db).get_stats()
        return stats
