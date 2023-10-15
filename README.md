# TGMsgRecorder

Telegram channel/group message recorder using pyrogram/fastapi/vue3.

## Development

```shell
python -m venv ./venv

# Open Powershell Limited
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip --index-url=https://pypi.org/simple

pip install -r requirements.txt --index-url=https://pypi.org/simple

uvicorn app.main:app --port 8000 --reload
```

or..

```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Production Deploy

FastAPI Docker

### Build Docker image

```shell
docker build -f FastAPIDockerfile -t tgfastapi .

docker run -d --name=TGMonitorFastAPI \
-v /wfwork/FastAPI-TGMonitor/:/app/ \
-e PORT=80 \
-e APP_MODULE=app.main:app \
-p 9800:80 \
tgfastapi


```
