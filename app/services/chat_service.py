import traceback
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect

from app.constants.constants import ChatConstants
from app.data_controllers.chat_data_controller import ChatDataController
from app.data_controllers.chat_history_data_controller import ChatHistoryDataController
from app.database.database import AsyncSessionLocal
from app.models.chat_message import ChatSenderEnum
from app.utils.embedding_utils import EmbeddingUtils


class ChatService:
    async def handle_chat_websocket(
        self, websocket: WebSocket, user_id: UUID, session_id: UUID
    ):
        await websocket.accept()
        EmbeddingUtils.get_embedding_model()
        try:
            while True:
                query = await websocket.receive_text()
                query = query.strip()
                if not query:
                    continue

                await self._save_user_message(session_id=session_id, query=query)
                results = await self.search_products(query)
                await self._save_bot_products(session_id=session_id, products=results)
                await websocket.send_json(results)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            traceback.print_exc()
            try:
                await websocket.send_json({"error": str(e)})
            except Exception:
                pass

    async def search_products(
        self, query: str, top_k: int = ChatConstants.TOP_K_RESULTS
    ) -> list[dict]:
        
        filters={}
        model = EmbeddingUtils.get_embedding_model()

        encode_text = query 

        query_vector = model.encode(encode_text).tolist()

        async with AsyncSessionLocal() as db:
            controller = ChatDataController(db)
            return await controller.search_products(
                query_vector=query_vector,
                filters=filters,
                top_k=top_k,
            )

    async def _save_user_message(self, session_id: UUID, query: str) -> None:
        async with AsyncSessionLocal() as db:
            controller = ChatHistoryDataController(db)
            await controller.create_message(
                session_id=session_id,
                sender=ChatSenderEnum.USER,
                message={"text": query},
            )

    async def _save_bot_products(self, session_id: UUID, products: list[dict]) -> None:
       
        async with AsyncSessionLocal() as db:
            controller = ChatHistoryDataController(db)
            await controller.create_message(
                session_id=session_id,
                sender=ChatSenderEnum.BOT,
                message={"products": products},
            )
