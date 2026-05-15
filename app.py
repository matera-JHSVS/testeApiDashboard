import streamlit as st
import pandas as pd
import os
import xml.etree.ElementTree as ET
import glob
import io
import time
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# --- CONFIGURAÇÃO DE CAMINHO ---
DIRETORIO_RESULTS = r"C:\Desenvolvimento\robot\renda-fixa-testes-funcionais\robot-framework\acceptance-tests\api-renda-fixa\results"


@st.cache_data(ttl=5)
def carregar_dados_xml():
    lista_testes = []
    arquivos = glob.glob(os.path.join(DIRETORIO_RESULTS, "**/*.xml"), recursive=True)
    for arquivo in arquivos:
        if "sikuli" in arquivo.lower(): continue
        try:
            tree = ET.parse(arquivo)
            root = tree.getroot()
            nome_feature = os.path.basename(os.path.dirname(arquivo))
            for test in root.iter('test'):
                status = test.find('status').attrib.get('status', 'FAIL').upper()
                lista_testes.append({
                    "Feature": nome_feature,
                    "Cenário": test.attrib.get('name'),
                    "Status": status
                })
        except:
            continue
    return pd.DataFrame(lista_testes)


def limpar_texto_pdf(texto):
    """Remove caracteres Unicode que a fonte Helvetica não suporta"""
    if not texto: return ""
    mapeamento = {
        "\u2014": "-", "\u2013": "-",
        "\u201c": '"', "\u201d": '"',
        "\u2018": "'", "\u2019": "'",
    }
    for original, substituto in mapeamento.items():
        texto = texto.replace(original, substituto)
    return texto.encode('latin-1', 'ignore').decode('latin-1')


def gerar_excel_deploy(df):
    output = io.BytesIO()
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Resumo Geral"
    ws1.append(["Total Statistics (Feature)", "Total", "Pass", "Fail"])
    resumo = df.groupby('Feature')['Status'].value_counts().unstack(fill_value=0)
    for feat, row in resumo.iterrows():
        p, f = row.get('PASS', 0), row.get('FAIL', 0)
        ws1.append([feat, p + f, p, f])

    ws2 = wb.create_sheet("Cenários com Falha")
    ws2.append(["Cenário com Falha", "Status"])
    df_fail = df[df['Status'] == 'FAIL'].sort_values('Feature')
    row_idx = 2
    for feat in df_fail['Feature'].unique():
        ws2.cell(row=row_idx, column=1, value=feat).font = Font(bold=True, italic=True)
        row_idx += 1
        for ct in df_fail[df_fail['Feature'] == feat]['Cenário']:
            cell = ws2.cell(row=row_idx, column=1, value=ct)
            cell.font = Font(bold=True)  # CT Negrito
            ws2.cell(row=row_idx, column=2, value="FAIL")
            row_idx += 1
    wb.save(output)
    return output.getvalue()


def gerar_pdf_deploy(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(190, 10, "Relatorio de Deploy - Renda Fixa",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(190, 10, "Cenarios com Falha:",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    df_fail = df[df['Status'] == 'FAIL'].sort_values('Feature')
    for feat in df_fail['Feature'].unique():
        pdf.set_font("helvetica", "BI", 10)
        pdf.cell(190, 7, f"Feature: {limpar_texto_pdf(feat)}",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font("helvetica", "B", 9)  # CTs em NEGRITO no PDF
        for ct in df_fail[df_fail['Feature'] == feat]['Cenário']:
            texto_limpo = limpar_texto_pdf(f"  - {ct} [FAIL]")
            pdf.multi_cell(190, 6, texto_limpo,
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    # CRITICAL FIX: Converter bytearray para bytes para o Streamlit aceitar
    return bytes(pdf.output())


# --- INTERFACE ---
st.set_page_config(page_title="QA Dashboard", layout="wide")
st.title("🚀 Dashboard de Testes - Renda Fixa")

with st.sidebar:
    st.title("⚙️ Painel")
    df = carregar_dados_xml()
    if not df.empty:
        st.write("### 📥 Exportar")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Excel", key="btn_excel"):
                st.download_button("Baixar Excel", gerar_excel_deploy(df),
                                   f"Relatorio_{datetime.now().strftime('%H%M')}.xlsx")
        with col2:
            if st.button("📄 PDF", key="btn_pdf"):
                # Agora retornando 'bytes', o StreamlitAPIException desaparece
                pdf_bytes = gerar_pdf_deploy(df)
                st.download_button("Baixar PDF", pdf_bytes,
                                   f"Relatorio_{datetime.now().strftime('%H%M')}.pdf",
                                   mime="application/pdf")

if not df.empty:
    st.divider()
    st.subheader("Resultados por Feature")
    resumo_view = df.groupby('Feature')['Status'].value_counts().unstack(fill_value=0)
    st.dataframe(resumo_view, width="stretch")

time.sleep(10)
st.rerun()