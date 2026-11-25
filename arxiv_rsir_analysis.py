#!/usr/bin/env python3
"""
arxiv_rsir_analysis.py
Companion script for the paper on Recommender Systems & Information Retrieval.

Streams the Kaggle arXiv metadata snapshot (arxiv-metadata-oai-snapshot.json,
one JSON record per line) and computes corpus-level statistics for records
whose categories include cs.IR.

Usage:
    python arxiv_rsir_analysis.py arxiv-metadata-oai-snapshot.json --out results/

Outputs (CSV): yearly_counts.csv, era_counts.csv, keyword_prevalence.csv,
cocategories.csv, summary.txt
"""
import argparse, csv, json, os, random, re
from collections import Counter, defaultdict

ERAS = {
    "I_lexical_neighbourhood": (1991, 2008),
    "II_latent_factor":        (2009, 2016),
    "III_deep_neural":         (2017, 2022),
    "IV_LLM_RAG":              (2023, 2100),
}

KEYWORDS = {
    "collaborative_filtering": r"collaborative filtering",
    "matrix_factorization":    r"matrix factori[sz]ation|latent factor",
    "bm25_tfidf":              r"\bbm25\b|tf-?idf",
    "neural":                  r"neural|deep learning",
    "graph_neural":            r"graph neural|graph convolution|\bgnn\b",
    "sequential":              r"sequential recommend|session-based|next-item",
    "transformer_bert":        r"transformer|\bbert\b",
    "dense_retrieval":         r"dense retriev|dense passage|bi-encoder|late interaction",
    "llm":                     r"large language model|\bllms?\b|\bgpt-?[0-9]",
    "rag":                     r"retrieval[- ]augmented",
    "reproducibility":         r"reproducib|replicab|baseline",
}
KW = {k: re.compile(v, re.I) for k, v in KEYWORDS.items()}

def era_of(year):
    for name, (a, b) in ERAS.items():
        if a <= year <= b:
            return name
    return None

def first_year(rec):
    # Prefer the date of the first version; fall back to the arXiv id prefix.
    try:
        v = rec["versions"][0]["created"]          # e.g. 'Mon, 2 Apr 2007 19:18:42 GMT'
        return int(re.search(r"\b(19|20)\d{2}\b", v).group(0))
    except Exception:
        m = re.match(r"(\d{2})(\d{2})\.", rec.get("id", ""))
        if m:
            yy = int(m.group(1)); return 2000 + yy if yy < 90 else 1900 + yy
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--out", default="results")
    ap.add_argument("--audit", type=int, default=200, help="records per era for manual audit sample")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    yearly, era_n = Counter(), Counter()
    kw = defaultdict(Counter)          # kw[era][keyword]
    cocat = Counter()
    audit = defaultdict(list)          # reservoir sample per era
    seen = defaultdict(int)
    total = 0

    with open(a.path, encoding="utf-8") as f:
        for line in f:
            total += 1
            rec = json.loads(line)
            cats = rec.get("categories", "").split()
            if "cs.IR" not in cats:
                continue
            y = first_year(rec)
            e = era_of(y) if y else None
            if e is None:
                continue
            yearly[y] += 1; era_n[e] += 1
            text = (rec.get("title", "") + " " + rec.get("abstract", "")).replace("\n", " ")
            for k, rx in KW.items():
                if rx.search(text):
                    kw[e][k] += 1
            for c in cats:
                if c != "cs.IR":
                    cocat[c] += 1
            # reservoir sampling for the manual audit
            seen[e] += 1
            if len(audit[e]) < a.audit:
                audit[e].append(rec["id"])
            else:
                j = random.randint(0, seen[e] - 1)
                if j < a.audit:
                    audit[e][j] = rec["id"]

    with open(f"{a.out}/yearly_counts.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["year", "cs_IR_records"])
        for y in sorted(yearly): w.writerow([y, yearly[y]])

    with open(f"{a.out}/era_counts.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["era", "records"])
        for e in ERAS: w.writerow([e, era_n[e]])

    with open(f"{a.out}/keyword_prevalence.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["era", "keyword", "records", "share_of_era"])
        for e in ERAS:
            for k in KEYWORDS:
                n = kw[e][k]; w.writerow([e, k, n, round(n / era_n[e], 4) if era_n[e] else 0])

    with open(f"{a.out}/cocategories.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["category", "co_occurrences"])
        for c, n in cocat.most_common(25): w.writerow([c, n])

    with open(f"{a.out}/audit_ids.json", "w") as f:
        json.dump(audit, f, indent=1)

    ys = sorted(yearly)
    with open(f"{a.out}/summary.txt", "w") as f:
        f.write(f"records scanned: {total}\ncs.IR records: {sum(yearly.values())}\n")
        if len(ys) > 1:
            t0, t1 = ys[0], ys[-2] if len(ys) > 2 else ys[-1]   # drop the (partial) last year
            n0, n1 = yearly[t0], yearly[t1]
            if n0 and t1 > t0:
                f.write(f"CAGR {t0}-{t1}: {(n1 / n0) ** (1 / (t1 - t0)) - 1:.4f}\n")
    print("done ->", a.out)

if __name__ == "__main__":
    main()
