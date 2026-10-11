const { P, H, B, N, Q, T, doc, save } = require('./lib.js');
const c = [];
const add = (...x) => c.push(...x);

// ------------------------------------------------------------------ title and use
add(H('Revision R2 — instructions for Claude in Word', 1),
  P('Manuscript ENVDEV-D-26-01510R1, "Technological Innovation and the Growth–Environment Relationship: Evidence from Asia and Africa by Region and Income Group". Reviewer 1, second round (Major Revision). This document covers major comments 4–18 and minimum requirements 4–10; minimum requirements 1–3 have already been addressed by the author.'),
  H('How to use this document', 2),
  N('Open the manuscript (Manuscript_10.5.docx) in Word with **Track Changes on**, open Claude in Word, and attach or paste this document. Ask Claude to apply Part B edit by edit, in order, and to stop after each section for review.'),
  N('Run **do_10.6.do** in Stata before finalising. The numbers in Parts C and D come from an exact Python replication of the do-file (it reproduces Table 10 within 0.003; the Asian columns are identical). Replace them with the Stata output where the table title says "from do_10.6.do, section R2.x". Bootstrap-based standard errors (R2.4, R2.5) will differ slightly between Python and Stata.'),
  N('Part D contains draft replies for the response letter (Response_10.5.docx). Part E lists the points that need your decision or a check before submission.'),
  H('Instructions for Claude in Word (paste this block first)', 2),
  Q('You are revising an academic manuscript in response to a referee. Apply the edits listed in Part B of the attached guidance, in order, with Track Changes on. Keep the author\'s structure, equations, numbering and reference style. Follow academic register: formal, objective, hedged where the evidence is limited, with precise terminology and no rhetorical flourish. Do not add citations other than those named in the guidance. Where an edit says [CHECK], insert the text with the bracket kept and highlight it so that the author can verify it. After each section, list the edits made and any edit you could not locate.'),
  H('Global rules for the whole manuscript (apply while editing)', 2),
  B('**Causal language for innovation (comment 4).** Patent coefficients are conditional associations. Replace "raises", "promotes", "drives", "contributes to", "reduces", "improves", "the effect of innovation", "innovation has a large mitigating effect" with "is associated with", "is linked to", "the association between patent stock and …". Keep "effect" only in the technical phrase "marginal effect" of a regression.'),
  B('**EKC language (comment 8).** Never write "no EKC", "absence of a valid EKC" or "the EKC is rejected". Write "no EKC curvature is identified within the observed income range under the retained specification".'),
  B('**Terminology (comments 11 and 18).** Use "ecological footprint" for the variable (consumption-based footprint per capita) and "ecological pressure" for the concept it measures. Use "environmental degradation" only when describing emission-based studies in the literature. Do not use "environmental sustainability" or "sustainability transitions" as the outcome of this study; use "the growth–environment relationship", "ecological pressure" and "development-stage heterogeneity".'),
  B('**Descriptive figures (comment 16).** Replace "drove", "driving", "led to" in descriptions of figures with "coincided with" or "is consistent with"; replace "volatility" with "dispersion".'),
  B('**Samples (comment 17).** The design estimates separate Asian and African systems, each with a PAT × INC interaction. Write "regional estimations with income-group interactions", never "regional and income-group samples".'),
  B('**Higher-income group.** Whenever the higher-income Asian result is mentioned, state that it rests on four countries (Israel, Japan, the Republic of Korea, Malaysia) classified as upper-middle or high income in 2000.'));

// ------------------------------------------------------------------ Part A: what changed in the evidence
add(H('Part A — What the new analyses show (read before editing)', 1),
  P('These results determine the wording of Part B. All are from do_10.6.do (Python replication), 43 countries, 2000–2023, unless stated.'),
  T([['Question (comment)', 'Result', 'Consequence for the text'],
     ['Is the Asian PAT × INC interaction driven by one country? (6)', 'No. Dropping IL, JP, KR or MY in turn leaves it negative and significant under 3SLS (−0.076 to −0.148). Under Driscoll–Kraay, dropping KR leaves the higher-income marginal effect at −0.042 (p > 0.10).', 'Sign and magnitude are robust; precision is lower without Korea.'],
     ['Does it depend on the year-2000 classification? (7)', 'No. A 2000–2004 majority rule and a 2005 benchmark give the same four Asian countries. A 2010 benchmark (adds CN, TH) gives −0.044***; a continuous 2000-income interaction gives −0.017***.', 'Robust to predetermined alternatives.'],
     ['Is it statistically robust to the error structure? (5, 6, 8, 9)', 'Only partly. Significant with the default 3SLS SE (p < 0.01) and Driscoll–Kraay SE (p = 0.010). With country-clustered SE it is not: 3SLS clustered SE = 0.079; FE with clustered SE p = 0.117; wild cluster bootstrap p = 0.161 (4 treated clusters).', 'Report as a robust point estimate whose statistical significance depends on the assumed error structure.'],
     ['Is the patent stock exogenous? (4)', 'Untestable with confidence. The WIPO shift-share instrument is weak for the total patent stock (Sanderson–Windmeijer F 0.01–3.9 in most equations). Exogeneity is not rejected in the pooled and Asian equations (C-test p = 0.30–0.85) but is rejected in the African environmental equation (p < 0.001).', 'Treat all patent coefficients as conditional associations; report the instrument test in Appendix D1.'],
     ['Is the growth association with patents general? (5)', 'Africa: robust across 3SLS, FE, Driscoll–Kraay and clustered 3SLS (0.078–0.097). Asia: 0.027*** under 3SLS only; 0.028 (p > 0.10) under FE and Driscoll–Kraay.', 'The growth margin is robust only in Africa; revise abstract, H2 discussion and conclusion.'],
     ['Do 3SLS and FE agree on income terms? (5)', 'Asia yes (EF income elasticity 0.737 vs 0.570). Africa no: 0.323** under 3SLS vs −0.011 under FE; GDP-equation lnEF 1.181 vs 0.210.', 'State that the African income results depend on the estimator.'],
     ['Does biocapacity drive the results? (15)', 'No. Without lnBIO the Asian interaction is −0.122***; the Asian income elasticity is 0.764***.', 'Report as robustness.'],
     ['Collinearity in the identifying variation? (10)', 'Within (two-way demeaned) correlations: lnGDP–lnPAT 0.330 (pooled 0.888), lnGDP–HCI 0.020 (0.847). Maximum within-VIF 1.56.', 'Collinearity is not a concern for the within estimates.'],
     ['Cross-sectional dependence and slope heterogeneity? (9)', 'FE residuals remain cross-sectionally dependent (CD = −2.77, p = 0.006); CCE-pooled leaves CD = −2.43 (p = 0.015) and does not reproduce the interaction (Asia 0.083, p > 0.10). CCE mean group: the average country slope of lnPAT is −0.261 (p < 0.10) for the four higher-income Asian countries and −0.051 (p > 0.10) for the other thirteen.', 'Report honestly: heterogeneity in direction is supported by country-specific slopes, not by the pooled CCE interaction.'],
     ['3-year averages (smooths annual shocks)', 'Asia PAT × INC −0.085** (0.040), marginal effect −0.077**; identification of income in the EF equation is not improved (F = 2.99 Asia, 3.84 pooled).', 'Report as robustness; does not fix comment 1.'],
     ['Data errors (14, 17)', 'Table 2 PAT row is the annual flow, not the stock per million. Ethiopia has CAP = 0 in 2000–2010 in the WDI extract; without Ethiopia the pooled EF income elasticity is 1.158 (vs 0.629) and the African one 0.265 (p > 0.10).', 'Correct Table 2; verify Ethiopia (Part E).']],
    [2300, 4060, 3278]));

