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
    
    # from fastapi import APIRouter, Request, HTTPException
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, Field
# import os
# import logging
# from openai import OpenAI
# from typing import Literal, Optional, Dict, Any, Union, List
# from datetime import datetime, timedelta

# logger = logging.getLogger("ella_app")
# logger.setLevel(logging.DEBUG)  # Set to DEBUG for more verbose logging

# # Add a file handler
# file_handler = logging.FileHandler("ella_app.log")
# file_handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

# router = APIRouter()


# class ChatMessage(BaseModel):
#     message: str
#     player_id: str
#     npc_id: str
#     limit: int = 200
#     request_type: str = "chat"
#     context: Optional[Union[Dict[str, Any], List[str]]] = Field(default_factory=dict)
#     npc_name: Optional[str] = None

# class ExploreAction(BaseModel):
#     type: Literal["explore"]
#     x: float
#     y: float
#     z: float

# class FollowAction(BaseModel):
#     type: Literal["follow"]
#     target: str

# class InteractAction(BaseModel):
#     type: Literal["interact"]
#     target: str

# class NPCResponse(BaseModel):
#     message: str
#     action: Optional[ExploreAction | FollowAction | InteractAction]

# class ConversationManager:
#     def __init__(self):
#         self.conversations = {}
#         self.expiry_time = timedelta(minutes=30)

#     def get_conversation(self, player_id, npc_id):
#         key = (player_id, npc_id)
#         if key in self.conversations:
#             conversation, last_update = self.conversations[key]
#             if datetime.now() - last_update > self.expiry_time:
#                 del self.conversations[key]
#                 return []
#             return conversation
#         return []

#     def update_conversation(self, player_id, npc_id, message):
#         key = (player_id, npc_id)
#         if key not in self.conversations:
#             self.conversations[key] = ([], datetime.now())
#         conversation, _ = self.conversations[key]
#         conversation.append(message)
#         self.conversations[key] = (conversation[-50:], datetime.now())  # Keep last 50 messages

# conversation_manager = ConversationManager()

# @router.post("/robloxgpt")
# async def chatgpt_endpoint(request: Request):
#     logger.info(f"Received request to /robloxgpt endpoint")
    
#     body = await request.body()
#     logger.debug(f"Raw request body: {body.decode()}")
    
#     try:
#         data = json.loads(body)
#         logger.debug(f"Parsed request data: {data}")
        
#         # Convert context to dict if it's a list
#         if isinstance(data.get('context'), list):
#             data['context'] = {'nearby_players': data['context']}
        
#         chat_message = ChatMessage(**data)
#         logger.info(f"Validated chat message: {chat_message}")
#     except json.JSONDecodeError as e:
#         logger.error(f"Failed to parse JSON: {e}")
#         raise HTTPException(status_code=400, detail="Invalid JSON in request body")
#     except ValueError as e:
#         logger.error(f"Failed to validate data: {e}")
#         raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")

#     OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
#     if not OPENAI_API_KEY:
#         logger.error("OpenAI API key not found")
#         raise HTTPException(status_code=500, detail="OpenAI API key not found")

#     client = OpenAI(api_key=OPENAI_API_KEY)

#     # Get conversation history
#     conversation = conversation_manager.get_conversation(chat_message.player_id, chat_message.npc_id)
    
#     try:
#         if chat_message.request_type == "chat":
#             functions = [{
#                 "name": "generate_chat_response",
#                 "description": "Generate a chat response as Eldrin the Wise",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "message": {
#                             "type": "string",
#                             "description": "The chat response from Eldrin"
#                         }
#                     },
#                     "required": ["message"]
#                 }
#             }]
            
#             context_summary = (
#                 f"Player: {chat_message.context.get('player_name', 'Unknown')}. "
#                 f"New conversation: {chat_message.context.get('is_new_conversation', True)}. "
#                 f"Time since last interaction: {chat_message.context.get('time_since_last_interaction', 'N/A')}. "
#                 f"Nearby players: {', '.join(chat_message.context.get('nearby_players', []))}. "
#                 f"NPC location: {chat_message.context.get('npc_location', 'Unknown')}."
#             )
            
#             messages = [
#                 {"role": "system", "content": f"You are Eldrin the Wise, a centuries-old wizard who resides in the enchanted forest of Eldoria. {context_summary}"},
#                 *[{"role": "assistant" if i % 2 else "user", "content": msg} for i, msg in enumerate(conversation)],
#                 {"role": "user", "content": f"Respond concisely within {chat_message.limit} characters to this message: {chat_message.message}"}
#             ]
#         elif chat_message.request_type == "behavior_update":
#             functions = [{
#                 "name": "generate_npc_response",
#                 "description": "Generate an NPC response and action for Eldrin the Wise",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "message": {
#                             "type": "string",
#                             "description": "Eldrin's thoughts or speech"
#                         },
#                         "action": {
#                             "type": "object",
#                             "properties": {
#                                 "type": {
#                                     "type": "string",
#                                     "enum": ["explore", "follow", "interact"],
#                                     "description": "The type of action Eldrin should take"
#                                 },
#                                 "x": {
#                                     "type": "number",
#                                     "description": "X coordinate for explore action"
#                                 },
#                                 "y": {
#                                     "type": "number",
#                                     "description": "Y coordinate for explore action"
#                                 },
#                                 "z": {
#                                     "type": "number",
#                                     "description": "Z coordinate for explore action"
#                                 },
#                                 "target": {
#                                     "type": "string",
#                                     "description": "Target for follow or interact action"
#                                 }
#                             },
#                             "required": ["type"]
#                         }
#                     },
#                     "required": ["message", "action"]
#                 }
#             }]
#             context_summary = (
#                 f"Nearby players: {', '.join(chat_message.context.get('nearby_players', []))}. "
#                 f"NPC location: {chat_message.context.get('npc_location', 'Unknown')}."
#             )
#             messages = [
#                 {"role": "system", "content": f"You are controlling Eldrin the Wise, a wizard NPC in a game. {context_summary}"},
#                 {"role": "user", "content": f"Decide on the next action for Eldrin based on this situation: {chat_message.message or 'No specific context provided. Eldrin is idly waiting.'}"}
#             ]
#         else:
#             logger.error(f"Invalid request_type: {chat_message.request_type}")
#             raise HTTPException(status_code=400, detail="Invalid request type")

#         logger.info(f"Sending request to OpenAI API")
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages,
#             functions=functions,
#             function_call={"name": "generate_chat_response" if chat_message.request_type == "chat" else "generate_npc_response"}
#         )
        
#         function_response = response.choices[0].message.function_call.arguments
#         parsed_response = eval(function_response)
#         logger.info(f"AI response: {parsed_response}")

#         if chat_message.request_type == "chat":
#             # Update conversation history
#             conversation_manager.update_conversation(chat_message.player_id, chat_message.npc_id, chat_message.message)
#             conversation_manager.update_conversation(chat_message.player_id, chat_message.npc_id, parsed_response["message"])
#             logger.info(f"Returning chat response: {parsed_response['message']}")
#             return JSONResponse({"message": parsed_response["message"]})
#         else:
#             logger.info(f"Returning behavior response: {parsed_response}")
#             return JSONResponse(NPCResponse(**parsed_response).dict())

#     except Exception as e:
#         logger.error(f"Error processing request: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")

