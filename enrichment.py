"""
enrichment.py
=============
Funções para:
- Remover duplicatas entre bases de dados
- Detectar alimento testado, tipo de estudo, polímeros e análises
  a partir do título e abstract dos artigos
"""

import re
from collections import Counter


# ── DEDUPLICAÇÃO ──────────────────────────────────────────────────────────────

def deduplicate(articles):
    """
    Remove artigos duplicados comparando DOI (primeiro) ou título (fallback).
    Quando encontra duplicata, merge as fontes e mantém o abstract mais completo.

    Parâmetros:
        articles (list): Lista de artigos (dicionários)

    Retorna:
        list: Lista de artigos únicos
    """
    seen = {}
    unique = []

    for art in articles:
        doi = art['doi'].strip().lower().rstrip('.')
        title_key = re.sub(r'[^a-z0-9]', '', art['title'].lower())[:50]
        key = doi if doi else title_key

        if not key:
            unique.append(art)
            continue

        if key in seen:
            existing = seen[key]
            # Merge fontes
            sources = set(existing['source'].split(' + '))
            sources.add(art['source'])
            existing['source'] = ' + '.join(sorted(sources))
            # Mantém abstract mais completo
            if not existing['abstract'] and art['abstract']:
                existing['abstract'] = art['abstract']
            # Mantém lista de autores maior
            if isinstance(art['authors'], list) and len(art['authors']) > len(existing.get('authors', [])):
                existing['authors'] = art['authors']
        else:
            seen[key] = art
            unique.append(art)

    removed = len(articles) - len(unique)
    print(f"Duplicatas removidas: {removed} | Artigos únicos: {len(unique)}")
    return unique


# ── DETECÇÃO DE ALIMENTO ──────────────────────────────────────────────────────

FOOD_KEYWORDS = {
    # Oleaginosas (prioridade)
    'brazil nut': 'Castanha do Pará',
    'pine nut': 'Pinhão',
    'cashew': 'Castanha de Caju',
    'pistachio': 'Pistache',
    'walnut': 'Noz',
    'almond': 'Amêndoa',
    'hazelnut': 'Avelã',
    'peanut': 'Amendoim',
    'pecan': 'Pecã',
    'macadamia': 'Macadâmia',
    'nut': 'Oleaginosa (geral)',
    # Frutas
    'strawberry': 'Morango',
    'apple': 'Maçã',
    'mango': 'Manga',
    'banana': 'Banana',
    'avocado': 'Abacate',
    'grape': 'Uva',
    'tomato': 'Tomate',
    'blueberry': 'Mirtilo',
    'cherry': 'Cereja',
    'peach': 'Pêssego',
    'pear': 'Pera',
    'plum': 'Ameixa',
    'citrus': 'Cítrico',
    'orange': 'Laranja',
    'lemon': 'Limão',
    'papaya': 'Mamão',
    'guava': 'Goiaba',
    'kiwi': 'Kiwi',
    'melon': 'Melão',
    'pomegranate': 'Romã',
    'pineapple': 'Abacaxi',
    'passion fruit': 'Maracujá',
    'dragon fruit': 'Pitaya',
    'fresh-cut': 'Minimamente Processado',
    # Carnes e proteínas
    'fish': 'Peixe',
    'shrimp': 'Camarão',
    'salmon': 'Salmão',
    'beef': 'Carne Bovina',
    'chicken': 'Frango',
    'meat': 'Carne (geral)',
    # Outros
    'cheese': 'Queijo',
    'egg': 'Ovo',
    'bread': 'Pão',
    # Genéricos
    'review': 'Revisão',
    'fruit': 'Fruta (geral)',
    'vegetable': 'Vegetal (geral)',
}

NUTS = {
    'Castanha do Pará', 'Castanha de Caju', 'Pistache', 'Noz',
    'Amêndoa', 'Avelã', 'Amendoim', 'Pecã', 'Macadâmia', 'Pinhão',
    'Oleaginosa (geral)'
}

def detect_food(title):
    """Detecta o alimento testado a partir do título do artigo."""
    t = title.lower()
    # Multi-palavra primeiro (mais específico)
    for kw in ['brazil nut', 'pine nut', 'passion fruit', 'dragon fruit', 'fresh-cut']:
        if kw in t:
            return FOOD_KEYWORDS.get(kw, kw)
    # Palavra única
    for kw, food in FOOD_KEYWORDS.items():
        if kw in t:
            return food
    return 'Não identificado'


