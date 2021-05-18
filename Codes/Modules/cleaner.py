from nltk.tokenize import TweetTokenizer
import re
import unidecode

class Cleaner():
    def __init__(self):
        self.tokenizer = TweetTokenizer() 
           
        self.patterns = {
            'non_alpha': r"(?:[^\w\s]|_)+", # Clean non-alphanumeric and non-space chars
            'lonley_chars': r'(?:^|[\s])+([a-hj-z](?:$|[\s])+)+' # Clean all alone chars except 'i' (Because of english lenguage)
                         }
        self.subs = {
            'non_alpha': r' ',
            'lonley_chars': r' '
                         }
        
        self.matchers = {}
        
        for name,patt in self.patterns.items():
            self.matchers[name] = re.compile(patt)
    
    def text_cleaner(self,text):

        sub = r' '

        # Lowercase text
        text = text.lower()
        # Clean accents
        text = unidecode.unidecode(text)

        # Apply patterns cleans
        for name,matcher in self.matchers.items():
            sub = self.subs[name]
            text = matcher.sub(sub,text)
            
        return text
    
    def clean_and_tokenize(self,text):

        text = self.text_cleaner(text)
        text = self.tokenizer.tokenize(text)

        return text