// ------------------------------------------------------------------ Part B: edits
add(H('Part B — Edits to the manuscript, section by section', 1));

add(H('B1. Abstract (comments 4, 5, 6, 8, 18)', 2),
  P('**Location:** the sentences from "The results reveal substantial heterogeneity regions…" to the end of the abstract. **Action:** replace with:'),
  Q('The results reveal substantial heterogeneity across regions and development stages. Sequential testing of cubic, quadratic and linear specifications identifies no Environmental Kuznets Curve (EKC) curvature within the observed income range in either region; a monotonically increasing association between income and ecological footprint is retained, and it is robust across estimators in Asia but sensitive to the estimator in Africa. Patent stock is positively associated with income in both regions, although this association is robust across estimators only in the African sample. A negative association between patent stock and ecological footprint is found only for the four Asian economies classified as upper-middle or high income in 2000; this estimate is stable in sign and magnitude when each of these countries is omitted and under alternative predetermined income classifications, but its statistical significance depends on the error structure assumed. Because no sufficiently strong external instrument for patenting is available, the innovation coefficients are interpreted as conditional associations. The findings indicate that the association between technological innovation and ecological pressure varies with regional and development context, and they caution against assuming that innovation yields uniform environmental benefits across countries.'));

add(H('B2. Introduction (comments 11, 12, 18)', 2),
  B('Paragraph 1, last sentence: delete the citation "(Tu et al., 2008)" (the article concerns tariff escalation and invasive species). Either leave the sentence uncited or cite Grossman and Krueger (1995), already in the reference list.'),
  B('Paragraph 2: replace "support broader sustainability transitions" with "alter the relationship between economic growth and ecological pressure". Replace "(Chu et al., 2021)" at the end with "; see, for example, Chu et al. (2021) for Vietnam" and change "Recent studies increasingly highlight" to "Country studies suggest".'),
  B('Paragraph 3, last sentence: delete "(Duong et al., 2015)" (a trade-creation study without environmental outcomes) or replace it with Usman et al. (2020), already cited, which compares regions on the ecological footprint.'),
  B('Contribution paragraph: replace the second contribution with:'),
  Q('Second, the study examines whether patent stock is associated with both higher income and lower ecological pressure, and whether these associations differ by development stage within Asia and Africa. The contribution lies in disciplined specification testing, a consumption-based measure of ecological pressure, and a transparent assessment of how sensitive the heterogeneous innovation associations are to individual countries, development classifications, estimators and error-structure assumptions; the design does not identify a causal effect of innovation.'));

add(H('B3. Section 2 — Literature review and hypotheses (comments 11, 12; section comments on H1–H3)', 2),
  B('Heading 2.2: "Innovation and Sustainability Transitions" → "Innovation and the Growth–Environment Relationship". In 2.1 last paragraph and 2.3, replace "sustainability transitions" with "the growth–environment relationship" (search all occurrences).'),
  B('2.2, paragraph 3 ("Nevertheless, the environmental consequences…"): check the use of Khan et al. (2022) [CHECK]: that article studies poverty and inequality, not innovation. Remove it from the sentence on innovation if it does not report an innovation result.'),
  B('Before H1 insert: "H1 is stated as a falsifiable benchmark derived from the EKC literature rather than as an expected trajectory; the sequential procedure in Section 3.1 determines whether the data identify curvature within the observed income range."'),
  B('Replace H2 by two hypotheses, so that full and partial support are defined:'),
  Q('H2a. Patent stock is positively associated with income per capita.\nH2b. Patent stock is negatively associated with ecological footprint per capita, at least under favourable development conditions.\nH2 (the dual role in the Green Solow sense) is fully supported in a group only when H2a and H2b hold jointly in that group; this is tested with a joint Wald test.'),
  B('After H3 insert: "Development stage is operationalised by a binary indicator for World Bank upper-middle- or high-income status in 2000, not by direct measures of technological or institutional maturity; Section 5.4 reports alternative predetermined classifications and a continuous measure based on income per capita in 2000."'));

add(H('B4. Section 3.1 — patent stock and identification (comments 4, 14)', 2),
  P('**Location:** the paragraph beginning "We proxy technological progress by the stock of patents…" and the equation S_t. **Action:** replace the paragraph and add the following after the equation:'),
  Q('We proxy technological progress by the patent stock rather than the annual flow of applications, following the knowledge-capital tradition (Griliches, 1979). P_t is the WIPO indicator "Total patent applications (direct and PCT national phase entries)" by applicant origin (WIPO IP Statistics Data Center): applications filed by residents of country i at all patent offices, at home and abroad, counted by the residence of the first-named applicant and dated by filing year. PCT applications enter only at the national or regional phase, so an international application is not counted twice. Where the home office did not report resident applications to WIPO, P_t equals the applications filed abroad. The stock is accumulated by the perpetual-inventory method from 1980, S_t = (1 − δ)S_{t−1} + P_t, with δ = 0.15 (Hall et al., 2005). The initial stock is S_1980 = P_1980/(g_i + δ), where g_i is the country\'s average annual growth of applications over 1980–1985, replaced by 5 percent when it is missing or non-positive. The variable entering the model is ln[(S_t + 1)/population], with population in millions (Penn World Table 11.0).'),
  P('**Location:** Section 3.1, after the paragraph on the interaction term. **Action:** insert a new paragraph:'),
  Q('Patent stock is treated as predetermined in the main system. Because income, education, institutions and patenting may be jointly determined, Appendix D1 examines this assumption with a shift-share instrument that predicts each country\'s exposure to foreign patenting: the 1990–1999 shares of foreign applicants\' filings at the country\'s patent offices, multiplied by those applicants\' lagged filings abroad, excluding filings into the country itself (Goldsmith-Pinkham et al., 2020; Borusyak et al., 2022). The instrument is weak for the patent stock used here (Appendix D1), so the exogeneity of patent stock cannot be established or rejected with confidence, and all patent coefficients are interpreted as conditional associations rather than causal effects.'),
  B('Table 1: PAT row, column "Type": "Exogenous" → "Predetermined (see Appendix D1)". CAP row, "Sources": "Penn World Table 11.0 and authors\' calculation" → "World Bank, World Development Indicators (NE.GDI.TOTL.ZS)". PAT row, "Definition": add "; applications by applicant origin, all offices, direct and PCT national phase".'));

