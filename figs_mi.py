import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams["font.family"]="serif"; rcParams["font.serif"]=["Times New Roman","DejaVu Serif"]; rcParams["font.size"]=11.5
NAVY,PETROL,GOLD,GREY,RED="#1C4076","#007A88","#B8860B","#7F8C8D","#A23B3B"
import os; FIG=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","figures"); os.makedirs(FIG,exist_ok=True)
HERE=os.path.dirname(os.path.abspath(__file__)); d=pd.read_csv(os.path.join(HERE,"analysis_sample.csv")); R=json.load(open(os.path.join(HERE,"reg_results.json")))
# Fig 1: insurance use vs account ownership, by region, regulation marker
fig,ax=plt.subplots(figsize=(8,5))
cols={"East Asia & Pacific":NAVY,"Europe & Central Asia":GREY,"Latin America & Caribbean":GOLD,"Middle East & North Africa":RED,"South Asia":"#5B7DB1","Sub-Saharan Africa":PETROL}
for reg,c in cols.items():
    s=d[d.region==reg]
    ax.scatter(s.acc*100,s.ins*100,s=28+s.mm*80,c=c,alpha=.75,label=reg,edgecolor="white",linewidth=.5)
    s2=s[s.reg==1]; ax.scatter(s2.acc*100,s2.ins*100,s=90,facecolors="none",edgecolors="k",linewidth=.6)
x=np.linspace(15,100,50); b=np.polyfit(d.acc*100,d.ins*100,1); ax.plot(x,np.polyval(b,x),"k--",lw=1)
for c in ["Egypt, Arab Rep.","Kenya","Philippines","India","China","Zimbabwe","Morocco","Ethiopia","Pakistan","Bangladesh","Saudi Arabia"]:
    s=d[d.countrynewwb==c]
    if len(s): ax.annotate(c.replace(", Arab Rep.",""),(s.acc.iloc[0]*100,s.ins.iloc[0]*100),fontsize=9,xytext=(4,3),textcoords="offset points")
ax.set_xlabel("Adults with an account, 2024 (%)"); ax.set_ylabel("Adults making regular insurance payments, 2024 (%)")
ax.legend(fontsize=9,frameon=False,loc="upper left"); ax.text(0.99,0.02,"Bubble size scales with mobile-money account share; black ring = inclusive-insurance regulation in place (2023)",transform=ax.transAxes,ha="right",fontsize=8.5,color=GREY)
plt.tight_layout(); plt.savefig(f"{FIG}/fig1_scatter.png",dpi=300,bbox_inches="tight"); plt.close()
# Fig 2: coefficient plot M4 + FL AME
m=R["M4_regionFE"]; names=[("acc_z","Account ownership (z)"),("mm_z","Mobile-money account (z)"),("lgdp_z","log GDP per capita (z)"),("rural_z","Rural share (z)"),("vuln_z","Vulnerable employment (z)"),("dis_z","Disaster exposure (z)"),("reg","Inclusive-insurance regulation (0/1)")]
fig,ax=plt.subplots(figsize=(7.5,4))
y=np.arange(len(names))[::-1]
ax.errorbar([m["coef"][k]*100 for k,_ in names],y+0.15,xerr=[1.96*m["se"][k]*100 for k,_ in names],fmt="o",color=NAVY,capsize=3,label="OLS with region effects (M4)")
ame=R["FL_AME"]; ax.scatter([ame[k]*100 for k,_ in names],y-0.15,marker="s",color=GOLD,label="Fractional logit, average marginal effect")
ax.axvline(0,color="k",lw=.8); ax.set_yticks(y); ax.set_yticklabels([n for _,n in names],fontsize=10); ax.set_xlabel("Effect on insurance use (percentage points per 1 SD, or for regulation = 1)")
ax.legend(fontsize=9,frameon=False,loc="upper center",bbox_to_anchor=(0.5,-0.18),ncol=2); plt.tight_layout(); plt.savefig(f"{FIG}/fig2_coef.png",dpi=300,bbox_inches="tight"); plt.close()
# Fig 3: inclusion gradient dumbbell poorest 40 vs richest 60
g=d.dropna(subset=["ins_poorest_40","ins_richest_60"]).sort_values("ins_richest_60")
fig,ax=plt.subplots(figsize=(7.5,7)); yy=np.arange(len(g))
ax.hlines(yy,g.ins_poorest_40*100,g.ins_richest_60*100,color=GREY,lw=1.2)
ax.scatter(g.ins_poorest_40*100,yy,color=RED,s=22,label="Poorest 40%",zorder=3); ax.scatter(g.ins_richest_60*100,yy,color=NAVY,s=22,label="Richest 60%",zorder=3)
ax.set_yticks(yy); ax.set_yticklabels([c.replace(", Arab Rep.","").replace(", Dem. Rep."," DR") for c in g.countrynewwb],fontsize=10)
ax.set_xlabel("Adults making regular insurance payments, 2024 (%)"); ax.legend(frameon=False,fontsize=9.5,loc="lower right"); ax.set_xlim(0,60)
for i,(_,r) in enumerate(g.iterrows()):
    if r.reg==1: ax.text(0.6,i,"■",fontsize=5,color=PETROL,va="center",ha="center")
