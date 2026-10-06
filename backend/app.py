from flask import Flask, request, jsonify
from models import db, Cliente, Profissional, Servico

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/espelho_meu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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

if __name__ == '__main__':
    app.run(debug=True)