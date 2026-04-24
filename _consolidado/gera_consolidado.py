# @title Gerar Excel e CSV com Timestamps das Odds
import pandas as pd
import json
import glob
import os
from datetime import datetime, timedelta

# ======================================================
# CONFIGURAÇÃO
# ======================================================
MES = "abril"
FUSO_HORARIO = -3 
PASTA_ODDS = rf"C:\proj\apostas\analise-pontual\oddsapi.io\odds\{MES}"
PASTA_JOGOS = rf"C:\proj\apostas\analise-pontual\oddsapi.io\jogos\odds-baixadas"
# Nome base para os arquivos
DATA_ATUAL = datetime.now().strftime('%Y-%m-%d')
ARQUIVO_SAIDA_XLSX = f"analise_vulp_detalhada_{DATA_ATUAL}.xlsx"
ARQUIVO_SAIDA_CSV = f"analise_vulp_detalhada_{DATA_ATUAL}.csv"

def formatar_data_hora(iso_string, fuso):
    """Converte ISO UTC para string formatada no fuso local"""
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
        
        return (
            historico_ord[0].get("price"), 
            historico_ord[0].get("createdAt"),
            historico_ord[-1].get("price"),
            historico_ord[-1].get("createdAt")
        )
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
            
            # Extração das Odds e Timestamps
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

    # Criar o DataFrame único com todos os resultados
    df = pd.DataFrame(dados_finais)

    if df.empty:
        print("❌ Nenhum dado processado. Verifique os arquivos JSON.")
        return

    # --- GERAÇÃO DO CSV ---
    # Usamos sep=';' e utf-8-sig para que o Excel abra o CSV corretamente no Brasil
    df.to_csv(ARQUIVO_SAIDA_CSV, index=False, sep=';', encoding='utf-8-sig')
    print(f"✅ Arquivo CSV gerado com sucesso: {ARQUIVO_SAIDA_CSV}")

    # --- GERAÇÃO DO EXCEL (XLSX) ---
    with pd.ExcelWriter(ARQUIVO_SAIDA_XLSX, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analise')
        
        # Ajuste automático de largura das colunas
        ws = writer.sheets['Analise']
        for col in ws.columns:
            max_len = max([len(str(cell.value)) for cell in col] + [10])
            ws.column_dimensions[col[0].column_letter].width = max_len + 2
    
    print(f"✅ Arquivo Excel gerado com sucesso: {ARQUIVO_SAIDA_XLSX}")

if __name__ == "__main__":
    processar_dados()