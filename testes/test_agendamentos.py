import pytest
from backend.app import app as flask_app, db
from backend.models import Servico


@pytest.fixture(scope='session')
def app():
    """Configura o app e o banco SQLite em memória uma única vez para a sessão."""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    if 'sqlalchemy' in flask_app.extensions:
        del flask_app.extensions['sqlalchemy']
    db.init_app(flask_app)

    yield flask_app


@pytest.fixture(autouse=True)
def setup_database(app):
    """Garante um banco limpo e populado individualmente para CADA teste."""
    with app.app_context():
        db.create_all()

        # Cadastra o serviço necessário para os testes
        servico_teste = Servico(
            id=1,
            nome="Corte de Cabelo",
            descricao="Corte padrão",
            preco=50.0,
            duracaoEmMinutos=30
        )
        db.session.add(servico_teste)
        db.session.commit()

        yield

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de testes do Flask."""
    return app.test_client()


def test_criar_agendamento_sucesso(client):
    """Testa a criação de um agendamento com dados válidos."""
    dados_agendamento = {
        "cliente_id": 1,
        "profissional_id": 1,
        "servico_id": 1,
        "dataHora": "2026-10-10T14:00:00"
    }

    response = client.post('/agendamentos', json=dados_agendamento)

    assert response.status_code == 201
    assert response.json["mensagem"] == "Agendamento realizado com sucesso!"


def test_criar_agendamento_dados_incompletos(client):
    """Testa a tentativa de agendamento com campos faltando."""
    dados_invalidos = {
        "cliente_id": 1
    }

    response = client.post('/agendamentos', json=dados_invalidos)

    assert response.status_code == 400
    assert "Campos obrigatórios" in response.json["erro"]

def test_criar_agendamento_conflito_horario(client):
    """Testa a tentativa de agendamento no mesmo horário (RNF-008)."""
    dados = {
        "cliente_id": 1,
        "profissional_id": 1,
        "servico_id": 1,
        "dataHora": "2026-10-10T14:00:00"
    }

    # Primeiro agendamento deve funcionar
    res1 = client.post('/agendamentos', json=dados)
    assert res1.status_code == 201

    # Segundo agendamento no mesmo horário deve ser bloqueado
    res2 = client.post('/agendamentos', json=dados)
    assert res2.status_code in [400, 409]
