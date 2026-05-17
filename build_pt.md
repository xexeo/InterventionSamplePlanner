<!-- File version: 2.2; date: 2026-05-17 -->

# Guia de Build

## Aplicativo Python

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m unittest discover -s tests
python run_app.py
```

## Executável para Windows

O executável é gerado com PyInstaller. Como o `ISP v2.2` depende de `intervention_sample_planner/explanations.json`, o comando de build precisa incluir esse arquivo.

Exemplo:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onefile --name InterventionSamplePlanner --add-data "intervention_sample_planner\explanations.json;intervention_sample_planner" --add-data "intervention_sample_planner\web_static;intervention_sample_planner\web_static" run_app.py
```

Depois de gerar um executável Windows para release, crie ou verifique o checksum SHA256:

```powershell
Get-FileHash .\dist\InterventionSamplePlanner.exe -Algorithm SHA256
```

O checksum de release versionado no repositório fica em:

```text
release/checksums.sha256
```

## Exportação de relatório

O aplicativo desktop pode exportar o resultado atual como texto, HTML ou PDF. O gerador de PDF é propositalmente simples e local; ele não exige navegador nem dependência externa de PDF.

## Interface web

A interface web usa Flask para a API REST e arquivos estáticos locais para o cliente no navegador.

```powershell
python -m pip install -r requirements.txt
python -m flask --app intervention_sample_planner.web_app run
```

Para deploy no Render, veja [docs/render_deploy_pt.md](docs/render_deploy_pt.md).

## Capturas de tela

As capturas de tela de release podem ser regeneradas no Windows com:

```powershell
python scripts\capture_screenshots.py
```

## Manual educacional

O manual educacional usa LuaLaTeX.

Compilar:

```powershell
cd D:\GitHub\InterventionSamplePlanner\docs\educational_manual
.\compile_manual.bat
```

Limpar arquivos auxiliares e manter o PDF:

```powershell
.\compile_manual.bat clean
```

Limpar todos os arquivos gerados e manter apenas os arquivos-fonte:

```powershell
.\compile_manual.bat clean-all
```
