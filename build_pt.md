<!-- File version: 2.0; date: 2026-05-11 -->

# Guia de Build

## Aplicativo Python

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m unittest discover -s tests
python run_app.py
```

## Executável para Windows

O executável é gerado com PyInstaller. Como o `ISP v2.0` agora depende de `intervention_sample_planner/explanations.json`, o comando de build precisa incluir esse arquivo.

Exemplo:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onefile --name InterventionSamplePlanner --add-data "intervention_sample_planner\explanations.json;intervention_sample_planner" run_app.py
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
