import os
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
mongo_uri = "mongodb://root:example@mongo:27017/"
client = MongoClient(mongo_uri)
db = client.bebidas
colecao = db.contador
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Inicializa valores se não existirem
def inicializar_dados():
    print("Inicializando dados...")
    if colecao.count_documents({}) == 0:
        colecao.insert_many([
            {"nome": "tu", "quantidade": 0},
            {"nome": "amigo", "quantidade": 0}
        ])

@app.route("/")
def index():
    print("Acessando a página inicial...")
    inicializar_dados()
    dados = {item["nome"]: item["quantidade"] for item in colecao.find()}
    return render_template("index.html", dados=dados)


@app.route('/upload-imagem', methods=['POST'])
def upload_imagem():
    if 'imagem' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo encontrado'}), 400
    file = request.files['imagem']
    if file.filename == '':
        return jsonify({'erro': 'Arquivo sem nome'}), 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return jsonify({'mensagem': 'Upload feito com sucesso', 'caminho': filepath})

@app.route("/atualizar", methods=["POST"])
def atualizar():
    nome = request.json.get("nome")
    delta = request.json.get("delta")
    colecao.update_one({"nome": nome}, {"$inc": {"quantidade": delta}})
    novo_valor = colecao.find_one({"nome": nome})["quantidade"]
    return jsonify({"quantidade": novo_valor})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
