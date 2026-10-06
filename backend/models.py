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

class Agendamento(db.Model):
    __tablename__ = 'agendamento'

    id = db.Column(db.Integer, primary_key=True)
    dataHora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Agendado')
    dataCriacao = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    dataAlteracao = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id', ondelete='CASCADE'), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissional.id', ondelete='CASCADE'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id', ondelete='CASCADE'), nullable=False)

    cliente = db.relationship('Cliente')
    profissional = db.relationship('Profissional')
    servico = db.relationship('Servico')

    def __repr__(self):
        return f"<Agendamento {self.id} - {self.dataHora}>"
