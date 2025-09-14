# 使用一个包含 docker-compose 的基础镜像
FROM docker/compose:latest

# 设置工作目录
WORKDIR /app

# 将您项目的所有文件（包括 docker-compose.yml、frontend/ 和 backend/ 目录）复制到容器中
COPY . .

# 当容器启动时，运行 docker-compose up 命令来构建并启动您的服务
# --build 参数会强制重新构建镜像
CMD ["docker-compose", "up", "--build"]