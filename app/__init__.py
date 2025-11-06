# Exemplo em app/__init__.py
from flask import Flask

app = Flask(__name__)
# OBRIGATÓRIO para usar sessions
app.secret_key = 'J9@hS8!bLpQx7&MzC2vK4yN6dT1eA5gU0' 

# IMPORTANTE: Carregue as rotas para evitar problemas de dependência circular
from app import routes