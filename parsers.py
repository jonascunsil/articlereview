"""
parsers.py
==========
Funções para ler arquivos exportados de diferentes bases de dados científicas.

Bases suportadas:
- PubMed (.txt formato MEDLINE)
- CAPES Periódicos (.ris)
- ScienceDirect (.txt formato exportação)
"""

import re


def parse_pubmed(text):
    """
    Lê arquivo exportado do PubMed no formato MEDLINE (.txt).
    Retorna lista de dicionários com os campos do artigo.
    """
    records = re.split(r'\n(?=PMID-)', text.strip())
    articles = []

    for record in records:
        data = {}
        current_field = None
        current_value = []
        authors = []

        for line in record.split('\n'):
            if len(line) > 4 and line[4] == '-':
                if current_field:
                    val = ' '.join(current_value).strip()
                    if current_field == 'AU':
                        authors.append(val)
                    else:
                        data[current_field] = val
                current_field = line[:4].strip()
                current_value = [line[6:].strip()]
            elif line.startswith('      ') and current_field:
                current_value.append(line.strip())

        if current_field:
            val = ' '.join(current_value).strip()
            if current_field == 'AU':
                authors.append(val)
            else:
                data[current_field] = val

        # Extrai DOI
        doi = ''
        for field in ['LID', 'AID']:
            m = re.search(r'(10\.\S+)\s*\[doi\]', data.get(field, ''))
            if m:
                doi = m.group(1)
                break

        year_m = re.search(r'\d{4}', data.get('DP', ''))

        articles.append({
            'title': data.get('TI', ''),
            'authors': authors,
            'year': year_m.group(0) if year_m else '',
            'journal': data.get('TA', ''),
            'doi': doi,
            'abstract': data.get('AB', ''),
            'source': 'PubMed'
        })

    return articles


def parse_ris(text):
    """
    Lê arquivo exportado no formato RIS (.ris).
    Compatível com CAPES Periódicos, Scopus e Web of Science.
    """
    records = [r.strip() for r in re.split(r'\nER\s*-', text) if r.strip()]
    articles = []

    for record in records:
        data = {}
        for line in record.split('\n'):
            m = re.match(r'^([A-Z]{2})\s*-\s*(.+)', line)
            if m:
                tag, val = m.group(1), m.group(2).strip()
                if tag in data:
                    data[tag] += '; ' + val
                else:
                    data[tag] = val

        authors = [a.strip() for a in data.get('AU', '').split(';') if a.strip()]

        articles.append({
            'title': data.get('TI', ''),
            'authors': authors,
            'year': data.get('PY', '')[:4] if data.get('PY') else '',
            'journal': data.get('JO', '') or data.get('T2', ''),
            'doi': data.get('DO', ''),
            'abstract': data.get('AB', ''),
            'source': 'CAPES/RIS'
        })

    return articles


def parse_sciencedirect(text):
    """
    Lê arquivo exportado do ScienceDirect (.txt).
    Cada registro é separado por linha em branco.
    """
    records = [r.strip() for r in text.split('\n\n') if r.strip() and len(r.strip()) > 50]
    articles = []

    for record in records:
        lines = [l for l in record.split('\n') if l.strip()]
        if len(lines) < 2:
            continue

        authors = [a.strip().rstrip(',') for a in lines[0].rstrip(',').split(',') if a.strip()]
        title = lines[1].rstrip(',') if len(lines) > 1 else ''
        journal = lines[2].rstrip(',') if len(lines) > 2 else ''

        year_m = re.search(r'\b(20\d{2}|19\d{2})\b', record)
        doi_m = re.search(r'https://doi\.org/(10\.[^\s\.\)]+)', record)
        ab_m = re.search(r'Abstract:\s*(.+?)(?=\nKeywords:|$)', record, re.DOTALL)

        if title:
            articles.append({
                'title': title,
                'authors': authors,
                'year': year_m.group(0) if year_m else '',
                'journal': journal,
                'doi': doi_m.group(1) if doi_m else '',
                'abstract': ab_m.group(1).strip().replace('\n', ' ') if ab_m else '',
                'source': 'ScienceDirect'
            })

    return articles


def load_files(file_paths):
    """
    Carrega e parseia múltiplos arquivos automaticamente,
    detectando o formato pelo conteúdo.

    Parâmetros:
        file_paths (list): Lista de caminhos para os arquivos

    Retorna:
        list: Lista de artigos de todos os arquivos
    """
    all_articles = []

    for path in file_paths:
        with open(path, encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Detecta formato automaticamente
        if content.strip().startswith('PMID-') or '\nPMID-' in content:
            articles = parse_pubmed(content)
            print(f"[PubMed] {path}: {len(articles)} artigos")
        elif re.search(r'^TY\s*-', content, re.MULTILINE):
            articles = parse_ris(content)
            print(f"[RIS] {path}: {len(articles)} artigos")
        else:
            articles = parse_sciencedirect(content)
            print(f"[ScienceDirect] {path}: {len(articles)} artigos")

        all_articles += articles

    return all_articles
