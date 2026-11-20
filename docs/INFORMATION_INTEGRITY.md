# Information Integrity and Reality Analysis (O42-IIRA-01)

Proposed by ChatGPT 6 (OpenAI) in answer to the Originator's question "Can Omega42 apply its math to identify AI-created content, misinformation and disinformation?", relayed on 20 November 2026; recorded here by the Navigator (claude-opus-5-5). A research initiative at level B; the Core additions are proposal CA-33, for ESC. Website: integrity.html.

## The question

Can the mathematical structure of Omega42 help distinguish the origin, integrity, transformation and propagation of information, and find relationships that conventional methods overlook? And, more widely: can it help tell the appearance of consensus from the existence of independently supported knowledge?

## Three questions kept apart

Origin (human, AI, both, unknown); accuracy (are the statements true?); intent and use (inform, mislead, impersonate, deceive). Terms: AI-generated content; misinformation (false or misleading, intent aside); disinformation (spread deliberately to deceive); malinformation (genuine information used harmfully); manipulated content; synthetic impersonation. The content alone rarely shows intent, so deception is not inferred from inaccuracy.

## Six mathematical directions

1. **Structure:** a feature vector x = [x1, ..., xn] per item and divergence from a reference distribution, D_KL(P||Q). Unusual is not AI-generated, and AI-generated is not false.
2. **Provenance:** a directed graph G = (V, E) of documents, versions and sources joined by copied, derived, edited, quoted, translated or attributed. Missing provenance is missing evidence, not proof of fabrication.
3. **Claims:** C = {c1, ..., cn}, each joined to evidence, sources, dependants and contradictions. Claim statuses: VERIFIED, SUPPORTED, PARTIALLY SUPPORTED, CONTRADICTED, UNVERIFIED, INSUFFICIENT EVIDENCE, OUTDATED, MISREPRESENTED; they describe claims, never people or publishers.
4. **Propagation:** a changing network G_t = (V, E_t), I(t+1) = F(I_t, A_t, N_t, E_t). The number of repetitions is not the number of independent confirmations.
5. **Time:** T(c) = (t_event, t_creation, t_publication, t_redistribution); old material presented as new is caught by comparing them.
6. **Uncertainty:** Shannon entropy H(X) = −Σ p_i log2 p_i over candidate explanations (0.5, 0.3, 0.2 gives 1.49 bits); calibrated uncertainty, and the freedom to say the evidence is too thin to estimate.

## Where Omega42's own mathematics could enter (experiments, not assumptions)

- **IIRA-07:** map information features into the 81-state space; test whether the map preserves distinctions, groups similar records, separates kinds of manipulation, adds information beyond ordinary feature vectors, and survives translation and paraphrase.
- **Recurrence:** read successive versions C0 → C1 → ... → Cn of a claim as a transformation sequence; test whether progressive distortion and reused manipulation techniques can be detected.
- **Shared ancestry:** S_ij = w1 L_ij + w2 C_ij + w3 E_ij + w4 T_ij over linguistic, claim-structure, evidence and timing similarity; a high score marks a cluster to investigate, never coordination or intent by itself.

## The Information Integrity Engine (O42-IIE-01)

Six modules: synthetic content analysis; provenance and source reconstruction; claim verification; propagation analysis; temporal and contextual analysis; reliability assessment. Each information object I_i = [O_i, C_i, P_i, T_i, N_i, E_i] (origin, claims, provenance, time, network, evidence); the system I(t) = {I_1, ..., I_n, G_t} evolves as I(t+1) = F(I(t), U(t), ε_t), a modeling architecture and not a law. Output: an integrity profile (origin evidence, factual support, source independence, temporal consistency, provenance, propagation), never a single trust score.

Report format: material examined; question and scope; origin; claims; source and provenance; timeline; network; mathematical analysis; alternative explanations; findings and uncertainty; further investigation; and which findings came from internal Omega42 mathematics and which from outside research.

## Hypotheses (to be registered under STP before any run)

| ID | Hypothesis |
|---|---|
| H-IIE01 | Structural patterns help distinguish some AI-generated content from human-generated content, beyond conventional detectors and simple baselines |
| H-IIE02 | Provenance graphs expose hidden source dependencies |
| H-IIE03 | Recurrence and transformation patterns identify progressive distortion |
| H-IIE04 | Claim-relationship analysis improves factual assessment over document-level assessment |
| H-IIE05 | Integrated analysis improves out-of-sample detection of coordinated manipulation |

Benchmark: original human writing; unedited, human-edited and AI-edited AI content; paraphrased and translated material; accurate, false and misleading-but-accurate claims; fabricated references; altered images and video; coordinated but harmless repetition; deliberate campaigns; and unusual, formulaic, technical, translated and non-native human writing, so that distinctive people are not mislabeled. Compare conventional statistics, existing detectors, provenance, network analysis, Omega42 methods and the combined system; measure precision, recall, false-positive and false-negative rates, F1, AUROC, calibration, robustness to paraphrase and adversarial editing, and generalization to unseen generators. Development and held-out data kept apart; the final evaluation administered independently.

## Research records

IIRA-01 architecture · IIRA-02 AI-generated content and mathematical signatures · IIRA-03 provenance and source dependency · IIRA-04 claim verification and contradiction graphs · IIRA-05 propagation and coordinated activity · IIRA-06 temporal and contextual integrity · IIRA-07 the 81-state classification experiment · IIRA-08 integrated benchmark and independent validation. Proposed identifiers; none is yet a registered test.

## Roadmap

1. Claim and evidence verification (usable now through the Navigator prompt on integrity.html). 2. Provenance and source relationships. 3. AI-generated content research and the benchmark. 4. Propagation. 5. The integrated engine, evaluated independently.

## Safeguards

Never declare AI authorship from a detector score; never call anyone deliberately deceptive without evidence of intent; never treat agreement between AI systems sharing a model or sources as independent verification; never confuse reputation with truth; never treat absence of evidence as proof of absence; never let an automated assessment become an unquestionable authority; keep the material, the steps and the evidence so conclusions can be challenged; protect privacy; challenge misinformation without suppressing disagreement, unconventional research or unpopular ideas. The same method applies to a scientific paper, a political speech, an ancient manuscript, a channeled text or a reported extraterrestrial communication: the subject does not decide the conclusion in advance.

## Background

NIST, Reducing Risks Posed by Synthetic Content: An Overview of Technical Approaches to Digital Content Transparency (2024). C2PA, Content Credentials specification and explainer. Reviews of AI-text detection report performance that varies with model, subject, length and paraphrasing, with false positives. These describe the field; they do not show that Omega42's mathematics has value for these tasks.
