# Utku Uğurlu 231201016
import os
import json
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from dotenv import load_dotenv

load_dotenv()

from src.lib.db.models.chat import ChatHistory
from src.lib.db.models.idea import Idea

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("HATA: GEMINI_API_KEY bulunamadı!")
else:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = """
Sen deneyimli bir girişim mentörüsün. Kullanıcıyla Türkçe sohbet edeceksin.
Görevin: Kullanıcının girişim fikrini anlamak ve JSON döndürmek.
ÇIKTI KURALI — SADECE JSON döndür:
{
  "idea_ready": false,
  "message": "<soru>"
}
veya fikir hazırsa tam rapor JSON döndür.
"""

class AIService:
    @staticmethod
    def _to_gemini_history(chats: list[ChatHistory]) -> list[dict]:
        history = []
        for chat in chats:
            role = "model" if chat.sender == "ai" else "user"
            history.append({"role": role, "parts": [chat.message]})
        return history

    @staticmethod
    async def get_chat_history(session_id: str, db: AsyncSession) -> list[ChatHistory]:
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at.asc())
        )
        return result.scalars().all()

    @staticmethod
    async def save_idea(user_id: int, session_id: str, ai_data: dict, db: AsyncSession) -> Idea:
        report = ai_data.get("report", ai_data)
        
        title = report.get("title") or report.get("startup_name") or report.get("name") or "İsimsiz Fikir"
        summary = report.get("executive_summary") or report.get("summary") or report.get("description") or ""
        swot = report.get("swot_analysis", {})
        market = report.get("market_analysis") or report.get("market") or {}
        model = report.get("business_model") or report.get("revenue_model") or ""

        idea = Idea(
            user_id=user_id,
            session_id=session_id,
            title=str(title),
            executive_summary=str(summary),
            swot_analysis=json.dumps(swot),
            market_analysis=json.dumps(market),
            business_model=str(model),
        )
        db.add(idea)
        await db.flush()
        return idea

    @classmethod
    async def process_message(cls, session_id: str, user_message: str, user_id: int, db: AsyncSession) -> dict:
        all_chats = await cls.get_chat_history(session_id, db)
        past_chats = all_chats[:-1] if len(all_chats) > 0 else []

        model_name = "gemini-3-flash"
        
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_PROMPT,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                ),
            )
            gemini_history = cls._to_gemini_history(past_chats)
            chat_session = model.start_chat(history=gemini_history)
            response = await chat_session.send_message_async(user_message)
            raw_text = response.text
        except Exception as e:
            if "429" in str(e):
                return {"reply": "Çok fazla istek gönderildi. Lütfen 1 dakika bekleyip tekrar deneyin.", "idea_created": False, "created_idea_id": None}
            return {"reply": f"AI Bağlantı Hatası: {str(e)}", "idea_created": False, "created_idea_id": None}
        
        try:
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            ai_json = json.loads(clean_text)
        except Exception:
            ai_json = {"idea_ready": False, "message": raw_text}

        assistant_message = ai_json.get("message", raw_text)
        
        # Eğer bir rapor oluşturulduysa, chat'te kısa ve öz bir mesaj ver
        if ai_json.get("idea_ready") is True:
            assistant_message = "Harika! Bilgiler yeterli, senin için kapsamlı bir rapor hazırladım ve 'Fikirlerim' bölümüne kaydettim. Oradan tüm detayları inceleyebilirsin."

        idea_created = False
        created_idea_id = None

        if ai_json.get("idea_ready") is True:
            try:
                idea = await cls.save_idea(user_id, session_id, ai_json, db)
                idea_created = True
                created_idea_id = idea.id
            except Exception as e:
                print(f"DEBUG - Fikir Kayıt Hatası: {e}")

        return {
            "reply": assistant_message,
            "idea_created": idea_created,
            "created_idea_id": created_idea_id
        }