add(H('B5. Section 3.2 — estimator and inference (comments 5, 9)', 2),
  B('First paragraph: "Pesaran\'s (2007) simple cross-sectional dependence test" → "Pesaran\'s (2021) cross-sectional dependence (CD) test" [CHECK citation: Pesaran 2007 is the CIPS unit-root test].'),
  B('Paragraph on 3SLS (after "Zellner and Theil, 1962"): delete the sentence citing Zegeye (1994) on 3SLS being "more accurate" [the article does not establish this in general]; replace with: "3SLS is more efficient than equation-by-equation 2SLS when the system is correctly specified, but a misspecified equation can contaminate the estimates of the other; equation-by-equation estimates are therefore reported alongside (Section 5.3)."'),
  B('Last paragraph ("Three-stage least squares nonetheless maintains…"): replace from "To ensure robustness…" to the end with:'),
  Q('The conventional 3SLS standard errors assume errors that are homoskedastic and independent across countries and years. Because the panel shows cross-sectional dependence and the residuals are serially correlated, we report three alternatives: (i) a country-clustered pairs bootstrap of the 3SLS system; (ii) two-way fixed-effects estimates of each equation with Driscoll and Kraay (1998) standard errors, robust to cross-sectional and serial dependence; and (iii) for the PAT × INC interaction, which is identified from very few higher-income countries, the restricted wild cluster bootstrap (MacKinnon and Webb, 2018; Roodman et al., 2019). We also report common correlated effects estimates (Pesaran, 2006) and a slope-homogeneity test (Pesaran and Yamagata, 2008). These approaches address inference and residual dependence within single equations; none of them relaxes the homogeneous-slope and error-structure assumptions of the 3SLS system itself, which remain a limitation (Section 7.3).'));

add(H('B6. Section 3.3 — data (comments 14, 17; section comment on the higher-income group)', 2),
  B('After "A detailed list of included and excluded countries is provided in Appendix A." insert: "Table 1b lists the seven countries classified as upper-middle or high income in 2000: Israel, Japan, the Republic of Korea and Malaysia in Asia; Botswana, Mauritius and South Africa in Africa."'),
  B('Insert Table 1b (two columns: Region | Countries with INC = 1): Asia | Israel, Japan, Republic of Korea, Malaysia; Africa | Botswana, Mauritius, South Africa.'),
  B('[CHECK] Ethiopia: see Part E1 before finalising the sample description.'));

add(H('B7. Section 4 — descriptive statistics and figures (comments 10, 16, 17)', 2),
  B('Table 2, PAT rows: replace the values with those of the variable `pat` (patent stock per million people) from do_10.6.do, Section 4.1; the current values (mean 32,349, maximum 1,642,643) are annual application flows. Update the sentence "Asia\'s patent stock exceeds Africa\'s by nearly three orders of magnitude" and the figures quoted with it after rerunning.'),
  B('After Table 4 insert Table 4b (Part C, Table 4b) and the paragraph: "Once country and year effects are removed (Table 4b), the correlations that dominate Table 4 largely disappear: lnGDP and lnPAT correlate at 0.330 rather than 0.888, and lnGDP and HCI at 0.020 rather than 0.847. Variance-inflation factors of the within-transformed regressors do not exceed 1.56 in either equation, so collinearity does not limit the identifying variation."'),
  B('Replace the sentence "The strong correlation between lnGDP and lnEF (0.835) is the empirical counterpart of the joint determination motivating the system estimator." with "The strong correlation between lnGDP and lnEF (0.835) is consistent with, but does not by itself establish, joint determination."'),
  B('Text under Figures 1–2: "driving a corresponding increase" → "which coincided with an increase"; "indicating an early development stage where growth-driven environmental pressures remain latent" → "consistent with limited income growth over the period". Text under Figure 3: "volatility" → "dispersion"; "skews both distributions upward" stays; delete "The co-expansion of income and footprint dispersion is thus attributable to intra-sample heterogeneity rather than independent stochastic trends."'),
  B('Figure 1 and 2 notes: add "Lines show cross-country means; shaded bands show [CHECK: ± one cross-country standard deviation / the interquartile range] in each year." Confirm in the figure code which statistic the band shows.'));

add(H('B8. Section 5.1 — EKC results (comments 5, 8)', 2),
  B('After the Asian paragraph and after the African paragraph, replace "neither region shows an EKC turning point within the sample range" with "no EKC curvature is identified within the observed income range in either region under the retained specification".'),
  B('African paragraph: after "This estimate is not robust:" keep the existing sentence and add: "The fixed-effects estimates in Table 12b confirm this estimator dependence for Africa in both equations: the income elasticity of the footprint is 0.323 under 3SLS and −0.011 under fixed effects, and the footprint coefficient in the growth equation is 1.181 and 0.210, respectively."'));

add(H('B9. Section 5.2 — innovation results (comments 4, 5, 6, 7, 17)', 2),
  B('Replace "Innovation raises income in every specification, and by more in Africa than in Asia." with "Patent stock is positively associated with income in both regional systems, more strongly in Africa than in Asia."'),
  B('Replace "The growth channel of Hypothesis 2 is supported in both regions and is the most precisely estimated relationship in the table." with "Under 3SLS the growth margin (H2a) is supported in both regions. Section 5.3 shows that the African association is robust across estimators, whereas the Asian one is not significant under fixed effects (Table 12b)."'),
  B('Replace "The environmental return to innovation therefore improves markedly with development." with "The association between patent stock and the footprint therefore differs markedly by development stage in Asia."'),
  B('After Table 11 insert Table 11b (joint Wald tests, Part C) and: "Joint tests confirm the pattern. In Asia the hypothesis that patent stock is unrelated to the footprint in both income groups is rejected (χ²(2) = 11.38, p = 0.003), as is the hypothesis that the growth and environmental associations are jointly zero in the higher-income group (χ²(2) = 14.02, p = 0.001). In Africa the interaction is significant only at the 10 percent level (χ²(1) = 3.27, p = 0.071)."'),
  B('Replace the paragraph beginning "Hypothesis 2 is fully supported on the growth margin…" with:'),
  Q('Hypothesis 2a is supported in both regions under 3SLS, and robustly so only in Africa. Hypothesis 2b, and therefore the dual role in the Green Solow sense, is supported only for the four Asian economies that were upper-middle or high income in 2000. In the three remaining cells the association between patent stock and the footprint is either negligible or imprecisely estimated. These are conditional associations: the patent stock is treated as predetermined, and the instrument available to test this assumption is weak (Appendix D1).'),
  B('Replace the H3 paragraph\'s first sentence with: "Hypothesis 3 is supported within the Asian sample, where the result rests on four higher-income countries, and only marginally within the African sample."'),
  B('Delete or move the stray paragraph "The estimated elasticity exceeds unity in the pooled and African samples…" to Section 5.1 directly after the sentence on the GDP equation, where it belongs.'));