# ── DETECÇÃO DE TIPO DE ESTUDO ────────────────────────────────────────────────

def detect_study_type(title, abstract):
    """Classifica o tipo de estudo com base no título e abstract."""
    t = (title + ' ' + abstract).lower()
    if any(w in t for w in ['review', 'meta-analysis', 'systematic review', 'overview']):
        return 'Revisão'
    if any(w in t for w in ['in vitro', 'cell line', 'cytotoxic', 'mic ', 'mbc ']):
        return 'In vitro'
    if any(w in t for w in ['in vivo', 'animal model', 'rat ', 'mice ', 'mouse ']):
        return 'In vivo'
    if any(w in t for w in ['clinical', 'human trial', 'randomized', 'volunteer']):
        return 'Clínico'
    if any(w in t for w in ['sensory', 'consumer', 'panel', 'organoleptic']):
        return 'Experimental + Sensorial'
    if any(w in t for w in ['storage', 'shelf life', 'postharvest', 'post-harvest']):
        return 'Experimental (armazenamento)'
    if any(w in t for w in ['molecular docking', 'simulation', 'computational']):
        return 'Computacional'
    return 'Experimental'


# ── DETECÇÃO DE POLÍMEROS ─────────────────────────────────────────────────────

# Lista ordenada do mais específico para o mais genérico
# (a ordem garante que CMC não seja contado como "celulose genérica")
POLYMER_MAP = [
    (['carboxymethyl cellulose', 'carboxymethylcellulose', r'\bcmc\b'],
     'CMC (Carboximetilcelulose)'),
    (['hydroxypropyl methylcellulose', 'hydroxypropyl methyl cellulose', r'\bhpmc\b'],
     'HPMC (Hidroxipropilmetilcelulose)'),
    (['methylcellulose', r'\bmethyl cellulose\b'],
     'Metilcelulose'),
    (['cellulose nanofiber', 'cellulose nanocrystal', 'nanocellulose',
      'bacterial cellulose', 'microcrystalline cellulose'],
     'Nanocelulose'),
    (['sodium alginate', 'calcium alginate', 'alginate'],
     'Alginato'),
    (['whey protein isolate', 'whey protein concentrate', 'whey protein', r'\bwhey\b'],
     'Proteína de Soro (Whey)'),
    (['soy protein isolate', 'soy protein'],
     'Proteína de Soja'),
    (['corn starch'],           'Amido de Milho'),
    (['cassava starch', 'tapioca starch'], 'Amido de Mandioca'),
    (['rice starch'],           'Amido de Arroz'),
    (['potato starch'],         'Amido de Batata'),
    (['pea starch'],            'Amido de Ervilha'),
    (['wheat starch'],          'Amido de Trigo'),
    (['starch'],                'Amido'),
    (['carnauba wax'],          'Cera de Carnaúba'),
    (['candelilla wax'],        'Cera Candelilla'),
    (['beeswax'],               'Cera de Abelha'),
    (['shellac'],               'Shellac'),
    (['wax'],                   'Cera'),
    (['gum arabic'],            'Goma Arábica'),
    (['locust bean gum'],       'Goma Locusta'),
    (['guar gum'],              'Goma Guar'),
    (['xanthan gum', 'xanthan'], 'Goma Xantana'),
    (['chitosan'],              'Quitosana'),
    (['chitin'],                'Quitina'),
    (['pectin'],                'Pectina'),
    (['gelatin'],               'Gelatina'),
    (['collagen'],              'Colágeno'),
    (['casein', 'caseinate'],   'Caseína'),
    (['zein'],                  'Zeína'),
    (['gluten'],                'Glúten'),
    (['pullulan'],              'Pululana'),
    (['carrageenan'],           'Carragena'),
    (['agar'],                  'Ágar'),
    (['maltodextrin'],          'Maltodextrina'),
    (['konjac'],                'Konjac'),
    (['mucilage'],              'Mucilagem'),
]

CEL_DERIVATIVES = [
    'CMC (Carboximetilcelulose)',
    'HPMC (Hidroxipropilmetilcelulose)',
    'Metilcelulose',
    'Nanocelulose',
]

