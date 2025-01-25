from typing_extensions import Annotated, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from typing import Type, cast
from langchain_core.language_models.chat_models import BaseChatModel

# TypedDicts -------------
class LlmStruct(TypedDict):
    pass
class BitcoinExchangeInfo(LlmStruct):
    """Use this tool to structure the response to the user."""
    btc: Annotated[float|None,"the bitcoin value"]
    exchange_name: Annotated[str|None,"the exchange name"]

class BitcoinInfo(LlmStruct):
    """Use this tool to structure the response to the user."""
    btc: Annotated[float|None,"the bitcoin value"]

class ExchangeInfo(LlmStruct):
    """Use this tool to structure the response to the user."""
    exchange_name: Annotated[str|None,"the exchange name"]
#--------------------------
def read_prompt(file_name:str):
    with open(file_name, "r") as file:
        content = file.read()
    return content

async def structured_model(model:BaseChatModel,
                           output_foramt:Type[LlmStruct],
                           system:str,user_msg:str)->LlmStruct :
    structured_llm = model.with_structured_output(output_foramt)
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")])
    few_shot_structured_llm = prompt | structured_llm
    model_out = await few_shot_structured_llm.ainvoke({"input":user_msg})
    return cast(LlmStruct, model_out)

async def bitcoin_exchange_inof_extractor(model:BaseChatModel,user_msg: str) -> BitcoinExchangeInfo:
    system = read_prompt('./prompts/btc_exchange_prompt.txt')
    bitcoin_exchange_struct = await structured_model(model, BitcoinExchangeInfo, system, user_msg)
    return cast(BitcoinExchangeInfo, bitcoin_exchange_struct)

async def bitcoin_info_extractor(model:BaseChatModel,user_msg: str) -> BitcoinInfo:
    system = read_prompt('./prompts/btc_prompt.txt')
    bitcoin_exchange_struct = await structured_model(model, BitcoinInfo, system, user_msg)
    return cast(BitcoinInfo, bitcoin_exchange_struct)

async def exchange_info_extractor(model:BaseChatModel,user_msg: str) -> ExchangeInfo:
    system = read_prompt('./prompts/exchange_prompt.txt')
    bitcoin_exchange_struct = await structured_model(model, ExchangeInfo, system, user_msg)
    return cast(ExchangeInfo, bitcoin_exchange_struct)


