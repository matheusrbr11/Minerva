# 🏛️ Programa Minerva

> Sistema de automação contábil desenvolvido pela **Equipe de Otimização Processual (EOP/SUPCONC)** do **Tesouro do Estado do Rio de Janeiro**.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green?logo=selenium)](https://www.selenium.dev/)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-informational)](https://github.com/TomSchimansky/CustomTkinter)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?logo=sqlite)](https://www.sqlite.org/)
[![Versão](https://img.shields.io/badge/Versão-2.0-orange)](.)

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Como Usar](#-como-usar)
- [Banco de Dados](#-banco-de-dados)
- [Contribuição](#-contribuição)

---

## 📖 Sobre o Projeto

O **Programa Minerva** é uma ferramenta de automação desenvolvida para a **Coordenadoria de Controle e Conciliação Bancária (COOCCB)** da Superintendência de Contabilidade e Conciliação (SUPCONC), com o objetivo de automatizar a contabilização das **Guias de Recolhimento (GR)** e **Programação de Desembolso de Transferência (PD)** referentes às transferências federais recebidas pelo Estado do Rio de Janeiro.

O sistema elimina a necessidade de lançamentos manuais no **SIAFE-Rio2**, reduzindo erros operacionais e o tempo gasto em tarefas repetitivas, processando automaticamente as seguintes transferências federais:

- ANP  - Royalties pela Produção do Petróleo – Até 5% (Lei 7.990/89)
- ANP  - Royalties pela Produção do Petróleo – Excedente a 5% (Lei 9.478/97)
- PEA  - Participação Especial do Petróleo
- FEP  - Fundo Especial do Petróleo
- FPE  - Fundo de Participação dos Estados
- IPI  - Imposto sobre Produtos Industrializados Exportação
- CFM  - Compensação Financeira pela Exploração Mineral
- CFH  - Compensação Financeira pela Utilização de Recursos Hídricos
- CIDE - Contribuição de Intervenção no Domínio Econômico
- ADO  - LC 176/2020

---

## ✨ Funcionalidades

### 1. Processamento do DAF (Demonstrativo de Arrecadação Federal)
- Download automatizado do DAF via **Selenium** no portal do Banco do Brasil
- Parsing e limpeza do CSV exportado
- Cálculo automático de deduções constitucionais
- Armazenamento estruturado em banco de dados **SQLite** com controle de duplicidades

### 2. Contabilização Automática no SIAFE-Rio2
- Preenchimento automático de todos os campos necessários via automação no navegador
- Suporte a dois tipos de documento:
  - **GR** – Guia de Recolhimento (receitas orçamentárias)
  - **PD** – Programação de Desembolso (retenção de PASEP)
- Registro do número dos documentos contabilizados ao final do processo

### 3. Interface Gráfica (GUI)
- Tela de login com autenticação via CPF e senha do SIAFE-Rio2
- Menu principal com botões para **Processar DAF** e **Contabilizar**
- Seleção do tipo de contabilização (GR ou PD)
- Tela de execução com log em tempo real e barra de progresso
- Acesso rápido ao Manual de Uso (F2) e à tela "Sobre" (F1)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                     exe.py                          │
│            (ponto de entrada / atalho)              │
└─────────────────┬───────────────────────────────────┘
                  │ subprocess
                  ▼
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│         MinervaApp (CustomTkinter + Siafe)          │
│  ┌──────────────┐        ┌────────────────────────┐ │
│  │  GUI / Login │        │  Execução / Progresso  │ │
│  └──────┬───────┘        └────────────┬───────────┘ │
│         │                             │             │
│         ▼                             ▼             │
│  ┌──────────────┐        ┌────────────────────────┐ │
│  │    DAF.py    │        │      jupiter-subtes    │ │
│  │  (Selenium)  │        │   Automação SIAFE-Rio2 │ │
│  └──────┬───────┘        └────────────────────────┘ │
│         │                                           │
│         ▼                                           │
│  ┌──────────────┐                                   │
│  │  Extrato.py  │  ◄── ETL: CSV → SQLite            │
│  └──────┬───────┘                                   │
│         │                                           │
│         ▼                                           │
│  ┌──────────────┐                                   │
│  │    DAF.db    │  (SQLite)                         │
│  └──────────────┘                                   │
└─────────────────────────────────────────────────────┘
```

**Fluxo de dados:**

```
Portal BB → [DAF.py] → demonstrativoDAF.csv
                              │
                       [Extrato.py]
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
       tabela contabilizacoes           tabela daf
               │
            [main.py]
               │
          SIAFE-Rio2 (Edge)
```

---

## ⚙️ Pré-requisitos

- **Python** 3.10 ou superior
- **Microsoft Edge** instalado (WebDriver compatível com a versão do navegador)
- **Microsoft Edge WebDriver** no PATH do sistema
- Credenciais válidas no **SIAFE-Rio2**

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/minerva.git
cd minerva
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv env
# Windows
env\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

> **Dependências principais:**

| Pacote | Uso |
|---|---|
| `customtkinter` | Interface gráfica |
| `selenium` | Automação web (DAF + SIAFE) |
| `pandas` | Processamento e transformação do CSV |
| `numpy` | Operações numéricas auxiliares |
| `Pillow` | Carregamento de imagens na interface |
| `office365-rest-python-client` | Integração com SharePoint |
| `jupiter-subtes` | Biblioteca interna de automação do SIAFE-Rio2 |

### 4. Execute o programa

```bash
python exe.py
```

---

## 📁 Estrutura de Arquivos

```
minerva/
│
├── exe.py                  # Ponto de entrada (usado pelo atalho .exe)
├── main.py                 # Aplicação principal + GUI (MinervaApp)
├── DAF.py                  # Download automatizado do DAF via Selenium
├── Extrato.py              # ETL: parse do CSV e carga no SQLite
│
├── base de dados/
│   └── DAF.db              # Banco de dados SQLite
|
├── dist/
│   └── exe.exe             # atalho .exe
│
├── img/
│   ├── icon.ico            # Ícone do programa
|   ├── icon2.png           # Ícone do programa em PNG
|   ├── tesouro.png         # Logo do Tesouro RJ
│   └── voltar.png          # Ícone de voltar
│
├── Manual de Uso.pdf       # Manual do usuário
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🖥️ Como Usar

### Passo 1 – Login
Abra o programa pelo atalho ou via `exe.py`. Na tela de login, insira seu **CPF** (usuário) e **senha** do SIAFE-Rio2 e clique em **LOGIN**.

### Passo 2 – Processar DAF
Na tela principal, clique em **PROCESSAR DAF**. O programa irá:
1. Abrir o navegador Edge em modo headless
2. Acessar o portal de arrecadação federal do Banco do Brasil
3. Preencher automaticamente o estado (Rio de Janeiro) e o período do mês corrente
4. Baixar o arquivo `demonstrativoDAF.csv` para a pasta Downloads
5. Processar o CSV, calcular retenções de PASEP e carregar os dados no banco de dados

> ⚠️ Esta etapa **não realiza contabilizações** no SIAFE. Ela apenas prepara os dados.

### Passo 3 – Contabilizar
Selecione o tipo de contabilização no menu suspenso:
- **GR** – Para registrar as receitas (Guias de Recolhimento)
- **PD** – Para registrar as transferências de PASEP (Programação de Desembolso)

Clique em **CONTABILIZAR**. O programa abrirá o SIAFE-Rio2 e preencherá automaticamente todos os campos para cada lançamento. Ao final, o número dos documentos contabilizados será exibido no log.

---

## 🗄️ Banco de Dados

O arquivo `base de dados/DAF.db` contém duas tabelas principais:

### Tabela `contabilizacoes`
Armazena os lançamentos a serem (ou já) contabilizados no SIAFE.

| Coluna | Tipo | Descrição |
|---|---|---|
| `data` | TEXT | Data do lançamento (DD/MM/AAAA) |
| `valor` | TEXT | Valor monetário do lançamento |
| `observacao` | TEXT | Descrição gerada automaticamente |
| `num_documento` | TEXT | Número do documento no SIAFE (preenchido após contabilização) |
| `tipo_id` | INTEGER | Identificador do tipo de transferência (1–20) |
| `usuario` | TEXT | Login do usuário que processou |
| `data_hora` | TEXT | Timestamp do processamento |
| `tempo_contab` | TEXT | Tempo de execução da contabilização |

### Tabela `daf`
Armazena os dados brutos extraídos do CSV do DAF.

| Coluna | Tipo | Descrição |
|---|---|---|
| `fundo` | TEXT | Nome do fundo |
| `data` | TEXT | Data do repasse |
| `parcela` | TEXT | Tipo de parcela (ex: ANP-LEI 7990/89) |
| `valor` | REAL | Valor da parcela |
| `tipo` | TEXT | Tipo do lançamento (crédito/débito) |

---

## 🤝 Contribuição

Este projeto é desenvolvido e mantido pela **Equipe de Otimização Processual (EOP)** da **SUPCONC – Tesouro do Estado do Rio de Janeiro**.

Dúvidas, sugestões e reportes de inconsistências operacionais devem ser encaminhados diretamente à equipe. Em caso de mudanças nas premissas operacionais (estrutura do DAF, roteiros contábeis, contas, etc.), a equipe deve ser notificada para atualização do sistema e do manual de uso.

O manual de uso está arquivado no **SEI-RJ** sob o processo `SEI-040009/000183/2026`, denominado *"Manual de Uso Nº 02/2026"*.

---

<div align="center">
  <sub>EOP / SUPCONC – Tesouro do Estado do Rio de Janeiro &nbsp;|&nbsp; Versão 2.0 &nbsp;|&nbsp; 09/04/2026</sub>
</div>