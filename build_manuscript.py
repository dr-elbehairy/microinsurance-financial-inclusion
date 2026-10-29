# -*- coding: utf-8 -*-
"""Microinsurance & financial inclusion — manuscript v4 (final, 29 October 2026).
Every statistic is read from reg_results.json (regress.py + 06_reviewer_checks.py). Flags: --blind, --ar-abstract.
Word counts per section are written to wordcount.json (main text = Sections 1–5 body paragraphs only)."""
import json, sys, re, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); VER = os.path.dirname(HERE); FIGS = f"{VER}/figures"
_h = open(f"{HERE}/helpers_head.py").read()
_h = _h.replace('R = json.load(open(f"{OUT}/results.json"))', 'R = {}')
_h = re.sub(r'OUT = "[^"]*"', f'OUT = "{VER}"', _h, count=1)
exec(_h)   # defines doc, P, H, RTL, TABLE, FIG, EQ, BLIND, FONT, OUT, Pt, Cm, WD_ALIGN_PARAGRAPH
from docx.enum.text import WD_COLOR_INDEX
R = json.load(open(f"{HERE}/reg_results.json")); V = R["review"]
M = {k: R[k] for k in ["M1_baseline", "M2_rails", "M3_regulation", "M4_regionFE", "M5_interaction", "G1_income_gap", "G2_poorest40_level", "G3_gender_gap"]}
AME = R["FL_AME"]; M1, M2, M3, M4, M5, G1, G2, G3 = (M[k] for k in ["M1_baseline", "M2_rails", "M3_regulation", "M4_regionFE", "M5_interaction", "G1_income_gap", "G2_poorest40_level", "G3_gender_gap"])
g_inc = R["gap_desc"]["income"]; g_gen = R["gap_desc"]["gender"]; g_rur = R["gap_desc"]["rural"]; H_ = {h["countrynewwb"]: h for h in R["highlights"]}
reg_by = R["desc_by_region"]
def pp(m, k, d=1): return f"{100*m['coef'][k]:.{d}f}"
def pv(m, k):
    p = m["p"][k]; return "p < 0.001" if p < 0.001 else f"p = {p:.3f}" if p < 0.01 else f"p = {p:.2f}"
def star(m, k):
    p = m["p"][k]; return "∗∗∗" if p < 0.01 else "∗∗" if p < 0.05 else "∗" if p < 0.10 else ""
def cell(m, k, scale=100, d=1):
    if k not in m["coef"]: return "–"
    return f"{scale*m['coef'][k]:.{d}f}{star(m,k)} ({scale*m['se'][k]:.{d}f})"
def c2(m, k, scale=100, d=1, pk=None):
    return f"{scale*m['coef'][k]:.{d}f} ({m['p'][pk or k]:.2f})" if m['p'][pk or k] >= 0.001 else f"{scale*m['coef'][k]:.{d}f} (<0.001)"
gen_mult = math.exp(G3["coef"]["reg"]); gen_pct = 100 * (gen_mult - 1)
acc_lo = 100 * min(V["M4_loo"]["acc_min"], V["M4_trim30"]["coef"]["acc_z"]); acc_hi = 100 * max(V["M4_loo"]["acc_max"], V["M4_HC3"]["coef"]["acc_z"])
REPO = "https://github.com/dr-elbehairy/microinsurance-financial-inclusion"
AR = "--ar-abstract" in sys.argv

# ---------------------------------------------------------------- word counting
WC = {"abstract": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0}; _sec = [None]
def T(text, **kw):
    """Body paragraph that counts toward the section budget."""
    if _sec[0] in WC: WC[_sec[0]] += len(re.sub(r"\*\*|\*", "", text).split())
    return P(text, indent=kw.pop("indent", True), **kw)
_H0 = H
def H(text, lvl=1):
    m = re.match(r"(\d)", text)
    if lvl == 1: _sec[0] = m.group(1) if m else ("abstract" if text == "Abstract" else None)
    return _H0(text, lvl)
WC_DECL = json.load(open(f"{HERE}/wordcount.json"))["main_text"] if os.path.exists(f"{HERE}/wordcount.json") else 8000

# ---------------------------------------------------------------- title page
TITLE = "Microinsurance and Financial Inclusion: Pricing and Distribution Models and Cross-Country Evidence from 91 Developing Economies"
P(TITLE, bold=True, align="c", size=15, after=14)
if AR:
    _t = P("التأمين متناهي الصغر والشمول المالي: نماذج التسعير والتوزيع وأدلة عبر البلدان من 91 اقتصادًا ناميًا", bold=True, align="c", size=14, after=12); RTL(_t)
    for _r in _t.runs: _r.font.size = Pt(15); _r.bold = True
if not BLIND:
    P("Moustafa Elbehairy ¹ *", align="c", size=12, after=2)
    P("¹ Department of Statistics and Insurance, Faculty of Commerce, Suez Canal University, Ismailia, Egypt", align="c", size=11, after=2)
    P("* Corresponding author: moustafayosri@commerce.suez.edu.eg  |  ORCID 0009-0009-1062-9420", align="c", size=11, after=10)
else:
    P("[Author details removed for double-blind review]", align="c", size=11, italic=True, after=10)
if not AR:
    P(f"Manuscript type: Research article (comparative analysis with a cross-country empirical component)   |   Main text ≈ {WC_DECL:,} words "
      f"(Sections 1–5, excluding abstract, tables, captions and references)   |   Tables: 9   |   Figures: 4   |   JEL: G22, G52, O16, O17, D14", align="c", size=10, after=14)

# ---------------------------------------------------------------- abstract
ABS = (f"Payments inclusion has outrun protection inclusion in developing economies, and the evidence on how microinsurance closes the "
       f"distance is fragmented. This paper asks through which mechanisms microinsurance converts "
       f"access into use, how the main pricing and distribution models compare, and which structural and policy factors go with more, and more equal, "
       f"insurance use. It pairs a structured comparison of pricing and distribution architectures, anchored in the Landscape of Microinsurance "
       f"census, with cross-country regressions on the new Global Findex measure of adults making regular insurance payments "
       f"in 91 developing economies, with extensive sensitivity analysis. Account ownership is the "
       f"one structural correlate that holds in every specification, at {pp(M4,'acc_z')} percentage points per standard deviation in the full sample "
       f"and {100*V['M4_trim30']['coef']['acc_z']:.1f} points without four high-use economies; mobile money adds nothing beyond the account. Dedicated inclusive-insurance regulation is unrelated to the level of use, and its association with a "
       f"narrower gender gap survives resampling but not region effects. The poorest 40 percent use insurance at {100*g_inc['50%']:.0f} percent of the "
       f"rate of the richest 60 percent, and the gradient steepens with national income. A constraint-contingent typology follows: distribution "
       f"innovation widens access only where financial rails exist, and pricing innovation converts access into use only where timing and trust "
       f"allow. Egypt's Financial Regulatory Authority should make embedded cover visible and collect premiums over the account rails being "
       f"licensed; Saudi Arabia's Insurance Authority should measure use among low-income and expatriate residents; the IAIS and the Access to "
       f"Insurance Initiative should judge proportionate regulation by whom it includes.")
if not AR:
    H("Abstract", 1); WC["abstract"] = len(ABS.split())
    P(ABS, after=6)
    P("**Keywords:** microinsurance; financial inclusion; insurance demand; distribution channels; inclusive insurance regulation; Global Findex", after=10)
if AR:
    p = P("الملخص", bold=True, align="r", after=2); RTL(p)
    ar = (f"سبق الشمولُ في المدفوعات الشمولَ في الحماية التأمينية في معظم العالم النامي، وتأتي الأدلة على كيفية تضييق التأمين متناهي الصغر لهذه المسافة في "
          f"أغلبها من تجارب في بلد واحد ومن إحصاءات جانب العرض. يسأل هذا البحث عن الآليات التي يحوّل بها التأمين متناهي الصغر الوصول إلى استخدام، وكيف "
          f"تتقارن نماذج التسعير والتوزيع الرئيسية، وما العوامل البنيوية والسياساتية المصاحبة لاستخدام أكبر وأكثر عدالة للتأمين. ويجمع بين مقارنة منهجية لهياكل "
          f"التسعير والتوزيع، مستندة إلى مسح Landscape of Microinsurance الذي غطى 985 منتجًا في 37 دولة، وبين انحدارات عبر البلدان على مؤشر Global Findex "
          f"الجديد لنسبة البالغين الذين يسددون أقساط تأمين بانتظام في 91 اقتصادًا منخفض ومتوسط الدخل، مقدَّرة بالمربعات الصغرى بأخطاء متينة ومُتحقَّقًا منها "
          f"بنموذج لوجستي كسري وآثار إقليمية واستبعاد المشاهدات واحدةً واحدة واستدلال بالتباديل. ملكية الحساب المالي هي المتغير البنيوي الوحيد الذي يصمد في "
          f"كل المواصفات، بنحو {pp(M4,'acc_z')} نقطة مئوية لكل انحراف معياري في العينة الكاملة و{100*V['M4_trim30']['coef']['acc_z']:.1f} نقطة بعد استبعاد "
          f"أربعة اقتصادات مرتفعة الاستخدام؛ ولا تضيف أموال الهاتف المحمول شيئًا حتى عند إدخال حسابات المؤسسات المالية وحسابات الهاتف منفصلتين. ولا يرتبط "
          f"التنظيم المخصص للتأمين الشامل بمستوى الاستخدام؛ أما ارتباطه بفجوة أضيق بين الجنسين، بنسبة استخدام للنساء إلى الرجال أعلى بنحو {gen_pct:.0f}%، "
          f"فيصمد أمام إعادة المعاينة لكنه لا يصمد أمام الآثار الإقليمية، ولذلك يُعرَض بوصفه مؤشرًا أوليًا. وداخل الدول يستخدم أفقر 40% التأمين بمعدل يعادل "
          f"{100*g_inc['50%']:.0f}% من معدل أغنى 60%، وتزداد الفجوة اتساعًا مع ارتفاع الدخل القومي. ويترتب على ذلك تصنيف تصميمي مشروط بالقيود: ابتكار التوزيع "
          f"يوسّع الوصول فقط حيث توجد البنية المالية الأساسية، وابتكار التسعير يحوّل الوصول إلى استخدام فقط حيث تُعالَج قيود التوقيت والثقة. وينبغي للهيئة العامة "
          f"للرقابة المالية في مصر إظهار التغطية المضمَّنة للمؤمَّن عليهم وتحصيل الأقساط عبر مسارات الحسابات المرخَّصة؛ ولهيئة التأمين السعودية قياس الاستخدام بين "
          f"منخفضي الدخل والمقيمين الوافدين؛ وللجمعية الدولية لمراقبي التأمين ومبادرة الوصول إلى التأمين تقييم التنظيم المتناسب بمَن يشمله.")
    p = P(ar, align="r", after=4); RTL(p)
    p = P("الكلمات المفتاحية: التأمين متناهي الصغر؛ الشمول المالي؛ الطلب على التأمين؛ قنوات التوزيع؛ تنظيم التأمين الشامل؛ Global Findex", align="r", after=12); RTL(p)
    doc.save(f"{VER}/Microinsurance_Financial_Inclusion_Manuscript_v4_الملخص_العربي.docx"); print("saved arabic abstract"); sys.exit(0)

# ================================================================ 1 INTRODUCTION
H("1.  Introduction", 1)
T("Risk is a defining feature of poverty. Households in the informal economies of emerging markets are the most exposed to illness, death, crop "
  "failure and asset loss and the least equipped with formal tools to absorb them. Without insurance they sell assets, cut consumption and pull "
  "children out of school, and they forgo productive investment simply to stay safe, so the welfare cost of being uninsured runs well above the "
  "realised loss (Dercon et al., 2014; Karlan et al., 2014; Janzen & Carter, 2019). The 2025 Global Findex gives the scale. About a quarter of adults "
  "in low- and middle-income economies lived through a natural disaster or extreme weather event in the past three years, more than half of them "
  "lost income or assets, and only 55 percent could raise emergency money within a month without great difficulty (Klapper et al., 2025).")