add(H('B10. Section 5.3 — robustness, rewritten (comments 5, 6, 7, 8, 9, 15)', 2),
  P('**Action:** keep Table 12 and replace the text of Section 5.3 with the following five sub-sections; insert Tables 12b, 13, 14, 15 and Appendix D (Part C) where indicated.'),
  Q('5.3.1 Equation-by-equation comparison. Table 12b compares every 3SLS coefficient with its two-way fixed-effects counterpart, with country-clustered and Driscoll–Kraay standard errors. Three results are robust across estimators: the positive income elasticity of the footprint in Asia (0.737 under 3SLS, 0.570 under fixed effects), the positive association between biocapacity and the footprint, and the positive association between patent stock and income in Africa (0.078 and 0.097). Three are not. The African income elasticity of the footprint is 0.323 under 3SLS but −0.011 under fixed effects; the footprint coefficient in the African growth equation falls from 1.181 to 0.210; and the Asian association between patent stock and income (0.027 under 3SLS) is not significant under fixed effects (0.028, p > 0.10). The fixed-effects estimates do not instrument income or the footprint, so the comparison separates results that depend on the system identification from those that do not.'),
  Q('5.3.2 Sensitivity to individual countries. Because the higher-income Asian result rests on four countries, Table 13 re-estimates the Asian system omitting each of them in turn. The interaction remains negative and significant in all four cases under 3SLS (between −0.076 and −0.148), and the implied marginal effect for the higher-income group ranges from −0.066 to −0.140. Under Driscoll–Kraay standard errors the marginal effect remains negative throughout but loses significance when the Republic of Korea is omitted (−0.042, p > 0.10). The corresponding African interaction is not robust: omitting Botswana reverses its sign.'),
  Q('5.3.3 Alternative development classifications. Table 14 replaces the year-2000 classification with predetermined alternatives. A majority rule over 2000–2004 and a 2005 benchmark assign the same four Asian countries to the higher-income group and leave the results unchanged. A 2010 benchmark, which adds China and Thailand but is no longer predetermined, gives a smaller interaction (−0.044, p < 0.01) and marginal effect (−0.028, p < 0.10). A continuous interaction with the logarithm of income per capita in 2000 gives a negative and significant slope in Asia (−0.017, p < 0.01) and in Africa (−0.009, p < 0.05), indicating that the result does not depend on the binary threshold.'),
  Q('5.3.4 Inference with few higher-income countries. The statistical significance of the Asian interaction depends on the assumed error structure (Table 15). It is significant with conventional 3SLS standard errors (p < 0.01) and with Driscoll–Kraay standard errors (p = 0.010), but not with standard errors clustered by country: the clustered fixed-effects estimate has p = 0.117 and the restricted wild cluster bootstrap, appropriate when only four clusters are treated, gives p = 0.161. The point estimate is therefore robust in sign and magnitude, but its precision should be interpreted with caution.'),
  Q('5.3.5 Cross-sectional dependence, slope heterogeneity and further checks. Residuals of the two-way fixed-effects environmental equation remain cross-sectionally dependent (Pesaran CD = −2.77, p = 0.006). Common correlated effects pooled estimation (Pesaran, 2006) leaves weaker but significant dependence and does not reproduce the interaction (Asia: 0.083, p > 0.10). Country-specific CCE slopes, however, show the same heterogeneity in direction: the mean slope of patent stock is −0.261 (p < 0.10) for the four higher-income Asian countries, three of which have slopes between −0.32 and −0.36, against −0.051 (p > 0.10) for the other thirteen Asian countries (Appendix D2). The results are also robust to excluding biocapacity from the system (Asian interaction −0.122, p < 0.01; Appendix D3), to non-overlapping three-year averages that smooth annual shocks (−0.085, p < 0.05; Appendix D4), and to ending the sample in 2022, the last year of published footprint accounts (−0.082, p < 0.01; Appendix D5).'),
  Q('Taken together, the higher-income Asian association is the most robust result of the paper in sign and magnitude, while its statistical significance and the African and income-equation results are sensitive to the estimator and the error-structure assumptions.'));

add(H('B11. Section 6 — discussion (comments 11, 12)', 2),
  B('Heading 6.1 → "Heterogeneous growth–ecological footprint relationships across development stages". Heading 6.2 → "Innovation and ecological pressure: a conditional association".'),
  B('6.1, second paragraph: "The absence of a valid EKC place these results alongside…" → "The absence of identified EKC curvature places these results alongside…". "Pata et al. (2023) confirm the EKC for ASEAN" [CHECK]: Pata et al. (2023) in the reference list studies Germany; replace with the correct ASEAN study or delete the clause.'),
  B('6.2: restructure into three explicitly labelled layers. Insert at the start of 6.2:'),
  Q('We distinguish three layers of interpretation: what the model estimates directly, what is consistent with prior theory, and what remains a plausible but untested mechanism.'),
  B('In 6.2, paragraph 2, replace "it is consistent with the possibility that technological absorptive capacity, institutional quality, and complementary policy support enable countries…" with "Prior studies suggest, as a plausible but untested explanation, that technological absorptive capacity, institutional quality and complementary policy support may enable countries… (Chu et al., 2021); these variables are not included in our model." Apply the same labelling to the paragraph on regional differences ("Differences in industrial structure…").'),
  B('6.2, last paragraph: delete "innovation appears to acquire an environmental role when embedded within broader technological, institutional, and policy conditions that support knowledge diffusion, cleaner production, resource efficiency, and structural upgrading" and replace with "the negative association between patent stock and the footprint is confined to a small group of higher-income Asian economies, which is consistent with, but does not demonstrate, the view that complementary conditions matter".'));

