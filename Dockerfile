# FROM python:3.10

# # 设置环境变量
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # 设置工作目录
# WORKDIR /app

# # 安装系统依赖
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#     gcc \
#     libpq-dev \
#     libmariadb-dev \
#     default-mysql-client \ 
#     && rm -rf /var/lib/apt/lists/*

# COPY *.whl .

# # 安装 Python 依赖
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# # 复制项目文件
# COPY wait_for_db.py /app/wait_for_db.py 
# COPY . .


FROM python:3.10

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 创建并配置阿里云镜像源
RUN { \
    echo "deb http://mirrors.aliyun.com/debian/ trixie main contrib non-free"; \
    echo "deb http://mirrors.aliyun.com/debian/ trixie-updates main contrib non-free"; \
    echo "deb http://mirrors.aliyun.com/debian-security/ trixie-security main contrib non-free"; \
    } > /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libmariadb-dev \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 使用国内 PyPI 镜像源
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 复制项目文件
COPY . .