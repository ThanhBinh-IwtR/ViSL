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

# Lấy đường dẫn tuyệt đối tới thư mục Backend
BASE_DIR = Path(__file__).resolve().parent.parent

# Đường dẫn tới thư mục Frontend
frontend_path = BASE_DIR.parent / "Frontend"

# Đường dẫn tới thư mục static trong Frontend
static_path = frontend_path / "static"

app.mount("/static", StaticFiles(directory=frontend_path / "static"), name="static")


# config routes
app.include_router(userRoute.userRouter)



if __name__ == "__main__":
    uvicorn.run("main:app",reload=True)
