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

## Como Configurar e Executar

Siga os passos abaixo para ter o ambiente de desenvolvimento funcionando.

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes do Python)

### 1. Clonar e Acessar o Repositório

```bash
# (Se estiver no Git)
git clone <url-do-repositorio>
cd HelpubliAI-Final
```

### 2. Criar e Ativar o Ambiente Virtual

É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

**No Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**No macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as Dependências

Com o ambiente virtual ativado, instale todas as bibliotecas Python necessárias:

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

O backend precisa de algumas variáveis de ambiente para funcionar. Crie um arquivo chamado `.env` dentro da pasta `backend/` (`backend/.env`) e adicione o seguinte conteúdo, substituindo os valores conforme necessário:

```
# Chave secreta para o Flask e JWT (use valores aleatórios e seguros)
SECRET_KEY='uma-chave-secreta-muito-forte'
JWT_SECRET_KEY='outra-chave-secreta-super-segura'

# URL do Banco de Dados
# Para SQLite (padrão):
DATABASE_URL='sqlite:///../instance/app.db'
# Para PostgreSQL (exemplo):
# DATABASE_URL='postgresql://user:password@host:port/dbname'

# Chave da API do Google Generative AI
GOOGLE_API_KEY='SUA_API_KEY_DO_GOOGLE_AI'

# Configuração de Email (opcional, para recuperação de senha)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@example.com
MAIL_PASSWORD=sua-senha-de-email
MAIL_DEFAULT_SENDER=seu-email@example.com
```

**Importante:** O arquivo `.gitignore` já está configurado para ignorar o arquivo `.env`, garantindo que suas chaves secretas não sejam enviadas para o repositório Git.

### 5. Aplicar as Migrações do Banco de Dados

Para criar o banco de dados e as tabelas, execute os seguintes comandos a partir da raiz do projeto (`HelpubliAI-Final/`):

```bash
# Define o app Flask para o CLI
# (No Windows CMD)
set FLASK_APP=backend.run:app
# (No PowerShell)
$env:FLASK_APP="backend.run:app"
# (No macOS/Linux)
export FLASK_APP=backend/run.py

# Executa as migrações
flask db upgrade
```

### 6. Executar a Aplicação

Finalmente, para iniciar o servidor de desenvolvimento, execute:

```bash
python backend/run.py
```

O servidor estará disponível em `http://127.0.0.1:5000`.
