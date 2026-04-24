import os
import json
import glob

# ======================================================
# CAMINHOS (Windows)
# ======================================================
PATH_JOGOS = r"C:\proj\apostas\api-oddsapi.io\jogos\nao-processadas-odds"
PATH_ODDS = r"C:\proj\apostas\analise-pontual\oddsapi.io\odds\abril"

def conferir_downloads():
    # 1. Coletar todos os fixtureIds que estão nas LISTAS de jogos
    ids_na_lista = set()
    arquivos_lista = glob.glob(os.path.join(PATH_JOGOS, "*.json"))
    
    print(f"📂 Analisando {len(arquivos_lista)} arquivos de lista...")
    
    for arq in arquivos_lista:
        try:
            with open(arq, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                for jogo in dados:
                    # Só adicionamos se for jogo finalizado (opcional, remova o if se quiser todos)
                    #if jogo.get('statusName') == 'Finished':
                    ids_na_lista.add(str(jogo.get('fixtureId')))
        except Exception as e:
            print(f"❌ Erro ao ler {arq}: {e}")

    # 2. Coletar os fixtureIds que já possuem ARQUIVO PRÓPRIO na pasta de odds
    # Removemos a extensão .json para comparar apenas o ID
    ids_baixados = set()
    if os.path.exists(PATH_ODDS):
        arquivos_odds = os.listdir(PATH_ODDS)
        for arq in arquivos_odds:
            if arq.endswith(".json"):
                ids_baixados.add(arq.replace(".json", ""))
    
    # 3. Comparação (Diferença de conjuntos)
    faltantes = ids_na_lista - ids_baixados

    # 4. Resultado
    print("-" * 50)
    print(f"📊 Resumo da Conferência:")
    print(f"✅ IDs únicos finalizados na lista: {len(ids_na_lista)}")
    print(f"📁 IDs já baixados (arquivos na pasta): {len(ids_baixados)}")
    print(f"🚨 IDs FALTANTES: {len(faltantes)}")
    print("-" * 50)

    if faltantes:
        print("\n📝 Lista de IDs Faltantes:")
        for id_f in sorted(list(faltantes)):
            print(id_f)
            
        # Opcional: Salvar os faltantes num TXT para usar no script de download
        with open("ids_faltantes.txt", "w") as f:
            f.write("\n".join(sorted(list(faltantes))))
        print(f"\n💾 Salvo em 'ids_faltantes.txt' para facilitar o download.")
    else:
        print("🎯 Tudo em ordem! Todos os jogos da lista foram baixados.")

if __name__ == "__main__":
    conferir_downloads()