ax.text(0.99,0.01,"■ = inclusive-insurance regulation in place",transform=ax.transAxes,fontsize=8.5,color=PETROL,ha="right")
plt.tight_layout(); plt.savefig(f"{FIG}/fig3_gradient.png",dpi=300,bbox_inches="tight"); plt.close()
print("figs ok", len(g))
# Fig 4: regulation coefficient in G3 across specifications + leave-one-out distribution
V=R["review"]; G3=R["G3_gender_gap"]
specs=[("G3 as reported (HC1)",G3["coef"]["reg"],G3["se"]["reg"]),("HC3 errors",V["G3_HC3"]["coef"]["reg"],V["G3_HC3"]["se"]["reg"]),
       ("FI account instead of any account",V["G3_fiacc"]["coef"]["reg"],V["G3_fiacc"]["se"]["reg"]),("Drop Kenya & Tunisia",V["G3_drop_top2_cook"]["coef"]["reg"],V["G3_drop_top2_cook"]["se"]["reg"]),
       ("+ rural, informality, exposure",V["G3_controls"]["coef"]["reg"],V["G3_controls"]["se"]["reg"]),("Regulation in force or in development",V["G3_regany"]["coef"]["reg_any"],V["G3_regany"]["se"]["reg_any"]),
       ("+ region effects",V["G3_regionFE"]["coef"]["reg"],V["G3_regionFE"]["se"]["reg"])]
fig,(a1,a2)=plt.subplots(1,2,figsize=(10,4.2),gridspec_kw={"width_ratios":[1.6,1]})
y=np.arange(len(specs))[::-1]
a1.errorbar([s[1] for s in specs],y,xerr=[1.96*s[2] for s in specs],fmt="o",color=NAVY,capsize=3)
a1.axvline(0,color="k",lw=.8); a1.set_yticks(y); a1.set_yticklabels([s[0] for s in specs],fontsize=9.5); a1.set_xlabel("Regulation coefficient in ln(women ÷ men), 95% CI")
# leave-one-out: recompute quickly
import statsmodels.formula.api as smf
gr=d.dropna(subset=["ins_gap_gender"]).copy(); gr["gap_gen"]=np.log(gr.ins_gap_gender)
loo=[smf.ols("gap_gen ~ lgdp_z + acc_z + mm_z + mm_missing + reg",data=gr.drop(i)).fit(cov_type="HC1").params["reg"] for i in gr.index]
a2.hist(loo,bins=14,color=PETROL,alpha=.85); a2.axvline(G3["coef"]["reg"],color="k",ls="--",lw=1); a2.set_xlabel("Leave-one-out coefficient (47 samples)"); a2.set_ylabel("Count")
plt.tight_layout(); plt.savefig(f"{FIG}/fig4_g3_sens.png",dpi=300,bbox_inches="tight"); plt.close()
print("figures done")