T("Financial inclusion has moved to the centre of the development agenda, and it has moved fastest on the payments side. Account ownership reached "
  "79 percent of adults worldwide in 2024 and 75 percent in low- and middle-income economies, and registered mobile-money accounts passed 2.3 billion in "
  "2025 (GSMA, 2026; Klapper et al., 2025). Insurance has not kept pace. The Landscape of Microinsurance, the sector's own census, counts 344 million "
  "people covered by 985 products in 37 countries, about 12 percent of the three billion low- and middle-income people those markets contain, with "
  "USD 6.2 billion of premium against an estimated market of USD 40.6 billion (Microinsurance Network, 2025). That distance between payments inclusion "
  "and protection inclusion is the problem this paper takes up.")
T("Following the IAIS, microinsurance is insurance accessed by the low-income population, supplied by a range of carriers and run according to "
  "generally accepted insurance practice (IAIS & CGAP, 2007). What sets it apart is its operating environment rather than its actuarial mechanics: "
  "small and irregular premiums, scarce data, weak enforceability, limited literacy and high relative transaction costs (Churchill, 2006; Biener & "
  "Eling, 2012). A large experimental literature keeps meeting the same puzzle. Even where microinsurance raises welfare and is priced at or below "
  "the actuarially fair level, voluntary uptake is low and renewal fragile (Cole et al., 2013; Platteau et al., 2017). Whether that is a problem of "
  "supply, of demand or of the financial infrastructure between them matters to every supervisor now writing inclusive-insurance rules, and most "
  "where protection inclusion lags furthest behind payments inclusion.")
T("The objective is to establish whether, and under what conditions, microinsurance converts payments inclusion into protection inclusion, using "
  "evidence that can be compared across countries rather than read off single cases. The contribution is threefold. **(1)** The principal pricing "
  "and distribution architectures are compared on one analytical framework and the comparison is grounded in the Landscape census, so that the "
  "trade-offs between reach, cost, value and trust appear in the sector's own numbers. **(2)** A new Findex indicator, the share of adults who made "
  "regular payments to an insurer in the past year, is used across 91 developing economies to test whether the financial rails on which "
  "microinsurance rides, and the regulatory frameworks built to enable it, go with more and more equal use, with the fragility of each estimate "
  "stated rather than assumed. **(3)** The documentary and econometric evidence are brought together in a constraint-contingent design typology "
  "against which two under-studied markets, Egypt and Saudi Arabia, are read.")
T("Three questions organise the analysis. **RQ1:** Through which mechanisms, and under what conditions, does microinsurance advance inclusion, and how "
  "do the leading pricing and distribution models compare? **RQ2:** Across developing economies, which structural and policy factors are associated "
  "with the level of insurance use and with its distribution across income, gender and location? **RQ3:** What follows for design and regulation, in "
  "particular in the Middle East and North Africa? Section 2 reviews the literature by theme, Section 3 sets out the data, the estimators and the "
  "checks announced in advance, Section 4 reports the results, their sensitivity and the discussion, and Section 5 concludes with recommendations "
  "to named bodies, the limitations and a research agenda.")

# ================================================================ 2 LITERATURE
H("2.  Literature Review", 1)
H("2.1  Financial Inclusion as a Layered Construct", 2)
T("Inclusion is better understood as three nested levels than as a banked-or-not binary (Beck et al., 2007; Demirgüç-Kunt et al., 2022). Access is "
  "the availability of a suitable product within physical, administrative and price reach; usage is sustained take-up and renewal, which turns on "
  "trust, comprehension and liquidity; welfare is the realised contribution to consumption smoothing, asset protection and productive risk-taking. "
  "Interventions routinely succeed at access and fail at usage or welfare, and collapsing the three into one number explains much of the apparent "
  "contradiction in the evidence. The distinction maps onto Sen's (1999) capability approach, in which what counts is the substantive freedom a policy "
  "enables, conditional on conversion factors such as literacy, liquidity and trust. The Findex indicator used here measures usage and the Landscape "
  "census measures access; reading them together is what makes the comparison informative.")
H("2.2  Information Economics and the Transaction-Cost Floor", 2)
T("Asymmetric information is the classical barrier to insurance markets (Akerlof, 1970; Rothschild & Stiglitz, 1976), but in microinsurance the "
  "frictions take a different shape. Adverse selection is sharpened by the absence of actuarial data and softened by group or compulsory enrolment; "
  "moral hazard looms in health cover and vanishes in index products. The dominant problem is administrative cost. Writing the gross premium as")
EQ("P = E[L] · (1 + λ) / (1 − c)", 1)
T("where E[L] is the expected claim, λ the risk and profit loading and c the expense ratio, shows why small policies fail: c carries a fixed per-policy "
  "cost of enrolment, collection and verification, so it rises as E[L] falls, and for sums insured of a few hundred dollars it can exceed the pure "
  "premium (Biener & Eling, 2012). The census bears this out: median claims ratios across the 985 products run between 21 and 30 percent by product "
  "size and line, so on a typical product most of each premium dollar goes to cost, commission and margin (Microinsurance Network, 2025). Viability "
  "therefore depends less on refining risk classification than on cutting c, which is the rationale for parametric pricing and embedded distribution.", indent=False)
H("2.3  Behavioural Demand: Timing, Trust and Liquidity", 2)
T("Expected-utility theory predicts solid demand for fairly priced cover against large losses, so low uptake points to systematic departures from it "
  "(Clarke, 2016). Prospect theory explains part of the shortfall: insurance is felt as a certain loss set against a probabilistic gain, and probability "
  "weighting with loss aversion depresses demand for exactly the low-probability, high-severity risks it covers best (Kahneman & Tversky, 1979). The "
  "experimental record identifies which frictions bind. In rural India demand for rainfall insurance was price-elastic yet would not have reached wide "
  "take-up even at U.S. payout ratios (Cole et al., 2013). In Kenya, moving the premium from up-front to pay-at-harvest raised take-up from 5 to 72 "
  "percent (Casaburi & Willis, 2018); in Ethiopia a delayed-payment product lifted uptake from 8 to 24 percent and marketing through funeral societies "
  "lifted it to 43 percent (Belissa et al., 2019); Mexican life-insurance buyers who could pay in instalments kept their cover far more often than those "
  "asked for a lump sum (Bauchet & Morduch, 2019); in Bangladesh discounts moved demand more than equivalent rebates (Hill et al., 2019). Where cover is "
  "bundled into a loan, take-up says little about demand: when an Indian lender made health insurance mandatory with its credit, clients left rather "
  "than buy it (Banerjee et al., 2014). Timing, trust and awareness, not price alone, are the binding constraints (Cole & Xiong, 2017; Jensen & Barrett, 2017).")
H("2.4  Institutions: Trust Substitution and Regulatory Enablement", 2)
T("Where formal enforcement is weak, schemes borrow trust from networks people already rely on: microfinance institutions, cooperatives, mobile "
  "operators and faith-based mutual structures such as Takaful (Biener et al., 2014; Beshir et al., 2023). Regulation cuts both ways. Rules written "
  "for conventional insurers can shut microinsurance out through disproportionate capital and intermediation requirements, while proportionate, "
  "tiered regimes can bring a market into being, and supervisory emphasis has shifted from licensing to conduct of business and product oversight "
  "(IAIS, 2015, 2017). By 2023 the Access to Insurance Initiative counted 40 jurisdictions with inclusive-insurance regulation in force, and four of "
  "the five countries with the highest microinsurance penetration have dedicated regulation (Microinsurance Network, 2025); whether that association "
  "survives controls for income, rails and region is a question Section 4 answers. Mobile money matters here too: M-Pesa strengthened informal "
  "risk-sharing and lifted households out of poverty in Kenya (Jack & Suri, 2014; Suri & Jack, 2016), digital loans cushioned shocks (Suri et al., "
  "2021), mobile money raised health-care use in East Africa (Ahmed & Cowan, 2021) and changed rural saving in Mozambique (Batista & Vicente, 2025). "
  "None of these studies observes formal insurance.")
H("2.5  Integrative Framework", 2)
T("Putting the four lenses together (Table 1) treats inclusion outcomes as jointly determined by a supply-side architecture of design, pricing and "
  "distribution and by demand- and institution-side conversion factors. The framework is conditional: each design choice relaxes some constraints and "
  "activates others, so no model dominates everywhere. It also yields the expectations tested in Section 4. If distribution innovation works by "
  "lowering transaction costs on existing rails, the depth of those rails, account ownership, should predict insurance use more strongly than any "
  "single channel such as mobile money. If regulation works by structuring markets rather than by creating demand, its footprint should appear in "
  "the composition of users rather than in their number. Gender gaps in access to finance are documented across Sub-Saharan Africa (Aterido et al., "
  "2013), and religiosity shapes the uptake of formal finance in Muslim-majority economies (Ozili, 2025; Shair et al., 2026), so the composition "
  "test is not a formality.")
TABLE("Table 1. Integrative framework linking theoretical lenses to inclusion outcomes and to testable expectations",
      ["Theoretical lens", "Core mechanism", "Constraint on inclusion", "Implied design response", "Cross-country expectation"],
      [["Information economics", "Selection, hazard, transaction costs", "Expense ratio exceeds pure premium on small policies", "Group enrolment; parametric triggers; embedded delivery", "Use rises with the depth of payment rails (accounts)"],
       ["Behavioural theory", "Loss aversion, probability weighting, present bias", "Suppressed demand despite favourable pricing", "Premium timing; framing; trust signals; bundling", "Use is not explained by disaster exposure alone"],
       ["Institutional theory", "Trust substitution; regulatory (dis)enablement", "Stalled diffusion; intermediation gaps", "Proportionate regulation; trusted-network distribution", "Regulation changes who is covered more than how many"],
       ["Capability approach", "Conversion of access into freedom", "Access without usage or welfare", "Literacy, liquidity, timing as design parameters", "Usage gradients by income and gender persist within countries"]],
      note="Note. Access, usage and welfare are nested outcomes jointly determined by supply-side architecture and demand- and institution-side conversion factors.",
      widths=[2.6, 3.2, 3.2, 3.4, 3.6])
T("Read together, the four strands leave two things undone. The explanations for low uptake have been tested one at a time in randomised trials, "
  "and the reviews that synthesise them (Eling et al., 2014; Platteau et al., 2017) catalogue determinants drawn from those trials and from single-"
  "country household surveys. The typology of pricing and distribution models that "
  "practitioners work with (Churchill, 2006; Biener & Eling, 2012; Biener et al., 2014) was built from case studies and from supply-side counts of lives "
  "covered rather than from comparable data on who pays for insurance, because until the 2025 Findex round no demand-side measure of insurance use "
  "existed that could be compared across developing economies. The framework's central prediction, that distribution and pricing innovation convert "
  "access into usage only where rails, trust and liquidity allow, has therefore not been confronted with cross-country adult-level data: in the "
  "taxonomy of Müller-Bloch and Kranz (2015) and Robinson et al. (2011), an empirical gap. The second shortcoming is one of coverage. The experimental "
  "evidence comes from South Asia and Sub-Saharan Africa, the Landscape census has no Middle Eastern grouping, and Egypt, Saudi Arabia and the wider "
  "region, where the religious-legitimacy barrier and the Takaful response remain under-measured, are thinly represented: a population gap. RQ1 and "
  "RQ2 address the first and RQ3 the second.")

