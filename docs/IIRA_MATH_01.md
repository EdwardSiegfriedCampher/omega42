# O42-IIRA-MATH-01: machine-verifiable mathematics for information integrity

Proposed by ChatGPT 6 (OpenAI), relayed by the Originator on 20 November 2026; implemented and checked by the Navigator (claude-opus-5-5) in `records/integrity/iira_math.py`, which runs in CI on every change. Part of the Information Integrity initiative (`docs/INFORMATION_INTEGRITY.md`, O42-IIRA-01; proposal CA-33, for ESC).

Any AI, researcher or programmer can check every number here without trusting Omega42: run `python3 records/integrity/iira_math.py` (standard library only; checked on Python 3.11, 3.12 and 3.13), or translate it into another language and compare.

## Three verification levels

1. **Arithmetic:** can another system reproduce the numbers? (modular arithmetic, matrix products, probabilities, statistics)
2. **Mathematics:** are the definitions, assumptions, equations and derivations valid? (invertibility, loop decomposition, convergence, independence assumptions)
3. **Application:** does the method work on real information-integrity problems? (benchmarks, misinformation, source reconstruction)

A method can pass level 1 and fail level 2, or pass levels 1 and 2 and fail level 3. Every module below is at levels 1 and 2. Level 3 is untested for all of them.

## The verification contract

Every mathematical record states: RESEARCH ID · MATHEMATICAL CLAIM · STATUS · DEFINITIONS · ASSUMPTIONS · INPUTS · EQUATIONS · DERIVATION · WORKED EXAMPLE · REFERENCE IMPLEMENTATION · EXPECTED OUTPUT · INDEPENDENT TESTS · KNOWN LIMITATIONS · INTERPRETATION · OPEN QUESTIONS. "AI verified" is not enough: a verification record says what was checked, how, and whether the checking system was independent of the author (an AI sharing the author's model or sources is not).

## The modules

| ID | Statement | Equation | Worked example (expected output) | Interpretation and limits |
|---|---|---|---|---|
| M1 | The Omega42 law is invertible and splits the 81 states into five loops | T(a, b) = (b, a + b) mod 9; det A = −1 ≡ 8, a unit; T⁻¹(a, b) = (b − a, a) | loops [1, 8, 24, 24, 24]; fixed point (0, 0); (1, 2) → (2, 3) → (3, 5) → (5, 8) → (8, 4) | Invertibility means no two states merge in the model; it says nothing about loss of real information |
| M2 | Robust anomaly score | z_r = 0.6745 (x − median) / MAD | x = 20 against [8, 9, 10, 10, 11, 12, 13]: 6.745 | An anomaly against a stated reference, not evidence of AI authorship |
| M3 | Distribution difference | JSD = ½ KL(P‖M) + ½ KL(Q‖M), base 2, 0 ≤ JSD ≤ 1 | (0.5, 0.3, 0.2) vs (0.2, 0.3, 0.5): 0.095816; disjoint: 1 | Difference is not provenance |
| M4 | Effective number of independent source groups | N_eff = 1 / Σ w_k² | one group: 1; five equal: 5; groups 6, 2, 2 of ten: 2.2727 | The groups themselves must be established from evidence |
| M5 | Evidence in odds form | posterior odds = prior odds × Π LR_k, for conditionally independent evidence | LR 3 and 4 from even odds: 12 : 1, 0.9231; if the second only copies the first: 3 : 1, 0.75 | Multiplying dependent evidence overstates confidence |
| M6 | Claim drift | c = (assertion, scope, causal strength) on 0..4; d Euclidean; D_path = Σ steps, D_direct = d(C₀, Cₙ) | C₀ = (1, 2, 0), C₃ = (4, 3, 4): √26 = 5.099; D_path ≥ D_direct always | The scale needs validation and annotator agreement |
| M7 | Linear propagation | x(t + 1) = W x(t), W row-stochastic | x(1) = (0.5, 0, 0.5), x(2) = (0.25, 0.25, 0.5); this W is doubly stochastic, so x(t) → (⅓, ⅓, ⅓) | Real spread is nonlinear: thresholds, reinforcement, forgetting |
| M8 | Provenance completeness | P_c = verified applicable fields / applicable fields | 4 of 5: 0.8 | 80 % of fields verified, not 80 % authentic |
| M9 | Uncertainty over explanations | H = −Σ p log₂ p | (0.5, 0.3, 0.2): 1.4855 bits | A measure of what is not known, not a truth score |
| M10 | The 81-state information map (experimental) | two characteristics on nine levels → (a, b) ∈ (Z/9)²; report its loop | 1, 8 and 72 states on loops of length 1, 8 and 24; (2, 5) is on a 24-loop | Well defined; whether the loop carries meaning is H-IIE06, untested |

**A correction to the proposal.** The proposal read D_path > D_direct as a sign that changes partly reversed one another. By the triangle inequality D_path ≥ D_direct always, with equality only when every step moves in the same direction; a strict inequality shows that the steps changed direction (a turn or a reversal), not specifically a reversal. The module checks both cases.

## The key experiment (H-IIE06, MATH-IIRA-01)

Does adding the 81-state representation to carefully defined information characteristics improve classification, comparison or prediction of information integrity? Three arms on unseen material: (A) conventional statistical features; (B) A plus source-dependency and claim graphs; (C) B plus the 81-state representation. Measured by accuracy, precision, recall, false-positive and false-negative rates, calibration, and robustness to editing and paraphrase across content types. If C is no better than B, that is reported. Registered under STP before any run.

## Further mathematical questions

MATH-IIRA-01 the 81-state structure and information patterns · MATH-IIRA-02 recurrence and progressive distortion · MATH-IIRA-03 quantifying independent confirmation (source graphs with M4 and M5) · MATH-IIRA-04 information integrity as a dynamic system · MATH-IIRA-05 an integrated model against conventional baselines on held-out data. Research questions, not results.

## A prompt for an independent verifier

Paste into any AI: "Read docs/IIRA_MATH_01.md and records/integrity/iira_math.py from the Omega42 repository. Recalculate every worked example from the definitions alone, check each derivation, translate the reference implementation into another language and run it, test boundary cases (empty or zero-spread inputs, weights not summing to 1, zero probabilities), look for counterexamples and unstated assumptions, and separate valid mathematics from unsupported interpretation. Report what you checked, how, and whether you share a model or sources with the author."
