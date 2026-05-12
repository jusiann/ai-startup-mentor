from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from src.lib.db.models.chat import ChatHistory
from src.lib.db.models.idea import Idea

class AIService:
    @staticmethod
    async def process_message(session_id: str, user_message: str, user_id: int, db: AsyncSession):
        # 1. Fetch previous conversation history for context
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.session_id == session_id, ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at)
        )
        history = result.scalars().all()
        
        # Format history for LLM (Mocked context building)
        context = [{"role": msg.sender, "content": msg.message} for msg in history]
        context.append({"role": "user", "content": user_message})

        # TODO: Here you would call your actual LLM (e.g., OpenAI, Anthropic, or custom Agentic flow)
        # using the `context` to generate the next response.
        # For demonstration, we simulate an AI decision:
        
        # Simulated LLM response evaluation based on prompt logic:
        # If the LLM determines all elements (Market, SWOT, Business Model) are gathered:
        idea_is_ready = False  # Set by LLM output parser
        ai_reply = "Bu çok iyi bir fikir, peki hedef kitleniz detaylı olarak kimlerden oluşuyor?"
        created_idea_id = None
        
        # Mock logic triggering idea creation (e.g., if user mentions certain keywords)
        if "tamam" in user_message.lower() or len(context) > 5:
            idea_is_ready = True
            ai_reply = "Harika! Fikriniz yeterli olgunluğa ulaştı. Gerekli tüm verileri (Pazar, SWOT, İş Modeli) topladım. Girişim fikri raporunuz oluşturuluyor..."
            
            # Create Idea in DB
            new_idea = Idea(
                user_id=user_id,
                session_id=session_id,
                title="Yapay Zeka Tarafından Oluşturulan Girişim Fikri",
                executive_summary="Özet metin...",
                market_analysis="Pazar analizi...",
                swot_analysis="Güçlü Yönler:\nZayıf Yönler:\nFırsatlar:\nTehditler:",
                business_model="İş modeli...",
            )
            db.add(new_idea)
            await db.flush() # flush to get the id
            created_idea_id = new_idea.id

        return {
            "reply": ai_reply,
            "idea_created": idea_is_ready,
            "created_idea_id": created_idea_id
        }
