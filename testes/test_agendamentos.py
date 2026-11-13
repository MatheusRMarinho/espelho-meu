import pytest
from backend.app import app as flask_app, db
from backend.models import Profissional, Servico


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
            duracaoEmMinutos=30,
            especialidade="Cabeleireira"
        )
        profissional_teste = Profissional(
            id=1,
            nome="Julia Maria",
            especialidade="Cabeleireira",
            tel="21988888888",
            horarios="10:00,14:00"
        )
        db.session.add_all([servico_teste, profissional_teste])
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


def test_agendamento_fora_dos_horarios_do_profissional(client):
    """O horário precisa estar na lista de horários do profissional."""
    dados = {
        "cliente_id": 1,
        "profissional_id": 1,
        "servico_id": 1,
        "dataHora": "2026-10-10T16:00:00"
    }

    response = client.post('/agendamentos', json=dados)

    assert response.status_code == 400
    assert "não atende nesse horário" in response.json["erro"]


def test_agendamento_especialidade_diferente(client):
    """Um serviço só pode ser agendado com profissional da mesma especialidade."""
    client.post('/servicos', json={
        "nome": "Manicure Simples",
        "preco": 45.0,
        "duracaoEmMinutos": 60,
        "especialidade": "Manicure"
    })

    dados = {
        "cliente_id": 1,
        "profissional_id": 1,
        "servico_id": 2,
        "dataHora": "2026-10-10T10:00:00"
    }

    response = client.post('/agendamentos', json=dados)

    assert response.status_code == 400
    assert "não realiza esse serviço" in response.json["erro"]


def test_cadastrar_profissional_com_horarios(client):
    """Os horários são validados, ordenados e devolvidos como lista."""
    response = client.post('/profissionais', json={
        "nome": "Carla Souza",
        "especialidade": "Pedicure",
        "tel": "21977777777",
        "horarios": "16:30, 08:00,13:00"
    })
    assert response.status_code == 201

    profissionais = client.get('/profissionais').json
    carla = next(p for p in profissionais if p["nome"] == "Carla Souza")
    assert carla["horarios"] == ["08:00", "13:00", "16:30"]


def test_cadastrar_profissional_horario_invalido(client):
    response = client.post('/profissionais', json={
        "nome": "Carla Souza",
        "especialidade": "Pedicure",
        "horarios": "8h"
    })

    assert response.status_code == 400
    assert "Horário inválido" in response.json["erro"]


def test_cadastrar_servico_sem_especialidade(client):
    response = client.post('/servicos', json={
        "nome": "Hidratação",
        "preco": 90.0,
        "duracaoEmMinutos": 60
    })

    assert response.status_code == 400


def test_excluir_profissional_remove_agendamentos(client):
    """Excluir um profissional também remove os agendamentos dele."""
    client.post('/agendamentos', json={
        "cliente_id": 1,
        "profissional_id": 1,
        "servico_id": 1,
        "dataHora": "2026-10-10T14:00:00"
    })

    response = client.delete('/profissionais/1')

    assert response.status_code == 200
    assert response.json["agendamentos_removidos"] == 1
    assert client.get('/profissionais').json == []
    assert client.get('/agenda').json == []


def test_excluir_servico_remove_agendamentos(client):
    """Excluir um serviço também remove os agendamentos dele."""
    client.post('/agendamentos', json={
        "cliente_id": 1,
        "profissional_id": 1,
        "servico_id": 1,
        "dataHora": "2026-10-10T10:00:00"
    })

    response = client.delete('/servicos/1')

    assert response.status_code == 200
    assert response.json["agendamentos_removidos"] == 1
    assert client.get('/servicos').json == []


def test_excluir_inexistente(client):
    assert client.delete('/profissionais/999').status_code == 404
    assert client.delete('/servicos/999').status_code == 404