add(H('B12. Section 7 — conclusions, policy, limitations (comments 8, 13, 18)', 2),
  B('7.1, first insight: replace "the evidence does not support an EKC for either Asia or Africa" with "no EKC curvature is identified within the observed income range in either Asia or Africa under the retained specification". Replace "By comparing countries at different regions" with "By comparing countries across regions".'),
  B('7.1, second insight: replace "The patent stock raises income per capita in both regions." with "Patent stock is positively associated with income per capita in both regions, robustly so in Africa." Add after the sentence on Asia: "This association is stable when each of the four higher-income Asian countries is omitted and under alternative predetermined classifications, but its statistical significance depends on the error structure assumed."'),
  B('7.1, add a closing sentence: "The strongest result is the conditional association in higher-income Asian economies; the other structural results are more sensitive to identification and to the choice of estimator."'),
  B('7.2: replace the whole section with:'),
  Q('Because the estimated relationships are conditional associations and some rest on small groups of countries, the implications below are stated as implications of the estimated patterns, not as estimated effects of policy.\nFirst, for the low- and lower-middle-income economies that form 36 of the 43 countries, the footprint rises monotonically with income over the observed range and patent stock shows no measurable association with the footprint. Growth in these economies should therefore not be expected to reduce ecological pressure by itself, nor should innovation capacity alone be relied upon to do so.\nSecond, patent stock is robustly associated with higher income in Africa. Strengthening innovation capacity there is consistent with the growth evidence; whether it also lowers ecological pressure is not supported by our estimates.\nThird, the negative association between innovation and the footprint in higher-income Asian economies, but not in higher-income African economies, suggests that results observed in one region should not be transferred to another without evidence. Prior literature points to complementary conditions such as regulation, absorptive capacity and green finance; these are not estimated in this study and are suggested as directions for policy evaluation rather than as tested recommendations.'),
  B('7.3: add as the first two limitations:'),
  Q('First, the income coefficient of the retained linear environmental equation is weakly identified, and the African income results depend on the estimator; they are interpreted as conditional associations. Second, the negative association between patent stock and the footprint in higher-income Asian economies rests on four countries; its sign and magnitude are robust, but its statistical significance depends on the error structure assumed. Third, patent stock is treated as predetermined; the shift-share instrument constructed to test this assumption is too weak to settle it. Fourth, the 3SLS system maintains homogeneous slopes and an error structure that are strong assumptions for a 43-country panel, although fixed-effects, Driscoll–Kraay and common-correlated-effects checks are reported.'),
  B('7.3, second limitation (existing): replace "explicitly accounts for endogeneity and bidirectional relationships among economic growth, innovation, and ecological pressure" with "accounts for the joint determination of income and ecological footprint".'));

add(H('B13. Language and references (comment 18)', 2),
  B('Abstract: "heterogeneity regions and income groups" → "heterogeneity across regions and income groups" (done in B1).'),
  B('6.1: "The absence of a valid EKC place" → "The absence of identified EKC curvature places" (done in B11).'),
  B('7.1: "By comparing countries at different regions" → "By comparing countries across regions" (done in B12).'),
  B('2.1: "Several studies challenges" → "Several studies challenge". 2.2: "Although the EKC model is well supported" → "Although the EKC has received considerable empirical support". 3.1: "polynomial forms of income enters" → "polynomial terms in income enter"; "help mitigating" → "helps to mitigate"; "we also considers" → "we also consider"; "Production-based data may misleads" → "Production-based data may misread"; "accumulate into a productive asset" → "accumulates into a productive asset". 3.1: delete the duplicated sentence "The resulting system is specified as follows:" which precedes no equation.'),
  B('References to remove or replace: Tu et al. (2008); Duong et al. (2015); Zegeye (1994) (if the 3SLS sentence is replaced as in B5); Khan et al. (2022) if its use is not about innovation [CHECK]. Correct the ASEAN citation in 6.1 [CHECK].'),
  B('References to add (verify every entry before submission; an automatic lookup could not be completed in this session): Pesaran (2006); Pesaran and Yamagata (2008); Pesaran (2021); MacKinnon and Webb (2018); Roodman et al. (2019); Goldsmith-Pinkham et al. (2020); Borusyak et al. (2022); WIPO (2026). Full entries are listed in Part E3.'));

