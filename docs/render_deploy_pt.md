<!-- File version: 2.1; date: 2026-05-12 -->

# Guia de Deploy no Render

Este projeto agora tem duas interfaces de usuário:

- interface desktop local: Tkinter, iniciada com `python run_app.py`
- interface web: API REST em Flask mais cliente estático no navegador, servido por `intervention_sample_planner.web_app`

O motor de cálculo continua sendo a mesma API Python em `intervention_sample_planner/calculator.py`. A interface web não duplica fórmulas de tamanho de amostra.

## Por que Flask

Flask foi usado porque mantém o servidor pequeno, não exige banco de dados, serve arquivos estáticos locais diretamente e expõe endpoints REST com pouca configuração no Render. O front end é HTML/CSS/JavaScript puro em `intervention_sample_planner/web_static`, então não há etapa de build com Node.js.

## Execução Web Local

Instale as dependências web:

```powershell
python -m pip install -r requirements.txt
```

Inicie o app web:

```powershell
python -m flask --app intervention_sample_planner.web_app run
```

Abra:

```text
http://127.0.0.1:5000
```

## Endpoints REST

- `GET /health`
- `GET /api/version`
- `GET /api/default-config`
- `GET /api/explanations?language=pt`
- `GET /api/ui-text?language=pt`
- `POST /api/calculate`
- `POST /api/report/text`
- `POST /api/report/html`
- `POST /api/report/pdf`

Os endpoints `POST` aceitam um objeto JSON compatível com `schemas/study_config.schema.json`.

## Arquivos do usuário

O app web não usa banco de dados e não mantém arquivos de estudo do usuário no servidor. O cliente no navegador pode:

- carregar um arquivo JSON local escolhido pelo usuário
- salvar a configuração atual como um JSON baixado
- baixar relatórios em texto, HTML ou PDF

## Configuração do Serviço no Render

O Render pode ler `render.yaml` como Blueprint. A configuração do serviço é:

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn intervention_sample_planner.web_app:app`
- Python version: `3.11.9`
- Banco de dados: nenhum
- Disco persistente: nenhum

Se criar o serviço manualmente no painel do Render, use os mesmos comandos de build e start.

## Deploy somente quando uma tag for enviada

O Render normalmente permite deploy automático a partir de uma branch conectada. Para este projeto, o fluxo solicitado é controlado por tag:

1. Nas configurações do serviço no Render, desative o auto-deploy normal se não quiser publicar todo push na branch.
2. Copie a Deploy Hook URL do serviço no Render.
3. No GitHub, abra as configurações do repositório.
4. Entre em `Secrets and variables` > `Actions`.
5. Crie um segredo chamado `RENDER_DEPLOY_HOOK_URL`.
6. Cole a Deploy Hook URL do Render como valor.
7. Mantenha `.github/workflows/deploy-render-on-tag.yml` no repositório.

Quando uma tag como `v2.1` for enviada, o GitHub Actions:

- faz checkout do commit taggeado
- instala `requirements.txt`
- roda os testes unitários
- chama a Deploy Hook do Render com `ref=<SHA do commit taggeado>`

Usar o parâmetro `ref` pede ao Render para publicar exatamente o commit associado à tag, não apenas o commit mais novo da branch conectada.

## Checklist de Release

1. Rode os testes locais:

```powershell
python -m unittest discover -s tests
```

2. Teste o app web localmente:

```powershell
python -m flask --app intervention_sample_planner.web_app run
```

3. Faça o commit da release.

4. Crie a tag:

```powershell
git tag -a v2.1 -m "version 2.1"
```

5. Envie a branch e a tag:

```powershell
git push
git push origin v2.1
```

O push da tag inicia o GitHub Action, e o action inicia o deploy no Render.

## Referências

- [Render Deploy Hooks](https://render.com/docs/deploy-hooks)
- [Processo e comandos de deploy no Render](https://render.com/docs/deploys/)
- [Deploy de commit específico com `ref` em Deploy Hook](https://render.com/docs/deploying-a-commit)
- [Sintaxe do GitHub Actions para tags em push](https://docs.github.com/actions/reference/workflows-and-actions/workflow-syntax#onpushbranchestagsbranches-ignoretags-ignore)
