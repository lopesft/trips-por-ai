import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados usando variável de ambiente
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://auto-trips-db_owner:npg_ZayKXMBOU49Y@ep-noisy-cake-a8yal9qu.eastus2.azure.neon.tech/auto-trips-db?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para a tabela Viagem
class Viagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destino = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(20), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # Categoria da viagem
    agencia = db.Column(db.String(100), nullable=False)   # Nome da agência
    imagem_url = db.Column(db.String(255), nullable=True)  # URL da imagem

    def __repr__(self):
        return f"<Viagem {self.destino}>"

# Rota inicial
@app.route('/')
def home():
    return "Bem-vindo à API de Viagens!"

# Rota para cadastrar uma nova viagem
@app.route('/viagens', methods=['POST'])
def cadastrar_viagem():
    dados = request.json
    campos_obrigatorios = {"destino", "data", "preco", "descricao", "categoria", "agencia"}
    if not campos_obrigatorios.issubset(dados):
        return jsonify({"erro": f"Os campos {', '.join(campos_obrigatorios)} são obrigatórios!"}), 400

    nova_viagem = Viagem(
        destino=dados["destino"],
        data=dados["data"],
        preco=dados["preco"],
        descricao=dados["descricao"],
        categoria=dados["categoria"],
        agencia=dados["agencia"],
        imagem_url=dados.get("imagem_url")
    )
    db.session.add(nova_viagem)
    db.session.commit()

    return jsonify({
        "id": nova_viagem.id,
        "destino": nova_viagem.destino,
        "data": nova_viagem.data,
        "preco": nova_viagem.preco,
        "descricao": nova_viagem.descricao,
        "categoria": nova_viagem.categoria,
        "agencia": nova_viagem.agencia,
        "imagem_url": nova_viagem.imagem_url
    }), 201

@app.route('/viagens', methods=['GET'])
def listar_viagens():
    categoria = request.args.get('categoria')
    index = request.args.get('index', type=int)
    if categoria:
        viagens = Viagem.query.filter_by(categoria=categoria).all()
    else:
        viagens = Viagem.query.all()

    if not viagens:
        return jsonify({"quantidade_trips": 0, "trips": []}), 200

    if index is not None:
        adjusted_index = index - 1
        if 0 <= adjusted_index < len(viagens):
            viagem = viagens[adjusted_index]
            return jsonify({
                "agencia": viagem.agencia,
                "categoria": viagem.categoria,
                "data": viagem.data,
                "descricao": viagem.descricao,
                "destino": viagem.destino,
                "id": viagem.id,
                "preco": viagem.preco,
                "imagem_url": viagem.imagem_url
            }), 200
        else:
            return jsonify({"erro": "Índice fora do intervalo!"}), 400

    trips = [{"agencia": v.agencia, "categoria": v.categoria, "data": v.data,
              "descricao": v.descricao, "destino": v.destino, "id": v.id,
              "preco": v.preco, "imagem_url": v.imagem_url} for v in viagens]

    return jsonify({"quantidade_trips": len(trips), "trips": trips}), 200

@app.route('/viagens/<int:id>', methods=['DELETE'])
def deletar_viagem(id):
    viagem = Viagem.query.get(id)
    if not viagem:
        return jsonify({"erro": "Viagem não encontrada!"}), 404

    db.session.delete(viagem)
    db.session.commit()

    return jsonify({"mensagem": "Viagem deletada com sucesso!"}), 200

# Adicione um handler para inicializar o banco de dados no Vercel
@app.before_request
def setup_db():
    db.create_all()

# Exporta o app para o Vercel
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
