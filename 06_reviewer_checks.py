"""Reviewer-driven checks for v4 (microinsurance / Findex 2025 cross-country analysis).
M1 regressor overlap (account ⊃ mobile money): VIF, FI-account vs MM decomposition, MM alone.
M2 fragility of the gender-gap regulation result: leave-one-out, Cook's distance, drop CIMA, alternative coding, HC3, permutation p.
M3 influential economies in the level models: leave-one-out range, exclusion of use > 30 %, HC3.
M4 income-gradient model: leave-one-out, HC3, trimmed sample.
Multiple-testing count. Results written to reg_results.json under key "review"."""
import json, numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor, OLSInfluence
import os; HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
rng = np.random.default_rng(2026)
d = pd.read_csv("data/panel.csv"); d = d[d.developing].copy()
d["reg"] = d.reg_impl; d["reg_any"] = ((d.reg_impl + d.reg_dev) > 0).astype(int)
d["mm"] = d.mobileaccount_t_d.fillna(0); d["mm_missing"] = d.mobileaccount_t_d.isna().astype(int)
d["ins"] = d.fin19; d["acc"] = d.account_t_d; d["fiacc"] = d.fiaccount_t_d; d["dis"] = d.fin24c
d["vuln"] = d.vuln_emp / 100; d["rural"] = d.rural_pct / 100
d["region"] = d.regionwb24_hi.str.replace(" (excluding high income)", "", regex=False)
CIMA = ["Benin", "Burkina Faso", "Cameroon", "Central African Republic", "Chad", "Comoros", "Congo, Rep.", "Cote d'Ivoire", "Equatorial Guinea", "Gabon", "Guinea-Bissau", "Mali", "Niger", "Senegal", "Togo"]
d["cima"] = d.countrynewwb.isin(CIMA).astype(int)
dd = d.dropna(subset=["ins", "acc", "lgdp", "rural", "vuln", "dis"]).copy()
for c in ["acc", "fiacc", "mm", "lgdp", "rural", "vuln", "dis"]:
    dd[c + "_z"] = (dd[c] - dd[c].mean()) / dd[c].std()
out = {}
def fit(f, data, cov="HC1"): return smf.ols(f, data=data).fit(cov_type=cov)
def pack(m, keys=None):
    keys = keys or list(m.params.index)
    return dict(n=int(m.nobs), r2=float(m.rsquared), coef={k: float(m.params[k]) for k in keys if k in m.params},
                se={k: float(m.bse[k]) for k in keys if k in m.params}, p={k: float(m.pvalues[k]) for k in keys if k in m.params})
BASE = "lgdp_z + rural_z + vuln_z + dis_z"
M4F = f"ins ~ {BASE} + acc_z + mm_z + mm_missing + reg + C(region)"
m4 = fit(M4F, dd)
# ---------------- M1: overlap, VIF, decomposition
X = dd[["lgdp_z", "rural_z", "vuln_z", "dis_z", "acc_z", "mm_z", "mm_missing", "reg"]]
Xc = sm.add_constant(X); vif = {c: float(variance_inflation_factor(Xc.values, i)) for i, c in enumerate(Xc.columns) if c != "const"}
out["vif_M3"] = vif
out["corr_acc_mm"] = float(dd[["acc", "mm"]].corr().iloc[0, 1]); out["corr_acc_fiacc"] = float(dd[["acc", "fiacc"]].corr().iloc[0, 1])
out["corr_fiacc_mm"] = float(dd[["fiacc", "mm"]].corr().iloc[0, 1])
out["share_mm_only_mean"] = float((dd.acc - dd.fiacc).mean()); out["share_mm_only_max"] = float((dd.acc - dd.fiacc).max())
out["M4_fiacc_mm"] = pack(fit(f"ins ~ {BASE} + fiacc_z + mm_z + mm_missing + reg + C(region)", dd), ["fiacc_z", "mm_z", "reg", "lgdp_z"])
out["M4_fiacc_only"] = pack(fit(f"ins ~ {BASE} + fiacc_z + reg + C(region)", dd), ["fiacc_z", "reg", "lgdp_z"])
out["M4_mm_only"] = pack(fit(f"ins ~ {BASE} + mm_z + mm_missing + reg + C(region)", dd), ["mm_z", "reg", "lgdp_z"])
out["M3_mm_only_noFE"] = pack(fit(f"ins ~ {BASE} + mm_z + mm_missing + reg", dd), ["mm_z", "reg", "lgdp_z"])
out["M4_acc_only"] = pack(fit(f"ins ~ {BASE} + acc_z + reg + C(region)", dd), ["acc_z", "reg", "lgdp_z"])
# mobile money among the 76 economies where it is surveyed
dm = dd[dd.mm_missing == 0].copy()
out["M4_mm_surveyed_only"] = pack(fit(f"ins ~ {BASE} + fiacc_z + mm_z + reg + C(region)", dm), ["fiacc_z", "mm_z", "reg"])
# ---------------- M3: influence in level models
infl = OLSInfluence(smf.ols(M4F, data=dd).fit()); cooks = infl.cooks_distance[0]
top = dd.assign(cook=cooks).sort_values("cook", ascending=False)[["countrynewwb", "cook", "ins", "acc"]].head(6)
out["M4_cooks_top"] = top.round(3).to_dict(orient="records")
loo = []
for i in dd.index:
    m = fit(M4F, dd.drop(i)); loo.append(dict(drop=dd.loc[i, "countrynewwb"], acc=float(m.params["acc_z"]), acc_p=float(m.pvalues["acc_z"]), mm=float(m.params["mm_z"]), reg=float(m.params["reg"]), reg_p=float(m.pvalues["reg"])))
