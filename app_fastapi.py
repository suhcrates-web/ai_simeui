from fastapi import FastAPI, Depends, Request, HTTPException
from starlette.responses import StreamingResponse
from typing import Optional
import time
import openai
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from timeit import default_timer
# import grequests
import aiohttp
import datetime
import logging
import re
from main import AssessModule, get_llm, ModuleData
import timeit
app = FastAPI()

origins = [
    "http://localhost:5234",  # This is the origin of your client, change it if needed
    "http://165.132.142.56:5234/",
]


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",#origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch_sse(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp


openai.api_key = "asdf"


########## LLM setup #################
assessor_cot1 =  AssessModule(get_llm(
            'gpt-4-1106-preview',
            streaming=False,
            max_tokens=2000,
        ), type0='cot1')

assessor_cot2 = AssessModule(get_llm(
            'gpt-4-1106-preview',
            streaming=False,
            max_tokens=2000,
        ), type0='cot2')


assessor_cot3 = AssessModule(get_llm(
            'gpt-4-1106-preview',
            streaming=False,
            max_tokens=2000,
        ), type0='cot3')

assessor_cot4 = AssessModule(get_llm(
            'gpt-4-1106-preview',
            streaming=False,
            max_tokens=2000,
        ), type0='adv1')

assessor_cot5 = AssessModule(get_llm(
            'gpt-4-1106-preview',
            streaming=False,
            max_tokens=2000,
        ), type0='adv2')

assessor_summary = AssessModule(get_llm(
            'gpt-4-1106-preview',
            streaming=True,
            max_tokens=1000,
        ), type0='summary_v2')

async def async_execute(module, data):
    loop = asyncio.get_event_loop()
    # Using run_in_executor to adapt synchronous code to async
    return await loop.run_in_executor(None, module.execute, data)


#############################



@app.get('/stream')
async def stream(data):
    async def event_stream():

        #질문
        # data = data.replace(' ', '●')  
        
        start = timeit.default_timer()
        back1 = f"<br><br>==================<br>#[기사]<br> {data} <br><br>#심의중: 중간 추론 단계 진행...<br><br>".replace('\n', '<br>') 
        yield f"data: {back1}\n\n"
        await asyncio.sleep(0)
     
        data1 = ModuleData(srs_text_refined=data)  # 같은 data1 을 양쪽에 넣으면 결과도 덮어씌워져 하나로 나옴. 따로 만들어서 넣야함.
        data2 = ModuleData(srs_text_refined=data)
        data3 = ModuleData(srs_text_refined=data)
        data5 = ModuleData(srs_text_refined=data)
        data4 = ModuleData(srs_text_refined=data)
        result1, result2, result3, result4, result5 = await asyncio.gather(
            async_execute(assessor_cot1, data1),
            async_execute(assessor_cot2, data2),
            async_execute(assessor_cot3, data3),
            async_execute(assessor_cot4, data4),
            async_execute(assessor_cot5, data5),
        )
        sim1 = result1.assess.replace('\n', '<br>')
        if '★' not in sim1:
            sim1 = '지적사항 없음'
        else:
            sim1 = re.sub(r'.+★','',sim1)

        sim2 = result2.assess.replace('\n', '<br>')
        sim3 = result3.assess.replace('\n', '<br>')
        sim4 = result4.assess.replace('\n', '<br>')
        sim5 = result5.assess.replace('\n', '<br>')

        if '★' not in sim4:
            sim4 = '지적사항 없음'
        else:
            sim4 = re.sub(r'.+★','',sim4)

        if '★' not in sim5:
            sim5 = '지적사항 없음'
        else:
            sim5 = re.sub(r'.+★','',sim5)
        yield f"data: <심의1> {sim1}\n\n"
        yield f"data: <심의2> {sim2}\n\n"
        yield f"data: <심의3> {sim3}\n\n"
        yield f"data: <비판1> {sim4}\n\n"
        yield f"data: <비판2> {sim5}\n\n"



        prompt0 = f"""[심의1] {result1.assess} \n\n [심의2] {result2.assess}  \n\n [심의3] {result3.assess}"""
        # yield f"data: \n\n"
        # await asyncio.sleep(0)
        # yield f"data:================<br><br>\n\n"
        # await asyncio.sleep(0)


        data3 = ModuleData(srs_text_refined=prompt0)

        async for chunk in  assessor_summary.execute_stream(data=data3):
            if not isinstance(chunk.ops[0]['value'], dict):
                content = chunk.ops[0]['value']
                if content is not None:
                    content = content.replace('\n','<br>')
                    content = content.replace(' ', '●')  
                
                    yield f"data:{content}\n\n"
                    # await asyncio.sleep(0) # langchain에서는 오히려 오류
            

        yield f"data: end\n\n"
        await asyncio.sleep(0)
        # print("here2")

    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == '__main__':
    uvicorn.run(app, port=5284, host='0.0.0.0')