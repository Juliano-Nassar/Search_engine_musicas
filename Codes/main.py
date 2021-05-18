from Modules.indexer import load_index
from Modules.cleaner import Cleaner
from Modules.query import Query_master

import pandas as pd

query_master = Query_master()

print("="*80)
print("LOADING INDEX")

INDEX_PATH = '../Data/index/index.json'
index = load_index(INDEX_PATH)

print("LOADING DONE")

print("="*80)

print("LOADING MUSICS FILE")

MUSICS_PARSED_PATH = '../Data/music_info/musics_parsed.csv'
musics_parsed = pd.read_csv(MUSICS_PARSED_PATH)

print("LOADING DONE")

print("="*80)
print('Querys operations: NEAR, OR, NOT')
print('')
print('Palavras e termos adjacentes são consideradas como AND')
print('')
print('Prioridades: Parenteses, NOT, NEAR, OR, AND')
print('Exemplo de query:')
print('((mulher OR homem) (alto OR baixa)) NEAR bonito medico')
print("="*80)

query = input('Inserir query de pesquisa: ')

print("="*80)
print("PESQUISANDO")

result = query_master.search(query,index,musics_parsed)
print("="*80)
print("PESQUISA COMPLETA, ARQUIVOS SALVOS EM resultado_da_pesquisa.xlsx")
