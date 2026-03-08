# 📚 Literature Review System

Sistema em Python para **unificar, limpar e analisar artigos científicos** exportados de múltiplas bases de dados indexadas.

Desenvolvido para automatizar o processo de revisão sistemática de literatura em food science, mas adaptável para qualquer área.

---

## ✨ O que o sistema faz

- **Lê arquivos** exportados do PubMed, CAPES Periódicos, ScienceDirect, Scopus e Web of Science
- **Remove duplicatas** automaticamente comparando DOI e título
- **Extrai informações** do título e abstract de cada artigo:
  - Alimento testado (castanha, fruta, carne etc.)
  - Tipo de estudo (revisão, experimental, in vitro etc.)
  - Polímeros/revestimentos utilizados (quitosana, CMC, alginato etc.)
  - Análises realizadas (PV, TBARS, antimicrobiano etc.)
- **Gera um Excel** com duas abas:
  - **Artigos** — tabela completa com todos os dados e links DOI clicáveis
  - **Análises** — dashboard com rankings de autores, polímeros, análises e mais

---

## 🗂️ Estrutura do projeto

```
literature-review-system/
│
├── main.py           # Script principal — ponto de entrada
├── parsers.py        # Leitura de arquivos (PubMed, RIS, ScienceDirect)
├── enrichment.py     # Deduplicação, detecção e estatísticas
├── export.py         # Geração do arquivo Excel
├── requirements.txt  # Dependências
└── README.md         # Este arquivo
```

---

## 🚀 Como usar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Exportar artigos das bases de dados

| Base | Como exportar | Formato |
|---|---|---|
| **PubMed** | Save → Format: PubMed | .txt |
| **CAPES Periódicos** | Exportar → RIS | .ris |
| **ScienceDirect** | Export → Citation text | .txt |
| **Scopus** | Export → RIS | .ris |
| **Web of Science** | Export → Plain Text | .txt |

### 3. Rodar o sistema

```bash
python main.py arquivo1.txt arquivo2.ris arquivo3.txt
```

Por padrão, gera `revisao_literatura.xlsx`. Para escolher o nome:

```bash
python main.py *.txt *.ris -o minha_revisao.xlsx
```

---

## 📊 Exemplo de saída

```
========================================
  LITERATURE REVIEW SYSTEM
========================================

[1/4] Carregando arquivos...
      [PubMed] pubmed_export.txt: 931 artigos
      [RIS] capes_export.ris: 30 artigos
      [ScienceDirect] sd_export.txt: 100 artigos
      Total bruto: 1061 artigos

[2/4] Removendo duplicatas...
      Duplicatas removidas: 88 | Artigos únicos: 973

[3/4] Analisando artigos (título + abstract)...
[4/4] Calculando estatísticas...

✓ Arquivo salvo em: revisao_literatura.xlsx

========================================
  RESUMO
========================================
  Total de artigos únicos : 973
  Com abstract            : 970
  Sobre oleaginosas       : 112

  TOP 5 POLÍMEROS:
    236x  Quitosana
    111x  Amido
    101x  Pectina
     97x  Alginato
     60x  CMC (Carboximetilcelulose)

  TOP 5 ANÁLISES:
    315x  Antimicrobiano
    280x  Antioxidante
    210x  Shelf Life
    180x  Umidade
    150x  Cor
========================================
```

---

## ⚙️ Personalização

### Adicionar novos polímeros

Em `enrichment.py`, adicione uma entrada na lista `POLYMER_MAP`:

```python
(['nome_do_polimero', 'variante_abreviada'], 'Nome Canônico'),
```

### Adicionar novos alimentos

Em `enrichment.py`, adicione no dicionário `FOOD_KEYWORDS`:

```python
'keyword_em_ingles': 'Nome em Português',
```

### Adicionar novas análises

Em `enrichment.py`, adicione no dicionário `ANALYSIS_KEYWORDS`:

```python
'keyword_em_ingles': 'Nome da Análise',
```

---

## 📋 Requisitos

- Python 3.8+
- openpyxl >= 3.1.0

---

## 👤 Autor

Desenvolvido como ferramenta de apoio à revisão sistemática de literatura científica em food science.

---

## 📄 Licença

MIT License — livre para usar, modificar e distribuir.
