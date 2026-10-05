from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Instância do bd
db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'cliente'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False) # Guarda apenas o hash, nunca a senha pura

    def definir_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)

    def __repr__(self):
        return f"<Cliente {self.nome}>"

class Profissional(db.Model):
    __tablename__ = 'profissional'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100))
    tel = db.Column(db.String(20)) # Ajustado para bater com o diagrama

    def __repr__(self):
        return f"<Profissional {self.nome} - {self.especialidade}>"

class Servico(db.Model):
    __tablename__ = 'servico'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    duracaoEmMinutos = db.Column(db.Integer, nullable=False) # Ajustado para bater com o diagrama

    def __repr__(self):
        return f"<Servico {self.nome}>"