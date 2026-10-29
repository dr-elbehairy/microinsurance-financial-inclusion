"""Cross-country analysis: insurance use among adults (Findex 2025, fin19) in developing economies.
Determinants: financial-inclusion rails (account, mobile money), income, informality, rurality, disaster exposure,
inclusive-insurance regulation (A2ii map 2023). Inclusion gradients: poorest 40% vs richest 60%, rural/urban, women/men."""
import pandas as pd, numpy as np, json, os, statsmodels.api as sm, statsmodels.formula.api as smf
os.chdir(os.path.dirname(os.path.abspath(__file__)))
d = pd.read_csv("data/panel.csv"); d = d[d.developing].copy()
d["reg"] = d.reg_impl; d["reg_any"] = ((d.reg_impl + d.reg_dev) > 0).astype(int)
d["mm"] = d.mobileaccount_t_d.fillna(0)          # economies without mobile-money data are treated as 0 (no MM ecosystem)
d["mm_missing"] = d.mobileaccount_t_d.isna().astype(int)
d["ins"] = d.fin19; d["acc"] = d.account_t_d; d["dis"] = d.fin24c; d["vuln"] = d.vuln_emp / 100; d["rural"] = d.rural_pct / 100
d["region"] = d.regionwb24_hi.str.replace(" (excluding high income)", "", regex=False)
d["ssa"] = (d.region == "Sub-Saharan Africa").astype(int)
out = {}
def fit(formula, data, name, cov="HC1"):
    m = smf.ols(formula, data=data).fit(cov_type=cov)
    out[name] = dict(n=int(m.nobs), r2=float(m.rsquared), r2a=float(m.rsquared_adj),
                     coef={k: float(v) for k, v in m.params.items()}, se={k: float(v) for k, v in m.bse.items()},
                     p={k: float(v) for k, v in m.pvalues.items()})
    print(f"\n=== {name}  N={int(m.nobs)} R2={m.rsquared:.3f}"); print(m.summary().tables[1])
    return m
dd = d.dropna(subset=["ins", "acc", "lgdp", "rural", "vuln", "dis"]).copy()
# standardise continuous regressors for comparability (beta coefficients)
for c in ["acc", "mm", "lgdp", "rural", "vuln", "dis"]:
    dd[c + "_z"] = (dd[c] - dd[c].mean()) / dd[c].std()
m1 = fit("ins ~ lgdp_z + rural_z + vuln_z + dis_z", dd, "M1_baseline")
m2 = fit("ins ~ lgdp_z + rural_z + vuln_z + dis_z + acc_z + mm_z + mm_missing", dd, "M2_rails")
m3 = fit("ins ~ lgdp_z + rural_z + vuln_z + dis_z + acc_z + mm_z + mm_missing + reg", dd, "M3_regulation")
m4 = fit("ins ~ lgdp_z + rural_z + vuln_z + dis_z + acc_z + mm_z + mm_missing + reg + C(region)", dd, "M4_regionFE")
m5 = fit("ins ~ lgdp_z + rural_z + vuln_z + dis_z + acc_z + mm_z + mm_missing + reg + mm_z:reg + C(region)", dd, "M5_interaction")
# fractional logit robustness (GLM binomial with robust SE)
X = sm.add_constant(dd[["lgdp_z", "rural_z", "vuln_z", "dis_z", "acc_z", "mm_z", "mm_missing", "reg"]])
fl = sm.GLM(dd["ins"], X, family=sm.families.Binomial()).fit(cov_type="HC1")
out["FL_fractional_logit"] = dict(n=int(fl.nobs), coef={k: float(v) for k, v in fl.params.items()}, p={k: float(v) for k, v in fl.pvalues.items()})
# average marginal effects for fractional logit
mu = fl.predict(X); ame = {k: float((fl.params[k] * mu * (1 - mu)).mean()) for k in X.columns if k != "const"}
out["FL_AME"] = ame; print("\nFractional logit AME:", {k: round(v, 4) for k, v in ame.items()})
# ---- inclusion gradients (subsample with income breakdown) ----
g = dd.dropna(subset=["ins_gap_income"]).copy()
g["gap_inc"] = np.log(g.ins_gap_income)          # log ratio poorest40 / richest60
fit("gap_inc ~ lgdp_z + acc_z + mm_z + mm_missing + reg", g, "G1_income_gap")
fit("ins_poorest_40 ~ lgdp_z + rural_z + vuln_z + dis_z + acc_z + mm_z + mm_missing + reg", g, "G2_poorest40_level")
gr = dd.dropna(subset=["ins_gap_gender"]).copy(); gr["gap_gen"] = np.log(gr.ins_gap_gender)
fit("gap_gen ~ lgdp_z + acc_z + mm_z + mm_missing + reg", gr, "G3_gender_gap")
# descriptive tables
out["desc_by_region"] = dd.groupby("region")[["ins", "acc", "mm", "dis", "reg"]].mean().round(3).to_dict(orient="index")
_t = dd.groupby("reg")[["ins", "acc", "mm", "lgdp"]].agg(["mean", "median", "count"]).round(3)
out["desc_by_reg"] = {str(k): {f"{a}_{b}": float(v) for (a, b), v in row.items()} for k, row in _t.iterrows()}
out["gap_desc"] = dict(income=g.ins_gap_income.describe().round(3).to_dict(), gender=gr.ins_gap_gender.describe().round(3).to_dict(),
                       rural=dd.ins_gap_rural.describe().round(3).to_dict())
# country highlights
hl = dd.set_index("countrynewwb")[["ins", "acc", "mm", "dis", "lgdp", "reg", "ins_poorest_40", "ins_richest_60", "region"]]
out["highlights"] = hl.loc[[c for c in ["Egypt, Arab Rep.", "Kenya", "Ghana", "Philippines", "India", "Bangladesh", "Zambia", "Zimbabwe", "Morocco", "Jordan", "Tunisia", "Pakistan", "Ethiopia", "South Africa", "Peru", "Saudi Arabia"] if c in hl.index]].round(3).reset_index().to_dict(orient="records")
out["N_dev"] = int(len(dd)); out["N_gap"] = int(len(g))
# partial correlation of mm and ins controlling for account
r_mm = np.corrcoef(dd.mm, dd.ins)[0, 1]; out["corr_mm_ins"] = float(r_mm)
json.dump(out, open("reg_results.json", "w"), indent=2, default=float)
dd.to_csv("analysis_sample.csv", index=False)
print("\nN developing:", len(dd), "gap sample:", len(g))
print(pd.DataFrame(out["highlights"]).to_string())