# ================================================================ 3 METHODOLOGY
H("3.  Methodology", 1)
H("3.1  Research Design and Data", 2)
T("The study has two parts. The first is a structured comparison of pricing and distribution architectures that follows the disciplines of an "
  "integrative review (Snyder, 2019): explicit selection criteria, an analytical scheme fixed in advance and a replicable comparison matrix. Sources "
  "were identified through Scopus, Web of Science and EconLit and the repositories of the ILO Impact Insurance Facility, CGAP and the Microinsurance "
  "Network, and the comparison is anchored in the Landscape of Microinsurance, which compiles self-reported data from 294 insurers on 985 products in "
  "37 countries for 2023, including people covered, premiums, claims ratios, channels and payment methods by region and line (Microinsurance Network, "
  "2025). Each architecture is assessed on four dimensions fixed in advance, pricing logic, distribution cost, trust and value, and regulatory "
  "dependence, and on the three inclusion outcomes of Section 2.1. Four pricing architectures are distinguished, community or flat rating, risk "
  "rating, parametric or index pricing and subsidised pricing, and four distribution architectures, agents and brokers, financial institutions and "
  "microfinance institutions, mobile-network operators, and cooperatives, NGOs and embedded enrolment. The census supplies, for each, the lives "
  "covered, the premium share, the median claims ratio and the payment method by region, and the comparison uses those figures rather than the "
  "case-study anecdotes on which earlier typologies rested.")
T("The second part uses country-level data from the 2025 Global Findex, built on interviews with about 145,000 adults in 141 economies during 2024 "
  "(Klapper et al., 2025). The dependent variable is the share of adults aged 15 and over who report having made regular payments to an insurance "
  "agent or company in the past twelve months, an indicator new to this round and, as far as I can establish, the first demand-side measure of "
  "insurance use available on a comparable basis across developing economies. Findex also reports it for the poorest 40 and richest 60 percent of "
  "households, for women and men and for rural and urban residents, so within-country gradients can be measured directly. The explanatory variables "
  "capture the framework's conversion factors: account ownership (any account at a financial institution or mobile-money provider), financial-"
  "institution account ownership and mobile-money account ownership from Findex; log GDP per capita, the rural population share and the vulnerable-"
  "employment share, a proxy for informality, from the World Development Indicators; the share of adults who experienced a natural disaster in the "
  "past three years from Findex; and a binary indicator of inclusive-insurance regulation in force in 2023, coded from the Access to Insurance "
  "Initiative map reproduced in the Landscape report. The map distinguishes jurisdictions with a dedicated framework in force from those with one "
  "under development; the main coding counts only the former, and the fourteen member states of the Conférence Interafricaine des Marchés d'Assurances "
  "(CIMA), whose microinsurance book of regulations has applied regionally since 2012, are coded as regulated. A broader coding that also counts "
  "frameworks under development is carried as a sensitivity. Mobile-money ownership is set to zero, with a separate indicator, in the economies where "
  "Findex does not field the mobile-money module, so that those economies are not lost from the sample. Because the Findex account measure contains "
  "mobile-money accounts, the two rails overlap by construction; Section 4.2 separates them using the financial-institution account series that "
  "Findex publishes alongside.")
T(f"The sample is every low- and middle-income economy with non-missing data: {M4['n']} in the level models, {G1['n']} where Findex publishes the income "
  f"split and {G3['n']} where it publishes the gender split. The restriction to developing economies is deliberate. The research questions concern "
  f"microinsurance's target population, and in high-income economies the indicator is dominated by compulsory motor and employer-based health cover, so "
  f"pooling them would let a different mechanism drive the variance. Within that population the sample is exhaustive rather than selected, which is what "
  f"makes the estimates representative of the developing world rather than of a convenience sample of success stories. The WDI regressors are taken "
  f"at the latest available year between 2019 and 2024 so that no economy is lost to a single missing year, and GDP per capita enters in logs because "
  f"the relationship between income and formal finance is proportional rather than linear across the income range covered. Missing mobile-money data "
  f"are a feature of the Findex design rather than non-response: the module is fielded only where a mobile-money service operates, so the economies "
  f"without it are those without the rail, and they are retained with an indicator rather than dropped. Table 2 lists the variables.")
TABLE("Table 2. Variables, definitions and sources",
      ["Variable", "Definition", "Source", "Mean (SD)"],
      [["Insurance use", "Adults 15+ who made regular payments to an insurance agent or company in the past year (%)", "Findex 2025 (fin19)", "13.2 (9.5)"],
       ["Account ownership", "Adults with an account at a financial institution or mobile-money provider (%)", "Findex 2025", "59.7 (19.9)"],
       ["Financial-institution account", "Adults with an account at a bank or similar institution (%)", "Findex 2025", "48.9 (25.0)"],
       ["Mobile-money account", "Adults with a mobile-money account (%); 0 where no service is surveyed, with a missing-data indicator", "Findex 2025", "31.5 (20.9)"],
       ["GDP per capita", "Current USD, log", "WDI", "8.21 (0.95)"],
       ["Rural share", "Rural population (% of total)", "WDI", "43.5 (19.4)"],
       ["Vulnerable employment", "Own-account and contributing family workers (% of employment)", "WDI (ILO)", "46.2 (23.4)"],
       ["Disaster exposure", "Adults who experienced a natural disaster or severe weather event in the past three years (%)", "Findex 2025 (fin24c)", "25.5 (17.2)"],
       ["Inclusive-insurance regulation", "1 if dedicated inclusive or microinsurance regulation in force in 2023", "A2ii map (Microinsurance Network, 2025)", "0.53"],
       ["Income gradient", "Insurance use of poorest 40% ÷ richest 60%", "Findex 2025", f"{g_inc['mean']:.2f} ({g_inc['std']:.2f})"],
       ["Gender gradient", "Insurance use of women ÷ men", "Findex 2025", f"{g_gen['mean']:.2f} ({g_gen['std']:.2f})"]],
      note=f"Note. Means and standard deviations refer to the {M4['n']}-economy estimation sample ({G1['n']} and {G3['n']} economies for the gradients); mobile-money data are missing for {M4['n']-75} economies. WDI = World Development Indicators, latest available year 2019–2024.",
      widths=[3.3, 6.6, 3.6, 2.4], size=9)
H("3.2  Model and Estimation", 2)
T("Cross-country regressions of Findex indicators on income, infrastructure and policy variables, estimated by ordinary least squares with "
  "heteroskedasticity-robust standard errors, are the established first-pass design in this literature: Allen et al. (2016) model account ownership "
  "and use across economies in this way, the Findex reports do so for successive rounds (Demirgüç-Kunt et al., 2022) and the finance-and-inequality "
  "work on which they build used the same cross-section of countries (Beck et al., 2007). The level of insurance use is modelled as")
EQ("Ins_i = α + β′X_i + γ Reg_i + δ_r + ε_i", 2)
T("where X_i collects the standardised continuous regressors, Reg_i the regulation indicator and δ_r region effects. Four steps follow. Findex, WDI and "
  "regulation data are merged at the economy level and the continuous regressors are standardised within the estimation sample, so coefficients read "
  "as percentage points of insurance use per standard deviation. Specifications are built up from a baseline with income, rurality, informality and "
  "exposure (M1), adding the rails (M2), regulation (M3) and region effects (M4), with an indicator for economies without mobile-money data carried from "
  "M2 onwards, so the transfer of explanatory power from income to rails can be watched as controls enter. Because the dependent variable is a "
  "proportion, the level equation is re-estimated as a fractional logit, the quasi-likelihood estimator of Papke and Wooldridge (1996), implemented as "
  "a binomial generalised linear model with a logit link and robust errors and summarised by average marginal effects, each coefficient multiplied by "
  "the fitted μ(1 − μ) and averaged over economies. Inclusion gradients are modelled as", indent=False)
EQ("ln(Ins_i^poorest40 / Ins_i^richest60) = α + β′X_i + γ Reg_i + ε_i", 3)
T("and analogously for women relative to men, so coefficients read as approximate proportional changes in the ratio; a companion model takes the level "
  "of use among the poorest 40 percent as dependent variable with the full controls. HC1 errors are used throughout, with HC3 as a check. The design is "
  "cross-sectional and the estimates are associations, not causal effects; Section 5.2 says what that limits.", indent=False)
H("3.3  Tests, Sensitivity Analyses and Reproducibility", 2)
T("The tests follow the order in which the framework generates them. The documentary comparison comes first because it fixes the architectures whose "
  "correlates the regressions test (Section 4.1.1). The level models M1 to M4 follow (Section 4.1.2), with the account coefficient as the test of the "
  "rails expectation and the regulation coefficient as the test of the regulation expectation. The gradient models G1 to G3 (Section 4.1.3) test whether "
  "regulation's footprint lies in the composition of users, and a regional reading closes the results (Section 4.1.4). Section 4.2 then reports, in this "
  "order, checks announced here. (a) The fractional logit, region effects (M4 against M3), a regulation-by-mobile-money interaction (M5) and the "
  "re-estimation of the headline effects on sub-populations. (b) The overlap between the two rails: variance-inflation factors, a specification with "
  "financial-institution and mobile-money accounts entered separately, and mobile money entered alone. (c) Influence and sample composition: Cook's "
  "distances, leave-one-out re-estimation over every economy, HC3 errors, exclusion of economies with use above 30 percent, exclusion of the CIMA "
  "states and the broader regulation coding that counts frameworks under development. (d) The regulation-gender association in particular, which "
  "rests on 47 economies: leave-one-out, influential-case deletion, additional controls, region effects, a permutation test and a wild bootstrap of "
  "the regulation coefficient, and a Holm adjustment across the regulation tests reported in the paper. The permutation test reassigns the regulation "
  "label at random across the 47 economies 5,000 times, refits the model each time and asks how often a t-statistic as large as the observed one "
  "arises by chance; the wild bootstrap holds the design fixed, multiplies the restricted residuals by random signs and refits, which guards against "
  "the small-sample behaviour of robust standard errors. The Holm adjustment is the conservative correction for having reported the regulation "
  "coefficient in several models. Conclusions are drawn from the range of estimates these checks produce, not from the point estimate of one "
  "specification, and where a result survives some checks and not others the paper says so rather than choosing the specification that flatters it.")
if BLIND:
    T("All computations use Python 3.11 with pandas and statsmodels (Seabold & Perktold, 2010). The estimators are deterministic; the permutation and "
      "bootstrap draws use seed 2026. The scripts that build the merged sample, estimate every model, run the sensitivity analyses and draw the figures "
      "reproduce every number in Tables 2 and 5 to 8 and every figure from the public source files, and are available in a public repository (link "
      "withheld for review).")
else:
    _p = T("All computations use Python 3.11 with pandas and statsmodels (Seabold & Perktold, 2010). The estimators are deterministic; the permutation and "
           f"bootstrap draws use seed 2026. The scripts that build the merged sample, estimate every model, run the sensitivity analyses and draw the figures "
           f"reproduce every number in Tables 2 and 5 to 8 and every figure from the public source files, and are openly available at {REPO} (release v1.0.0). ")
    _r = _p.add_run("Zenodo DOI: to be inserted after release."); _r.font.name = FONT; _r.font.highlight_color = WD_COLOR_INDEX.YELLOW

# ================================================================ 4 EMPIRICAL ANALYSIS
H("4.  Empirical Analysis", 1)
H("4.1  Results", 2)
H("4.1.1  Pricing and Distribution Architectures and Where the Sector Stands", 3)
T("Table 3 compares four pricing and four distribution architectures on the framework's dimensions and, where the census allows, on the sector's own "
  "numbers. The channels that reach the most people are not the channels that collect the most premium or return the most value. In Asia and the "
  "Pacific agents and brokers reach 186 million people, 163 million of them in India, yet collect 23 percent of premiums while financial institutions "
  "collect 74 percent; in Africa agents and brokers account for 34 percent of premiums and reach 7.8 million people, whereas mobile-network operators "
  "reach 2.5 million and drive 2 percent of premiums (Microinsurance Network, 2025). Low-touch channels buy breadth at the cost of ticket size and, often, "
  "of awareness. Value returned to customers is highest where distribution runs through member-based organisations, with claims ratios for "
  "cooperative channels far above the sector's medians, and mandatory or embedded products return more than voluntary ones, largely because lenders "
  "want credit-life claims paid. Agricultural index products depend on subsidy: 58 percent receive some subsidy and those products carry 97 percent of "
  "the people covered in the line. Parametric pricing has solved the verification problem but not the affordability problem. Payment method tells the "
  "same story from the customer's side. Premiums are still collected mostly in cash or deducted from a loan or a salary; mobile money pays for a minority "
  "of products even in Africa, where it is most developed, and the products it does pay for are the small, often free, airtime-linked covers whose "
  "holders rarely know they are insured. The architecture that reaches people and the architecture that collects a premium they recognise as their "
  "own are, in the census, different architectures.")