// ------------------------------------------------------------------ Part C: tables
add(H('Part C — New tables (insert where indicated; replace with do_10.6.do output)', 1),
  P('Notes for every table: *** p < 0.01, ** p < 0.05, * p < 0.10; standard errors in parentheses; country and year fixed effects in all models; 43 countries (17 Asian, 26 African), 2000–2023 unless stated.'),
  H('Table 4b. Within-transformed correlations (do_10.6.do, Table 4 block)', 3),
  T([['', 'lnGDP', 'CAP', 'HCI', 'lnPAT', 'lnEF', 'lnBIO', 'URB'],
     ['lnGDP', '1.000', '', '', '', '', '', ''],
     ['CAP', '0.190', '1.000', '', '', '', '', ''],
     ['HCI', '0.020', '−0.217', '1.000', '', '', '', ''],
     ['lnPAT', '0.330', '−0.020', '0.090', '1.000', '', '', ''],
     ['lnEF', '0.546', '0.128', '−0.040', '0.169', '1.000', '', ''],
     ['lnBIO', '0.505', '−0.018', '0.158', '0.081', '0.539', '1.000', ''],
     ['URB', '0.306', '0.086', '0.141', '0.300', '0.198', '0.173', '1.000']]),
  P('Note: variables demeaned by country and year. Within-VIF, growth equation: lnEF 1.05, CAP 1.07, HCI 1.06, lnPAT 1.04; environmental equation: lnGDP 1.56, lnBIO 1.36, URB 1.16, lnPAT 1.19.'),
  H('Table 11b. Joint Wald tests for H2 and H3 (do_10.6.do, Section 5.2)', 3),
  T([['Null hypothesis', 'Pooled', 'Asia', 'Africa'],
     ['H2a: [GDP] lnPAT = 0', 'χ²(1) = 36.85 (0.000)', '8.35 (0.004)', '74.97 (0.000)'],
     ['[EF] lnPAT = [EF] PAT×INC = 0', 'χ²(2) = 7.54 (0.023)', '11.38 (0.003)', '9.25 (0.010)'],
     ['H3: [EF] PAT×INC = 0', 'χ²(1) = 1.09 (0.297)', '11.05 (0.001)', '3.27 (0.071)'],
     ['H2 dual role, INC = 1: [GDP] lnPAT = 0 and [EF] lnPAT + PAT×INC = 0', 'χ²(2) = 37.43 (0.000)', '14.02 (0.001)', '79.52 (0.000)']],
    [3700, 1890, 1890, 1890]),
  P('Note: p-values in parentheses; tests after the 3SLS systems of Table 10 (conventional 3SLS covariance).'),
  H('Table 12b. Coefficient-by-coefficient comparison of 3SLS and fixed effects (do_10.6.do, Sections 5.3 and R2.5)', 3),
  T([['Equation', 'Variable', 'Sample', '3SLS', '3SLS, clustered SE', 'FE, clustered SE', 'FE, Driscoll–Kraay'],
     ['GDP', 'lnEF', 'Asia', '0.595*** (0.077)', '(0.166)***', '0.667*** (0.089)', '(0.026)***'],
     ['GDP', 'lnEF', 'Africa', '1.181*** (0.117)', '(0.525)**', '0.210 (0.134)', '(0.052)***'],
     ['GDP', 'lnPAT', 'Asia', '0.027*** (0.009)', '(0.036)', '0.028 (0.037)', '(0.018)'],
     ['GDP', 'lnPAT', 'Africa', '0.078*** (0.009)', '(0.022)***', '0.097*** (0.019)', '(0.013)***'],
     ['EF', 'lnGDP', 'Asia', '0.737*** (0.121)', '(0.209)***', '0.570*** (0.113)', '(0.039)***'],
     ['EF', 'lnGDP', 'Africa', '0.323** (0.139)', '(0.443)', '−0.011 (0.100)', '(0.040)'],
     ['EF', 'lnPAT', 'Asia', '0.009 (0.010)', '(0.029)', '0.021 (0.023)', '(0.008)**'],
     ['EF', 'lnPAT', 'Africa', '−0.013 (0.015)', '(0.046)', '0.025** (0.012)', '(0.007)***'],
     ['EF', 'PAT×INC', 'Asia', '−0.086*** (0.026)', '(0.079)', '−0.093* (0.054)', '(0.036)***'],
     ['EF', 'PAT×INC', 'Africa', '−0.011* (0.006)', '(0.016)', '−0.019 (0.029)', '(0.013)']],
    [800, 950, 900, 1700, 1600, 1700, 1710]),
  P('Note: columns with only a standard error share the point estimate of the column to their left. FE estimates do not instrument lnEF or lnGDP. The clustered 3SLS standard errors here are analytic; do_10.6.do (R2.5) computes them by a country-clustered pairs bootstrap. Full table for all variables and the pooled sample: results/E_reconciliation.csv.'),
  H('Table 13. Leave-one-country-out, higher-income countries (do_10.6.do, R2.2)', 3),
  T([['Region', 'Omitted', 'PAT×INC, 3SLS', 'Marginal effect INC = 1, 3SLS', 'PAT×INC, FE-DK', 'Marginal effect INC = 1, FE-DK'],
     ['Asia', 'none', '−0.086*** (0.026)', '−0.077*** (0.023)', '−0.093*** (0.036)', '−0.073** (0.035)'],
     ['Asia', 'Israel', '−0.086*** (0.029)', '−0.081*** (0.026)', '−0.098*** (0.036)', '−0.077** (0.033)'],
     ['Asia', 'Japan', '−0.100*** (0.029)', '−0.094*** (0.027)', '−0.108*** (0.040)', '−0.094** (0.041)'],
     ['Asia', 'Rep. of Korea', '−0.076** (0.030)', '−0.066** (0.027)', '−0.062* (0.035)', '−0.042 (0.034)'],
     ['Asia', 'Malaysia', '−0.148*** (0.039)', '−0.140*** (0.036)', '−0.168*** (0.056)', '−0.146*** (0.055)'],
     ['Africa', 'none', '−0.011* (0.006)', '−0.024* (0.012)', '−0.019 (0.013)', '0.006 (0.015)'],
     ['Africa', 'Botswana', '0.021** (0.009)', '0.012 (0.018)', '0.041*** (0.008)', '0.065*** (0.013)'],
     ['Africa', 'Mauritius', '−0.025** (0.011)', '−0.047*** (0.010)', '−0.057*** (0.020)', '−0.033 (0.021)'],
     ['Africa', 'South Africa', '−0.014** (0.006)', '−0.026** (0.012)', '−0.023* (0.012)', '−0.001 (0.014)']],
    [900, 1300, 1800, 1800, 1780, 1780]),
  H('Table 14. Alternative predetermined development classifications (do_10.6.do, R2.3)', 3),
  T([['Classification', 'Region', 'Higher-income countries', 'PAT×INC', 'Marginal effect INC = 1'],
     ['Year 2000 (main)', 'Asia', 'IL, JP, KR, MY', '−0.086*** (0.026)', '−0.077*** (0.023)'],
     ['Majority of 2000–2004', 'Asia', 'IL, JP, KR, MY', '−0.086*** (0.026)', '−0.077*** (0.023)'],
     ['Year 2005', 'Asia', 'IL, JP, KR, MY', '−0.086*** (0.026)', '−0.077*** (0.023)'],
     ['Year 2010 (stress test)', 'Asia', 'CN, IL, JP, KR, MY, TH', '−0.044*** (0.014)', '−0.028* (0.015)'],
     ['Continuous: ln GDP pc 2000', 'Asia', 'all', '−0.017*** (0.005)', '—'],
     ['Year 2000 (main)', 'Africa', 'BW, MU, ZA', '−0.011* (0.006)', '−0.024* (0.012)'],
     ['Majority of 2000–2004', 'Africa', 'BW, MU', '−0.013** (0.006)', '−0.025** (0.012)'],
     ['Year 2005', 'Africa', 'BW, MU, ZA', '−0.011* (0.006)', '−0.024* (0.012)'],
     ['Year 2010 (stress test)', 'Africa', 'BW, MU, TN, ZA', '−0.013* (0.007)', '−0.022* (0.012)'],
     ['Continuous: ln GDP pc 2000', 'Africa', 'all', '−0.009** (0.005)', '—']],
    [2300, 900, 2300, 1930, 1930]),
  P('Note: the 2010 benchmark is not predetermined and is reported only as a stress test. For the continuous measure the column PAT×INC reports the coefficient on lnPAT × (ln GDP per capita in 2000, centred).'),
  H('Table 15. Inference on the Asian PAT × INC interaction (do_10.6.do, R2.4–R2.5)', 3),
  T([['Estimator and standard error', 'Coefficient', 'Standard error', 'p-value'],
     ['3SLS, conventional', '−0.086', '0.026', '< 0.01'],
     ['3SLS, clustered by country', '−0.086', '0.079', '0.28'],
     ['FE, Driscoll–Kraay', '−0.093', '0.036', '0.010'],
     ['FE, clustered by country (CRV1, t with 16 df)', '−0.093', '0.056', '0.117'],
     ['FE, restricted wild cluster bootstrap (Webb, 9,999 draws)', '−0.093', '—', '0.161'],
     ['3SLS, 3-year averages, conventional', '−0.085', '0.040', '< 0.05']],
    [4300, 1700, 1700, 1660]),
  P('Note: 17 Asian countries, of which 4 have INC = 1. Bootstrap p-values from do_10.6.do (boottest) will differ slightly from the Python values shown.'),
  H('Appendix D1. Patent-stock endogeneity (do_10.6.do, R2.1)', 3),
  T([['Sample', 'Equation', 'SW F (lnPAT)', 'SW F (PAT×INC)', 'C-test of exogeneity, p', 'IV coefficient lnPAT', 'IV coefficient PAT×INC'],
     ['Pooled (40)', 'GDP', '2.73', '—', '0.304', '0.141 (0.087)', '—'],
     ['Pooled (40)', 'EF', '0.01', '0.01', '0.766', '1.176 (9.352)', '−0.254 (1.422)'],
     ['Asia (15)', 'GDP', '3.86', '—', '0.848', '0.039 (0.102)', '—'],
     ['Asia (15)', 'EF', '17.07', '5.73', '0.784', '0.027 (0.091)', '0.027 (0.160)'],
     ['Africa (25)', 'GDP', '2.44', '—', '0.365', '0.148** (0.062)', '—'],
     ['Africa (25)', 'EF', '0.97', '1.70', '< 0.001', '0.246 (0.177)', '−0.150 (0.095)']],
    [1300, 900, 1200, 1300, 1500, 1580, 1580]),
  P('Note: instruments lnZ (shift-share) and lnZ × INC; income and footprint instrumented as in the main system. No instrument exists for DR Congo, Cambodia and the Philippines (their offices reported no origin breakdown for 1990–1999). With the stock of filings abroad the pooled EF first stage reaches F = 14.5 (lnPAT) and 7.3 (PAT×INC), and exogeneity is not rejected (p = 0.120). A 3SLS system with patent stock instrumented gives an Asian interaction of 0.052 (0.056), which is uninformative given the weak first stage.'),
  H('Appendix D2. Common correlated effects (do_10.6.do, R2.6)', 3),
  T([['', 'Pooled', 'Asia', 'Africa'],
     ['Residual CD, two-way FE', '−2.77 (0.006)', '−2.07 (0.038)', '−3.21 (0.001)'],
     ['Residual CD, CCE pooled', '−2.43 (0.015)', '−2.57 (0.010)', '−2.25 (0.025)'],
     ['CCE pooled: lnGDP', '0.316*** (0.073)', '0.282*** (0.102)', '0.306*** (0.075)'],
     ['CCE pooled: lnPAT', '0.032** (0.013)', '0.003 (0.024)', '0.012** (0.006)'],
     ['CCE pooled: PAT×INC', '0.043* (0.023)', '0.083 (0.071)', '0.064*** (0.012)'],
     ['CCE mean group, lnPAT slope, INC = 0', '—', '−0.051 (0.055), 13 countries', '−0.001 (0.025), 23 countries'],
     ['CCE mean group, lnPAT slope, INC = 1', '—', '−0.261* (0.084), 4 countries', '−0.246 (0.157), 3 countries']],
    [3000, 2120, 2120, 2120]),
  P('Note: country-specific slopes, INC = 1: Israel −0.353, Japan −0.011, Korea −0.356, Malaysia −0.324; Botswana −0.056, Mauritius −0.126, South Africa −0.557. Mean-group standard errors are the cross-country standard deviation divided by √n; with four countries they are imprecise. Run xthst in do_10.6.do for the Pesaran–Yamagata slope-homogeneity test.'),
  H('Appendix D3–D6. Further sensitivity (do_10.6.do, R2.7–R2.10)', 3),
  T([['Specification', 'Region', 'GDP eq.: lnEF', 'EF eq.: lnGDP', 'PAT×INC', 'Marginal effect INC = 1'],
     ['Main (Table 10)', 'Asia', '0.595***', '0.737***', '−0.086***', '−0.077***'],
     ['D3: no biocapacity', 'Asia', '0.687***', '0.764***', '−0.122***', '−0.106***'],
     ['D4: 3-year averages', 'Asia', '0.601***', '0.734***', '−0.085**', '−0.077**'],
     ['D5: 2000–2022', 'Asia', '0.593***', '0.782***', '−0.082***', '−0.077***'],
     ['Main (Table 10)', 'Africa', '1.181***', '0.323**', '−0.011*', '−0.024*'],
     ['D3: no biocapacity', 'Africa', '0.236', '0.301***', '−0.022**', '−0.022*'],
     ['D4: 3-year averages', 'Africa', '1.322***', '0.262', '−0.012', '−0.019'],
     ['D5: 2000–2022', 'Africa', '1.096***', '0.289**', '−0.012*', '−0.021*'],
     ['D6: without Ethiopia', 'Africa', '0.733***', '0.265', '−0.020**', '−0.024'],
     ['D6: without Ethiopia', 'Pooled', '0.996***', '1.158***', '0.002', '−0.054***']],
    [2300, 900, 1500, 1500, 1500, 1660]),
  P('Note: 3SLS, conventional standard errors (full results with standard errors in results/H_biocapacity.csv, L_three_year_averages.csv, I_period_2022.csv, M_ethiopia_cap.csv). In the 3-year panel the first-stage F for income in the EF equation is 2.99 (Asia) and 3.84 (pooled), so averaging does not resolve the weak identification of the environmental equation.'));

