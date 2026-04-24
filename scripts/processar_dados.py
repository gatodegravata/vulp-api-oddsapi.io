import pandas as pd
import json
import glob
import os
import locale
from datetime import datetime, timedelta

# Tenta configurar para português para pegar o nome do mês
try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except:
    pass # Caso o runner não tenha o locale, ele usará o padrão

# ======================================================
# CONFIGURAÇÃO DINÂMICA
# ======================================================
# Pega o nome do mês atual em minúsculo (ex: "abril")
# No início do script, mantenha a detecção do mês
MES_ATUAL = datetime.now().strftime('%B').lower() 

# Nomes fixos por mês para garantir a sobreposição
ARQUIVO_SAIDA_XLSX = f"analise_vulp_{MES_ATUAL}.xlsx"
ARQUIVO_SAIDA_CSV = f"analise_vulp_{MES_ATUAL}.csv"

# No GitHub Actions, os arquivos estarão dentro da pasta do repositório
PASTA_ODDS = os.path.join("odds", MES_ATUAL)
PASTA_JOGOS = os.path.join("jogos", "odds-baixadas")

FUSO_HORARIO = -3 

def formatar_data_hora(iso_string, fuso):
    if not iso_string: return "N/A"
    try:
        dt_utc = datetime.strptime(iso_string.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")
        dt_local = dt_utc + timedelta(hours=fuso)
        return dt_local.strftime("%d/%m/%Y %H:%M")
    except:
        return "N/A"

def extrair_dados_completos_104(fixture_id):
    caminho = os.path.join(PASTA_ODDS, f"{fixture_id}.json")
    if not os.path.exists(caminho): return [None]*4
    try:
        with open(caminho, "r") as f:
            dados = json.load(f)
        markets = dados.get("bookmakers", {}).get("bet365", {}).get("markets", {})
        btts_outcome = markets.get("104", {}).get("outcomes", {}).get("104", {})
        historico = btts_outcome.get("players", {}).get("0", [])
        if not historico: return [None]*4
        historico_ord = sorted(historico, key=lambda x: x['createdAt'])
        return (historico_ord[0].get("price"), historico_ord[0].get("createdAt"),
                historico_ord[-1].get("price"), historico_ord[-1].get("createdAt"))
    except:
        return [None]*4

def processar_dados():
    dados_finais = []
    arquivos_lista = glob.glob(os.path.join(PASTA_JOGOS, "jogos_*.json"))

    if not arquivos_lista:
        print(f"⚠️ Nenhum arquivo encontrado em: {PASTA_JOGOS}")
        return

    for arquivo in arquivos_lista:
        with open(arquivo, "r") as f:
            jogos = json.load(f)
        for jogo in jogos:
            if jogo.get("statusName") != "Finished": continue
            f_id = jogo.get("fixtureId")
            o_price, o_time, c_price, c_time = extrair_dados_completos_104(f_id)
            dados_finais.append({
                "Data": formatar_data_hora(jogo["startTime"], FUSO_HORARIO).split()[0],
                "Horário": formatar_data_hora(jogo["startTime"], FUSO_HORARIO).split()[1],
                "Torneio": jogo.get("tournamentName"),
                "Mandante": jogo.get("participant1Name"),
                "Visitante": jogo.get("participant2Name"),
                "Timestamp Open": formatar_data_hora(o_time, FUSO_HORARIO),
                "Odd Open (BTTS)": o_price,
                "Timestamp Close": formatar_data_hora(c_time, FUSO_HORARIO),
                "Odd Close (BTTS)": c_price,
                "Fixture ID": f_id
            })

    df = pd.DataFrame(dados_finais)
    if df.empty:
        print("❌ Nenhum dado processado.")
        return

    df.to_csv(ARQUIVO_SAIDA_CSV, index=False, sep=';', encoding='utf-8-sig')
    with pd.ExcelWriter(ARQUIVO_SAIDA_XLSX, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analise')
    
    print(f"✅ Arquivos gerados para o mês: {MES_ATUAL}")

if __name__ == "__main__":
    processar_dados()