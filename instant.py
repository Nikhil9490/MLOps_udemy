from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openai import OpenAI
app = FastAPI()

@app.get("/", response_class = HTMLResponse)
def instant():
    client = OpenAI()
    message = "Hello!!! You are on a website that has just been deployed. say something with enthusiasm to welcome visitors to this website."
    messages = [{"role": "user", "content": message}]
    response = client.chat.completions.create(model = 'gpt-4o-mini', messages = messages)
    reply = response.choices[0].message.content.replace("\n", "<br>")
    html = f"<html><head><title> live in an instant</title></head><body><p>{reply}</p></body></html>"
    return html