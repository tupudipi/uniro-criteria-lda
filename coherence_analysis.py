import matplotlib.pyplot as plt
import pandas as pd
from gensim.models import CoherenceModel

from preprocessing import build_corpus, load_documents, preprocess
from train_lda import train

K = range(4, 16)


def plot(df):
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
                         "font.size": 9, "mathtext.fontset": "stix"})
    fig, axes = plt.subplots(1, 2, figsize=(13.6 / 2.54, 2.6))
    for ax, measure, label in [(axes[0], "cv", r"$C_{\mathrm{V}}$"), (axes[1], "umass", r"$C_{\mathrm{UMass}}$")]:
        ax.plot(df.k, df[f"filtered_{measure}"], "o-", color="#0072B2", ms=3.5, lw=1.1, label="Filtered")
        ax.plot(df.k, df[f"unfiltered_{measure}"], "s--", color="#D55E00", ms=3.5, lw=1.1, label="Unfiltered")
        ax.axvline(6, color="0.6", lw=0.6, ls=":")
        ax.set_title(label + " coherence", fontsize=9)
        ax.set_xlabel("Number of topics")
        ax.set_ylabel(label + " score")
        ax.set_xticks(list(K))
        ax.tick_params(labelsize=8)
        ax.grid(alpha=0.25, lw=0.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8, frameon=False)
    fig.tight_layout(w_pad=1.5)
    fig.savefig("results/coherence.png", dpi=600, bbox_inches="tight", pad_inches=0.03)


if __name__ == "__main__":
    df = pd.DataFrame({"k": list(K)})
    for name in ("filtered", "unfiltered"):
        docs = preprocess(load_documents(name))
        dictionary, corpus = build_corpus(docs)
        cv, umass = [], []
        for k in K:
            model = train(dictionary, corpus, k)
            cv.append(CoherenceModel(model=model, texts=docs, dictionary=dictionary, coherence="c_v").get_coherence())
            umass.append(CoherenceModel(model=model, corpus=corpus, dictionary=dictionary,
                                        coherence="u_mass").get_coherence())
        df[f"{name}_cv"], df[f"{name}_umass"] = cv, umass
    df.to_csv("results/coherence.csv", index=False)
    plot(df)
