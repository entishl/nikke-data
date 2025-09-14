---
title: nikke union management
emoji: 🚀
colorFrom: pink
colorTo: blue
sdk: docker
app_port: 7860
---

# Lucky

这是一个用于管理游戏角色数据的全栈应用。

## 如何在本地运行

1.  **构建 Docker 镜像:**
    ```bash
    docker build -t lucky-app .
    ```

2.  **运行 Docker 容器:**
    ```bash
    docker run -p 7860:7860 lucky-app
    ```

3.  **访问应用:**
    *   应用: [http://localhost:7860](http://localhost:7860)
    *   API 文档: [http://localhost:7860/docs](http://localhost:7860/docs)