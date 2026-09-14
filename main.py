from fastapi import FastAPI
import os

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'Hello Cloud Run'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=port)
