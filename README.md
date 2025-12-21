# Nexus - Gestão Centralizada de Infraestrutura

Descrição
- Backend em FastAPI para gerenciar clientes, desenvolvedores, serviços e infraestrutura.
- Dashboard estático na pasta `admin/` (pode ser servido pelo FastAPI ou hospedado separadamente).

**Requisitos**
- Python 3.12+
- Banco de dados compatível com SQLAlchemy (ex.: PostgreSQL)
- `pip` e ambiente virtual

**Variáveis de ambiente necessárias**
- `DATABASE_URL` : string de conexão (ex.: `postgresql://user:pass@host:port/dbname`)
- `SECRET_KEY` : chave JWT para assinatura de tokens
- `ENCRYPTION_KEY` : chave usada para criptografia (se aplicável)

Exemplo de arquivo `.env`
```
DATABASE_URL=postgresql://user:pass@host:5432/nexus
SECRET_KEY=sua_secret_key_aqui
ENCRYPTION_KEY=sua_chave_de_criptografia_aqui
```

**Instalação local**
1. Criar e ativar virtualenv

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux / macOS:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Se ainda não existir um `requirements.txt`, gere com:
```bash
pip freeze > requirements.txt
```

**Executando a aplicação**
- Com `uvicorn` (desenvolvimento):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- Em produção, use o mesmo comando sem `--reload` ou rode via processo/serviço.

**Servir a dashboard (`admin/`) junto com FastAPI**
No `main.py` monte a pasta estática:

```py
from fastapi.staticfiles import StaticFiles
app.mount("/admin", StaticFiles(directory="admin", html=True), name="admin")
```

A dashboard ficará acessível em `https://<host>/admin/`.

**Docker (opcional)**
Exemplo mínimo de `Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deploy rápido (opções)**
- Host sem container: Render, Railway, Fly — fornecer `web: uvicorn main:app --host 0.0.0.0 --port $PORT` no `Procfile`.
- Frontend estático separado: hospede `admin/` em Netlify ou Vercel; habilite CORS no backend para o domínio do site.
- Com container: Fly, DigitalOcean App Platform, AWS ECS, etc.

**Procfile (exemplo para Heroku/Render)**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**.gitignore mínimo sugerido**
```
__pycache__/
*.pyc
.venv/
.env
.env.*
.vscode/
```

**Subir para GitHub (rápido)**
- Inicializar e subir (usando GitHub CLI `gh`):
```bash
git init
git add .
git commit -m "Initial commit"
gh repo create USERNAME/nexus-gestao --public --source=. --remote=origin --push
```
- Sem `gh` (crie o repositório no site e, depois):
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/USERNAME/nexus-gestao.git
git push -u origin main
```

**Boas práticas antes do deploy**
- Nunca commitar chaves e segredos; use variáveis de ambiente no provedor.
- Use banco gerenciado e configure `DATABASE_URL` com credenciais seguras.
- Habilite HTTPS (provedores como Render, Fly, Vercel e Netlify já fornecem).

**Próximos passos sugeridos**
- Gerar `requirements.txt` atual com `pip freeze > requirements.txt`.
- Adicionar `.gitignore` (se desejar eu crio).
- Se desejar, eu crio o `Dockerfile` e o `Procfile` agora.

---

Arquivo criado automaticamente por assistente.
