from flask_sqlalchemy import SQLAlchemy

# Instância do bd
db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Cliente {self.nome}>"

class Profissional(db.Model):
    __tablename__ = 'profissionais'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Profissional {self.nome} - {self.especialidade}>"

class Servico(db.Model):
    __tablename__ = 'servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    duracao_minutos = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Servico {self.nome}>"