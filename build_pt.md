# Guia de Build

<!-- File version: 1.0; date: 2026-05-11 -->

Este guia explica como gerar versões executáveis do Planejador de Amostra para Intervenções para Windows, Linux e macOS.

Política de documentação: `build.md` é o original canônico em inglês. Este arquivo é sua tradução em português.

O app é uma aplicação Python/Tkinter normal. A ferramenta recomendada para empacotamento é o PyInstaller.

## Regra Importante

Gere o build no sistema operacional de destino.

- Gere `.exe` de Windows no Windows.
- Gere executável Linux no Linux.
- Gere app ou executável macOS no macOS.

O PyInstaller não é um cross-compiler confiável.

## Requisitos

- Python 3.10 ou mais novo.
- Tkinter disponível nessa instalação do Python.
- PyInstaller para gerar executáveis.

Verifique o Tkinter:

```powershell
python -c "import tkinter; print('tkinter ok')"
```

Instale a dependência de build:

```powershell
python -m pip install -r requirements-build.txt
```

ou:

```powershell
python -m pip install pyinstaller
```

## Build no Windows

A partir da raiz do repositório:

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m PyInstaller --noconfirm --clean --windowed --name InterventionSamplePlanner run_app.py
```

Saída:

```text
dist\InterventionSamplePlanner\InterventionSamplePlanner.exe
```

Para gerar um único arquivo `.exe`:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onefile --name InterventionSamplePlanner run_app.py
```

Saída:

```text
dist\InterventionSamplePlanner.exe
```

O build em pasta inicia mais rápido e é mais fácil de depurar. O build em arquivo único é mais fácil de distribuir.

## Build no Linux

Instale Python com Tkinter. Em sistemas Debian/Ubuntu, isso pode exigir:

```bash
sudo apt install python3-tk
```

Depois:

```bash
python3 -m pip install -r requirements-build.txt
python3 -m PyInstaller --noconfirm --clean --windowed --name InterventionSamplePlanner run_app.py
```

Saída:

```text
dist/InterventionSamplePlanner/InterventionSamplePlanner
```

Se o ambiente Linux não tiver display gráfico, use `--console` para diagnóstico.

## Build no macOS

Use uma instalação de Python com suporte a Tkinter. Depois:

```bash
python3 -m pip install -r requirements-build.txt
python3 -m PyInstaller --noconfirm --clean --windowed --name InterventionSamplePlanner run_app.py
```

A saída normalmente é:

```text
dist/InterventionSamplePlanner.app
```

Para uso local, apps não assinados podem precisar ser abertos pelo Finder com Control-click > Open. Para distribuição pública, use o fluxo de assinatura e notarização da Apple.

## Scripts de Build

Auxiliar para Windows:

```powershell
.\scripts\build_windows.ps1
```

Auxiliar para Windows em arquivo único:

```powershell
.\scripts\build_windows.ps1 -OneFile
```

Auxiliar para Linux/macOS:

```bash
./scripts/build_unix.sh
```

Auxiliar para Linux/macOS em arquivo único:

```bash
./scripts/build_unix.sh --onefile
```

## Teste Rápido Depois do Build

Depois de gerar o executável, abra o app e teste:

1. Carregue `examples/from_sources/statsiq_teaching_method_d05.json`.
2. Clique em **Calculate** ou **Calcular**.
3. Confirme que o resumo mostra `63` controle e `63` intervenção como alvo inicial válido.
4. Abra a aba Sensibilidade e confirme que ela aparece como tabela.
5. Carregue `examples/from_sources/methodology_two_proportions_completion_45_60.json`.
6. Confirme que o alvo inicial válido é `173 + 173 = 346`.

## Solução de Problemas

### PyInstaller não está instalado

Execute:

```powershell
python -m pip install -r requirements-build.txt
```

### Tkinter não está instalado

Use uma distribuição Python que inclua Tkinter. No Linux, instale o pacote do sistema, como `python3-tk`.

### O app abre com janela de console no Windows

Use `--windowed` ou o script de build do Windows incluído.

### O antivírus avisa sobre o executável

Apps PyInstaller não assinados podem gerar alertas. Para distribuição fora da sua máquina, assine o executável e distribua por um canal confiável.

### O executável em arquivo único inicia devagar

Isso é normal. Builds PyInstaller em arquivo único descompactam em uma pasta temporária antes de iniciar. Use o build em pasta quando velocidade for mais importante.

## Notas do Repositório

Arquivos gerados em `build/`, `dist/` e `.spec` são ignorados pelo Git. As saídas de build podem existir localmente sem serem commitadas.