def detect_polymers(title, abstract):
    """
    Detecta polímeros/revestimentos citados no título e abstract.
    Busca sempre do mais específico para o mais genérico para evitar
    contar CMC como "celulose genérica".
    """
    text = (title + ' ' + abstract).lower()
    found = []
    matched_positions = set()

    for aliases, canonical in POLYMER_MAP:
        for alias in aliases:
            for match in re.finditer(alias, text):
                s, e = match.start(), match.end()
                overlap = any(p in range(s, e) for p in matched_positions)
                if not overlap:
                    if canonical not in found:
                        found.append(canonical)
                    matched_positions.update(range(s, e))
                    break

    # Celulose genérica só se nenhum derivado específico foi encontrado
    if 'cellulose' in text and not any(d in found for d in CEL_DERIVATIVES):
        found.append('Celulose (geral)')

    return found


# ── DETECÇÃO DE ANÁLISES ──────────────────────────────────────────────────────

ANALYSIS_KEYWORDS = {
    # Multi-palavra (buscar primeiro)
    'peroxide value':   'Valor de Peróxidos (PV)',
    'acid value':       'Valor de Acidez (AV)',
    'fatty acid':       'Ácidos Graxos',
    'water activity':   'Atividade de Água',
    'scanning electron':'MEV (Microscopia Eletrônica)',
    'gc-ms':            'GC-MS',
    'zeta potential':   'Potencial Zeta',
    'particle size':    'Tamanho de Partícula',
    'water vapor':      'Permeabilidade ao Vapor (WVP)',
    'tensile strength': 'Resistência à Tração',
    'shelf life':       'Shelf Life',
    'lipid oxidation':  'Oxidação Lipídica',
    'thiobarbituric':   'TBARS',
    # Palavra única
    'peroxide':         'PV',
    'tbars':            'TBARS',
    'oxidation':        'Oxidação Lipídica',
    'moisture':         'Umidade',
    'antifungal':       'Antifúngico',
    'antimicrobial':    'Antimicrobiano',
    'antibacterial':    'Antibacteriano',
    'antioxidant':      'Antioxidante',
    'color':            'Cor',
    'colour':           'Cor',
    'texture':          'Textura',
    'hardness':         'Dureza',
    'sensory':          'Sensorial',
    'aflatoxin':        'Aflatoxina',
    'ftir':             'FTIR',
    'hplc':             'HPLC',
    'viscosity':        'Viscosidade',
}

def detect_analyses(title, abstract):
    """Detecta análises/experimentos realizados a partir do título e abstract."""
    text = (title + ' ' + abstract).lower()
    found = []

    # Multi-palavra primeiro
    multi = ['peroxide value', 'acid value', 'fatty acid', 'water activity',
             'scanning electron', 'gc-ms', 'zeta potential', 'particle size',
             'water vapor', 'tensile strength', 'shelf life', 'lipid oxidation',
             'thiobarbituric']
    for kw in multi:
        label = ANALYSIS_KEYWORDS.get(kw)
        if kw in text and label and label not in found:
            found.append(label)

    # Palavra única
    for kw, label in ANALYSIS_KEYWORDS.items():
        if len(kw.split()) == 1 and kw in text and label not in found:
            found.append(label)

    return found


# ── ENRIQUECER TODOS OS ARTIGOS ───────────────────────────────────────────────

def enrich_all(articles):
    """
    Aplica todas as detecções em cada artigo.
    Adiciona os campos: food, study_type, polymers, analyses.
    """
    for art in articles:
        art['food'] = detect_food(art['title'])
        art['study_type'] = detect_study_type(art['title'], art['abstract'])
        art['polymers'] = detect_polymers(art['title'], art['abstract'])
        art['analyses'] = detect_analyses(art['title'], art['abstract'])
    return articles


# ── ESTATÍSTICAS ──────────────────────────────────────────────────────────────

def compute_stats(articles):
    """
    Calcula as principais estatísticas do corpus de artigos.
    Retorna dicionário com os rankings de cada categoria.
    """
    from itertools import chain

    total = len(articles)

    all_authors = list(chain.from_iterable(
        a['authors'] if isinstance(a['authors'], list) else [a['authors']]
        for a in articles
    ))

    stats = {
        'total': total,
        'authors': Counter(all_authors).most_common(10),
        'foods': Counter(a['food'] for a in articles if a['food'] in NUTS).most_common(15),
        'analyses': Counter(chain.from_iterable(a['analyses'] for a in articles)).most_common(10),
        'polymers': Counter(chain.from_iterable(a['polymers'] for a in articles)).most_common(10),
        'study_types': Counter(a['study_type'] for a in articles).most_common(),
        'years': Counter(a['year'] for a in articles if a.get('year', '') >= '2010').most_common(15),
        'sources': Counter(a['source'] for a in articles).most_common(),
    }

    return stats
