# HelpubliAI - Projeto Otimizado

Este é o repositório reorganizado para o projeto HelpubliAI, um aplicativo web full-stack com backend em Flask e frontend em HTML/CSS/JS.

## Estrutura de Diretórios

A estrutura foi otimizada para separar claramente o backend do frontend:

```
/
├── backend/         # Contém toda a aplicação Flask
│   ├── app/         # O pacote principal da aplicação
│   ├── migrations/  # Migrações de banco de dados (Alembic)
│   ├── tests/       # Testes
│   ├── .env         # Arquivo para variáveis de ambiente (NÃO versionar)
│   ├── config.py    # Configurações da aplicação
│   └── run.py       # Ponto de entrada para iniciar o servidor
├── frontend/        # Contém todos os arquivos estáticos
│   ├── css/
│   ├── js/
│   └── *.html
├── .gitignore       # Arquivos e pastas a serem ignorados pelo Git
├── Procfile         # Para deploy em plataformas como Heroku/Railway
├── README.md        # Este arquivo
├── requirements.txt # Dependências Python
└── runtime.txt      # Versão do Python para deploy
```

## ✨ Tecnologias e Ferramentas

Este projeto utiliza uma combinação de tecnologias modernas para o desenvolvimento full-stack.

### **Backend**
*   **Python 3.11+**
*   **Flask:** Microframework web para construir a API REST.
*   **Flask-SQLAlchemy:** ORM para interação com o banco de dados.
*   **Flask-Migrate (Alembic):** Para gerenciamento de migrações do esquema do banco de dados.
*   **Flask-JWT-Extended:** Para autenticação baseada em JSON Web Tokens (JWT).
*   **Gunicorn:** Servidor WSGI para deploy.

### **Frontend**
*   **React:** Biblioteca para construir a interface de usuário.
*   **Material-UI (MUI):** Biblioteca de componentes React para um design moderno e consistente.
*   **React Router:** Para gerenciamento de rotas no lado do cliente.
*   **Tiptap:** Editor de texto rico (Rich Text Editor) para uma melhor experiência de criação de conteúdo.

### **Ferramentas e Boas Práticas**
*   **Docker:** Para containerização da aplicação, garantindo um ambiente de desenvolvimento e produção consistente.
*   **Storybook:** Para desenvolver e documentar componentes de UI de forma isolada.
*   **ESLint & Prettier:** Para garantir a qualidade e a padronização do código no frontend.

## Como Configurar e Executar

Siga os passos abaixo para ter o ambiente de desenvolvimento funcionando.

### Pré-requisitos

- Python 3.11 ou superior
- Node.js e npm (para o frontend React)
- Docker (opcional, para rodar com containers)

### 1. Clonar e Acessar o Repositório

```bash
git clone https://github.com/LuizGabrielCN/HelpubliAI.git
cd HelpubliAI
```

### 2. Configurar o Backend (Python)

**a. Criar e Ativar o Ambiente Virtual:**

É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

*No Windows:*
```bash
python -m venv venv
.\venv\Scripts\activate
```

*No macOS/Linux:*
```bash
python3 -m venv venv
source venv/bin/activate
```

**b. Instalar as Dependências:**

Com o ambiente virtual ativado, instale todas as bibliotecas Python:

```bash
pip install -r requirements.txt
```

**c. Configurar Variáveis de Ambiente:**

Crie um arquivo chamado `.env` na pasta `backend/` (`backend/.env`) e adicione as seguintes variáveis, substituindo os valores conforme necessário:

```
# Chave secreta para o Flask e JWT (use valores aleatórios e seguros)
SECRET_KEY='uma-chave-secreta-muito-forte'
JWT_SECRET_KEY='outra-chave-secreta-super-segura'

# URL do Banco de Dados (SQLite por padrão)
DATABASE_URL='sqlite:///../instance/app.db'

# Chave da API do Google Generative AI
GOOGLE_API_KEY='SUA_API_KEY_DO_GOOGLE_AI'
```

**d. Aplicar as Migrações do Banco de Dados:**

Para criar o banco de dados e as tabelas, execute os seguintes comandos a partir da raiz do projeto:

```bash
# (No Windows CMD)
set FLASK_APP=backend.run:app
# (No PowerShell)
$env:FLASK_APP="backend.run:app"
# (No macOS/Linux)
export FLASK_APP=backend/run.py

flask db upgrade
```

### 3. Configurar o Frontend (React)

**a. Acessar a pasta do React e instalar as dependências:**

```bash
cd frontend/react-app
npm install
```

### 4. Executar a Aplicação

**a. Iniciar o Backend:**

Na raiz do projeto, com o ambiente virtual ativado:
```bash
python backend/run.py
```
O servidor do backend estará disponível em `http://127.0.0.1:5000`.

**b. Iniciar o Frontend:**

Em outro terminal, dentro da pasta `frontend/react-app`:
```bash
npm start
```
A aplicação React estará disponível em `http://localhost:3000` e se comunicará com o backend.