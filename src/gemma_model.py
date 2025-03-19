import requests

class GemmaResponse:
    def __init__(self, text: str=""):
        self.text = text

class GemmaModel:
    def __init__(self, host="http://localhost:11434", model="gemma:2b"):
        self.host = host
        self.model = model
        
    def generate_content(self, prompt, stream=False):
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            answer = response.json()
            
            return GemmaResponse(text=answer['response'])#{"response": answer['response']}
            
            #return response.json()
        return {"error": f"request failed with status {response.status_code}"}