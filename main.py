"""
main.py
=======
Script principal do Literature Review System.

Como usar:
    python main.py arquivo1.txt arquivo2.ris arquivo3.txt -o resultados.xlsx

Ou edite a lista de arquivos diretamente neste script e rode:
    python main.py
"""

import sys
import argparse
from pathlib import Path

from parsers import load_files
from enrichment import deduplicate, enrich_all, compute_stats, NUTS
from export import export_excel


def main():
    parser = argparse.ArgumentParser(
        description='Literature Review System — Unifica e analisa artigos científicos de múltiplas bases de dados.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py pubmed.txt scopus.ris sciencedirect.txt
  python main.py *.txt *.ris -o minha_revisao.xlsx

Formatos suportados:
  .txt  → PubMed (MEDLINE) ou ScienceDirect
  .ris  → CAPES Periódicos, Scopus, Web of Science
        """
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Arquivos exportados das bases de dados'
    )
    parser.add_argument(
        '-o', '--output',
        default='revisao_literatura.xlsx',
        help='Nome do arquivo Excel de saída (padrão: revisao_literatura.xlsx)'
    )

    args = parser.parse_args()

    # Se nenhum arquivo foi passado, mostra ajuda
    if not args.files:
        parser.print_help()
        print("\n⚠️  Nenhum arquivo informado.")
        print("   Exemplo: python main.py pubmed_export.txt capes_export.ris\n")
        sys.exit(1)

    # Verifica se os arquivos existem
    valid_files = []
    for f in args.files:
        p = Path(f)
        if p.exists():
            valid_files.append(str(p))
        else:
            print(f"⚠️  Arquivo não encontrado: {f}")

    if not valid_files:
        print("❌ Nenhum arquivo válido encontrado.")
        sys.exit(1)

    print("\n" + "="*55)
    print("  LITERATURE REVIEW SYSTEM")
    print("="*55)

    # 1. Carregar e parsear
    print("\n[1/4] Carregando arquivos...")
    all_articles = load_files(valid_files)
    print(f"      Total bruto: {len(all_articles)} artigos")

    # 2. Remover duplicatas
    print("\n[2/4] Removendo duplicatas...")
    unique = deduplicate(all_articles)

    # 3. Enriquecer
    print("\n[3/4] Analisando artigos (título + abstract)...")
    enriched = enrich_all(unique)

    # 4. Estatísticas
    print("\n[4/4] Calculando estatísticas...")
    stats = compute_stats(enriched)
    stats['with_abstract'] = sum(1 for a in enriched if a.get('abstract'))
    stats['with_doi'] = sum(1 for a in enriched if a.get('doi'))
    stats['nut_count'] = sum(1 for a in enriched if a.get('food') in NUTS)

    # Exportar
    export_excel(enriched, stats, args.output)

    # Resumo no terminal
    print("\n" + "="*55)
    print("  RESUMO")
    print("="*55)
    print(f"  Total de artigos únicos : {stats['total']}")
    print(f"  Com abstract            : {stats['with_abstract']}")
    print(f"  Sobre oleaginosas       : {stats['nut_count']}")
    print()
    print("  TOP 5 POLÍMEROS:")
    for poly, count in stats['polymers'][:5]:
        print(f"    {count:3}x  {poly}")
    print()
    print("  TOP 5 ANÁLISES:")
    for anal, count in stats['analyses'][:5]:
        print(f"    {count:3}x  {anal}")
    print("="*55)
    print(f"\n✅ Concluído! Arquivo salvo: {args.output}\n")


if __name__ == '__main__':
    main()
