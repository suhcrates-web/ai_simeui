from abc import abstractmethod
from dataclasses import dataclass
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from utils.config import get_config
from pathlib import Path
from langchain.chat_models import ChatOpenAI
from pathlib import Path
import openai
import yaml
import asyncio

from utils.path import (
    load_prompt,
    read_text_file,
)

@dataclass
class ModuleData:
    srs_text: str = ''
    categories: str = ''
    assess: str = ''
    srs_text_refined: str = ''


class BaseModule:
    @abstractmethod
    def execute(self, data: ModuleData = None) -> ModuleData:
        raise NotImplementedError


def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

class AssessModule(BaseModule):
    def __init__(self, llm, type0):
        self.llm = llm
        prompt = load_prompt(f'srs_{type0}.txt')
        self.prompt = PromptTemplate(
            template=prompt,
            input_variables=["srs_text", "categories"])
        self.llm_chain = LLMChain(prompt=self.prompt, llm=llm)
        self.config = load_config('./conf.d/config.yaml')

    def execute(self, data: ModuleData = None):
        
        response = self.llm_chain.apply([{
            'srs_text': data.srs_text_refined,
        }])
        data.assess = response[0]['text']
        return data

    async def execute_async(self, data: ModuleData = None):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.llm_chain.apply, [{
            'srs_text': data.srs_text_refined,
        }])
        data.assess = response[0]['text']
        return data
    
    def execute_stream(self, data: ModuleData = None):
        return self.llm_chain.astream_log([{'srs_text':data}])


class SummaryModule(BaseModule):
    def __init__(self, llm, type0):
        self.llm = llm
        prompt = load_prompt(f'srs_{type0}.txt')
        self.prompt = PromptTemplate(
            template=prompt,
            input_variables=["srs_text", "categories"])
        self.llm_chain = LLMChain(prompt=self.prompt, llm=llm)
        self.config = load_config('./conf.d/config.yaml')

    def execute(self, data: ModuleData = None):
        
        response = self.llm_chain.apply([{
            'srs_text': data.srs_text_refined,
            'categories' : data.categories
        }])
        data.assess = response[0]['text']
        return data

    async def execute_async(self, data: ModuleData = None):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.llm_chain.apply, [{
            'srs_text': data.srs_text_refined,
            'categories' : data.categories
        }])
        data.assess = response[0]['text']
        return data
    
    def execute_stream(self, data: ModuleData = None):
        return self.llm_chain.astream_log([{'srs_text':data}])




def get_llm(model_name='gpt-4-1106-preview', streaming=False, max_tokens=None):
    openai_model = model_name
    config = load_config('./conf.d/config.yaml')
    return ChatOpenAI(
        model_name=openai_model,
        temperature=0.1,
        max_tokens=max_tokens,
        streaming=streaming,
        openai_api_key=config['openai']['key']
    )




#############  사용방법 #####
# assessor = AssessModule(get_llm(
#             'gpt-4o',
#             streaming=False,
#             max_tokens=1000,
#         ))


# data = ModuleData(srs_text_refined=a)
# text0 = assessor.execute(data=data)
# text0.assess