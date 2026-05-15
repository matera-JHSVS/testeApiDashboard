import streamlit as st
import pandas as pd
import os
import xml.etree.ElementTree as ET
import glob
import io
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# --- CONFIGURAÇÃO DE CAMINHO ---
# Ajuste este caminho para o diretório raiz onde ficam as pastas F01, F02, etc.
DIRETORIO_RESULTS = r"C:\Desenvolvimento\robot\renda-fixa-testes-funcionais\robot-framework\acceptance-tests\api-renda-fixa\results"


# --- FUNÇÃO PARA COLETAR DADOS DOS XMLS ---
@st.cache_data(ttl=60)  # Atualiza a cada 1 minuto
def carregar_dados_robot():
    lista_testes = []
    # Busca recursiva por arquivos XML, ignorando a pasta sikuli
    arquivos = glob.glob(os.path.join(DIRETORIO_RESULTS, "**/*.xml"), recursive=True)

    for arquivo in arquivos:
        if "sikuli" in arquivo.lower():
            continue

        try:
            tree = ET.parse(arquivo)
            root = tree.getroot()
            # O nome da Feature é o nome da pasta pai do XML
            nome_feature = os.path.basename(os.path.dirname(arquivo))

            for test in root.iter('test'):
                nome_ct = test.attrib.get('name')
                status = test.find('status').attrib.get('status', 'FAIL').upper()
                lista_testes.append({
                    "Feature": nome_feature,
                    "Cenário": nome_ct,
                    "Status": status
                })
        except Exception as e:
            print(f"Erro ao processar {arquivo}: {e}")

    return pd.DataFrame(lista_testes)


# --- FUNÇÃO DE GERAÇÃO DO EXCEL FORMATADO ---
def gerar_excel_deploy(df):
    output = io.BytesIO()
    wb = Workbook()

    # 1. ABA RESUMO GERAL
    ws_resumo = wb.active
    ws_resumo.title = "Resumo Geral"
    ws_resumo.append(["Total Statistics (Feature)", "Total", "Pass", "Fail"])

    resumo_df = df.groupby('Feature')['Status'].value_counts().unstack(fill_value=0)
    if 'PASS' not in resumo_df: resumo_df['PASS'] = 0
    if 'FAIL' not in resumo_df: resumo_df['FAIL'] = 0

    for feature, row in resumo_df.iterrows():
        total_f = row['PASS'] + row['FAIL']
        ws_resumo.append([feature, total_f, row['PASS'], row['FAIL']])

    # Linha ALL TESTS
    ws_resumo.append([
        "ALL TESTS (Resumo Geral)",
        len(df),
        len(df[df['Status'] == 'PASS']),
        len(df[df['Status'] == 'FAIL'])
    ])
    for cell in ws_resumo[ws_resumo.max_row]: cell.font = Font(bold=True)

    # 2. ABA CENÁRIOS COM FALHA (NEGRITO NOS CTS)
    ws_falhas = wb.create_sheet("Cenários com Falha")
    ws_falhas.append(["Cenário com Falha", "Status"])
    ws_falhas["A1"].font = Font(bold=True)

    fill_header = PatternFill(start_color="E9ECEF", end_color="E9ECEF", fill_type="solid")
    row_idx = 2

    df_fails = df[df['Status'] == 'FAIL'].sort_values('Feature')
    for feature in df_fails['Feature'].unique():
        # Linha da Feature (Cabeçalho do bloco)
        cell_feat = ws_falhas.cell(row=row_idx, column=1, value=feature)
        cell_feat.font = Font(bold=True, italic=True)
        cell_feat.fill = fill_header
        ws_falhas.cell(row=row_idx, column=2, value="FAIL").fill = fill_header
        row_idx += 1

        # Cenários da Feature (EM NEGRITO)
        for ct in df_fails[df_fails['Feature'] == feature]['Cenário']:
            cell_ct = ws_falhas.cell(row=row_idx, column=1, value=ct)
            cell_ct.font = Font(bold=True)  # CT em Negrito solicitado
            ws_falhas.cell(row=row_idx, column=2, value="FAIL")
            row_idx += 1

    # Ajustes de colunas
    ws_falhas.column_dimensions['A'].width = 100
    ws_resumo.column_dimensions['A'].width = 40

    wb.save(output)
    return output.getvalue()


# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Dashboard Renda Fixa", layout="wide")

# Sidebar com Botão de Exportação
with st.sidebar:
    st.title("📂 Menu de Exportação")
    df_atual = carregar_dados_robot()

    if not df_atual.empty:
        if st.button("📊 Preparar Planilha de Deploy"):
            dados_excel = gerar_excel_deploy(df_atual)
            st.download_button(
                label="📥 Baixar Excel AGORA",
                data=dados_excel,
                file_name=f"Relatorio_Deploy_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("Planilha gerada com CTs em negrito!")
    else:
        st.error("Nenhum arquivo XML encontrado no diretório.")

# Título e Cards de Métricas
st.title("🚀 Monitoramento de APIs - Renda Fixa")

if not df_atual.empty:
    total = len(df_atual)
    passou = len(df_atual[df_atual['Status'] == 'PASS'])
    falhou = len(df_atual[df_atual['Status'] == 'FAIL'])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Testes Totais", total)
    c2.metric("Passou", passou, f"{(passou / total) * 100:.1f}%")
    c3.metric("Quebrou", falhou, f"-{(falhou / total) * 100:.1f}%", delta_color="inverse")
    c4.metric("Features Ativas", len(df_atual['Feature'].unique()))

    # Tabela de Resumo no Dashboard
    st.divider()
    st.subheader("Situação por Feature (Total 38)")
    resumo_view = df_atual.groupby('Feature')['Status'].value_counts().unstack(fill_value=0)
    st.dataframe(resumo_view, use_container_width=True)

else:
    st.warning("Aguardando leitura de dados...")