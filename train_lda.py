from gensim.models import LdaModel

from preprocessing import build_corpus, load_documents, preprocess

PARAMS = dict(random_state=100, update_every=1, chunksize=100, passes=20, alpha="auto", per_word_topics=True)


def train(dictionary, corpus, k):
    return LdaModel(corpus=corpus, id2word=dictionary, num_topics=k, **PARAMS)


if __name__ == "__main__":
    for name in ("filtered", "unfiltered"):
        dictionary, corpus = build_corpus(preprocess(load_documents(name)))
        for k in (6, 10):
            model = train(dictionary, corpus, k)
            with open(f"results/topics_{name}_{k}.txt", "w", encoding="utf-8") as f:
                for i, words in model.print_topics(num_topics=-1, num_words=10):
                    f.write(f"{i}: {words}\n")
