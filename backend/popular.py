from app import db, app
from models import Profissional, Servico

with app.app_context():
    db.create_all()

    if Profissional.query.count() == 0:
        prof1 = Profissional(nome="Juliana Silva", especialidade="Manicure", tel="21999999999")
        prof2 = Profissional(nome="Julia Maria", especialidade="Cabeleireira", tel="21988888888")
        prof3 = Profissional(nome="Carla Souza", especialidade="Pedicure", tel="21977777777")

        serv1 = Servico(nome="Manicure Simples", descricao="Cutilagem e esmaltação", preco=45.00, duracaoEmMinutos=60)
        serv2 = Servico(nome="Corte e Escova", descricao="Lavagem, corte e finalização", preco=120.00, duracaoEmMinutos=45)
        serv3 = Servico(nome="Pedicure Composta", descricao="Cutilagem e hidratação", preco=37.00, duracaoEmMinutos=70)

        db.session.add_all([prof1, prof2, prof3, serv1, serv2, serv3])
        db.session.commit()
        print("Banco populado com 3 profissionais e 3 serviços!")
    else:
        print("O banco já possui dados cadastrados!")