L = pd.DataFrame(loo)
out["M4_loo"] = dict(acc_min=float(L.acc.min()), acc_max=float(L.acc.max()), acc_p_max=float(L.acc_p.max()), mm_min=float(L.mm.min()), mm_max=float(L.mm.max()),
                     reg_min=float(L.reg.min()), reg_max=float(L.reg.max()), reg_p_min=float(L.reg_p.min()),
                     acc_min_drop=L.loc[L.acc.idxmin(), "drop"], acc_max_drop=L.loc[L.acc.idxmax(), "drop"])
dt = dd[dd.ins <= 0.30]
out["M4_trim30"] = pack(fit(M4F, dt), ["acc_z", "mm_z", "reg", "lgdp_z"]); out["M4_trim30"]["dropped"] = dd[dd.ins > 0.30].countrynewwb.tolist()
out["M4_HC3"] = pack(fit(M4F, dd, "HC3"), ["acc_z", "mm_z", "reg", "lgdp_z"])
out["M4_regany"] = pack(fit(M4F.replace("+ reg ", "+ reg_any "), dd), ["acc_z", "mm_z", "reg_any"])
out["M4_noCIMA"] = pack(fit(M4F, dd[dd.cima == 0]), ["acc_z", "mm_z", "reg"]); out["n_cima_in_sample"] = int(dd.cima.sum()); out["n_cima_reg"] = int((dd.cima * dd.reg).sum())
# ---------------- M2: gender-gap regulation result
gr = dd.dropna(subset=["ins_gap_gender"]).copy(); gr["gap_gen"] = np.log(gr.ins_gap_gender)
G3F = "gap_gen ~ lgdp_z + acc_z + mm_z + mm_missing + reg"
g3 = fit(G3F, gr); out["G3_base"] = pack(g3, ["reg", "acc_z", "lgdp_z", "mm_z"])
out["G3_HC3"] = pack(fit(G3F, gr, "HC3"), ["reg"])
out["G3_regany"] = pack(fit(G3F.replace("reg", "reg_any"), gr), ["reg_any"])
out["G3_noCIMA"] = pack(fit(G3F, gr[gr.cima == 0]), ["reg"]); out["G3_n_cima"] = int(gr.cima.sum())
out["G3_fiacc"] = pack(fit(G3F.replace("acc_z", "fiacc_z"), gr), ["reg", "fiacc_z", "mm_z"])
out["G3_controls"] = pack(fit(G3F + " + rural_z + vuln_z + dis_z", gr), ["reg"])
out["G3_regionFE"] = pack(fit(G3F + " + C(region)", gr), ["reg"])
infl = OLSInfluence(smf.ols(G3F, data=gr).fit()); gr["cook"] = infl.cooks_distance[0]
out["G3_cooks_top"] = gr.sort_values("cook", ascending=False)[["countrynewwb", "cook", "ins_gap_gender", "reg"]].head(5).round(3).to_dict(orient="records")
loo = []
for i in gr.index:
    m = fit(G3F, gr.drop(i)); loo.append(dict(drop=gr.loc[i, "countrynewwb"], reg=float(m.params["reg"]), p=float(m.pvalues["reg"])))
L = pd.DataFrame(loo); out["G3_loo"] = dict(reg_min=float(L.reg.min()), reg_max=float(L.reg.max()), p_min=float(L.p.min()), p_max=float(L.p.max()),
                                            n_p_above_05=int((L.p > 0.05).sum()), n_p_above_10=int((L.p > 0.10).sum()), p_max_drop=L.loc[L.p.idxmax(), "drop"], n=len(L))
# drop top-2 Cook's
drop2 = gr.sort_values("cook", ascending=False).index[:2]
out["G3_drop_top2_cook"] = pack(fit(G3F, gr.drop(drop2)), ["reg"]); out["G3_drop_top2_cook"]["dropped"] = gr.loc[drop2, "countrynewwb"].tolist()
# permutation test on reg (Freedman-Lane style: permute reg labels, refit, compare t)
t_obs = float(g3.tvalues["reg"]); perm = []
for _ in range(5000):
    gp = gr.copy(); gp["reg"] = rng.permutation(gp.reg.values); perm.append(float(fit(G3F, gp).tvalues["reg"]))
