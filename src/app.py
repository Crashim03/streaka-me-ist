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

dados = {}
registros = []

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
    data = request.json.get()
    nome = data['nome']
    delta = data['delta']
    
    # Atualiza o valor de 'tu' ou 'amigo' (armazena no dicionário)
    dados[nome] += delta
    
    # Adiciona o registro de ação
    acao = 'Adicionado' if delta > 0 else 'Removido'
    registros.append({
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'quem': nome.capitalize(),
        'acao': f"{acao} {abs(delta)}"
    })
    
    # Retorna o novo valor para o frontend
    return jsonify({'quantidade': dados[nome]})
