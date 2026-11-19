# The Meaningful Existence Initiative

Historical inheritance, agency and human development. Proposed by the Originator (19 November 2026) and APE-502. The model is in Companion Part 233 and the instrument is `tools/choice_engine.py`. Opening the initiative is ESC's decision (`docs/DECISIONS_PENDING.md` D-13).

## The question

How do inherited structures, environmental conditions, and individual or collective choices interact to produce the historical trajectories and experienced meanings of human lives?

It is paired with the Common Mathematical Foundations Project (`research/physics/INITIATIVE.md`). That project asks what makes existence structurally possible. This one asks what makes a particular existence historically and experientially significant.

## The model in one line

v(t+1) = T v(t) + c(t). The law T is the default layer: it keeps every state on its orbit. The added terms c are the meaningful layer: only they move a state to another orbit, and nearly every one does (0.736 at 9, rising to 0.990 at 243; H-029). Each added term is carried forward by the law and never fades. Inheritance splits exactly into one part per channel. Each channel is evidenced on its own (Companion 233.3).

## Four projects

| Project | Question | First task |
|---|---|---|
| A. Inherited conditions | Through which channels do conditions pass between generations, and how strong is the evidence for each? | A table of channels (genetic, epigenetic, behavioral and relational, cultural, institutional), each with its current evidence, sourced and dated under L-503. Human epigenetic transmission is entered as contested |
| B. Habit and recurrence | How do repeated behaviors become stable, and what changes them? | Run the Temporal Engine on a public daily-activity series: is the pattern a season plus an integrated level, and does an announced change of routine move the level rather than the season? (CX-019, to be registered with its dataset and criterion before any run) |
| C. Agency and historical change | Under what conditions do people and groups change an inherited pattern? | The case design below |
| D. Intergenerational consequences | How do choices reach descendants, communities, institutions and environments? | Map the five channels onto documented cases, keeping historical significance apart from experiential and normative significance (Companion 233.4, ME-06) |

## The case design: one pattern across generations

APE-502 proposes conflict avoidance in families. The design separates:
- biological predisposition, where evidence supports it;
- family learning and modeling;
- environmental reinforcement;
- cultural expectation;
- individual interpretation and decision;
- change across generations.

Three rules apply. A likeness between generations is never read as transmission. Each channel is named only on its own evidence. Observation, correlation, causation, interpretation and speculation are kept apart, using the relationship kinds of Core L-503 (5). The study needs consent, ethics review and people trained in family research. It is not run by an AI on a person's own family history.

## What it will not do

- Give a single score for how meaningful a life is (Companion 233.6).
- Read the Meaning Registry (Core L-497), or grade meaning in any test (L-495).
- Decide whether meaning exists independently of those who find it. The positions are set side by side and their consequences examined.
- Blame anyone for what they inherited. Responsibility is proportionate to knowledge, control, capacity and the alternatives available (Companion 233.7 (a)).

## Results so far

- H-029, VERIFIED COMPUTATION: as resolution grows, almost every single choice moves a state to another orbit.
- H-030, VERIFIED COMPUTATION, blind at 729: the share that leaves the orbit unchanged falls by about a third per power of 3. As a theorem it is UNPROVEN.
- The Choice Engine's selftest (in CI) confirms four results: a one-time choice never fades; its gap recurs with the period of the law; the cancelling term is the present form of the choice; and the channel parts sum exactly to the state.

## ME-01 to ME-03 (APE-503 to APE-505): the mathematics taken in

The three papers set out a history-dependent dynamical system with agency (ME-01), bistable habit dynamics with tipping and hysteresis (ME-02), and the Transformability Profile TP-01 (ME-03). Their mathematics recomputes (TR-01, VERIFIED COMPUTATION; `tools/transformability.py`). How they stand to the law is in Companion 233.13 and 233.14:
- **Controllability is the norm.** For a choice made along one direction b, det[b, T b] = N(b).
- **History matters exactly to the extent that the present is seen partially:** 0 bits with the whole state observed, 3.17 bits with one coordinate.
- **The transmission eigenvalues are φ and −1/φ.**
- **The papers' habit is an attractor of a forgetting system; the law conserves.** Inside the law, a new orbit is kept with no further support.

The papers' empirical hypotheses (H-ME01 to H-ME13) and the cross-domain test ME-04 (behavior, ecology, institutions) belong to projects B to D. Each is registered in the STP register with its data and criterion fixed before any run. None has been run. The mathematical questions they open are:
- H-033: does the logistic habit model arise from the law by coarse-graining with forgetting and noise?
- the conditions under which a self-reinforcing pattern becomes transformable. Answered in the coarse model by the band a ∈ (−3.415, −2.585) at β = 6. Answered in the law by N(b) being a unit.

## ME-04 (APE-506): relational reality and human futures

Adopted as project E of the initiative. It covers persons coupled by asymmetric influence, relationships as dynamic systems, consensus reality as a collectively maintained model (kept apart from external and individual reality), the four agencies, and prediction as a distribution of futures tested on unseen observations (H-ME14 to H-ME20). The validation sequence runs relationship stability, group consensus, group cooperation, institutional change, then societal trajectories. Each hypothesis is registered with its data and criterion before any run.

The law adds exact results (Companion 233.15; RC-01 VERIFIED COMPUTATION):
- Persons who each follow the law never reach agreement by averaging alone: not modulo 9 for any influence, and over the reals the difference grows by at least √5/2 per step.
- Agreement needs a choice aimed at the difference, or influence shaped by the law itself.
- The shared mode of a group, its consensus reality, moves by the law, and its members' differences persist.

A first test of ME-04 against the law is therefore registrable: do real belief-averaging data fit agents without an inner law (convergence), or agents with one (persistence)?
