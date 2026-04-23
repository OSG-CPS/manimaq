set PATH=C:\Program Files\nodejs;%PATH%
cd C:\dev\manimaq\frontend
...
npm run dev


cd C:\dev\manimaq\backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env -Force
python -m scripts.seed
python -m uvicorn app.main:app --reload

Acessos:

app: http://localhost:3000
api docs: http://localhost:8000/docs
Login seed:

usuário: otavio
senha: Manimaq@123