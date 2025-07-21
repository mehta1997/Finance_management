from fastapi import FastAPI

app = FastAPI(title="Test API")

@app.get("/")
async def root():
    return {"message": "Test API is working!"}

@app.get("/test")
async def test():
    return {"status": "success", "api": "running"}

if __name__ == "__main__":
    import uvicorn
    print("Starting test API on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
