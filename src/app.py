import os
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
mongo_uri = "mongodb://root:example@mongo:27017/"
client = MongoClient(mongo_uri)
db = client.bebidas
colecao = db.contador
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

dados = {}
counts = {}


def calcular_quantidades():
    global dados
    global counts
    dados = colecao.find()
    counts = {}
    for dado in dados:
        nome = dado["nome"]
        if nome not in counts:
            counts[nome] = 1
        else:
            counts[nome] += 1


@app.route("/")
def index():
    print("Acessando a página inicial...")
    dados = colecao.find()
    calcular_quantidades()
    return render_template("index.html", dados=dados, counts=counts)


@app.route("/upload-imagem-ana", methods=["POST"])
def upload_imagem_ana():
    return upload_imagem("Ana")


@app.route("/upload-imagem-alex", methods=["POST"])
def upload_imagem_alex():
    return upload_imagem("Alex")


def upload_imagem(nome_usuario):
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhum arquivo encontrado"}), 400
    file = request.files["imagem"]
    if file.filename == "":
        return jsonify({"erro": "Arquivo sem nome"}), 400
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Adicionando o registro de upload na base de dados
    new_entry = {
        "nome": nome_usuario,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "acao": "Adicionado",
        "imagem_path": filepath,
    }
    colecao.insert_one(new_entry)
    calcular_quantidades()

    return jsonify({"mensagem": "Upload feito com sucesso", "caminho": filepath})


@app.route("/atualizar", methods=["POST"])
def atualizar():
    print("Atualizando dados...")
    nome = request.json.get("nome")
    delta = request.json.get("delta")

    print("nome:", nome)

    new_entry = {
        "nome": nome,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "acao": "Adicionado" if delta > 0 else "Removido",
    }

    colecao.insert_one(new_entry)

    # retorna a quantidade do nome dado
    quantidade = colecao.count_documents({"nome": nome, "acao": "Adicionado"})
    quantidade -= colecao.count_documents({"nome": nome, "acao": "Removido"})

    # Retorna o novo valor para o frontend
    return jsonify({"quantidade": quantidade})


@app.route("/dados-atualizados", methods=["GET"])
def dados_atualizados():
    calcular_quantidades()
    dados_serializaveis = [{**dado, "_id": str(dado["_id"])} for dado in colecao.find()]
    return jsonify({"dados": dados_serializaveis, "counts": counts})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
