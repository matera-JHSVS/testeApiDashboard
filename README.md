# testeApiDashboard

Dashboard especialista para análise de resultados de testes automatizados em APIs de Renda Fixa.

## Clonando o projeto

```
git clone https://github.com/matera-JHSVS/testeApiDashboard.git
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
- Ajuste o caminho da variável `DIRETORIO_RESULTS` em `app.py` para o local correto dos resultados XML.
- O diretório `assets/` contém arquivos estáticos como CSS.
- O arquivo `.gitignore` já ignora arquivos e pastas comuns de ambiente Python, IDEs e a pasta `assets/`.

---

**Autor:** Jean Heberth Especialista em Engenharia de Qualidade e Dados
**Data:** 2026-05-15

---

© 2026 Jean Heberth. Todos os direitos reservados.