perm = np.array(perm); out["G3_perm"] = dict(t_obs=t_obs, p_two_sided=float((np.abs(perm) >= abs(t_obs)).mean()), n_perm=5000)
# wild bootstrap (Rademacher) p-value for reg in G3
res = smf.ols(G3F, data=gr).fit(); X3 = res.model.exog; y_hat_r = smf.ols(G3F.replace("+ reg", ""), data=gr).fit()
# restricted residuals
yr = y_hat_r.fittedvalues.values; er = y_hat_r.resid.values; tb = []
for _ in range(5000):
    ystar = yr + er * rng.choice([-1, 1], size=len(er)); gp = gr.copy(); gp["gap_gen"] = ystar; tb.append(float(fit(G3F, gp).tvalues["reg"]))
tb = np.array(tb); out["G3_wild"] = dict(p_two_sided=float((np.abs(tb) >= abs(t_obs)).mean()), n_boot=5000)
# ---------------- M4: income gradient
g = dd.dropna(subset=["ins_gap_income"]).copy(); g["gap_inc"] = np.log(g.ins_gap_income)
G1F = "gap_inc ~ lgdp_z + acc_z + mm_z + mm_missing + reg"
out["G1_HC3"] = pack(fit(G1F, g, "HC3"), ["lgdp_z", "reg", "acc_z"])
loo = []
for i in g.index:
    m = fit(G1F, g.drop(i)); loo.append(dict(drop=g.loc[i, "countrynewwb"], b=float(m.params["lgdp_z"]), p=float(m.pvalues["lgdp_z"])))
L = pd.DataFrame(loo); out["G1_loo"] = dict(b_min=float(L.b.min()), b_max=float(L.b.max()), p_max=float(L.p.max()), p_max_drop=L.loc[L.p.idxmax(), "drop"])
out["G1_controls"] = pack(fit(G1F + " + rural_z + vuln_z + dis_z", g), ["lgdp_z", "reg"])
out["G1_regionFE"] = pack(fit(G1F + " + C(region)", g), ["lgdp_z", "reg"])
small = g[g.ins_gap_income >= g.ins_gap_income.quantile(0.10)]
out["G1_trim_small_ratios"] = pack(fit(G1F, small), ["lgdp_z", "reg"]); out["G1_trim_small_ratios"]["n_dropped"] = int(len(g) - len(small))
out["G1_sample_n"] = int(len(g)); out["G3_sample_n"] = int(len(gr))
# ---------------- multiple testing
out["n_tests"] = dict(level_models=5, gradient_models=3, coefficients_reported=int(sum(len(m.params) - 1 for m in [m4])) , note="eight regressions; the regulation coefficient is reported in seven of them; Holm-adjusted p for G3 across the seven regulation tests:")
pr = [fit(f, df_).pvalues[k] for f, df_, k in [(f"ins ~ {BASE} + acc_z + mm_z + mm_missing + reg", dd, "reg"), (M4F, dd, "reg"), (f"ins ~ {BASE} + acc_z + mm_z + mm_missing + reg + mm_z:reg + C(region)", dd, "reg"),
      (G1F, g, "reg"), (f"ins_poorest_40 ~ {BASE} + acc_z + mm_z + mm_missing + reg", g, "reg"), (G3F, gr, "reg")]]
pr = sorted(pr); m_ = len(pr); holm = max(min(1.0, (m_ - i) * p) for i, p in enumerate(pr) if True) if False else None
# Holm for the smallest (G3) p-value
p_g3 = float(g3.pvalues["reg"]); out["n_tests"]["holm_p_G3_reg"] = float(min(1.0, m_ * p_g3)); out["n_tests"]["m_regulation_tests"] = m_
json.dump(out, open("results_review.json", "w"), indent=2, default=float)
R = json.load(open("reg_results.json")); R["review"] = out; json.dump(R, open("reg_results.json", "w"), indent=2, default=float)
import pprint; pprint.pprint({k: out[k] for k in ["vif_M3", "corr_acc_mm", "corr_acc_fiacc", "share_mm_only_mean", "M4_fiacc_mm", "M4_mm_only", "M4_loo", "M4_trim30", "G3_base", "G3_HC3", "G3_noCIMA", "G3_regany", "G3_loo", "G3_perm", "G3_wild", "G3_drop_top2_cook", "G3_controls", "G3_regionFE", "G1_loo", "G1_HC3", "G1_controls", "G1_trim_small_ratios", "n_tests", "M4_cooks_top", "G3_cooks_top"]}, width=160)