TABLE("Table 3. Comparative assessment of microinsurance pricing and distribution architectures",
      ["Architecture", "Mechanism", "Principal limitation", "Landscape 2024 evidence (2023 data)", "Layer advanced"],
      [[("Pricing", True), "", "", "", ""],
       ["Community / flat rating", "Uniform group premium; solidarity-compatible", "Within-group cross-subsidy; selection if voluntary", "Dominant in funeral and Takaful schemes; in Zimbabwe most covered lives are funeral plans", "Access"],
       ["Risk-rated", "Actuarial fairness", "Data and verification cost exceed premium", "Confined to motor and to larger-ticket products", "—"],
       ["Parametric / index", "Objective trigger; no claims verification or moral hazard", "Basis risk; comprehension burden", "58% of agriculture products subsidised, covering 97% of agricultural lives", "Usage (if basis risk low)"],
       ["Subsidised", "Removes affordability barrier", "Fiscal sustainability; dependence", "Government schemes drive top-10 penetration in Peru and Zambia", "Access → Usage"],
       [("Distribution", True), "", "", "", ""],
       ["Agent / broker", "High-touch education and trust", "High unit cost", "Africa: 7.8 m lives, 34% of premiums; Asia: 186 m lives (163 m in India), 23% of premiums", "Usage, Welfare"],
       ["Financial institution / MFI", "Existing client base and collection rails", "Coverage tied to borrowing; low awareness", "Asia: 74% of premiums; LAC: MFIs 11.8 m lives", "Access, Usage"],
       ["Mobile-network operator", "Mobile-money collection and payout", "Low engagement; small tickets", "Africa: 2.5 m lives but 2% of premiums", "Access"],
       ["Cooperative / NGO / embedded", "Member trust; automatic enrolment", "Policyholders may be unaware of cover", "Highest claims ratios through cooperatives and NGOs; mandatory > voluntary", "Access (breadth); value"]],
      note="Note. LAC = Latin America and the Caribbean; MFI = microfinance institution. Figures from Microinsurance Network (2025).",
      widths=[3.0, 3.2, 3.0, 4.6, 2.2], size=8.5)
T("Table 4 summarises the census by region. Asia and the Pacific holds 268 million of the 344 million people covered and captures 36 percent of its "
  "estimated market value on a median premium of USD 7 per person; Africa and Latin America reach 8 to 9 percent of their target populations and "
  "capture 4 to 5 percent of value at three to six times the premium per person. That is the transaction-cost floor of equation (1) at regional scale: "
  "the largest, densest and most regulated market has driven unit premiums down and volumes up, while thinner markets remain stuck with high unit "
  f"costs. The Findex measure tells a complementary story. Across the {M4['n']} economies a mean of 13.2 percent of adults made regular insurance payments "
  f"in 2024, from {100*H_['Pakistan']['ins']:.1f} percent in Pakistan and {100*H_['Egypt, Arab Rep.']['ins']:.1f} percent in Egypt to "
  f"{100*H_['Ethiopia']['ins']:.0f} percent in Ethiopia, where community-based health insurance enrols tens of millions, and 50 percent in China. "
  f"Regional means run from {100*reg_by['South Asia']['ins']:.0f} percent in South Asia and {100*reg_by['Sub-Saharan Africa']['ins']:.0f} percent in "
  f"Sub-Saharan Africa to {100*reg_by['Middle East & North Africa']['ins']:.0f} percent in the Middle East and North Africa and "
  f"{100*reg_by['East Asia & Pacific']['ins']:.0f} percent in East Asia.")
TABLE("Table 4. Microinsurance reach and market capture by region, 2023",
      ["Region (focus countries)", "Target population (m)", "People covered (m)", "Share covered", "Premium per person (USD)", "Estimated market (USD bn)", "Value captured"],
      [["Africa (15)", "466.9", "38.1", "8.2%", "32", "9.8", "4%"],
       ["Asia and the Pacific (11)", "2,115.7", "268.2", "12.7%", "7", "13.8", "36%"],
       ["Latin America and the Caribbean (11)", "406.2", "37.3", "9.2%", "41", "16.9", "5%"],
       [("All regions (37)", True), ("2,988.8", True), ("343.6", True), ("11.5%", True), ("13", True), ("40.6", True), ("15%", True)]],
      note="Note. Target population = people earning 2–20 international dollars per day (PPP). Premium per person is the weighted average. Source: Microinsurance Network (2025, Table 2).",
      widths=[4.2, 2.2, 2.0, 1.8, 2.2, 2.2, 1.8], size=9)
H("4.1.2  What Predicts Insurance Use Across Developing Economies", 3)
T(f"Figure 1 plots insurance use against account ownership and Table 5 reports the regressions. In the baseline (M1) log GDP per capita is the main "
  f"correlate, at {pp(M1,'lgdp_z')} percentage points per standard deviation. Adding the rails (M2) raises the explained variance from "
  f"{100*M1['r2']:.0f} to {100*M2['r2']:.0f} percent and moves the income effect almost entirely onto account ownership, which is associated with "
  f"{pp(M2,'acc_z')} points per standard deviation ({pv(M2,'acc_z')}). Mobile-money penetration has no independent association with insurance use; its "
  f"coefficient is small and negative in every specification ({pp(M4,'mm_z')} points with region effects, {pv(M4,'mm_z')}). Regulation (M3) adds "
  f"nothing to the level of use ({pp(M3,'reg')} points, {pv(M3,'reg')}). Disaster exposure is unrelated to use in every model, which is the "
  f"cross-country face of the low-uptake puzzle: the economies whose adults report the most weather shocks are not the economies where more adults "
  f"insure. With region effects (M4) the account coefficient is {pp(M4,'acc_z')} points and the fit {100*M4['r2']:.0f} percent. The rural share "
  f"carries a small positive coefficient throughout and vulnerable employment a negative one, neither of them precisely estimated once the rails enter; "
  f"what the build-up from M1 to M4 shows is that income predicts insurance use mainly because richer economies have more accounts, not because "
  f"richer adults buy more cover at a given level of financial access.")
TABLE("Table 5. Correlates of insurance use among adults in developing economies, 2024 (dependent variable: adults making regular insurance payments, %)",
      ["Regressor", "M1 Baseline", "M2 Rails", "M3 Regulation", "M4 Region effects", "Fractional logit AME"],
      [["log GDP per capita (z)", cell(M1, "lgdp_z"), cell(M2, "lgdp_z"), cell(M3, "lgdp_z"), cell(M4, "lgdp_z"), f"{100*AME['lgdp_z']:.1f}"],
       ["Rural share (z)", cell(M1, "rural_z"), cell(M2, "rural_z"), cell(M3, "rural_z"), cell(M4, "rural_z"), f"{100*AME['rural_z']:.1f}"],
       ["Vulnerable employment (z)", cell(M1, "vuln_z"), cell(M2, "vuln_z"), cell(M3, "vuln_z"), cell(M4, "vuln_z"), f"{100*AME['vuln_z']:.1f}"],
       ["Disaster exposure (z)", cell(M1, "dis_z"), cell(M2, "dis_z"), cell(M3, "dis_z"), cell(M4, "dis_z"), f"{100*AME['dis_z']:.1f}"],
       ["Account ownership (z)", "–", cell(M2, "acc_z"), cell(M3, "acc_z"), cell(M4, "acc_z"), f"{100*AME['acc_z']:.1f}"],
       ["Mobile-money account (z)", "–", cell(M2, "mm_z"), cell(M3, "mm_z"), cell(M4, "mm_z"), f"{100*AME['mm_z']:.1f}"],
       ["Inclusive-insurance regulation", "–", "–", cell(M3, "reg"), cell(M4, "reg"), f"{100*AME['reg']:.1f}"],
       ["Region effects", "No", "No", "No", "Yes", "No"],
       ["Observations", str(M1["n"]), str(M2["n"]), str(M3["n"]), str(M4["n"]), str(R["FL_fractional_logit"]["n"])],
       ["R²", f"{M1['r2']:.3f}", f"{M2['r2']:.3f}", f"{M3['r2']:.3f}", f"{M4['r2']:.3f}", "–"]],
      note="Note. Coefficients are percentage points of insurance use per one standard deviation of the regressor (or for regulation = 1); HC1 heteroskedasticity-robust standard errors in parentheses. "
           "∗∗∗ p < 0.01, ∗∗ p < 0.05, ∗ p < 0.10. M2–M4 and the fractional logit include an indicator for economies without mobile-money data. AME = average marginal effect.",
      widths=[3.6, 2.4, 2.4, 2.4, 2.6, 2.4], size=8.5)
FIG(f"{FIGS}/fig1_scatter.png", f"Figure 1. Insurance use and account ownership in {M4['n']} developing economies, 2024. Bubble size scales with the share of adults holding a mobile-money account; "
    "black rings mark economies with inclusive-insurance regulation in force in 2023. Dashed line: bivariate fit. Sources: Klapper et al. (2025); Microinsurance Network (2025).", width_cm=15.5)
H("4.1.3  Who Is Included: Income, Gender and Location Gradients", 3)
T(f"Levels hide composition. Figure 2 shows use among the poorest 40 and richest 60 percent of households in the {G1['n']} economies with the split. "
  f"The median ratio is {g_inc['50%']:.2f}, so the poorer segment uses insurance at just over half the rate of the richer one, and in a quarter of "
  f"economies at less than {g_inc['25%']:.2f} of it. The gender ratio has a median of {g_gen['50%']:.2f} and the rural-to-urban ratio {g_rur['50%']:.2f}; the "
  f"location gradient is flatter than either. The ordering in Figure 2 is instructive. The smallest income ratios are found in economies where use is "
  f"low overall and concentrated in formal employment, and the ratios closest to one in economies with a public or community scheme that enrols the "
  f"poor directly; a steep gradient is therefore not a sign of a large market but of a market that has not reached below its formal-sector base. "
  f"Table 6 models the gradients. "
  f"of log GDP per capita goes with a {abs(100*G1['coef']['lgdp_z']):.0f} percent lower poorest-to-richest ratio ({pv(G1,'lgdp_z')}), while account "
  f"ownership raises use among the poorest 40 percent by {pp(G2,'acc_z')} points per standard deviation ({pv(G2,'acc_z')}), as much as for the "
  f"population as a whole. Regulation, unrelated to the level of use, is associated in G3 with a women-to-men ratio {gen_pct:.0f} percent higher "
  f"({pv(G3,'reg')}); its coefficient on the income ratio is negative and imprecise. Section 4.2.4 examines how much weight that gender estimate "
  f"can bear.")
TABLE("Table 6. Correlates of within-country inclusion gradients in insurance use, 2024",
      ["Regressor", "G1: ln(poorest 40% ÷ richest 60%)", "G2: Use among poorest 40% (pp)", "G3: ln(women ÷ men)"],
      [["log GDP per capita (z)", cell(G1, "lgdp_z", 1, 2), cell(G2, "lgdp_z"), cell(G3, "lgdp_z", 1, 2)],
       ["Account ownership (z)", cell(G1, "acc_z", 1, 2), cell(G2, "acc_z"), cell(G3, "acc_z", 1, 2)],
       ["Mobile-money account (z)", cell(G1, "mm_z", 1, 2), cell(G2, "mm_z"), cell(G3, "mm_z", 1, 2)],
       ["Inclusive-insurance regulation", cell(G1, "reg", 1, 2), cell(G2, "reg"), cell(G3, "reg", 1, 2)],
       ["Rural, informality, exposure controls", "No", "Yes", "No"],
       ["Observations", str(G1["n"]), str(G2["n"]), str(G3["n"])],
       ["R²", f"{G1['r2']:.3f}", f"{G2['r2']:.3f}", f"{G3['r2']:.3f}"]],
      note="Note. G1 and G3 coefficients are changes in the log ratio (approximately proportional changes); G2 coefficients are percentage points. HC1 robust standard errors in parentheses. ∗∗∗ p < 0.01, ∗∗ p < 0.05, ∗ p < 0.10. All models include the missing-mobile-money indicator.",
      widths=[4.2, 4.0, 3.8, 3.8], size=9)
