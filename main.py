import datetime
import pytz
from flask import Flask, render_template, request, redirect, url_for
import os
from os import path
import json

app = Flask(__name__)

# Define o fuso horário de Manaus
fuso_horario = pytz.timezone("America/Manaus")

# Define o diretório de destino dos arquivos
diretorio_destino = "dados_coletados"

# Verifica se o diretório de destino existe, caso contrário, cria-o
if not path.exists(diretorio_destino):
    os.makedirs(diretorio_destino)

# Lista de dados salvos
dados_salvos = []

# Carrega todos os dados dos arquivos JSON no diretório de destino
def carregar_dados_salvos():
    global dados_salvos
    dados_salvos = listar_dados_arquivos()

# Carrega todos os dados dos arquivos JSON no diretório de destino
def listar_dados_arquivos():
    dados_totais = []
    for arquivo in os.listdir(diretorio_destino):
        if arquivo.endswith(".json"):
            arquivo_dados = path.join(diretorio_destino, arquivo)
            with open(arquivo_dados, "r") as arquivo_json:
                dados_arquivo = json.load(arquivo_json)
                dados_totais.extend(dados_arquivo)
    return dados_totais

# Filtra os dados para exibir apenas os do dia atual
def filtrar_dados_dia_atual(dados):
    data_atual = datetime.datetime.now(fuso_horario).date()
    dados_filtrados = []
    for dado in dados:
        data_hora = datetime.datetime.strptime(dado['data_hora'], '%d/%m/%Y %H:%M')
        if data_hora.date() == data_atual:
            dados_filtrados.append(dado)
    return dados_filtrados

# Rota principal para exibir a página de coleta
@app.route('/')
def index():
    return render_template('index.html')

# Rota para página de arquivos salvos
@app.route('/coletar_dados')
def exibir_dados_salvos():
    carregar_dados_salvos()
    
    # Filtra os dados do dia atual
    data_atual = datetime.datetime.now(fuso_horario).strftime('%d/%m/%Y')
    dados_dia_atual = [dados for dados in dados_salvos if dados['data_hora'].startswith(data_atual)]
    return render_template('dados_salvos.html', dados=dados_dia_atual)

# Rota para coletar os dados
@app.route('/coletar_dados', methods=['POST'])
def coletar_dados():
    # Obtém os valores do formulário
    testador = request.form.get('testador').upper()
    modelo = request.form.get('modelo').upper()
    op = request.form.get('op')
    numero_serie = request.form.get('numero_serie')
    ipmi = request.form.get('ipmi')
    pwd = request.form.get('pwd').upper()  # '.upper()' Converte para caixa alta

    # Obtém a data e hora atual no fuso horário definido
    data_hora_atual = datetime.datetime.now(fuso_horario).strftime('%d/%m/%Y %H:%M')

    # Cria um dicionário com os dados coletados, incluindo a hora específica
    dados = {
        "data_hora": data_hora_atual,
        "modelo": modelo,
        "op": op,
        "numero_serie": numero_serie,
        "ipmi": ipmi,
        "pwd": pwd,
        "testador": testador
    }

    # Salva os dados no arquivo correspondente à data e hora atual
    arquivo_dados = path.join(diretorio_destino, f"coleta_{data_hora_atual.replace('/', '-').replace(':', '-')}.json")
    dados_registrados = []
    if path.exists(arquivo_dados):
        with open(arquivo_dados, "r") as arquivo:
            dados_registrados = json.load(arquivo)
    dados_registrados.append(dados)
    with open(arquivo_dados, "w") as arquivo:
        json.dump(dados_registrados, arquivo)

    # Atualiza a lista de dados salvos
    carregar_dados_salvos()

    # Retorna a mensagem de sucesso e redireciona para a página principal
    return redirect(url_for('index'))



# Rota para página de arquivos salvos
@app.route('/listar_arquivos')
def listar_arquivos():
    carregar_dados_salvos()
    return render_template('listar_arquivos.html', dados=dados_salvos)

if __name__ == '__main__':
    carregar_dados_salvos()
    app.run(host='0.0.0.0', port=5555)
