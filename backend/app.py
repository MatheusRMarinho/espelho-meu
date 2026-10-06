from flask import Flask, request, jsonify
from datetime import datetime, time
from models import db, Cliente, Profissional, Servico, Agendamento
from flask_cors import CORS
from datetime import datetime, time, timedelta

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/espelho_meu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)
# rotas cliente
@app.route('/clientes', methods=['POST'])
def cadastrar_cliente():
    dados = request.get_json()
    try:
        novo_cliente = Cliente(
            nome=dados['nome'],
            telefone=dados.get('telefone', ''),
            email=dados['email']
        )
        novo_cliente.definir_senha(dados['senha'])
        db.session.add(novo_cliente)
        db.session.commit()
        return jsonify({"mensagem": "Cliente cadastrado!", "id": novo_cliente.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 400

@app.route('/clientes', methods=['GET'])
def listar_clientes():
    clientes = Cliente.query.all()
    resultado = [{"id": c.id, "nome": c.nome, "telefone": c.telefone, "email": c.email} for c in clientes]
    return jsonify(resultado), 200


# rota login
@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json(silent=True) or {}
    email = dados.get('email', '').strip()
    senha = dados.get('senha', '')

    if not email or not senha:
        return jsonify({"erro": "Informe e-mail e senha."}), 400

    cliente = Cliente.query.filter_by(email=email).first()
    # Mesma mensagem para e-mail inexistente e senha errada, para não revelar quais e-mails existem
    if cliente is None or not cliente.verificar_senha(senha):
        return jsonify({"erro": "E-mail ou senha inválidos."}), 401

    return jsonify({
        "mensagem": "Login realizado com sucesso!",
        "cliente": {"id": cliente.id, "nome": cliente.nome, "email": cliente.email}
    }), 200


# rotas profissional
@app.route('/profissionais', methods=['POST'])
def cadastrar_profissional():
    dados = request.get_json()
    try:
        novo_profissional = Profissional(
            nome=dados['nome'],
            especialidade=dados.get('especialidade', ''),
            tel=dados.get('tel', '')
        )
        db.session.add(novo_profissional)
        db.session.commit()
        return jsonify({"mensagem": "Profissional cadastrado!", "id": novo_profissional.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 400

@app.route('/profissionais', methods=['GET'])
def listar_profissionais():
    profissionais = Profissional.query.all()
    resultado = [{"id": p.id, "nome": p.nome, "especialidade": p.especialidade, "tel": p.tel} for p in profissionais]
    return jsonify(resultado), 200


# rotas serviço
@app.route('/servicos', methods=['POST'])
def cadastrar_servico():
    dados = request.get_json()
    try:
        novo_servico = Servico(
            nome=dados['nome'],
            descricao=dados.get('descricao', ''),
            preco=dados['preco'],
            duracaoEmMinutos=dados['duracaoEmMinutos']
        )
        db.session.add(novo_servico)
        db.session.commit()
        return jsonify({"mensagem": "Serviço cadastrado!", "id": novo_servico.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 400

@app.route('/servicos', methods=['GET'])
def listar_servicos():
    servicos = Servico.query.all()
    resultado = [
        {
            "id": s.id, 
            "nome": s.nome, 
            "descricao": s.descricao, 
            "preco": str(s.preco), 
            "duracaoEmMinutos": s.duracaoEmMinutos
        } for s in servicos
    ]
    return jsonify(resultado), 200

# rotas de agendamento
@app.route('/agendamentos', methods=['POST'])
def criar_agendamento():
    dados = request.get_json() or {}
    
    cliente_id = dados.get('cliente_id')
    profissional_id = dados.get('profissional_id')
    servico_id = dados.get('servico_id')
    data_hora_str = dados.get('dataHora') # Formato esperado: "2026-10-10T14:00:00"

    if not all([cliente_id, profissional_id, servico_id, data_hora_str]):
        return jsonify({"erro": "Campos obrigatórios: cliente_id, profissional_id, servico_id, dataHora"}), 400

    try:
        data_hora_inicio = datetime.fromisoformat(data_hora_str)
    except ValueError:
        return jsonify({"erro": "Formato de dataHora inválido. Use formato ISO (ex: YYYY-MM-DDTHH:MM:SS)."}), 400

    # Busca o serviço para consultar a duração
    servico = db.session.get(Servico, servico_id)
    if not servico:
        return jsonify({"erro": "Serviço não encontrado."}), 404

    data_hora_fim = data_hora_inicio + timedelta(minutes=servico.duracaoEmMinutos)

    # Implementação do RNF-008: Validação de conflito de agenda do profissional
    agendamentos_existentes = Agendamento.query.filter(
        Agendamento.profissional_id == profissional_id,
        Agendamento.status != 'Cancelado'
    ).all()

    for ag in agendamentos_existentes:
        existente_inicio = ag.dataHora
        existente_fim = existente_inicio + timedelta(minutes=ag.servico.duracaoEmMinutos)

        # Validação da sobreposição de horários
        if data_hora_inicio < existente_fim and data_hora_fim > existente_inicio:
            return jsonify({
                "erro": "Horário indisponível. O profissional já possui um atendimento nesse intervalo."
            }), 409

    try:
        novo_agendamento = Agendamento(
            cliente_id=cliente_id,
            profissional_id=profissional_id,
            servico_id=servico_id,
            dataHora=data_hora_inicio,
            status='Agendado'
        )
        db.session.add(novo_agendamento)
        db.session.commit()

        return jsonify({
            "mensagem": "Agendamento realizado com sucesso!",
            "id": novo_agendamento.id,
            "dataHora": novo_agendamento.dataHora.isoformat()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro interno ao agendar: {str(e)}"}), 400

    
# rotas agenda
@app.route('/agenda', methods=['GET'])
def consultar_agenda():
    """Consulta os agendamentos, com filtros opcionais por data e profissional."""
    consulta = Agendamento.query

    data = request.args.get('data')
    profissional_id = request.args.get('profissional_id', type=int)

    if data:
        try:
            data_consulta = datetime.strptime(data, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"erro": "Data inválida. Use o formato YYYY-MM-DD."}), 400

        inicio = datetime.combine(data_consulta, time.min)
        fim = datetime.combine(data_consulta, time.max)
        consulta = consulta.filter(Agendamento.dataHora.between(inicio, fim))

    if profissional_id is not None:
        consulta = consulta.filter(Agendamento.profissional_id == profissional_id)

    agendamentos = consulta.order_by(Agendamento.dataHora.asc()).all()

    resultado = [
        {
            "id": a.id,
            "dataHora": a.dataHora.isoformat(),
            "status": a.status,
            "cliente": {
                "id": a.cliente.id,
                "nome": a.cliente.nome
            },
            "profissional": {
                "id": a.profissional.id,
                "nome": a.profissional.nome,
                "especialidade": a.profissional.especialidade
            },
            "servico": {
                "id": a.servico.id,
                "nome": a.servico.nome,
                "duracaoEmMinutos": a.servico.duracaoEmMinutos,
                "preco": str(a.servico.preco)
            }
        }
        for a in agendamentos
    ]

    return jsonify(resultado), 200

if __name__ == '__main__':
    app.run(debug=True)