FIG(f"{FIGS}/fig3_gradient.png", f"Figure 2. Insurance use among the poorest 40 percent and the richest 60 percent of households, {G1['n']} developing economies, 2024. Teal squares mark economies with inclusive-insurance regulation in force in 2023. Source: Klapper et al. (2025).", width_cm=14.5)
H("4.1.4  Regional Patterns", 3)
T(f"South and Southeast Asia is the index-insurance laboratory and the regulatory exemplar. India's rural and social-sector obligations and its 2005 "
  f"microinsurance regulations, and the Philippines' tiered framework built out from 2010, underpin the region's 12.7 percent reach and 36 percent value "
  f"capture, yet Findex use in India ({100*H_['India']['ins']:.0f} percent) and the Philippines ({100*H_['Philippines']['ins']:.0f} percent) sits below "
  f"the sample mean, a reminder that census reach and self-reported use diverge when cover is embedded in credit or public schemes. Sub-Saharan "
  f"Africa's path was shaped by mobile money, which now gives Kenya and Ghana account ownership above 80 percent; both record insurance use of only "
  f"{100*H_['Kenya']['ins']:.0f} percent, and Kenya's poorest 40 percent use insurance at half the rate of its richest 60 percent. Mobile rails have "
  f"widened access without, on their own, converting it into protection. The Middle East and North Africa combines the lowest account ownership of any "
  f"region ({100*reg_by['Middle East & North Africa']['acc']:.0f} percent) with middling use ({100*reg_by['Middle East & North Africa']['ins']:.0f} percent) "
  f"and almost no dedicated regulation, a profile in which formal-sector and compulsory cover, not microinsurance, explains most of what use there is. "
  f"Latin America combines the highest median premium per person in the census with modest reach and, in the Findex data, use close to the sample mean "
  f"at account ownership well above it, which is where the typology expects trust and product design rather than rails to bind; Europe and Central "
  f"Asia, with near-universal accounts and compulsory motor cover, records the highest use outside China and is the clearest case of the indicator "
  f"measuring formal insurance rather than microinsurance. Table 4 and Figure 1 should therefore be read together: the census locates where "
  f"microinsurance is sold, and Findex locates where adults, for whatever reason, pay for cover.")

# ---------------------------------------------------------------- 4.2 ROBUSTNESS
H("4.2  Robustness and Sensitivity", 2)
H("4.2.1  Planned Checks: Estimator, Region Effects, Interaction and Sub-populations", 3)
T(f"The fractional logit reproduces the OLS pattern. Its average marginal effect for account ownership is {100*AME['acc_z']:.1f} points per standard "
  f"deviation against {pp(M4,'acc_z')} in M4 and {pp(M3,'acc_z')} in M3; the marginal effects of regulation and mobile money are {100*AME['reg']:.1f} and "
  f"{100*AME['mm_z']:.1f}, so neither the ranking of regressors nor the two null results depends on treating a bounded share as unbounded (Figure 3). "
  f"Region effects change little: moving from M3 to M4 lifts the fit from {100*M3['r2']:.0f} to {100*M4['r2']:.0f} percent, the account coefficient "
  f"moves from {pp(M3,'acc_z')} to {pp(M4,'acc_z')} and the regulation coefficient stays at {pp(M4,'reg')} ({pv(M4,'reg')}). The interaction model (M5) "
  f"asks whether regulation works through the mobile channel. It does not: the product term is {pp(M5,'mm_z:reg')} points ({pv(M5,'mm_z:reg')}), the "
  f"regulation main effect {pp(M5,'reg')} and the account coefficient {pp(M5,'acc_z')}. On sub-populations, the account coefficient among the poorest 40 "
  f"percent (G2) is {pp(G2,'acc_z')} points ({pv(G2,'acc_z')}) and regulation again has no level association there ({pp(G2,'reg')} points, {pv(G2,'reg')}). "
  f"Figure 3 puts the two estimators side by side: the OLS intervals and the fractional-logit marginal effects overlap for every regressor, and only "
  f"the account coefficient excludes zero in both.")
FIG(f"{FIGS}/fig2_coef.png", "Figure 3. Estimated effects on insurance use from the region-effects OLS model (M4, with 95 percent confidence intervals) and average marginal effects from the fractional logit.", width_cm=14)
H("4.2.2  The Two Rails Overlap: Separating Financial-Institution and Mobile-Money Accounts", 3)
T(f"The Findex account measure counts anyone with a financial-institution or a mobile-money account, so a mobile-money regressor entered beside it "
  f"can only pick up mobile money's contribution over and above an account of any kind. That is the comparison the framework wants, but it invites the "
  f"objection that the mobile-money null is mechanical. It is not. Collinearity is moderate (variance-inflation factors of {V['vif_M3']['acc_z']:.1f} for "
  f"account ownership and {V['vif_M3']['mm_z']:.1f} for mobile money; the correlation between the two is {V['corr_acc_mm']:.2f}, and on average mobile-money-"
  f"only accounts add {100*V['share_mm_only_mean']:.0f} points to account ownership). When financial-institution accounts and mobile-money accounts enter "
  f"as separate regressors with region effects, the former carries {100*V['M4_fiacc_mm']['coef']['fiacc_z']:.1f} points per standard deviation "
  f"({pv(V['M4_fiacc_mm'],'fiacc_z')}) and the latter {100*V['M4_fiacc_mm']['coef']['mm_z']:.1f} ({pv(V['M4_fiacc_mm'],'mm_z')}); restricted to the 75 "
  f"economies where mobile money is surveyed the figures are {100*V['M4_mm_surveyed_only']['coef']['fiacc_z']:.1f} and "
  f"{100*V['M4_mm_surveyed_only']['coef']['mm_z']:.1f}. Entered alone, without any account variable, mobile money has a coefficient of "
  f"{100*V['M4_mm_only']['coef']['mm_z']:.1f} points ({pv(V['M4_mm_only'],'mm_z')}) and the income effect reappears at {100*V['M4_mm_only']['coef']['lgdp_z']:.1f}. "
  f"Mobile money does not predict insurance use in this sample even when it is given the field to itself (Table 7).")
H("4.2.3  Influence, Sample Composition and Coding", 3)
T(f"Table 7 collects the sensitivity of the three level results. Cook's distances single out Ethiopia, China and Mongolia, the three economies with use "
  f"above 30 percent that also have unusual account profiles. Dropping each economy in turn moves the account coefficient between "
  f"{100*V['M4_loo']['acc_min']:.1f} and {100*V['M4_loo']['acc_max']:.1f} points with a maximum p-value of {V['M4_loo']['acc_p_max']:.3f}; dropping the four "
  f"economies with use above 30 percent lowers it to {100*V['M4_trim30']['coef']['acc_z']:.1f} points ({pv(V['M4_trim30'],'acc_z')}), which is the honest "
  f"lower bound of the headline. The mobile-money coefficient stays negative in every leave-one-out sample ({100*V['M4_loo']['mm_min']:.1f} to "
  f"{100*V['M4_loo']['mm_max']:.1f}) and the regulation coefficient never approaches significance (smallest p = {V['M4_loo']['reg_p_min']:.2f}). HC3 errors, "
  f"the exclusion of the {V['n_cima_in_sample']} CIMA states, whose regulation is regional rather than national, and the broader coding that counts "
  f"frameworks under development as regulated leave the pattern intact; under the broader coding the regulation coefficient is "
  f"{100*V['M4_regany']['coef']['reg_any']:.1f} points ({pv(V['M4_regany'],'reg_any')}). The income-gradient estimate in G1 is similarly stable to "
  f"leave-one-out ({V['G1_loo']['b_min']:.2f} to {V['G1_loo']['b_max']:.2f}, maximum p = {V['G1_loo']['p_max']:.3f}) and to trimming the five smallest "
  f"ratios ({V['G1_trim_small_ratios']['coef']['lgdp_z']:.2f}, {pv(V['G1_trim_small_ratios'],'lgdp_z')}), but its precision falls when the full controls "
  f"({V['G1_controls']['coef']['lgdp_z']:.2f}, {pv(V['G1_controls'],'lgdp_z')}) or region effects ({V['G1_regionFE']['coef']['lgdp_z']:.2f}, "
  f"{pv(V['G1_regionFE'],'lgdp_z')}) are added; the direction never changes. Two readings of the trimmed estimate are possible and the paper adopts the "
  f"cautious one. The four excluded economies are not errors; China's near-universal accounts and Ethiopia's community-based health insurance are real, "
  f"and they are exactly the cases in which a national scheme or a dense financial system converts access into use at scale. But a coefficient that "
  f"falls by a third when they leave is a coefficient that should be quoted as a range, and the recommendations in Section 5 are written so that they "
  f"hold at the lower end of it.")
TABLE("Table 7. Sensitivity of the level results: account, mobile-money and regulation coefficients across specifications and samples",
      ["Specification / sample", "n", "Account (pp per SD)", "Mobile money (pp per SD)", "Regulation (pp)"],
      [["M4, HC1 (Table 5)", str(M4["n"]), c2(M4, "acc_z"), c2(M4, "mm_z"), c2(M4, "reg")],
       ["M4, HC3 errors", str(V["M4_HC3"]["n"]), c2(V["M4_HC3"], "acc_z"), c2(V["M4_HC3"], "mm_z"), c2(V["M4_HC3"], "reg")],
       ["Financial-institution and mobile-money accounts separately", str(V["M4_fiacc_mm"]["n"]), c2(V["M4_fiacc_mm"], "fiacc_z") + " (FI account)", c2(V["M4_fiacc_mm"], "mm_z"), c2(V["M4_fiacc_mm"], "reg")],
       ["Mobile money alone (no account variable)", str(V["M4_mm_only"]["n"]), "–", c2(V["M4_mm_only"], "mm_z"), c2(V["M4_mm_only"], "reg")],
       ["Mobile money surveyed only, FI account", str(V["M4_mm_surveyed_only"]["n"]), c2(V["M4_mm_surveyed_only"], "fiacc_z") + " (FI account)", c2(V["M4_mm_surveyed_only"], "mm_z"), c2(V["M4_mm_surveyed_only"], "reg")],
       ["Excluding use > 30% (Bulgaria, China, Ethiopia, Mongolia)", str(V["M4_trim30"]["n"]), c2(V["M4_trim30"], "acc_z"), c2(V["M4_trim30"], "mm_z"), c2(V["M4_trim30"], "reg")],
       ["Excluding CIMA states", str(V["M4_noCIMA"]["n"]), c2(V["M4_noCIMA"], "acc_z"), c2(V["M4_noCIMA"], "mm_z"), c2(V["M4_noCIMA"], "reg")],
       ["Regulation in force or under development", str(V["M4_regany"]["n"]), c2(V["M4_regany"], "acc_z"), c2(V["M4_regany"], "mm_z"), c2(V["M4_regany"], "reg_any")],
       [f"Leave-one-out range ({M4['n']} samples)", str(M4["n"] - 1), f"{100*V['M4_loo']['acc_min']:.1f} to {100*V['M4_loo']['acc_max']:.1f}", f"{100*V['M4_loo']['mm_min']:.1f} to {100*V['M4_loo']['mm_max']:.1f}", f"{100*V['M4_loo']['reg_min']:.1f} to {100*V['M4_loo']['reg_max']:.1f}"]],
      note="Note. Entries are coefficients with p-values in parentheses; all rows include the baseline controls and region effects. FI = financial institution. Leave-one-out re-estimates M4 dropping each economy in turn.",
      widths=[6.2, 1.0, 3.0, 3.0, 2.6], size=8.5)
