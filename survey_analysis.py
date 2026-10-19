import pandas as pd

CRITERIA = {"courses": "Courses", "professors": "Professors", "accessibility": "Accessibility",
            "opportunities": "Opportunities", "administration": "Administration", "campus_life": "Campus Life"}
LIKERT = {"Foarte important": 5, "Important": 4, "Moderat": 3, "Puțin important": 2, "Deloc important": 1}
THRESHOLD = {"Excelent": 5, "Bun": 4, "Acceptabil": 3, "Slab": 2, "Foarte slab": 1, "Nu am un minim": 0}
TOP3 = {
    "courses": "Ce se predă și cât de actuală este materia",
    "professors": "Cum sunt profesorii și cum predau",
    "accessibility": "Cât de greu este și cât timp liber voi avea",
    "opportunities": "Ce șanse de angajare voi avea după absolvire",
    "administration": "Cum funcționează administrația",
    "campus_life": "Cum e viața de student acolo",
}
# expected category of each scenario (C = Courses, P = Professors, A = Accessibility)
SCENARIOS = ["P", "C", "A", "P", "C/P", "P", "A", "C", "P", "C", "C/P/A", "P"]
LABELS = {"C": "C = Cursuri", "P": "P = Profesori", "A": "A = Accesibilitate"}


def threshold(answer):
    # a few respondents ticked two levels, in which case only the higher one was kept
    return max(THRESHOLD[a.strip()] for a in answer.split(","))


def pct(count):
    return f"{count} ({count / n:.1%})"


df = pd.read_csv("data/survey_responses.csv")
n = len(df)

print(f"Respondents: {n}")
print(f"11th grade: {(df.grade == 'Clasa a XI-a').sum()}, 12th grade: {(df.grade == 'Clasa a XII-a').sum()}")
for track in ("Matematică-Informatică", "Filologie", "Științe"):
    print(f"{track}: {df.track.str.contains(track).sum()}")
print(f"University studies in Romania: {pct((df.university_intent == 'Da, în România').sum())}")

print("\nCriterion: Likert M (SD), rated 4 or 5, mean rank, top-3, threshold M, threshold counts 0-5")
for key, name in CRITERIA.items():
    likert = df[f"likert_{key}"].map(LIKERT)
    thresh = df[f"thresh_{key}"].apply(threshold)
    counts = "/".join(str((thresh == v).sum()) for v in range(6))
    print(f"{name}: {likert.mean():.2f} ({likert.std():.2f}), {pct((likert >= 4).sum())}, "
          f"{df[f'rank_{key}'].mean():.2f}, {pct(df.top3_choices.str.contains(TOP3[key], regex=False).sum())}, "
          f"{thresh[thresh > 0].mean():.2f}, {counts}")
print(f"Administration rated 3 (Moderat): {pct((df.likert_administration.map(LIKERT) == 3).sum())}")

print("\nScenario: expected, C/P/A (% of respondents)")
mentions = {"C": [], "P": [], "A": []}
for i, expected in enumerate(SCENARIOS, 1):
    answers = df[f"scenario_{i:02d}"]
    share = {c: answers.str.contains(label, regex=False).mean() * 100 for c, label in LABELS.items()}
    print(f"{i}: {expected}, {share['C']:.1f}/{share['P']:.1f}/{share['A']:.1f}")
    if expected in mentions:
        mentions[expected].append(share[expected])
for c, values in mentions.items():
    print(f"Mean for unambiguous {c} scenarios: {sum(values) / len(values):.1f}%")

print(f"\nSeparate scores preferred: {pct(df.score_display_preference.str.startswith('Scoruri separate').sum())}")
