# /robloxgpt.py
# API for AI interaction
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
import logging
from openai import OpenAI
from typing import Literal, Optional, Dict, Any, Union, List
from datetime import datetime, timedelta

logger = logging.getLogger("ella_app")
logger.setLevel(logging.DEBUG)

router = APIRouter()

# V1 Classes and Functions
class ChatMessage(BaseModel):
    message: str
    player_id: str
    npc_id: str
    limit: int = 200
    request_type: str = "chat"
    context: Optional[Union[Dict[str, Any], List[str]]] = Field(default_factory=dict)
    npc_name: Optional[str] = None

class NPCResponse(BaseModel):
    message: str
    action: Optional[Dict[str, Any]] = None

class ConversationManager:
    def __init__(self):
        self.conversations = {}
        self.expiry_time = timedelta(minutes=30)

    def get_conversation(self, player_id, npc_id):
        key = (player_id, npc_id)
        if key in self.conversations:
            conversation, last_update = self.conversations[key]
            if datetime.now() - last_update > self.expiry_time:
                del self.conversations[key]
                return []
            return conversation
        return []

    def update_conversation(self, player_id, npc_id, message):
        key = (player_id, npc_id)
        if key not in self.conversations:
            self.conversations[key] = ([], datetime.now())
        conversation, _ = self.conversations[key]
        conversation.append(message)
        self.conversations[key] = (conversation[-50:], datetime.now())  # Keep last 50 messages

conversation_manager = ConversationManager()

# NPC configurations
npc_configs = {
    "eldrin": {
        "name": "Eldrin the Wise",
        "system_prompt": "You are Eldrin the Wise, a centuries-old wizard who resides in the enchanted forest of Eldoria.",
    },
    "luna": {
        "name": "Luna the Stargazer",
        "system_prompt": "You are Luna the Stargazer, a mystical astronomer who lives in the Celestial Tower.",
    }
}

# V1 Endpoint (Unchanged)
@router.post("/robloxgpt")
async def chatgpt_endpoint(request: Request):
    logger.info(f"Received request to /robloxgpt endpoint")
    
    try:
        data = await request.json()
        logger.debug(f"Parsed request data: {data}")
        
        chat_message = ChatMessage(**data)
        logger.info(f"Validated chat message: {chat_message}")
    except Exception as e:
        logger.error(f"Failed to parse or validate data: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found")
        raise HTTPException(status_code=500, detail="OpenAI API key not found")

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Get NPC configuration
    npc_config = npc_configs.get(chat_message.npc_id.lower())
    if not npc_config:
        logger.error(f"NPC configuration not found for {chat_message.npc_id}")
        raise HTTPException(status_code=400, detail="Invalid NPC ID")

    # Get conversation history
    conversation = conversation_manager.get_conversation(chat_message.player_id, chat_message.npc_id)
    
    try:
        context_summary = (
            f"Player: {chat_message.context.get('player_name', 'Unknown')}. "
            f"New conversation: {chat_message.context.get('is_new_conversation', True)}. "
            f"Time since last interaction: {chat_message.context.get('time_since_last_interaction', 'N/A')}. "
            f"Nearby players: {', '.join(chat_message.context.get('nearby_players', []))}. "
            f"NPC location: {chat_message.context.get('npc_location', 'Unknown')}."
        )
        
        messages = [
            {"role": "system", "content": f"{npc_config['system_prompt']} {context_summary}"},
            *[{"role": "assistant" if i % 2 else "user", "content": msg} for i, msg in enumerate(conversation)],
            {"role": "user", "content": f"Respond concisely within {chat_message.limit} characters to this message: {chat_message.message}"}
        ]

        logger.info(f"Sending request to OpenAI API for {npc_config['name']}")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=chat_message.limit
        )
        
        ai_message = response.choices[0].message.content
        logger.info(f"AI response for {npc_config['name']}: {ai_message}")

        # Update conversation history
        conversation_manager.update_conversation(chat_message.player_id, chat_message.npc_id, chat_message.message)
        conversation_manager.update_conversation(chat_message.player_id, chat_message.npc_id, ai_message)

        return JSONResponse({"message": ai_message, "npc_name": npc_config['name']})

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")

# V2 Classes and Functions
class PerceptionData(BaseModel):
    visible_objects: List[str] = Field(default_factory=list)
    visible_players: List[str] = Field(default_factory=list)
    memory: List[Dict[str, Any]] = Field(default_factory=list)

class EnhancedChatMessage(BaseModel):
    message: str
    player_id: str
    npc_id: str
    limit: int = 200
    npc_name: str
    system_prompt: str
    perception: Optional[PerceptionData] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

# V2 Endpoint
@router.post("/robloxgpt/v2")
async def enhanced_chatgpt_endpoint(request: Request):
    logger.info(f"Received request to /robloxgpt/v2 endpoint")
    
    try:
        data = await request.json()
        logger.debug(f"Parsed request data: {data}")
        
        chat_message = EnhancedChatMessage(**data)
        logger.info(f"Validated enhanced chat message: {chat_message}")
    except Exception as e:
        logger.error(f"Failed to parse or validate data: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found")
        raise HTTPException(status_code=500, detail="OpenAI API key not found")

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Get conversation history
    conversation = conversation_manager.get_conversation(chat_message.player_id, chat_message.npc_id)
    
    try:
        context_summary = (
            f"NPC: {chat_message.npc_name}. "
            f"Player: {chat_message.context.get('player_name', 'Unknown')}. "
            f"New conversation: {chat_message.context.get('is_new_conversation', True)}. "
            f"Time since last interaction: {chat_message.context.get('time_since_last_interaction', 'N/A')}. "
            f"Nearby players: {', '.join(chat_message.context.get('nearby_players', []))}. "
            f"NPC location: {chat_message.context.get('npc_location', 'Unknown')}."
        )
        
        if chat_message.perception:
            context_summary += (
                f" Visible objects: {', '.join(chat_message.perception.visible_objects)}."
                f" Visible players: {', '.join(chat_message.perception.visible_players)}."
                f" Recent memories: {', '.join([str(m) for m in chat_message.perception.memory[-5:]])}."
            )

        messages = [
            {"role": "system", "content": f"{chat_message.system_prompt} {context_summary}"},
            *[{"role": "assistant" if i % 2 else "user", "content": msg} for i, msg in enumerate(conversation)],
            {"role": "user", "content": f"Respond concisely within {chat_message.limit} characters to this message: {chat_message.message}"}
        ]

        logger.info(f"Sending request to OpenAI API for {chat_message.npc_name}")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=chat_message.limit
        )
        
        ai_message = response.choices[0].message.content
        logger.info(f"AI response for {chat_message.npc_name}: {ai_message}")

        # Update conversation history
        conversation_manager.update_conversation(chat_message.player_id, chat_message.npc_id, chat_message.message)
        conversation_manager.update_conversation(chat_message.player_id, chat_message.npc_id, ai_message)

        return JSONResponse({"message": ai_message, "npc_name": chat_message.npc_name})

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")