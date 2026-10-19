"""Collects posts and comments from reddit.com/r/UniRO through the Reddit API.

The credentials are read from the REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.
"""
import csv
import os
from datetime import datetime, timedelta

import praw

DAYS = 730
QUERIES = {
    "uncertainty": 'title:"nu stiu" OR title:"habar n-am" OR title:"habar nu am" OR title:"ce sa fac" OR '
                   'title:"ce sa aleg" OR title:"incotro" OR title:"sunt pierdut" OR title:"nehotarat" OR '
                   'title:"nu sunt sigur" OR title:"ajutor" OR title:"sfat" OR title:"pareri" OR title:"orientare"',
    "comparison": 'title:"vs" OR title:"comparatie" OR title:"diferenta" OR title:"recomandare" OR title:"top" OR '
                  'title:"clasament" OR title:"review" OR title:"optiuni"',
    "criteria": '"profesori" OR "materii" OR "cursuri" OR "restante" OR "sesiune" OR "camine" OR "taxa" OR "buget" OR '
                '"job" OR "angajare" OR "salariu" OR "oportunitati" OR "practica" OR "orar" OR "secretariat"',
    "sentiment": '"dezamagire" OR "regret" OR "renuntare" OR "abandon" OR "inutila" OR "pierdere de timp" OR '
                 '"experienta placuta" OR "atmosfera" OR "colegi" OR "comunitate" OR "merita"',
}


def posts(subreddit, corpus):
    if corpus == "filtered":
        for query in QUERIES.values():
            yield from subreddit.search(query, sort="relevance", time_filter="all", limit=None, syntax="lucene")
    else:
        yield from subreddit.top(time_filter="all", limit=None)
        yield from subreddit.new(limit=None)


def scrape(subreddit, corpus):
    cutoff = (datetime.now() - timedelta(days=DAYS)).timestamp()
    seen = set()
    with open(f"data/uniro_posts_{corpus}.csv", "w", newline="", encoding="utf-8") as fp, \
            open(f"data/uniro_comments_{corpus}.csv", "w", newline="", encoding="utf-8") as fc:
        post_writer, comment_writer = csv.writer(fp), csv.writer(fc)
        post_writer.writerow(["Post ID", "Title", "Body Text", "Author", "Score", "Date", "URL"])
        comment_writer.writerow(["Parent Post ID", "Comment ID", "Body", "Author", "Score", "Date"])
        for post in posts(subreddit, corpus):
            if post.id in seen or post.created_utc < cutoff:
                continue
            seen.add(post.id)
            body = post.selftext.replace("\n", " ").replace("\r", "")
            if body in ("[removed]", "[deleted]"):
                body = ""
            post_writer.writerow([post.id, post.title, body, str(post.author), post.score,
                                  datetime.fromtimestamp(post.created_utc), post.url])
            post.comments.replace_more(limit=0)
            for c in post.comments.list():
                if c.body in ("[removed]", "[deleted]") or str(c.author) == "AutoModerator":
                    continue
                comment_writer.writerow([post.id, c.id, c.body.replace("\n", " ").replace("\r", ""),
                                         str(c.author), c.score, datetime.fromtimestamp(c.created_utc)])


if __name__ == "__main__":
    reddit = praw.Reddit(client_id=os.environ["REDDIT_CLIENT_ID"], client_secret=os.environ["REDDIT_CLIENT_SECRET"],
                         user_agent="uniro-criteria-lda")
    for corpus in ("filtered", "unfiltered"):
        scrape(reddit.subreddit("UniRO"), corpus)
