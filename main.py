from typing import Union

from fastapi import FastAPI, Request
from modules import shared
from modules.text_generation import encode, generate_reply

from util import build_parameters, try_start_cloudflared


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post("/api/vi/generate/")
async def read_root(request: Request):
    body = await request.json()
    # Access the POST parameters from the `post_data` dictionary
    prompt = body['prompt']
    generate_params = build_parameters(body)
    stopping_strings = generate_params.pop('stopping_strings')

    generator = generate_reply(
                prompt, generate_params, stopping_strings=stopping_strings)

    answer = ''
    for a in generator:
        if isinstance(a, str):
            answer = a
        else:
            answer = a[0]

    response = json.dumps({
        'results': [{
            'text': answer if shared.is_chat() else answer[len(prompt):]
        }]
    })

    # Process the parameters as needed
    return {"result": response}



if __name__ == '__main__':
    import nest_asyncio
    from pyngrok import ngrok
    import uvicorn

    ngrok_tunnel = ngrok.connect(8000)
    print('Public URL:', ngrok_tunnel.public_url)
    nest_asyncio.apply()
    uvicorn.run(app, port=8000)