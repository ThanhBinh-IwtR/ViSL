import uvicorn
from fastapi import FastAPI
from model import userModel
from database.connection import engine
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from routes import userRoute
# config DB
userModel.Base.metadata.create_all(bind=engine)

# instance 
app=FastAPI()

# config static and templates
BASE_DIR = Path(__file__).resolve().parent.parent.parent
frontend_path = BASE_DIR / "Frontend"

app.mount("/static", StaticFiles(directory=frontend_path / "static"), name="static")


# config routes
app.include_router(userRoute.userRouter)



if __name__ == "__main__":
    uvicorn.run("main:app",reload=True)
