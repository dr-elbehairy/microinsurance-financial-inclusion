# Microinsurance and Financial Inclusion — replication package

Zenodo DOI: pending (release v1.0.0)

Code, derived data and results to reproduce the empirical component of

> Elbehairy, M. (2026). *Microinsurance and Financial Inclusion: Pricing and Distribution Models and Cross-Country Evidence from 91 Developing Economies.* Manuscript, Department of Statistics and Insurance, Faculty of Commerce, Suez Canal University.

## Abstract

Payments inclusion has outrun protection inclusion in developing economies. The paper pairs a structured comparison of microinsurance pricing and distribution architectures, anchored in the Landscape of Microinsurance 2024 census, with cross-country regressions on the new Global Findex 2025 measure of adults making regular insurance payments in 91 low- and middle-income economies. Account ownership is the one structural correlate that holds in every specification (4.8 percentage points per standard deviation; 3.1 without four high-use economies); mobile money adds nothing beyond the account, even when financial-institution and mobile-money accounts enter separately. Dedicated inclusive-insurance regulation is unrelated to the level of use, and its association with a narrower gender gap survives resampling but not region effects, so it is reported as suggestive. The poorest 40 percent use insurance at 56 percent of the rate of the richest 60 percent, and the gradient steepens with national income.

## What the package reproduces

| Script | Purpose | Output |
|---|---|---|
| `regress.py` | Builds the 91-economy sample from `data/panel.csv`, standardises regressors, estimates M1–M5 (OLS, HC1), the fractional logit with average marginal effects, and the gradient models G1–G3 (Tables 5–6, descriptive tables). | `reg_results.json`, `data/analysis_sample.csv` |
| `06_reviewer_checks.py` | Sensitivity analyses: VIFs and the financial-institution / mobile-money decomposition (Table 7); Cook's distances, leave-one-out, HC3, trimmed and recoded samples (Table 7); the regulation–gender coefficient under leave-one-out, influential-case deletion, added controls, region effects, a 5,000-draw permutation test, a 5,000-draw wild bootstrap and a Holm adjustment (Table 8). Writes under the key `review` in `reg_results.json`. | `results_review.json` |
| `figs_mi.py` | Figures 1–4 (300 dpi PNG). | `figures/` |
| `build_manuscript.py` | Regenerates the manuscript .docx from `reg_results.json` (flags `--blind`, `--ar-abstract`); no number in the paper is typed by hand; writes `wordcount.json`. | — |

`results/` holds the JSON outputs the manuscript was built from, so every number in the paper can be traced without rerunning anything.

## Data

* **Global Findex Database 2025** (World Bank; Klapper, Singer, Starita & Norris, 2025, https://doi.org/10.1596/978-1-4648-2204-9), country-level indicators: `fin19` (made regular payments to an insurance agent or company, past year), account ownership, financial-institution account, mobile-money account, disaster exposure, and the income/gender/location splits. Open data, CC BY 4.0.
* **World Development Indicators** (World Bank), latest available year 2019–2024: GDP per capita, rural population share, vulnerable employment. Open data, CC BY 4.0.
* **Inclusive-insurance regulation indicator**, coded by the author from the Access to Insurance Initiative map reproduced in *The Landscape of Microinsurance 2024* (Microinsurance Network & UNDP IRFF, 2025); CIMA member states coded as regulated; `reg_dev` flags frameworks under development.

`data/panel.csv` is the merged country-level file; `data/analysis_sample.csv` is the 91-economy estimation sample with standardised regressors.

## Environment

```bash
pip install -r requirements.txt     # Python 3.11, statsmodels ≥ 0.14, pandas 2.0.3
python regress.py                   # deterministic
python 06_reviewer_checks.py        # ≈ 2 min (permutation and wild-bootstrap draws, seed 2026)
python figs_mi.py
```

## Citation and licence

Elbehairy, M. (2026). *microinsurance-financial-inclusion: Replication package for "Microinsurance and Financial Inclusion"* (v1.0.0) [Software]. GitHub. https://github.com/dr-elbehairy/microinsurance-financial-inclusion — Zenodo DOI to be added after the archived release.

Code: MIT (see `LICENSE`). Data: World Bank open data (CC BY 4.0) and author coding; please cite the original sources.
