set PATH=C:\Program Files\nodejs;%PATH%
cd C:\dev\manimaq\frontend
...
npm run dev


cd C:\dev\manimaq\backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env -Force
python -m scripts.seed
python -m uvicorn app.main:app --reload


PARA LAN:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


Acessos:

app: http://localhost:3000
api docs: http://localhost:8000/docs
Login seed:


SEED MASSIVO:
python -m scripts.seed --reset-operational



usuário: otavio
senha: Manimaq@123