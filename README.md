# arXiv cs.IR Analysis Script

Companion code for the research paper *Progress and Reliability in Recommender Systems and Information Retrieval Research: A Literature-Based Study Using the arXiv Dataset*.

**Author:** Seif Ahmed Abdelfattah, Vistula University

## What it does
`arxiv_rsir_analysis.py` reads the Kaggle arXiv metadata file and, for papers listed under the category `cs.IR`:
- counts papers per year and per method era (up to 2008, 2009-2016, 2017-2022, 2023 onward)
- tracks how often key terms appear in titles and abstracts (e.g. collaborative filtering, dense retrieval, large language model)
- lists the most common co-occurring categories
- saves a random sample of record IDs per era for manual checking

## Status
The script was only tested on a small synthetic file. It was **not** run on the full dataset for the paper. Check its output before relying on any numbers.

## How to reproduce
1. Download the dataset from Kaggle: https://www.kaggle.com/datasets/Cornell-University/arxiv
   (a free Kaggle account is needed). Unzip it to get `arxiv-metadata-oai-snapshot.json`.
2. Make sure Python 3.8+ is installed. The script uses only the standard library.
3. Run:
   ```
   python arxiv_rsir_analysis.py arxiv-metadata-oai-snapshot.json --out results/
   ```
4. Results appear in the `results/` folder: `yearly_counts.csv`, `era_counts.csv`, `keyword_prevalence.csv`, `cocategories.csv`, `audit_ids.json`, `summary.txt`.

## Notes
- The year of each paper comes from its first version date.
- Record the date you downloaded the Kaggle file, because the dataset changes over time.
- Dataset: Cornell University, arXiv Dataset, Kaggle.
