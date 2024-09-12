from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import logging
from openai import OpenAI

logger = logging.getLogger("ella_app")

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    player_id: str
    npc_id: str
    limit: int = 200  # Default character limit

@router.post("/robloxgpt")
async def chatgpt_endpoint(chat_message: ChatMessage, request: Request):
    logger.info(f"Received request to /robloxgpt endpoint")
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found")
        return JSONResponse(
            status_code=500,
            content={"message": "OpenAI API key not found"}
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Enhanced prompt to ensure a natural conversational style with a wizard backstory
    prompt = (
        f"You are Eldrin the Wise, a centuries-old wizard who resides in the enchanted forest of Eldoria. "
        f"You have spent your life studying the ancient arts of magic and possess vast knowledge of the mystical and arcane. "
        f"You are known for your wisdom, kindness, and willingness to help those in need. "
        f"You speak in a calm and measured tone, reflecting your years of experience and wisdom. "
        f"Despite your age, you are still curious about the world and enjoy learning new things from those you meet. "
        f"Respond concisely within {chat_message.limit} characters, ensuring the response is complete, makes sense, and is in a natural conversational style. "
        f"Do not use bullet points, double asterisks, double spaces, or any special formatting. "
        f"Here is the player's message: {chat_message.message}"
    )

    logger.info(f"Received message from {request.client.host}: {chat_message.message}, Player ID: {chat_message.player_id}, NPC ID: {chat_message.npc_id}, Limit: {chat_message.limit}")

    try:
        logger.info("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_response = response.choices[0].message.content.strip()
        logger.info(f"AI response: {ai_response}")
    except Exception as e:
        logger.error(f"Error interacting with ChatGPT: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Failed to interact with ChatGPT"}
        )

    return JSONResponse({"message": ai_response})