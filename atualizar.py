import os, shutil, json, subprocess, glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECEBIDOS = os.path.join(BASE_DIR, 'recebidos')
IMG_DIR = os.path.join(BASE_DIR, 'img')
JSON_FILE = os.path.join(BASE_DIR, 'dados.json')

os.makedirs(RECEBIDOS, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

hoje = datetime.now().strftime('%Y-%m-%d')

# Carrega histórico
dados = {"dias": []}
if os.path.exists(JSON_FILE):
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao ler JSON anterior: {e}")

novo_dia = {"data": hoje}
prefixos = {'lf': 'lotofacil', 'lm': 'lotomania', 'ms': 'megasena'}

# 1. Copia imagens
for prefixo, chave in prefixos.items():
    padrao = os.path.join(RECEBIDOS, f"{prefixo}_*.png")
    arquivos = sorted(glob.glob(padrao))

    caminhos = []
    for arquivo in arquivos:
        nome = os.path.basename(arquivo)
        dest = os.path.join(IMG_DIR, f"{hoje}-{nome}")
        shutil.copy2(arquivo, dest)
        caminhos.append(f"img/{hoje}-{nome}")

    novo_dia[chave] = caminhos[:6]  # limite de 6 por loteria

total_imgs = sum(len(novo_dia[k]) for k in prefixos.values())
if total_imgs == 0:
    print("⚠️ Nenhuma imagem em 'recebidos/'. Use: lf_01.png, lm_01.png, ms_01.png")
    exit(1)

# 2. Mescla se já existir no mesmo dia
idx_existente = next((i for i, d in enumerate(dados["dias"]) if d["data"] == hoje), None)
if idx_existente is not None:
    dia_existente = dados["dias"][idx_existente]
    for chave in prefixos.values():
        existentes = dia_existente.get(chave, [])
        novas = novo_dia.get(chave, [])
        mescladas = existentes + [n for n in novas if n not in existentes]
        dia_existente[chave] = mescladas[:6]
    dados["dias"][idx_existente] = dia_existente
    print("🔄 Dia já existente. Imagens mescladas sem duplicar.")
else:
    dados["dias"].insert(0, novo_dia)
    print("📅 Novo dia registrado.")

# 3. MANTÉM APENAS OS 2 DIAS MAIS RECENTES
dados["dias"] = dados["dias"][:2]

# 4. Salva JSON
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(dados, f, indent=2, ensure_ascii=False)

# 5. Git com logs detalhados
os.chdir(BASE_DIR)
try:
    print("⏳ Enviando para o GitHub...")
    subprocess.run(['git', 'add', 'img/', 'dados.json'], check=True, capture_output=True, text=True)
    
    commit_msg = f'Update: {hoje} ({total_imgs} imagens)'
    subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, text=True)
    
    push_result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    if push_result.returncode != 0:
        # Mostra o erro real do Git (auth, rede, etc.)
        print(f"❌ Falha no push:\n{push_result.stderr.strip()}")
        if "Authentication failed" in push_result.stderr:
            print("💡 Token expirado? Gere um novo em: github.com/settings/tokens")
        exit(1)
    
    # Limpa só se deu tudo certo
    for f in glob.glob(os.path.join(RECEBIDOS, '*.png')):
        os.remove(f)
    print("🧹 'recebidos/' limpa com sucesso.")
    print(f"✅ Postado! {hoje} | {total_imgs} imagens | Histórico: 2 dias")
    print("🌐 Site atualiza em ~15-30s.")

except subprocess.CalledProcessError as e:
    print(f"❌ Erro no Git: {e}")
    print("⚠️ Pasta 'recebidos/' mantida por segurança.")
    exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    exit(1)