H("4.2.4  How Much Weight the Regulation-Gender Association Can Bear", 3)
T(f"The G3 estimate rests on {G3['n']} economies and a binary indicator, so it was put through every check that a sceptical reader would ask for "
  f"(Table 8, Figure 4). It is not an artefact of one economy or of the error estimator: dropping each economy in turn keeps the coefficient between "
  f"{V['G3_loo']['reg_min']:.2f} and {V['G3_loo']['reg_max']:.2f} with p between {V['G3_loo']['p_min']:.3f} and {V['G3_loo']['p_max']:.3f}; removing the two "
  f"most influential cases, Kenya and Tunisia, gives {V['G3_drop_top2_cook']['coef']['reg']:.2f} ({pv(V['G3_drop_top2_cook'],'reg')}); HC3 errors give "
  f"{pv(V['G3_HC3'],'reg')}; a permutation test over 5,000 reassignments of the regulation label gives p = {V['G3_perm']['p_two_sided']:.3f} and a wild "
  f"bootstrap p = {V['G3_wild']['p_two_sided']:.3f}; replacing account ownership by financial-institution accounts changes nothing. It is, however, "
  f"sensitive to three things that matter more. Adding the rural, informality and exposure controls weakens it ({V['G3_controls']['coef']['reg']:.2f}, "
  f"{pv(V['G3_controls'],'reg')}); counting frameworks under development as regulated removes it ({V['G3_regany']['coef']['reg_any']:.2f}, "
  f"{pv(V['G3_regany'],'reg_any')}); and adding region effects removes it altogether ({V['G3_regionFE']['coef']['reg']:.2f}, {pv(V['G3_regionFE'],'reg')}). "
  f"Regulated economies in the gender sample are concentrated in Sub-Saharan Africa, Latin America and South and East Asia, regions whose gender "
  f"ratios differ for reasons unrelated to insurance law, and with {G3['n']} observations the within-region variation left to identify a regulation "
  f"effect is small. Across the {V['n_tests']['m_regulation_tests']} regulation coefficients reported in this paper the Holm-adjusted p-value of the G3 "
  f"estimate is {V['n_tests']['holm_p_G3_reg']:.2f}. The association is therefore reported as suggestive. It is consistent with the framework's expectation "
  f"that regulation shapes who is reached, and it is not distinguishable, on these data, from regional composition.")
TABLE("Table 8. Sensitivity of the regulation coefficient in the gender-gap model (G3: ln women ÷ men)",
      ["Specification", "n", "Regulation coefficient", "p-value"],
      [["G3 as reported (HC1)", str(G3["n"]), f"{G3['coef']['reg']:.2f}", f"{G3['p']['reg']:.3f}"],
       ["HC3 errors", str(V["G3_HC3"]["n"]), f"{V['G3_HC3']['coef']['reg']:.2f}", f"{V['G3_HC3']['p']['reg']:.3f}"],
       ["Financial-institution account in place of any account", str(V["G3_fiacc"]["n"]), f"{V['G3_fiacc']['coef']['reg']:.2f}", f"{V['G3_fiacc']['p']['reg']:.3f}"],
       ["Dropping Kenya and Tunisia (largest Cook's distances)", str(V["G3_drop_top2_cook"]["n"]), f"{V['G3_drop_top2_cook']['coef']['reg']:.2f}", f"{V['G3_drop_top2_cook']['p']['reg']:.3f}"],
       [f"Leave-one-out range ({V['G3_loo']['n']} samples)", str(V["G3_loo"]["n"] - 1), f"{V['G3_loo']['reg_min']:.2f} to {V['G3_loo']['reg_max']:.2f}", f"{V['G3_loo']['p_min']:.3f} to {V['G3_loo']['p_max']:.3f}"],
       ["Permutation test (5,000 draws)", str(G3["n"]), "–", f"{V['G3_perm']['p_two_sided']:.3f}"],
       ["Wild bootstrap (5,000 draws)", str(G3["n"]), "–", f"{V['G3_wild']['p_two_sided']:.3f}"],
       ["Adding rural, informality and exposure controls", str(V["G3_controls"]["n"]), f"{V['G3_controls']['coef']['reg']:.2f}", f"{V['G3_controls']['p']['reg']:.3f}"],
       ["Regulation in force or under development", str(V["G3_regany"]["n"]), f"{V['G3_regany']['coef']['reg_any']:.2f}", f"{V['G3_regany']['p']['reg_any']:.3f}"],
       ["Adding region effects", str(V["G3_regionFE"]["n"]), f"{V['G3_regionFE']['coef']['reg']:.2f}", f"{V['G3_regionFE']['p']['reg']:.3f}"],
       [f"Holm adjustment across {V['n_tests']['m_regulation_tests']} regulation tests", "–", "–", f"{V['n_tests']['holm_p_G3_reg']:.2f}"]],
      note="Note. All rows include log GDP per capita, account ownership, mobile money and the missing-mobile-money indicator unless stated. No CIMA member state is in the gender sample.",
      widths=[7.0, 1.2, 3.6, 2.4], size=9)
FIG(f"{FIGS}/fig4_g3_sens.png", "Figure 4. The regulation coefficient in the gender-gap model (G3) across specifications, with 95 percent confidence intervals, and its leave-one-out distribution.", width_cm=14)

# ---------------------------------------------------------------- 4.3 DISCUSSION
H("4.3  Discussion", 2)
H("4.3.1  Rails, Not Channels", 3)
T(f"The one result that survives everything is that account ownership, not mobile money and not income, predicts insurance use across developing "
  f"economies, within a range of {acc_lo:.1f} to {acc_hi:.1f} points per standard deviation depending on sample and estimator. This agrees with the "
  f"transaction-cost reading of the sector in Section 2.2 and with the Landscape's own observation that payment channels are the rails on which "
  f"microinsurance expands, but it qualifies the enthusiasm for mobile operators as a distribution channel. Mobile money is a powerful account-opening "
  f"technology and a resilience technology in its own right (Jack & Suri, 2014; Afawubo et al., 2020; Suri et al., 2021); on the cross-country evidence "
  f"it does not translate into formal insurance beyond what any account does, and Section 4.2.2 shows that this is not a by-product of how Findex "
  f"defines an account. The Landscape's channel data say why: mobile operators reach 2.5 million Africans and collect 2 percent of premiums, because "
  f"the products that ride on airtime and wallets are small, often free and often unnoticed. Distribution innovation buys access; usage needs a product "
  f"people know they hold and a reason to renew.")
T("Against the prior literature the result sits with the account-centred reading of inclusion in Allen et al. (2016) and Demirgüç-Kunt et al. (2022), "
  "for whom the account is the foundation on which other formal services are built, and extends it to a service those studies did not observe. It "
  "agrees with Jack and Suri (2014), Suri and Jack (2016) and Batista and Vicente (2025) that mobile money changes how households save and share risk, "
  "and it disagrees with the inference, common in practitioner writing and implicit in the Landscape's treatment of operators as a channel in their own "
  "right, that the wallet is itself a route to insurance. The disagreement is about the counterfactual: once an account of any kind is held constant, "
  "the wallet is one way of holding an account rather than an additional conversion factor. The experiments of Section 2.3 explain the aggregate "
  "pattern. Price alone did not carry rainfall insurance to wide take-up (Cole et al., 2013); timing, instalments and trusted intermediaries did "
  "(Casaburi & Willis, 2018; Belissa et al., 2019; Bauchet & Morduch, 2019). A wallet lowers the cost of paying a premium and does nothing, by itself, "
  "about when the premium falls due or whether the payer trusts the insurer. Rails are necessary for usage and, on this evidence, not sufficient.")
H("4.3.2  What Regulation Does, and What the Data Can and Cannot Say About It", 3)
T("The null association between inclusive-insurance regulation and the level of use holds in every sample, estimator and coding, and it is the "
  "paper's firmest regulatory finding. Once income, rails and region are controlled for, regulated and unregulated economies do not differ in how many "
  "adults pay premiums. The Landscape's observation that four of the five highest-penetration countries have dedicated regulation is best read as "
  "regulation enabling scale where demand and rails already exist, not as regulation creating demand, which is how Biener et al. (2014) describe its "
  "role and how the IAIS (2015, 2017) frames inclusive-insurance supervision, as conduct and product oversight rather than market creation. The "
  "composition result is weaker than I would like. The gender-gap association is in the direction the institutional lens predicts and it survives "
  "resampling, but it does not survive region effects or a broader coding of regulation, and with 47 economies it cannot. It is reported here as a "
  "hypothesis that panel data can test (P2 in Section 5.3), not as a finding. The income-gradient result is firmer in direction and softer in "
  "precision: Beck et al. (2007) showed that financial development disproportionately benefits the poor, and for insurance the steepening of the "
  "poorest-to-richest ratio with national income says the protective leg of finance does not follow automatically. The gap between census-measured "
  "reach and self-reported use in India and the Philippines is the aggregate counterpart of the awareness problem that Platteau et al. (2017) and "
  "Banerjee et al. (2014) identify at household level: cover embedded in credit or a public scheme protects people who do not know they are protected, "
  "and so appears in the Landscape and not in Findex. That measurement point has a practical edge. A supervisor who counts covered lives will see "
  "progress where a household survey sees none, and the two can be reconciled only by asking the insured whether they know what they hold; the "
  "Findex indicator, for all its breadth, is the first instrument that asks that question across countries, and the difference between the two "
  "measures is itself a diagnostic worth publishing.")
H("4.3.3  A Constraint-Contingent Typology", 3)
T("Bringing the documentary comparison and the cross-country evidence together gives the paper's synthesis (Table 9): a typology that maps design "
  "configurations to the inclusion outcome each is most likely to reach given the dominant binding constraint, with the evidence that supports each "
  "row and its strength stated. Where rails are thin, no distribution innovation will raise usage; where rails exist but trust and liquidity bind, timing "
  "and member-based channels matter more than price; where the constraint is affordability, subsidy buys access but not credibility; and where the "
  "constraint is legitimacy, micro-Takaful is a coherent vehicle rather than a workaround. The typology is meant to be used in a particular order. A "
  "designer or supervisor first asks whether the rail base exists, because without it the remaining rows are moot; then whether the product's premium "
  "falls due when income arrives; then whether the channel is one the target population already trusts; and only then whether price or subsidy is the "
  "lever. The last column grades the evidence so that the rows resting on experiments and on the cross-country estimates are not confused with the "
  "rows resting on documentary observation alone.")
TABLE("Table 9. Constraint-contingent typology: matching design configurations to inclusion contexts",
      ["Dominant binding constraint", "Recommended pricing", "Recommended distribution", "Outcome targeted", "Residual risk", "Supporting evidence (strength)"],
      [["Thin financial rails (low account ownership)", "Community / embedded", "Financial institution, cooperative", "Access", "Coverage tied to borrowing", f"Account ownership +{acc_lo:.1f} to +{acc_hi:.1f} pp per SD in every specification; mobile money no independent effect (Tables 5, 7) — strong"],
       ["High transaction cost, covariate risk", "Parametric / index", "Mobile or aggregator", "Access → Usage", "Basis risk; comprehension", "58% of agriculture products subsidised (Table 3); Jensen & Barrett (2017) — documentary"],
       ["Liquidity and timing", "Pay-at-harvest; instalments; deferred premium", "Value-chain buyer, contract farming", "Usage", "Default on deferred premiums", "Take-up 5% → 72% (Casaburi & Willis, 2018); 8% → 24% (Belissa et al., 2019); Bauchet & Morduch (2019) — experimental"],
       ["Low trust, weak enforcement", "Community / Takaful", "Cooperative, NGO, funeral society", "Usage; value", "Cross-subsidy; scale", "Highest claims ratios through cooperatives and NGOs (Table 3); uptake 43% via iddirs — documentary and experimental"],
       ["Low affordability", "Subsidised + community", "MFI-linked; government scheme", "Access", "Subsidy dependence", "Peru, Zambia top-10 penetration via public schemes — documentary"],
       ["Exclusion of women and the poor", "Simple, gender-tailored products", "Regulated inclusive channels", "Equity of usage", "Regulatory cost", f"Women/men ratio +{gen_pct:.0f}% with regulation, not robust to region effects (Table 8) — suggestive"],
       ["Religious-legitimacy barrier", "Micro-Takaful", "Cooperative and Islamic finance networks", "Access → Usage", "Regulatory fragmentation", f"MENA: {100*reg_by['Middle East & North Africa']['acc']:.0f}% accounts, {100*reg_by['Middle East & North Africa']['ins']:.0f}% use; Beshir et al. (2023); Ozili (2025) — indirect"]],
      note="Note. Microinsurance design is constraint-contingent: the configuration depends on which barrier binds hardest. The last column grades the evidence behind each row.",
      widths=[2.9, 2.3, 2.5, 1.8, 2.0, 4.5], size=8.5)
