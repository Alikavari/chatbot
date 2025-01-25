from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
from langchain_openai import ChatOpenAI
from chatbot import ChatBot
import os
import json
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from extractors import *
model_list = []
HIGHLIGHT = '\033[1;43m'  # Yellow background with bold text
RESET = '\033[0m' 

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()  # Load environment variables from a .env file
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    model_list.append(model)
    print(f"     {HIGHLIGHT} INFO {RESET}   openAI model is running now")
    yield
    
    

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get_chat_page():
    # Return the chat.html file as an HTTP response
    html_file_path = os.path.join("chat.html")
    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, media_type="text/html")
                        
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    chat_bot = ChatBot(model_list[0])
    await websocket.accept()
    while True:
        # Receive a message from the client
        data = await websocket.receive_text()
        if data.startswith("// "): ## if user send command for buying some bitcoin
            data = data[3:]
            model_response = await bitcoin_exchange_inof_extractor(model_list[0], data)
            await handle_incomplete_data(websocket, model_response)
            await websocket.send_text(json.dumps(model_response))
        else:     ## if user wants to chat with model
            async for chunk in chat_bot.send_message_stram(data):
                await websocket.send_text(chunk)
            
        await websocket.send_text("[END OF RESPONSE]")

async def handle_incomplete_data(websocket:WebSocket,model_response:BitcoinExchangeInfo) -> None:
    while (model_response["btc"] is None) or (model_response["exchange_name"] is None):
        if model_response["btc"] is None: 
            await websocket.send_text("please enter the BTC value:")
            await websocket.send_text("[END OF RESPONSE]")
            response = await websocket.receive_text()
            btc_value = await bitcoin_info_extractor(model_list[0], response)
            model_response["btc"] = btc_value["btc"]
        if model_response["exchange_name"] is None: 
            await websocket.send_text("please enter the exchange name(with exchange suffix):")
            await websocket.send_text("[END OF RESPONSE]")
            response = await websocket.receive_text()
            exchange_name = await exchange_info_extractor(model_list[0], response)
            model_response["exchange_name"] = exchange_name["exchange_name"]
