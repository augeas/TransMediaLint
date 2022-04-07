 
from gensim.corpora import Dictionary, MmCorpus
from gensim.models import LdaModel, TfidfModel
from gensim.parsing.preprocessing import STOPWORDS
from gensim.utils import tokenize

from sources.models import Article, Source

class CorpusBuilder(object):
    
    def __init__(self,source_slug):
        self.source = Source.objects.get(slug=source_slug)

        try:
            path = ''.join(['model_dump/',source_slug,'.dict'])
            self.corpus_dict = Dictionary.load(path)
        except:
            self.corpus_dict = Dictionary() 
     
    def build(self):
        self.corpus_dict = Dictionary(self.get_articles()) 
     
        stop_ids = [self.corpus_dict.token2id[stopword] for stopword in STOPWORDS
            if stopword in self.corpus_dict.token2id]
        
        once_ids = [tokenid for tokenid, docfreq in self.corpus_dict.dfs.items()
            if docfreq == 1]
        
        self.corpus_dict.filter_tokens(stop_ids + once_ids)

        path = '/'.join(['model_dump',self.source.slug])

        self.corpus_dict.save(path+'.dict')
        MmCorpus.serialize(path+'.mm', self)
            
    def get_articles(self):
        articles = Article.objects.filter(source=self.source)
        return (tokenize(a.text(), lower=True) for a in articles)
    
    def __iter__(self):
        try:
            path = ''.join(['model_dump/',self.source.slug,'.mm'])
            yield from MmCorpus(path).__iter__()
        except:
            yield from map(self.corpus_dict.doc2bow, self.get_articles())


class LdaCorpusBuilder(object):
    
    def __init__(self,source_slug):
        
        self.bow_corpus = CorpusBuilder(source_slug)
        
    def build(self,topics=300,passes=1):
        tfidf = TfidfModel(self.bow_corpus)
        tfidf_corpus = tfidf[self.bow_corpus]
        lda = LdaModel(tfidf_corpus, id2word=self.bow_corpus.corpus_dict,
            num_topics=topics, passes=passes)
        
        lda_corpus = lda[tfidf_corpus]
        
        path = ''.join(['model_dump/',self.bow_corpus.source.slug,'_lda','.mm'])
        
        MmCorpus.serialize(path+'.mm', lda_corpus)
