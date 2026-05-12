import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}


    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    probs = {}
    n_pages = len(corpus)
    links = corpus[page]


    if not links:
        for p in corpus:
            probs[p] = 1 / n_pages
        return probs


    random_prob = (1 - damping_factor) / n_pages

    for p in corpus:
        probs[p] = random_prob


    link_prob = damping_factor / len(links)
    for link in links:
        probs[link] += link_prob

    return probs




def sample_pagerank(corpus, damping_factor, n):
    pagerank = {page: 0 for page in corpus}


    current_page = random.choice(list(corpus.keys()))
    pagerank[current_page] += 1


    for _ in range(n - 1):
        model = transition_model(corpus, current_page, damping_factor)
        pages = list(model.keys())
        weights = list(model.values())


        current_page = random.choices(pages, weights=weights, k=1)[0]
        pagerank[current_page] += 1

    for page in pagerank:
        pagerank[page] /= n

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    n = len(corpus)

    pagerank = {page: 1 / n for page in corpus}
    new_rank = pagerank.copy()

    while True:
        for p in corpus:

            total = (1 - damping_factor) / n


            sigma = 0
            for i in corpus:

                if p in corpus[i]:
                    sigma += pagerank[i] / len(corpus[i])

                elif not corpus[i]:
                    sigma += pagerank[i] / n

            new_rank[p] = total + (damping_factor * sigma)


        diff = max(abs(new_rank[page] - pagerank[page]) for page in corpus)
        if diff < 0.001:
            break

        pagerank = new_rank.copy()

    return pagerank


if __name__ == "__main__":
    main()
