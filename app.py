import sys
import os


from dotenv import load_dotenv

# 必须在导入任何其他应用模块之前执行，以确保环境变量已准备就绪。
# 设置应用环境为 development，这只应在本地运行 app.py 时使用
# Docker 环境将不会设置此变量，从而保持原有的数据库主机名
os.environ['APP_ENV'] = 'development'

load_dotenv()

from backend.main import app
import uvicorn

# uvicorn 会使用这个 'app' 对象，此时所有配置都已加载。

if __name__ == "__main__":
    # 从环境变量 "PORT" 中获取端口，如果未设置，则默认为 18000
    port = int(os.getenv("PORT", "18000"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)