from app import db, app
from models import Cliente, Profissional, Servico

with app.app_context():
    db.create_all()

    # Cria a conta Admin padrão caso ainda não exista
    if not Cliente.query.filter_by(email="admin@espelhomeu.com").first():
        admin = Cliente(nome="Administrador", telefone="21900000000", email="admin@espelhomeu.com")
        admin.definir_senha("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Conta Admin criada: admin@espelhomeu.com / senha: admin123")

    # Cria os profissionais e serviços iniciais caso o banco esteja vazio
    if Profissional.query.count() == 0:
        prof1 = Profissional(nome="Juliana Silva", especialidade="Manicure", tel="21999999999",
                             horarios="09:00,10:00,11:00,14:00,15:00")
        prof2 = Profissional(nome="Julia Maria", especialidade="Cabeleireira", tel="21988888888",
                             horarios="10:00,13:00,15:00,17:00")
        prof3 = Profissional(nome="Carla Souza", especialidade="Pedicure", tel="21977777777",
                             horarios="08:00,09:30,13:00,16:30")

        serv1 = Servico(nome="Manicure Simples", descricao="Cutilagem e esmaltação", preco=45.00,
                        duracaoEmMinutos=60, especialidade="Manicure")
        serv2 = Servico(nome="Esmaltação em Gel", descricao="Esmaltação com secagem em cabine", preco=70.00,
                        duracaoEmMinutos=60, especialidade="Manicure")
        serv3 = Servico(nome="Corte e Escova", descricao="Lavagem, corte e finalização", preco=120.00,
                        duracaoEmMinutos=45, especialidade="Cabeleireira")
        serv4 = Servico(nome="Hidratação Capilar", descricao="Lavagem e máscara de tratamento", preco=90.00,
                        duracaoEmMinutos=60, especialidade="Cabeleireira")
        serv5 = Servico(nome="Pedicure Composta", descricao="Cutilagem e hidratação", preco=37.00,
                        duracaoEmMinutos=70, especialidade="Pedicure")

        db.session.add_all([prof1, prof2, prof3, serv1, serv2, serv3, serv4, serv5])
        db.session.commit()
        print("Banco populado com 3 profissionais e 5 serviços!")
    else:
        print("Os profissionais e serviços iniciais já estão cadastrados!")