from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage

class ChatBot:
    def __init__(self, chat_model:BaseChatModel)-> None:
        self.msg_list = []
        self.chat_model = chat_model
    def send_message(self,msg:str) -> str| list:
        self.msg_list.append(HumanMessage(msg))
        response = self.chat_model.invoke(self.msg_list)
        self.msg_list.append(AIMessage(response.content))
        return response.content
    async def send_message_stram(self,msg:str):
        self.msg_list.append(HumanMessage(msg))
        async for event in self.chat_model.astream_events(self.msg_list, version="v1"):
            if event['event'] == 'on_chat_model_end' and "output" in event['data']:
                contnet = event['data']['output'].content
                self.msg_list.append(AIMessage(contnet))
            if event['event'] == 'on_chat_model_stream' and 'chunk' in event['data']:
                yield event['data']['chunk'].content
    def clear_message_history(self) -> None:
        self.msg_list = []
