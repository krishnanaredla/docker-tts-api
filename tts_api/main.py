
from process import *
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
import datetime

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/tts/{query}")
def read_item(query: str):
    wav_bytes = text_to_wav(synthesizer,query)
    filename =  'converted/'+str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))+'.wav'
    f = open(filename, 'wb')
    f.write(wav_bytes)
    f.close()
    return FileResponse(filename)


if __name__ == "__main__":
    synthesizer = startmodel()
    uvicorn.run(app, host="0.0.0.0", port=8081)