// ------------------------------------------------------------------ Part D: response letter
add(H('Part D — Draft replies for the response letter (comments 4–18)', 1),
  P('Insert each reply under the corresponding comment in Response_10.5.docx. Adjust page and line numbers after editing.'));
const R = (n, t) => add(P(`**Comment ${n}.**`), Q(t));
R(4, 'We thank the reviewer for this important point. We constructed an external shift-share instrument for patenting: each country\'s 1990–1999 shares of foreign applicants\' filings at its patent offices, multiplied by those applicants\' lagged filings abroad, excluding filings into the country itself (WIPO data; Appendix D1). The instrument is weak for the patent stock used in the paper (Sanderson–Windmeijer F between 0.01 and 3.9 in most equations), and exogeneity is not rejected in the pooled and Asian equations (C-test p = 0.30–0.85) but is rejected in the African environmental equation. Because the instrument cannot settle the question, we follow the reviewer\'s alternative: the patent stock is described as predetermined, all patent coefficients are interpreted as conditional associations throughout, and causal wording ("raises", "promotes", "drives") has been removed (Sections 3.1, 5.2, 6, 7 and Abstract). The instrument analysis is reported in full in Appendix D1 for transparency.');
R(5, 'We agree and now evaluate robustness coefficient by coefficient. Table 12b reports every 3SLS coefficient alongside fixed-effects estimates with clustered and Driscoll–Kraay standard errors, and Section 5.3.1 discusses the divergences explicitly: the African income elasticity of the footprint (0.323 under 3SLS, −0.011 under FE), the African footprint coefficient in the growth equation (1.181 vs 0.210) and the Asian patent–income association (significant under 3SLS only). We no longer describe the findings as substantively consistent; the conclusion states which results are robust and which depend on the estimator.');
R(6, 'We have added a leave-one-country-out analysis (Table 13). Omitting Israel, Japan, the Republic of Korea or Malaysia in turn, the Asian interaction remains negative and significant under 3SLS (−0.076 to −0.148); under Driscoll–Kraay standard errors the marginal effect stays negative but is not significant when Korea is omitted. We also report the restricted wild cluster bootstrap, designed for few treated clusters (Table 15): the interaction is not significant under country clustering (p = 0.161). The paper now states that the result rests on four countries and that its sign and magnitude are robust while its significance depends on the error structure. The three African higher-income countries are also examined; the African interaction is not robust (its sign reverses without Botswana), which we now report.');
R(7, 'A baseline classification is preferred because a contemporaneous classification would be determined by the dependent variable of the growth equation; this justification is now given in Section 3.1. Table 14 reports three predetermined alternatives (majority status over 2000–2004, the 2005 classification and a continuous measure based on income per capita in 2000) and a 2010 benchmark as a stress test. The Asian results are unchanged under the first two, remain significant under the continuous measure (−0.017, p < 0.01), and are smaller but significant under the 2010 benchmark.');
R(8, 'We agree. All statements now read that no EKC curvature is identified within the observed income range under the retained specification (Abstract, Sections 5.1, 6.1 and 7.1).');
R(9, 'We now report residual cross-sectional dependence tests, common correlated effects pooled and mean-group estimates (Appendix D2) and the Pesaran–Yamagata slope-homogeneity test. Residual dependence remains after CCE; the pooled CCE estimator does not reproduce the interaction, while country-specific CCE slopes show the same heterogeneity in direction (mean slope −0.261 for the higher-income Asian countries against −0.051 for the others). The limitations section now states that the 3SLS system maintains homogeneous slopes and an error structure that are strong assumptions for a 43-country panel, and that the single-equation corrections do not relax them.');
R(10, 'We now report within-transformed correlations and variance-inflation factors (Table 4b). After removing country and year effects, the correlation between lnGDP and lnPAT is 0.330 (0.888 in the pooled data) and between lnGDP and HCI 0.020 (0.847); within-VIFs do not exceed 1.56.');
R(11, '"Sustainability transitions" has been removed as an interpretive frame; the paper now uses "growth–environment relationship", "ecological pressure" and "development-stage heterogeneity" (Sections 2.2, 2.3, 6 and 7, including section headings).');
R(12, 'Section 6.2 now distinguishes what is estimated, what is consistent with prior theory and what is a plausible but untested mechanism. Absorptive capacity, governance and policy support are presented as explanations from the literature that are not included in our model.');
R(13, 'Section 7.2 has been rewritten so that each implication follows from an estimated pattern; policies such as regulation, green finance or technology transfer are mentioned only as directions for evaluation suggested by the literature, not as effects demonstrated by the model.');
R(14, 'Section 3.1 now specifies the WIPO series (total applications by applicant origin, all offices, direct filings and PCT national-phase entries, so that PCT applications are not double counted), the treatment of years in which home offices did not report, the perpetual-inventory formula, the initial-stock rule (P_1980/(g_i + δ) with g_i the 1980–1985 growth rate) and the normalisation by population. The do-file is available on request. In checking reproducibility we found that Table 2 reported annual applications rather than the stock per million; this has been corrected.');
R(15, 'We re-estimated the system excluding biocapacity from the environmental equation and from the instrument set of the growth equation (Appendix D3), and estimated the growth equation with urbanisation as the only instrument. The Asian results are unchanged (interaction −0.122, p < 0.01); the African footprint coefficient in the growth equation is not robust, consistent with Table 12b.');
R(16, 'The figure notes now define the shaded bands [CHECK: as ± one cross-country standard deviation], "volatility" has been replaced by "dispersion", and causal descriptions such as "GDP growth drove the footprint increase" have been replaced by descriptive language ("coincided with", "is consistent with").');
R(17, 'We have carried out a line-by-line consistency audit. Corrections include: Table 2 (patent stock per million instead of annual applications), the CAP source in Table 1 (World Development Indicators), the PAT classification in Table 1, the description of the design as regional estimations with income-group interactions, a compact table of the seven higher-income countries (Table 1b), joint Wald tests for H2 and H3 (Table 11b), the attribution of the CD test, and the separation of model-selection evidence (Section 5.1) from hypothesis testing (Sections 5.2–5.3).');
R(18, 'The manuscript has been edited for language, including the sentences identified by the reviewer. Every citation has been checked for relevance: Tu et al. (2008) and Duong et al. (2015) were removed, a mis-attributed citation on the ASEAN EKC was corrected, and the claim about the relative accuracy of 3SLS is now supported by the general efficiency argument rather than a single application. [CHECK: arrange professional language editing and state it here.]');

