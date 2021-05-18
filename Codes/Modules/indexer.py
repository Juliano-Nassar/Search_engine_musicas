from collections import defaultdict
import json

def make_index(docs):
    index = defaultdict(lambda: defaultdict(list))
    for k, doc in enumerate(docs):
        words = doc
        for pos,word in enumerate(words):
            index[word][k].append(pos)
    return index

def save_index(index, path):
    with open(path, 'w') as file:
        json.dump(index, file, indent=4)


def load_index(path):
    with open(path, 'r') as file:
        return json.load(file)