import sys
import os

# 修复：强制将新环境的 site-packages 添加到 sys.path
site_packages_path = r'C:\Users\enty\miniconda3\envs\lucky-env\lib\site-packages'
if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)

from dotenv import load_dotenv

# 必须在导入任何其他应用模块之前执行，以确保环境变量已准备就绪。
load_dotenv()

from backend.main import app

# uvicorn 会使用这个 'app' 对象，此时所有配置都已加载。