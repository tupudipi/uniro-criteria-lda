import re

import gensim
import nltk
import pandas as pd
import spacy
from gensim.corpora import Dictionary
from nltk.corpus import stopwords
from unidecode import unidecode

nltk.download("stopwords", quiet=True)

STOP_WORDS = set(stopwords.words("romanian")) | {
    "poti", "vrei", "vrea", "putea", "placea", "bine", "precum", "data",
    "salut", "buna", "multumesc", "rog", "parere", "credeti", "stiti",
    "unde", "cand", "cum", "care", "cine", "fost", "fiind", "avea",
    "fac", "facut", "trebuie", "zic", "zis", "doar", "poate", "acum",
    "ceva", "altceva", "mult", "putin", "fel", "mod", "timp", "anul",
    "sunt", "esti", "este", "faci", "vazut", "mers", "luat", "dat",
    "automoderator", "removed", "deleted", "http", "https",
}
POS = {"NOUN", "ADJ", "VERB", "ADV"}

nlp = spacy.load("ro_core_news_sm", disable=["parser", "ner"])


def load_documents(corpus):
    """A document contains a post with its title, body, and all comments."""
    posts = pd.read_csv(f"data/uniro_posts_{corpus}.csv").fillna("")
    comments = pd.read_csv(f"data/uniro_comments_{corpus}.csv").fillna("")
    replies = comments.groupby("Parent Post ID")["Body"].agg(lambda b: " ".join(b.astype(str)))
    replies = posts["Post ID"].map(replies).fillna("")
    return (posts["Title"].astype(str) + " " + posts["Body Text"].astype(str) + " " + replies).tolist()


def preprocess(texts):
    docs = []
    for text in texts:
        text = re.sub(r"http\S+|u/\S+", "", str(text))
        text = re.sub(r"[^a-zA-ZăâîșțĂÂÎȘȚ\s]", "", text).lower()
        tokens = [t for t in gensim.utils.simple_preprocess(text, deacc=True) if t not in STOP_WORDS]
        if not tokens:
            continue
        lemmas = [unidecode(t.lemma_) for t in nlp(" ".join(tokens)) if t.pos_ in POS and len(t.lemma_) > 2]
        lemmas = [w for w in lemmas if w not in STOP_WORDS]
        if lemmas:
            docs.append(lemmas)
    return docs


def build_corpus(docs):
    dictionary = Dictionary(docs)
    dictionary.filter_extremes(no_below=5, no_above=0.4)
    return dictionary, [dictionary.doc2bow(d) for d in docs]
