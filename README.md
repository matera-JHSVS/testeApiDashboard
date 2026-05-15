# testeApiDashboard

Dashboard especialista para análise de resultados de testes automatizados em APIs de Renda Fixa.

## Clonando o projeto

```
git clone <URL_DO_REPOSITORIO>
cd testeApiDashboard
```

## Instalando as dependências

Recomenda-se o uso de ambiente virtual (venv):

```
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Executando o Dashboard

```
streamlit run app.py
```

O dashboard será iniciado e o link de acesso será exibido no terminal (ex: http://localhost:8501).

## Observações
- Ajuste o caminho da variável `DIRETORIO_RESULTS` em `app.py` e `gerar_relatorio.py` para o local correto dos resultados XML.
- O diretório `assets/` contém arquivos estáticos como CSS.
- O arquivo `.gitignore` já ignora arquivos e pastas comuns de ambiente Python, IDEs e a pasta `assets/`.

---

**Autor:** Especialista em Engenharia de Qualidade e Dados
**Data:** 2026-05-15

