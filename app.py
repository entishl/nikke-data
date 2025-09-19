import sys
import os


from dotenv import load_dotenv

# 必须在导入任何其他应用模块之前执行，以确保环境变量已准备就绪。
load_dotenv()

from backend.main import app
import uvicorn

# uvicorn 会使用这个 'app' 对象，此时所有配置都已加载。

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)