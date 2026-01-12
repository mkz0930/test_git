# 外挂大脑知识库 (FastAPI)

一个轻量级的 Web 个人知识库，支持新增、检索、查看、编辑与删除知识卡片。

## 功能

- 新增知识卡片（标题 / 内容 / 标签）
- 关键词检索（标题 / 内容 / 标签）
- 查看与编辑单条笔记
- SQLite 本地持久化

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

启动后访问：`http://127.0.0.1:8000`

## 数据库

- 默认使用 `knowledge.db` 保存数据（位于项目根目录）。
- 如需重置，停止服务后删除该文件即可。
