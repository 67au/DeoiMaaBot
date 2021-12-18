# DeoiMaaBot

一个用于 `Deoi Maa -> 兑码` 的 Telegram Bot

## 环境要求

- python>=3.7
- httpx==0.21.1
- httpx-socks==0.7.2
- Pyrogram==1.2.20
- TgCrypto==1.2.2

## 使用方法

### 从 Github 获取本仓库

```
git clone --recurse-submodules https://github.com/67au/deoimaabot.git
```

### 安装依赖

推荐使用虚拟环境 [venv](https://docs.python.org/zh-cn/3/library/venv.html) 安装依赖并运行项目

```
pip install -r requirement
```

### 创建配置文件

参考提供的 `config.sample.ini` ，使用 `--config` 参数指定配置文件，默认为 `'config.ini'`

为什么需要 `api_id` `api_hash` `bot_token`？详情可以查看 Pyrogram 的 [文档](https://docs.pyrogram.org/intro/setup#api-keys)

### 运行 Bot

```
python3 main.py
```

## 在 Docker 上使用

### 构建镜像

```
git clone --recurse-submodules https://github.com/67au/deoimaabot.git
cd deoimaabot
docker buildx build . -t doeimaabot:latest --load
```

### 运行容器

```
docker run -d --name=deoimaa \
    -e API_ID=<api_id> \
    -e API_HASH=<api_hash> \
    -e BOT_TOKEN=<bot_token> \
    -e ADMIN=<admin> \
    deoimaabot:latest
```

## 注意事项

- 暂不支持代理