H("4.3.4  Egypt and Saudi Arabia", 3)
T(f"Egypt shows the distance between access and use with unusual clarity. The Financial Regulatory Authority reported 10.5 million people covered by "
  f"microinsurance policies in the fiscal year to June 2024, up from 8.5 million a year earlier, on premiums of about EGP 568 million, and it raised the "
  f"coverage cap for the class to EGP 312,500 in 2025 (Amwal Al Ghad, 2025; Al Mal, 2025). Findex records, for the same population, that "
  f"{100*H_['Egypt, Arab Rep.']['ins']:.1f} percent of adults made regular insurance payments in 2024, the lowest figure in the region and the second-lowest "
  f"in the sample, beside account ownership of {100*H_['Egypt, Arab Rep.']['acc']:.0f} percent and mobile-money ownership of "
  f"{100*H_['Egypt, Arab Rep.']['mm']:.0f} percent. The two numbers do not contradict each other. Most covered lives are credit-life and group covers "
  f"attached to microfinance loans, which policyholders do not experience as insurance they pay for. Egypt has built access through embedded "
  f"distribution on a thin rail base. The Unified Insurance Law No. 155 of 2024, which gives microinsurance, Takaful and parametric cover a statutory "
  f"footing, is the opportunity to build use, and the typology says where to start: premium collection over the account and wallet rails now being "
  f"licensed, explicit awareness of embedded cover, and micro-Takaful for the segment the conventional label excludes. In Table 9 Egypt sits in the "
  f"first row; with account ownership well below the sample mean, the account coefficient implies that the rail base, not another channel, is the "
  f"binding constraint. The scale of the gap is easy to state. Microinsurance premiums of about EGP 568 million are roughly half of one percent of a "
  f"market that wrote EGP 114.1 billion in 2025 (Financial Regulatory Authority, 2026), and the covered lives sit in a few credit-linked products "
  f"rather than across the informal economy that Law 155 was written to reach. Egypt's response rate to the Landscape census, 82 percent of the "
  f"insurers approached, is the highest in the study, so the supply side is unusually well measured; what is missing is any demand-side measure beyond "
  f"the single Findex number, which is the first thing the Authority can change.")
T("Saudi Arabia sits at the opposite corner of the map, outside the estimation sample as a high-income economy but inside the question. Account "
  "ownership is near-universal, insurance is cooperative by law, and a dedicated Insurance Authority, established by Council of Ministers Resolution "
  "No. 85 of 15 August 2023, opened a regulatory sandbox for the sector in September 2024 (Council of Ministers, 2023; Insurance Authority, 2024). "
  "Rails and legitimacy are in place; what the cross-country evidence flags is composition, since the income gradient steepens with national income. "
  "The Authority's inclusive-insurance agenda would be served by measuring use among low-income residents and the expatriate workforce directly and by "
  "licensing funeral, health-cash and remittance-linked cooperative products for the segments where the cooperative principle is already trusted. In "
  "Table 9 the Kingdom's constraint is the sixth row, and the gender evidence of Section 4.2.4 is a reason to measure, not yet a reason to legislate.")

# ================================================================ 5 CONCLUSION
H("5.  Conclusion and Policy Implications", 1)
H("5.1  Conclusion and Recommendations", 2)
T(f"The three questions can now be answered. On RQ1, microinsurance advances inclusion by lowering the transaction-cost floor of equation (1) through "
  f"embedded and parametric designs, but it converts access into use only where rails, premium timing and trust allow, and no model dominates: the "
  f"channels that reach the most people return the least value, and the member-based channels that return the most value reach the fewest (Table 3). On "
  f"RQ2, account ownership is the structural factor associated with the level of use, between {acc_lo:.1f} and {acc_hi:.1f} percentage points per standard "
  f"deviation across every specification and sample, while mobile money, disaster exposure and dedicated regulation are not; the income gradient steepens "
  f"with national income, and the association between regulation and a narrower gender gap is suggestive rather than established (Tables 5 to 8). On RQ3, "
  f"design and regulation should be matched to whichever constraint binds hardest (Table 9), which in the Middle East and North Africa means building the "
  f"rail base and making embedded cover visible before expecting any channel innovation to raise use.")
T("Two kinds of evidence that had not been brought together before are read against each other here: the sector's census of what is sold, through which "
  "channels and at what value, and the first comparable demand-side measure of who pays for insurance across developing economies. The census shows a "
  "sector that solved the reach problem in one region by driving unit premiums down and volumes up and that elsewhere remains on the transaction-cost "
  "floor. The cross-country evidence shows that use follows the depth of financial rails rather than any particular channel, that it is regressive within "
  "countries and more so in richer ones, and that dedicated regulation goes with neither a larger nor, demonstrably, a differently composed market. "
  "Microinsurance is neither the cure-all its advocates implied nor the failure its critics feared; it is a conditional instrument whose contribution "
  "depends on aligning rails, product, distribution and regulation with the binding constraint.")
T(f"For Egypt's Financial Regulatory Authority the number that matters is the distance between 10.5 million covered lives and "
  f"{100*H_['Egypt, Arab Rep.']['ins']:.1f} percent of adults who know they pay for insurance. The secondary regulations under Law No. 155 of 2024 should "
  f"require every embedded or credit-linked cover to be disclosed at enrolment with a plain statement of what is covered and how to claim, so that census "
  f"reach begins to register as use; should admit micro-Takaful products under the microinsurer licence for the segment the conventional label "
  f"excludes; and should publish a sex- and income-disaggregated use indicator beside policy counts, because composition is where the evidence says "
  f"regulation may leave its mark and where Egypt currently has no measure at all.")
T(f"For the Central Bank of Egypt the result is the account coefficient and the mobile-money null. Use follows the account, not the wallet, so the "
  f"payments agenda that serves protection inclusion is the one that puts a transactional account in the hands of the adults still outside the system and "
  f"lets insurers debit small, regular premiums over it: interoperable low-cost accounts that a licensed insurer can charge on schedule, with premium "
  f"collection treated as a use case in the Bank's financial-inclusion strategy rather than left to agents.")
T("For Saudi Arabia's Insurance Authority and the Saudi Central Bank the relevant result is the steepening of the income gradient with national income. "
  "In a market whose rails and legitimacy are strong the inclusion risk is composition, not reach. The Authority should measure insurance use among "
  "low-income residents and the expatriate workforce through a national demand-side survey aligned with the Findex definition, and should license simple "
  "funeral, health-cash and remittance-linked cooperative products for those segments; the Central Bank's part is to keep low-cost accounts and "
  "payroll-linked wallets available to the same residents so that the premium can be collected where the income arrives.")
T(f"For the International Association of Insurance Supervisors and the Access to Insurance Initiative the lesson concerns measurement. Dedicated "
  f"regulation is associated with no change in the level of use, and whether it changes who uses insurance cannot be settled with a binary indicator in "
  f"{G3['n']} economies. The A2ii map should grade implementation rather than record the existence of a framework, and supervisors adopting the IAIS "
  f"application papers should report sex- and income-disaggregated use so that the composition effect this paper can only suggest becomes testable in "
  f"panel form.")
H("5.2  Limitations of the Study", 2)
T(f"Seven limitations apply. The cross-country evidence is a single cross-section and identifies associations; regulation in particular may follow "
  f"market development rather than precede it. The Findex indicator counts any regular insurance payment, including compulsory motor and formal-sector "
  f"health cover, so it measures insurance use among adults rather than microinsurance narrowly. The Findex account measure contains mobile-money "
  f"accounts, so the two rails overlap by construction; Section 4.2.2 separates them, but the separation relies on the published aggregates rather than "
  f"microdata. The regulation indicator is binary, dates from 2023 and cannot distinguish a working regime from one on paper, and the gender result in "
  f"particular is sensitive to its coding and to region effects. Four high-use economies move the account coefficient by about a third, and the gradient "
  f"samples of {G1['n']} and {G3['n']} economies limit what any composition test can detect. The Landscape census rests on voluntary self-reporting with "
  f"uneven response rates, 82 percent in Egypt but far lower elsewhere. And the evidence on the Middle East and North Africa, including the Takaful "
  f"mechanism, is asserted from institutional reasoning and small surveys rather than measured.")
H("5.3  Future Research", 2)
T("Five propositions follow from the evidence and its limits:")
for t in ["**P1.** Within countries, insurance use rises with account ownership among the poorest 40 percent at least as steeply as among the population as a whole, and mobile-money ownership adds nothing unless a product is bought through the wallet.",
          "**P2.** Inclusive-insurance regulation narrows the gender gradient in use within regions before it raises the level of use; the effect, if real, should appear within three to five years of implementation in panel data and should survive region effects, which it does not in cross-section.",
          "**P3.** Embedded distribution raises census-measured access and leaves self-reported use unchanged; the gap between the two measures policyholder unawareness.",
          "**P4.** Aligning premium collection with income realisation raises uptake more than an equivalent price cut, and the effect is largest where liquidity rather than price binds.",
          "**P5.** Where a religious-legitimacy barrier exists, micro-Takaful achieves higher voluntary uptake than actuarially equivalent conventional cover; Egypt's new statutory framework is a natural test case."]:
    p = T(t, after=3, indent=False); p.paragraph_format.left_indent = Cm(0.75)
T("P1 to P3 are testable with successive Findex rounds and the Landscape panel; P4 and P5 call for the randomised designs already established in the field.", before=4)

if not BLIND:
    H("Declarations", 1)
    _p = P(f"**Data and code availability.** The Global Findex Database 2025 and the World Development Indicators are openly available from the World Bank; the Landscape of Microinsurance 2024 is available from the Microinsurance Network. The merged dataset, the estimation and sensitivity scripts and the figure code are openly available at {REPO} (release v1.0.0). ", after=3)
    _r = _p.add_run("Zenodo DOI: to be inserted after release."); _r.font.name = FONT; _r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    P("**Funding.** None.   **Conflicts of interest.** None.   **Ethics.** The study uses published aggregate data; no ethics approval was required.", after=3)
    P("**Author contribution.** The author is solely responsible for the conception, analysis and writing of this article.", after=8)