// ------------------------------------------------------------------ Part E
add(H('Part E — Points for the author before submission', 1),
  H('E1. Ethiopia (data error)', 2),
  P('The WDI extract reports gross capital formation (NE.GDI.TOTL.ZS) equal to 0 for Ethiopia in 2000–2010. This value is implausible. Please re-download the series for Ethiopia from WDI. If WDI has valid values, rerun do_10.6.do; the pooled and African results will change (Appendix D6 shows the result without Ethiopia: pooled income elasticity of the footprint 1.158 instead of 0.629). If WDI has no values for those years, Ethiopia must leave the balanced sample (42 countries), and Sections 3.3, 4.1 and Appendix A must be updated.'),
  H('E2. Items marked [CHECK]', 2),
  B('Figure 1–2 band definition (B7, comment 16).'),
  B('ASEAN EKC citation in 6.1 (Pata et al. 2023 studies Germany) and the use of Khan et al. (2022) in 2.2.'),
  B('Pesaran CD test citation (B5).'),
  B('Which IMF series `cepi` is (do_10.6.do, block [cepi]); the default is the commodity export price index weighted by exports/GDP with fixed weights.'),
  B('Professional language editing statement (reply to comment 18).'),
  H('E3. References to add (verify each entry; automatic verification was unavailable)', 2),
  B('Borusyak K, Hull P and Jaravel X (2022) Quasi-experimental shift-share research designs. Review of Economic Studies 89(1): 181–213.'),
  B('Goldsmith-Pinkham P, Sorkin I and Swift H (2020) Bartik instruments: What, when, why, and how. American Economic Review 110(8): 2586–2624.'),
  B('MacKinnon JG and Webb MD (2018) The wild bootstrap for few (treated) clusters. Econometrics Journal 21(2): 114–135.'),
  B('Pesaran MH (2006) Estimation and inference in large heterogeneous panels with a multifactor error structure. Econometrica 74(4): 967–1012.'),
  B('Pesaran MH (2021) General diagnostic tests for cross-sectional dependence in panels. Empirical Economics 60(1): 13–50.'),
  B('Pesaran MH and Yamagata T (2008) Testing slope homogeneity in large panels. Journal of Econometrics 142(1): 50–93.'),
  B('Roodman D, Nielsen MØ, MacKinnon JG and Webb MD (2019) Fast and wild: Bootstrap inference in Stata using boottest. Stata Journal 19(1): 4–60.'),
  B('World Intellectual Property Organization (2026) WIPO IP Statistics Data Center, indicator "Total patent applications (direct and PCT national phase entries)", by filing office and applicant origin. Geneva: WIPO. Data updated May 2026.'),
  B('If cepi is used: Gruss B and Kebhaj S (2019) Commodity terms of trade: A new database. IMF Working Paper 19/21. Washington, DC: International Monetary Fund.'),
  H('E4. What the revision does not change', 2),
  B('The study period remains 2000–2023; the 2000–2022 estimates are a robustness check only (GFN marks 2023 as an estimate rather than a published account).'),
  B('The main estimator remains 3SLS with the year-2000 income classification; all new analyses are sensitivity checks.'),
  B('Minimum requirements 1–3 (already addressed by the author) are not revisited.'));

save(doc(c, 'Revision R2 guidance'), 'R2_revision_guidance_for_Claude_in_Word.docx').then(() => console.log('saved'));
