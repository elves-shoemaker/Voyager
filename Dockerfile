FROM python:3.10-slim

# ===== system deps =====
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# ===== python deps =====
RUN pip install --upgrade pip
RUN pip install setuptools==68.2.2 wheel

RUN pip install pybind11
RUN pip install numpy

# LangChain最新版本
RUN pip install langchain langchain-openai langchain-chroma openai

# ★ PEP517無効でインストール
RUN pip install -e . --no-build-isolation

# 升级到最新版本覆盖旧依赖
RUN pip install --upgrade langchain langchain-openai langchain-chroma pydantic

# ===== mineflayer build =====
WORKDIR /app/voyager/env/mineflayer
# 先build mineflayer-collectblock，再安装依赖
WORKDIR /app/voyager/env/mineflayer/mineflayer-collectblock
RUN npm install
RUN npx tsc || true

# 然后安装mineflayer依赖（这样file依赖会用已build的目录）
WORKDIR /app/voyager/env/mineflayer
RUN npm install

WORKDIR /app

EXPOSE 8080

CMD ["python", "-m", "voyager"]
