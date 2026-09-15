# backend

## ローカル実行（簡易）
デフォルトは SQLite（`./test.db`）で動きます。

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
