import os, shutil, json, subprocess, glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECEBIDOS = os.path.join(BASE_DIR, 'recebidos')
IMG_DIR = os.path.join(BASE_DIR, 'img')
JSON_FILE = os.path.join(BASE_DIR, 'dados.json')

os.makedirs(RECEBIDOS, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

hoje = datetime.now().strftime('%Y-%m-%d')

# Carrega histórico existente
dados = {"dias": []}
if os.path.exists(JSON_FILE):
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao ler JSON anterior: {e}")

novo_dia = {"data": hoje}
prefixos = {'lf': 'lotofacil', 'lm': 'lotomania', 'ms': 'megasena'}

for prefixo, chave in prefixos.items():
    padrao = os.path.join(RECEBIDOS, f"{prefixo}_*.png")
    arquivos = sorted(glob.glob(padrao))

    caminhos_relativos = []
    for arquivo in arquivos:
        nome_base = os.path.basename(arquivo)
        nome_destino = f"{hoje}-{nome_base}"
        dest = os.path.join(IMG_DIR, nome_destino)
        shutil.copy2(arquivo, dest)
        caminhos_relativos.append(f"img/{nome_destino}")

    # Limita a 6 imagens por loteria
    novo_dia[chave] = caminhos_relativos[:6]

# Verifica se há pelo menos 1 imagem para registrar o dia
total_imgs = sum(len(novo_dia[k]) for k in prefixos.values())
if total_imgs == 0:
    print("⚠️ Nenhuma imagem encontrada na pasta 'recebidos/'.")
    print("💡 Use prefixos: lf_01.png, lm_02.png, ms_03.png")
    exit(1)

# Insere no início e mantém apenas 10 dias
dados["dias"].insert(0, novo_dia)
dados["dias"] = dados["dias"][:10]

# Salva JSON
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(dados, f, indent=2, ensure_ascii=False)

# Commit e Push
os.chdir(BASE_DIR)
subprocess.run(['git', 'add', 'img/', 'dados.json'], check=True)
subprocess.run(['git', 'commit', '-m', f'Update: {hoje} ({total_imgs} imagens)'], check=True)
subprocess.run(['git', 'push'], check=True)

print(f"✅ Sucesso! Postado para {hoje}.")
print(f"📊 Total de imagens: {total_imgs}")
print("🌐 O site atualizará automaticamente em 15-30 segundos.")