# 部署指南

## 本地开发
```bash
pip install -r requirements.txt
python3 app.py
```

## Render部署
1. 推送代码到GitHub
2. 在Render创建Web Service
3. 构建命令: `pip install -r requirements.txt`
4. 启动命令: `gunicorn app:app`
5. 健康检查: `/health`

## 验证部署
```bash
curl https://your-app.onrender.com/health
```
