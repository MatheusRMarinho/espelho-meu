from app import db, app
from models import Profissional, Servico

with app.app_context():
    # Cria 1 profissional e 1 serviço
    prof = Profissional(nome="Juliana Silva", especialidade="Manicure", tel="21999999999")
    serv = Servico(nome="Manicure Simples", descricao="Cutilagem e esmaltação", preco=45.00, duracaoEmMinutos=60)
    
    db.session.add(prof)
    db.session.add(serv)
    db.session.commit()
    print("Banco populado com sucesso!")