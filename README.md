# uniro-criteria-lda

## Installation

```
pip install -r requirements.txt
```

The results of the paper were obtained with Python 3.12.

## Reproduction

```
python train_lda.py
python coherence_analysis.py
python survey_analysis.py
```

The first script trains the four latent Dirichlet allocation (LDA) models and saves the ten most probable words of each topic in `results/`. The second script computes the C<sub>V</sub> and C<sub>UMass</sub> coherence scores for 4 to 15 topics and draws the coherence figure of the paper. The third script prints the survey statistics, which are also saved in `results/survey.txt`. The scripts use a fixed random seed, so they should produce exactly the files in `results/`.

The analysis can be run in Google Colab with [colab.ipynb](https://colab.research.google.com/github/tupudipi/uniro-criteria-lda/blob/main/colab.ipynb).

## Data

The data are described in `data/README.md`. The script `scrape_reddit.py` collects a new corpus through the official application programming interface of Reddit, but it will be different from the corpus used in the paper, as the content of the forum changes over time.
