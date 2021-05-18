from collections import defaultdict
import re
from Modules.cleaner import Cleaner
from nltk.tokenize import TweetTokenizer
import numpy as np
import pandas as pd

class Query_master():
    def __init__(self):
        self.tokenizer = TweetTokenizer(strip_handles=False,reduce_len=False)
        self.cleaner = Cleaner()
        
    def easy_string(self,string):
        pattern = r'(\(|\))'
        return re.sub(pattern,r' \1 ',string)


    def get_dict_and_index_query(self,x,index):
        if type(x) == str:
            if x in index.keys():
                index_dict = index[x]
                index_query = set(index_dict)
                full_dict_querry = index_dict
            else:
                full_dict_querry = {}
                index_query = set([])
            return full_dict_querry, index_query
        else:
            index_query = set(x)
            return x, index_query


    def AND_query(self,index,query):

        dict_querry,index_query = self.get_dict_and_index_query(query[0],index)
        full_dict_querry = [dict_querry]


        for query_term in query[1:]:
            dict_querry,term_index_query = self.get_dict_and_index_query(query_term,index)
            index_query &= term_index_query
            full_dict_querry.append(dict_querry)

        dict_out = defaultdict(list)
        for doc in index_query:
            for current_dict in full_dict_querry:
                if doc in current_dict.keys():
                    dict_out[doc]+=current_dict[doc]

        return dict_out



    def OR_query(self,index,query):

        dict_querry,index_query = self.get_dict_and_index_query(query[0],index)
        full_dict_querry = [dict_querry]


        for query_term in query[1:]:
            dict_querry,term_index_query = self.get_dict_and_index_query(query_term,index)
            index_query |= term_index_query
            full_dict_querry.append(dict_querry)

        dict_out = defaultdict(list)
        for doc in index_query:
            for current_dict in full_dict_querry:
                if doc in current_dict.keys():
                    dict_out[doc]+=current_dict[doc]

        return dict_out

    def NOT_query(self,index,term):

        dict_querry,index_query = self.get_dict_and_index_query(term,index)

        okk = set()
        for i in index.values():
            okk |= set(i)

        index_query = okk-index_query

        dict_out = defaultdict(list)
        for doc in index_query:
            dict_out[doc] = []

        return dict_out

    def NEAR_query(self,index,query):

        dict_querry_1,index_query_1 = self.get_dict_and_index_query(query[0],index)
        dict_querry_2,index_query_2 = self.get_dict_and_index_query(query[1],index)

        index_query_1 &= index_query_2

        dict_out = defaultdict(list)

        for doc in index_query_1:
            vals_2 = dict_querry_2[doc]
            vals_1 = dict_querry_1[doc]
            for val_1 in vals_1:
                if (val_1+1 in vals_2) or (val_1-1 in vals_2):
                    dict_out[doc]= vals_1 + vals_2
                    break

        return dict_out

    def solve_query(self,index,query):
        query_tokens = query.copy()
        while 'NOT' in query_tokens:
            NOT_index = query_tokens.index('NOT')
            token = query_tokens[NOT_index+1]
            if type(token) == str:
                token = self.cleaner.clean_and_tokenize(token)
                if len(token) >1:
                    token = self.AND_query(index,token)
                elif len(token) ==0:
                    del query_tokens[NOT_index:NOT_index+2]
                    pass

            parsed_token = self.NOT_query(index,token)

            del query_tokens[NOT_index:NOT_index+2]

            query_tokens.insert(NOT_index,parsed_token)

        while 'NEAR' in query_tokens:
            NEAR_index = query_tokens.index('NEAR')

            token_1 = query_tokens[NEAR_index+1]
            token_2 = query_tokens[NEAR_index-1]

            if type(token_1) == str:
                    token_1 = self.cleaner.clean_and_tokenize(token_1)
                    if len(token_1)>1:
                        token_1 = self.AND_query(index,token_1)
                    else:
                        token_1 = token_1[0]

            if type(token_2) == str:
                    token_2 = self.cleaner.clean_and_tokenize(token_2)
                    if len(token_2)>1:
                        token_2 = self.AND_query(index,token_2)
                    else:
                        token_2 = token_2[0]

            token = [token_1,token_2]

            parsed_token = self.NEAR_query(index,token)

            del query_tokens[NEAR_index-1:NEAR_index+2]

            query_tokens.insert(NEAR_index-1,parsed_token)

        while 'OR' in query_tokens:
            OR_index = query_tokens.index('OR')

            token_1 = query_tokens[OR_index+1]
            token_2 = query_tokens[OR_index-1]

            if type(token_1) == str:
                    token_1 = self.cleaner.clean_and_tokenize(token_1)
                    if len(token_1)>1:
                        token_1 = self.AND_query(index,token_1)
                    else:
                        token_1 = token_1[0]

            if type(token_2) == str:
                    token_2 = self.cleaner.clean_and_tokenize(token_2)
                    if len(token_2)>1:
                        token_2 = self.AND_query(index,token_2)
                    else:
                        token_2 = token_2[0]

            token = [token_1,token_2]

            parsed_token = self.OR_query(index,token)

            del query_tokens[OR_index-1:OR_index+2]

            query_tokens.insert(OR_index-1,parsed_token)

        if len(query_tokens)>1:
            final_query = []

            for token in query_tokens:
                if type(token) == str:
                    final_query += self.cleaner.clean_and_tokenize(token)
                else:
                    final_query.append(token)

            query_tokens = self.AND_query(index,final_query)

        if type(query_tokens) == list:
            query_tokens = query_tokens[0]

        return query_tokens

    def parse_query(self,index,query):
        query = self.easy_string(query)
        query = self.tokenizer.tokenize(query)

        lista = query.copy()
        aux = 0
        pos_i = 0

        while True:
            char = lista[aux]
            if char == '(':
                pos_i = aux
            if char == ')':
                result = self.solve_query(index,lista[pos_i+1:aux])
                del lista[pos_i:aux+1]
                lista.insert(pos_i,result)

                aux = 0
            aux+=1
            if aux== len(lista):
                break

        if len(lista)>1:
            lista = self.solve_query(index,lista)
        return lista
    
    def clean_querys_functions(self,query):
        patt = r'\(|\)|OR|NOT|NEAR'
        query = re.sub(patt,' ',query).strip()
        query = re.sub('  +',' ',query).strip()
        query = self.cleaner.clean_and_tokenize(query)
        return query

    def tf_idf(self,fij,ni,N):
        return np.log2(1+fij)*np.log2(N/ni)
    
    def Ranking(self,query,result,index,musics_parsed):
        query_terms = self.clean_querys_functions(query)
        docs = set(result)
        rank_dict = {
            'Docs': [],
            'Ranks': []
        }

        for doc in docs:
            rank = 0
            for term in query_terms:
                term_dict = index[term]
                N = len(musics_parsed)
                ni = len(term_dict)

                if doc in term_dict.keys():
                    fij = len(term_dict[doc])
                else:
                    fij = 0

                rank += self.tf_idf(fij,ni,N)

            rank_dict['Docs'].append(doc)
            rank_dict['Ranks'].append(rank)

        out = pd.DataFrame(rank_dict).set_index('Docs')
        out.index = out.index.astype(int)
        return out
    
    def search(self,query,index,musics_parsed):
        result = self.parse_query(index,query)
        Rank = self.Ranking(query,result,index,musics_parsed)
        Rank = Rank.join(musics_parsed).sort_values('Ranks',ascending=False)
        Rank.to_excel('resultado_da_pesquisa.xlsx')
        return Rank