# ================================================================ REFERENCES
H("References", 1)
refs = [
 "Afawubo, K., Couchoro, M. K., Agbaglah, M., & Gbandi, T. (2020). Mobile money adoption and households' vulnerability to shocks: Evidence from Togo. *Applied Economics, 52*(10), 1141–1162. https://doi.org/10.1080/00036846.2019.1659496",
 "Ahmed, H., & Cowan, B. (2021). Mobile money and healthcare use: Evidence from East Africa. *World Development, 141*, 105392. https://doi.org/10.1016/j.worlddev.2021.105392",
 "Akerlof, G. A. (1970). The market for \"lemons\": Quality uncertainty and the market mechanism. *The Quarterly Journal of Economics, 84*(3), 488–500. https://doi.org/10.2307/1879431",
 "Al Mal. (2025, May 9). *Naqla naw'iya fi al-shumul al-ta'mini bi-Misr: Isdar 2.3 milyun wathiqa mutanahiya al-sighar tughatti 10.5 milyun muwatin* [A qualitative leap in insurance inclusion in Egypt: 2.3 million microinsurance policies covering 10.5 million citizens]. https://almalnews.com/2017577/",
 "Allen, F., Demirgüç-Kunt, A., Klapper, L., & Martinez Peria, M. S. (2016). The foundations of financial inclusion: Understanding ownership and use of formal accounts. *Journal of Financial Intermediation, 27*, 1–30. https://doi.org/10.1016/j.jfi.2015.12.003",
 "Amwal Al Ghad. (2025, May 8). *Al-Raqaba al-Maliya: 10.5 milyun mustafid min watha'iq al-ta'min mutanahi al-sighar khilal 2023/2024* [FRA: 10.5 million beneficiaries of microinsurance policies in 2023/2024]. https://amwalalghad.com/2025/05/08/",
 "Aterido, R., Beck, T., & Iacovone, L. (2013). Access to finance in Sub-Saharan Africa: Is there a gender gap? *World Development, 47*, 102–120. https://doi.org/10.1016/j.worlddev.2013.02.013",
 "Banerjee, A., Duflo, E., & Hornbeck, R. (2014). Bundling health insurance and microfinance in India: There cannot be adverse selection if there is no demand. *American Economic Review, 104*(5), 291–297. https://doi.org/10.1257/aer.104.5.291",
 "Batista, C., & Vicente, P. C. (2025). Is mobile money changing rural Africa? Evidence from a field experiment. *The Review of Economics and Statistics, 107*(3), 835–844. https://doi.org/10.1162/rest_a_01333",
 "Bauchet, J., & Morduch, J. (2019). Paying in pieces: A natural experiment on demand for life insurance under different payment schemes. *Journal of Development Economics, 139*, 69–77. https://doi.org/10.1016/j.jdeveco.2019.02.002",
 "Beck, T., Demirgüç-Kunt, A., & Levine, R. (2007). Finance, inequality and the poor. *Journal of Economic Growth, 12*(1), 27–49. https://doi.org/10.1007/s10887-007-9010-6",
 "Belissa, T. K., Bulte, E., Cecchi, F., Gangopadhyay, S., & Lensink, R. (2019). Liquidity constraints, informal institutions, and the adoption of weather insurance: A randomized controlled trial in Ethiopia. *Journal of Development Economics, 140*, 269–278. https://doi.org/10.1016/j.jdeveco.2019.06.006",
 "Beshir, H. A., Alhabshi, S. M., & Zakariyah, H. (2023). The potential of micro-Takaful in improving financial inclusion among low-income households in Ethiopia. *Journal of Islamic Finance, 12*(2), 30–47. https://doi.org/10.31436/jif.v12i2.823",
 "Biener, C., & Eling, M. (2012). Insurability in microinsurance markets: An analysis of problems and potential solutions. *The Geneva Papers on Risk and Insurance — Issues and Practice, 37*(1), 77–107. https://doi.org/10.1057/gpp.2011.29",
 "Biener, C., Eling, M., & Schmit, J. T. (2014). Regulation in microinsurance markets: Principles, practice, and directions for future development. *World Development, 58*, 21–40. https://doi.org/10.1016/j.worlddev.2013.12.012",
 "Casaburi, L., & Willis, J. (2018). Time versus state in insurance: Experimental evidence from contract farming in Kenya. *American Economic Review, 108*(12), 3778–3813. https://doi.org/10.1257/aer.20171526",
 "Churchill, C. (Ed.). (2006). *Protecting the poor: A microinsurance compendium*. International Labour Organization & Munich Re Foundation.",
 "Clarke, D. J. (2016). A theory of rational demand for index insurance. *American Economic Journal: Microeconomics, 8*(1), 283–306. https://doi.org/10.1257/mic.20140103",
 "Cole, S., Giné, X., Tobacman, J., Topalova, P., Townsend, R., & Vickery, J. (2013). Barriers to household risk management: Evidence from India. *American Economic Journal: Applied Economics, 5*(1), 104–135. https://doi.org/10.1257/app.5.1.104",
 "Cole, S. A., & Xiong, W. (2017). Agricultural insurance and economic development. *Annual Review of Economics, 9*, 235–262. https://doi.org/10.1146/annurev-economics-080315-015225",
 "Council of Ministers of the Kingdom of Saudi Arabia. (2023). *Resolution No. 85 of 28/1/1445 AH (15 August 2023) approving the establishment of the Insurance Authority and its statute*. Umm Al-Qura Gazette. https://www.uqn.gov.sa/details?p=23532",
 "Demirgüç-Kunt, A., Klapper, L., Singer, D., & Ansar, S. (2022). *The Global Findex Database 2021: Financial inclusion, digital payments, and resilience in the age of COVID-19*. World Bank. https://doi.org/10.1596/978-1-4648-1897-4",
 "Dercon, S., Hill, R. V., Clarke, D., Outes-Leon, I., & Taffesse, A. S. (2014). Offering rainfall insurance to informal insurance groups: Evidence from a field experiment in Ethiopia. *Journal of Development Economics, 106*, 132–143. https://doi.org/10.1016/j.jdeveco.2013.09.006",
 "Eling, M., Pradhan, S., & Schmit, J. T. (2014). The determinants of microinsurance demand. *The Geneva Papers on Risk and Insurance — Issues and Practice, 39*(2), 224–263. https://doi.org/10.1057/gpp.2014.5",
 "Financial Regulatory Authority. (2026). *Al-kitab al-ihsa'i al-sanawi 'an nashat al-ta'min khilal al-'am al-miladi 2025* [Annual statistical book on insurance activity, calendar year 2025]. Arab Republic of Egypt. https://fra.gov.eg/wp-content/uploads/2026/09/الكتاب-الاحصائي-2025.pdf",
 "GSMA. (2026). *The state of the industry report on mobile money 2026*. GSM Association. https://www.gsma.com/sotir/",
 "Hill, R. V., Kumar, N., Magnan, N., Makhija, S., de Nicola, F., Spielman, D. J., & Ward, P. S. (2019). Ex ante and ex post effects of hybrid index insurance in Bangladesh. *Journal of Development Economics, 136*, 1–17. https://doi.org/10.1016/j.jdeveco.2018.09.003",
 "Insurance Authority. (2024, September 3). *The Insurance Authority launches the regulatory sandbox platform for the insurance sector* [Press release]. Kingdom of Saudi Arabia. https://www.ia.gov.sa/en/media-center/news/1",
 "International Association of Insurance Supervisors. (2015). *Issues paper on conduct of business in inclusive insurance*. IAIS. https://iais.org/uploads/2022/01/151111-Issues-Paper-Conduct-of-Business-in-Inclusive-Insurance.pdf",
 "International Association of Insurance Supervisors. (2017). *Application paper on product oversight in inclusive insurance*. IAIS. https://iais.org/uploads/2022/01/171124-Application-Paper-on-Product-Oversight-in-Inclusive-Insurance.pdf",
 "International Association of Insurance Supervisors & CGAP Joint Working Group on Microinsurance. (2007). *Issues in regulation and supervision of microinsurance*. IAIS.",
 "Jack, W., & Suri, T. (2014). Risk sharing and transactions costs: Evidence from Kenya's mobile money revolution. *American Economic Review, 104*(1), 183–223. https://doi.org/10.1257/aer.104.1.183",
 "Janzen, S. A., & Carter, M. R. (2019). After the drought: The impact of microinsurance on consumption smoothing and asset protection. *American Journal of Agricultural Economics, 101*(3), 651–671. https://doi.org/10.1093/ajae/aay061",
 "Jensen, N., & Barrett, C. (2017). Agricultural index insurance for development. *Applied Economic Perspectives and Policy, 39*(2), 199–219. https://doi.org/10.1093/aepp/ppw022",
 "Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica, 47*(2), 263–291. https://doi.org/10.2307/1914185",
 "Karlan, D., Osei, R., Osei-Akoto, I., & Udry, C. (2014). Agricultural decisions after relaxing credit and risk constraints. *The Quarterly Journal of Economics, 129*(2), 597–652. https://doi.org/10.1093/qje/qju002",
 "Klapper, L., Singer, D., Starita, L., & Norris, A. (2025). *The Global Findex Database 2025: Connectivity and financial inclusion in the digital economy*. World Bank. https://doi.org/10.1596/978-1-4648-2204-9",
 "Microinsurance Network. (2025). *The landscape of microinsurance 2024*. Microinsurance Network & UNDP Insurance and Risk Finance Facility. https://landscape.microinsurancenetwork.org/",
 "Müller-Bloch, C., & Kranz, J. (2015). A framework for rigorously identifying research gaps in qualitative literature reviews. In *Proceedings of the 36th International Conference on Information Systems (ICIS 2015)*. Association for Information Systems. https://aisel.aisnet.org/icis2015/proceedings/ResearchMethods/2",
 "Ozili, P. K. (2025). Financial inclusion, religiosity and economic welfare in majority Christian, Hindu and Muslim countries. *foresight, 27*(4), 727–751. https://doi.org/10.1108/fs-03-2024-0046",
 "Papke, L. E., & Wooldridge, J. M. (1996). Econometric methods for fractional response variables with an application to 401(k) plan participation rates. *Journal of Applied Econometrics, 11*(6), 619–632. https://doi.org/10.1002/(SICI)1099-1255(199611)11:6<619::AID-JAE418>3.0.CO;2-1",
 "Platteau, J.-P., De Bock, O., & Gelade, W. (2017). The demand for microinsurance: A literature review. *World Development, 94*, 139–156. https://doi.org/10.1016/j.worlddev.2017.01.010",
 "Robinson, K. A., Saldanha, I. J., & McKoy, N. A. (2011). Development of a framework to identify research gaps from systematic reviews. *Journal of Clinical Epidemiology, 64*(12), 1325–1330. https://doi.org/10.1016/j.jclinepi.2011.06.009",
 "Rothschild, M., & Stiglitz, J. (1976). Equilibrium in competitive insurance markets: An essay on the economics of imperfect information. *The Quarterly Journal of Economics, 90*(4), 629–649. https://doi.org/10.2307/1885326",
 "Seabold, S., & Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with Python. *Proceedings of the 9th Python in Science Conference*, 92–96. https://doi.org/10.25080/Majora-92bf1922-011",
 "Sen, A. (1999). *Development as freedom*. Oxford University Press.",
 "Shair, W., Devi, V., Hayat, S., & Akram, M. (2026). Financial inclusion barriers in upper-middle-income countries: A comparison between Muslim-majority and non-Muslim-majority economies. *International Journal of Development Issues, 25*(3), 505–534. https://doi.org/10.1108/ijdi-04-2026-0136",
 "Snyder, H. (2019). Literature review as a research methodology: An overview and guidelines. *Journal of Business Research, 104*, 333–339. https://doi.org/10.1016/j.jbusres.2019.07.039",
 "Suri, T., Bharadwaj, P., & Jack, W. (2021). Fintech and household resilience to shocks: Evidence from digital loans in Kenya. *Journal of Development Economics, 153*, 102697. https://doi.org/10.1016/j.jdeveco.2021.102697",
 "Suri, T., & Jack, W. (2016). The long-run poverty and gender impacts of mobile money. *Science, 354*(6317), 1288–1292. https://doi.org/10.1126/science.aah5309",
]
refs = sorted(refs, key=lambda r: re.sub(r"^(van |de )", "", r).lower())
for ref in refs:
    p = P(ref, align="l", size=11, after=3); p.paragraph_format.left_indent = Cm(1.0); p.paragraph_format.first_line_indent = Cm(-1.0); p.paragraph_format.line_spacing = 1.0

name = "Microinsurance_Financial_Inclusion_Manuscript_v4_BLINDED.docx" if BLIND else "Microinsurance_Financial_Inclusion_Manuscript_v4.docx"
doc.save(f"{VER}/{name}"); print("saved", name)
if not BLIND:
    main = sum(WC[k] for k in "12345")
    json.dump({"main_text": main, "sections": WC, "budget": {"abstract": 250, "1": 650, "2": 950, "3": 1550, "4": 3800, "5": 1050, "main": 8000}}, open(f"{HERE}/wordcount.json", "w"), indent=2)
    print("wordcount", WC, "main", main)
