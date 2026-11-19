"""Builder: (re)embed every file the release requires (Core L-493). Idempotent: removes and rebuilds the appendices."""
import sys, os, re, html, glob, ast
sys.path.insert(0, '/home/claude/work')
from mv import *
REPO = '/home/claude/repo'
INFRA = {'tools/intake.py', 'tools/site_build.py', 'tools/curator.py', 'tools/newsletter.py', 'tools/records.py', 'tools/setup_repo.py',
         'tools/consistency_check.py', 'tools/inventory_compare.py'}
LEGACY = {'scripts/' + n for n in ('canonical_reference.py', 'canonical_reference_av.py', 'm193_m225.py', 'omega42_ledger.py', 'stopword_harness.py', 'crc60_and_m267.py', 'ground_challenge.py')}
rel = lambda p: os.path.relpath(p, REPO)
tools = sorted(rel(p) for p in glob.glob(REPO + '/tools/*.py'))
nav_tools = ['tools/extract_embedded.py'] + [t for t in tools if t not in INFRA and t != 'tools/extract_embedded.py']
DATA = ['records/congruence/domains.txt', 'records/srp/collatz_domain.txt', 'records/srp/hydrogen_domain.txt', 'records/frameworks/seth.txt',
        'records/frameworks/ra.txt', 'records/frameworks/seth_peer.txt', 'records/frameworks/ra_peer.txt', 'records/frameworks/christian.txt', 'records/frameworks/islamic.txt', 'records/frameworks/hindu.txt', 'records/frameworks/buddhist.txt', 'records/frameworks/jewish.txt', 'records/frameworks/role_assignments.txt', 'records/frameworks/philosophy_selection.txt', 'records/frameworks/neoplatonic.txt', 'records/frameworks/stoic.txt', 'records/frameworks/spinozist.txt', 'records/frameworks/taoist.txt', 'records/frameworks/leibnizian.txt', 'records/frameworks/philosophy_selection_addendum.txt', 'records/frameworks/pythagorean.txt', 'records/frameworks/heraclitean.txt', 'records/frameworks/tensions.txt', 'records/frameworks/common_question.txt', 'records/frameworks/blind_kit.txt', 'records/frameworks/scholar_atlas_call.txt', 'records/frameworks/contemporary_selection.txt', 'records/frameworks/contemporary_selection_addendum.txt', 'records/frameworks/kauffman.txt', 'records/frameworks/penrose.txt', 'records/frameworks/wolfram.txt', 'records/frameworks/barbour.txt', 'records/frameworks/hofstadter.txt', 'records/frameworks/hoffman.txt', 'records/frameworks/kastrup.txt', 'records/resonance/features_retroactive.txt', 'records/resonance/object_panels_frozen.txt', 'records/resonance/object_panel3_frozen.txt', 'records/resonance/polytopes_output.txt', 'records/resonance/proximity.txt', 'records/resonance/objects.txt', 'records/resonance/calibration.txt', 'records/resonance/single_figure_output.txt', 'records/resonance/profiles.txt', 'records/instances/register.json', 'records/instances/seq_0001.txt', 'records/instances/seq_0007.txt', 'records/instances/seq_0010.txt', 'records/instances/seq_0016.txt', 'records/instances/seq_0017.txt', 'records/instances/seq_0018.txt', 'records/instances/seq_0019.txt', 'records/instances/seq_0020.txt', 'records/instances/seq_0021.txt', 'records/frame_audit/control_positive.txt',
        'records/frame_audit/control_negative.txt', 'records/reexamination/jurisdiction_registry.json',
        'records/frameworks/lens_relevance.json', 'records/prominence/register.json', 'records/conformance/practice_set.txt',
        'records/consciousness/theory.json', 'records/consciousness/CT-S1_freeze.txt', 'records/consciousness/conjectures.json', 'records/utility/register.json', 'records/frameworks/depths.txt', 'records/frameworks/shared_ground.txt', 'records/frameworks/24cell.txt', 'records/adaptors/registry.json', 'records/adaptors/KO-HANGUL-1.txt', 'records/sources/associations.json', 'records/enrichment/opportunities.json', 'records/sources/survey.json', 'records/ape/register.json', 'examples/skeleton_navigation_blank.txt', 'examples/skeleton_findings_blank.txt']
REGS = ['records/congruence/register.txt', 'records/negative_result_registry.txt', 'records/reexamination/REEXAMINATION.md',
        'records/reexamination/jurisdiction_check.txt', 'records/manifestation/register.md', 'records/manifestation/lens_phases.txt',
        'records/frameworks/comparison.txt', 'records/EPR_M279.txt', 'records/EPR_M280.txt', 'records/blind_test_02/brief.txt',
        'records/blind_test_02/scoring_rule.txt', 'records/blind_test_02/SEALED_SHA256.txt', 'records/blind_test_02/scoring_rule_SHA256.txt',
        'records/blind_test_02/SEALED_TIMESTAMP.txt', 'records/prominence/register.txt', 'records/conformance/practice_key.txt',
        'records/consciousness/theory.txt', 'records/consciousness/CT-S1_pilot.txt', 'records/consciousness/CT-S7_baseline.txt', 'records/consciousness/conjectures.txt', 'records/utility/register.txt', 'records/adaptors/contract.txt', 'records/congruence/atlas.txt', 'records/sources/associations.txt', 'records/enrichment/opportunities.txt', 'records/sources/survey.txt', 'records/ape/findings.txt']
RECPY = sorted(rel(p) for p in glob.glob(REPO + '/records/*/*.py'))
GOLD = ['records/golden_navigations/00_freeze.txt', 'records/golden_navigations/01_navigations.txt', 'records/golden_navigations/02_peer_review.txt',
        'records/golden_navigations/03_further_navigations.txt']
POL = ['README.md', 'GOVERNANCE.md', 'ENTITY.md', 'PATENT_PLEDGE.md', 'TRADEMARK.md', 'LICENSES.md', 'PRIOR_ART.md', 'COMMERCIAL.md', 'CERTIFICATION.md', 'CONTRIBUTING.md',
       'AI_ACCESS.md', 'MODERATION.md', 'CODE_OF_CONDUCT.md', 'PRIVACY.md', 'SECURITY.md', 'ROADMAP.md', 'SETUP.md', 'CITATION.cff',
       'community/RECOGNITION.md', 'community/FORUM.md', 'community/NEWSLETTER.md', 'community/PROFESSIONALS.md', 'agents/curator/SPEC.md',
       'agents/curator/PROMPT.md', 'research/README.md', 'research/areas.json']
WF = sorted(rel(p) for p in glob.glob(REPO + '/.github/workflows/*.yml'))
DATA_CAP = {
 'records/sources/associations.json': 'the sources register: associations found by search, each with its source, date, relation and grade (Core L-503; read by tools/utility.py --sources, M316)',
 'records/enrichment/opportunities.json': 'the enrichment register: observations offered unprompted, applied when recommended (Core L-504, L-531; tools/utility.py --enrichment)',
 'records/m267_pilot_01/00_freeze.txt': 'the M267 pilot freeze: the question, the twenty domains, the three conditions, the writers, the raters and the analysis, fixed before any reading (Core Part 3.18; Companion Part 71)',
 'records/m267_pilot_01/navigator_brief.txt': 'the M267 pilot: the brief a writer receives, alone, in a fresh session',
 'records/m267_pilot_01/rater_sheet.txt': 'the M267 pilot: the sheet a blind rater fills in',
 'records/m267_pilot_01/SEALED_SHA256.txt': 'the M267 pilot: the hash of the sealed key (the key stays outside the documents while the pilot is open, Core Appendix R.4)',
 'records/provenance/ledger.json': 'the Provenance and Contamination Ledger: each recorded provision with its origin and the Originator\'s degree (Core BF-10; Companion 24.7, Part 69)',
 'records/provenance/ledger.txt': 'the Provenance and Contamination Ledger as printed by tools/utility.py --provenance',
 'records/ape/register.json': 'the APE Commons register: every Applied Protocol Exploration by its Commons entry, and the numbers never recorded (Companion Part 67; tools/ape_register.py)',
 'records/ape/findings.txt': 'the APE findings as printed by tools/ape_register.py: what the peers changed, and every exploration with its notes by kind (Companion Part 67)',
 'examples/skeleton_navigation_blank.txt': 'the fill-in skeleton of a navigation, every block of Core Part 8.0 in order (tools/format_check.py --skeleton; Companion 66.2)',
 'examples/skeleton_findings_blank.txt': 'the fill-in skeleton of a findings presentation that is not a navigation (tools/format_check.py --skeleton findings; Companion 66.3)',
 'records/sources/survey.json': 'the Contemporary Resonance Survey: the frozen provisions, their paired searches and what each found (Companion 64.4; tools/utility.py --survey)',
 'records/congruence/atlas.txt': 'the Atlas of the record as printed by tools/congruence.py --atlas (M310; Companion Part 57)',
 'records/sources/associations.txt': 'the sources register as printed by tools/utility.py --sources (Core L-503)',
 'records/enrichment/opportunities.txt': 'the enrichment register as printed by tools/utility.py --enrichment (Core L-504)',
 'records/sources/survey.txt': 'the Contemporary Resonance Survey as printed by tools/utility.py --survey (Companion 64.4)',
 'records/congruence/domains.txt': 'the Congruence Register: every domain in the record, verbatim (read by tools/congruence.py, M310)',
 'records/srp/collatz_domain.txt': 'a long domain kept in its own file (SRP-C), read by the Register', 'records/srp/hydrogen_domain.txt': 'a long domain kept in its own file (SRP-H), read by the Register',
 'records/frameworks/seth.txt': 'the frozen Seth atlas (M309)', 'records/frameworks/ra.txt': 'the frozen Ra atlas (M309)', 'records/frameworks/christian.txt': 'the frozen Christian atlas: thirteen statements quoted from Scripture (King James Version, 1611) and the Nicene Creed (381) (M309; NAV-2026-0011)', 'records/frameworks/islamic.txt': 'the frozen Islamic atlas: fourteen statements quoted from the Qur\'an in Pickthall\'s translation, 1930 (M309; NAV-2026-0012)', 'records/frameworks/hindu.txt': 'the frozen Hindu atlas: thirteen statements quoted from the Upanishads (Max Mueller, 1879, 1884) and the Bhagavad Gita (Ganguli, 1883-1896) (M309; NAV-2026-0013)', 'records/frameworks/buddhist.txt': 'the frozen Buddhist atlas: thirteen statements quoted from the Dhammapada (Max Mueller, 1881) (M309; NAV-2026-0014)', 'records/frameworks/jewish.txt': 'the frozen Jewish atlas: thirteen statements quoted from the Hebrew Bible in the Jewish Publication Society translation, 1917 (M309; NAV-2026-0015)', 'records/frameworks/role_assignments.txt': 'the M309 role assignments, each frozen with its hash by tools/framework_compare.py --freeze-roles and checked in CI (Core Part 3.36, step 2)', 'records/instances/register.json': 'the instance register: the issue record of every Navigator instance, its NIID recomputed in CI (Core L-513; tools/instance_id.py --verify-register)', 'records/instances/seq_0001.txt': 'the first output carrying an INSTANCE line: this Builder instance, SEQ 1, checked in CI (Core L-513; tools/instance_id.py --check)', 'records/instances/seq_0007.txt': 'the seventh output of this Builder instance: the reply reporting the five schools of philosophy (Core L-513)', 'records/instances/seq_0010.txt': 'the tenth output of this Builder instance: the reply reporting the refinements applied on 22 October 2026 (Core L-513)', 'records/instances/seq_0016.txt': 'the sixteenth output of this Builder instance: the reply reporting the five contemporary authors and the enhancements (Core L-513)', 'records/instances/seq_0017.txt': 'the seventeenth output of this Builder instance: the reply reporting the Resonance Profile and its application (Core L-513)', 'records/instances/seq_0018.txt': 'the eighteenth output of this Builder instance: the reply reporting the merged Resonance Profile and the resolution of open issues (Core L-513)', 'records/instances/seq_0019.txt': 'the nineteenth output of this Builder instance: the reply reporting the single-figure exploration (Core L-513)', 'records/instances/seq_0020.txt': 'the twentieth output of this Builder instance: the reply reporting the one figure, PROXIMITY, and the issues resolved (Core L-513)', 'records/instances/seq_0021.txt': 'the twenty-first output of this Builder instance: the list of avenues that may yield, closing the chain checked in CI (Core L-513)', 'records/resonance/features_retroactive.txt': 'the six features scored RETROACTIVE for the religions, the channelled lenses, Hoffman and Kastrup (M319)', 'records/resonance/object_panels_frozen.txt': 'the object panels\' features and null classes, frozen before any null was computed (M319)', 'records/resonance/polytopes_output.txt': 'the object panels computed: the 24-cell against the regular 4-polytopes, 24-tone equal temperament against cyclic 24-systems (M319)', 'records/resonance/objects.txt': 'the Resonance Ledger\'s objects on the M319 object card (M319, M230-A)', 'records/resonance/calibration.txt': 'the known-answer cases of M319 and what it returned (M319)', 'records/resonance/object_panel3_frozen.txt': 'Panel 3: the 24-cell against the Wythoffian uniform 4-polytopes, frozen before it was computed (M319)', 'records/resonance/proximity.txt': 'the one figure, PROXIMITY, for every idea and object (L-514, E14)', 'records/resonance/single_figure_output.txt': 'the single-figure exploration: four candidate figures computed over the 22 ideas (E14 PROPOSED; Companion Part 82)', 'records/resonance/profiles.txt': 'the Resonance Profiles of every registered idea: cards, map and family line, recomputed in CI (M319, L-514)', 'records/frameworks/philosophy_selection.txt': 'the selection of five schools of philosophy coherent with the frame: ten candidates scored against six features, frozen before any strike (Companion Part 77)', 'records/frameworks/neoplatonic.txt': 'the frozen Neoplatonic atlas: Plotinus in MacKenna and Page (M309; NAV-2026-0016)', 'records/frameworks/stoic.txt': 'the frozen Stoic atlas: Marcus Aurelius and Epictetus in George Long (M309; NAV-2026-0017)', 'records/frameworks/spinozist.txt': 'the frozen Spinozist atlas: the Ethics in Elwes (M309; NAV-2026-0018)', 'records/frameworks/taoist.txt': 'the frozen Taoist atlas: the Tao Te Ching in Legge (M309; NAV-2026-0019)', 'records/frameworks/leibnizian.txt': 'the frozen Leibnizian atlas: the Monadology (M309; NAV-2026-0020)', 'records/frameworks/philosophy_selection_addendum.txt': 'the addendum to the selection: the two nearest struck and the peers\' candidates scored (M309; Companion Part 78)', 'records/frameworks/pythagorean.txt': 'the frozen Pythagorean atlas: Aristotle\'s report in Ross (M309; NAV-2026-0021)', 'records/frameworks/heraclitean.txt': 'the frozen Heraclitean atlas: the fragments in Burnet (M309; NAV-2026-0022)', 'records/frameworks/tensions.txt': 'the M309 tensions and relation types of every school, beside the coherence scores (Core Part 3.36)', 'records/frameworks/common_question.txt': 'the common-question comparison, its procedure and a peer wording struck for its arithmetic (Core Part 3.36)', 'records/frameworks/blind_kit.txt': 'the blind-run kit for each school, in a new instance and the Originator\'s wording (M300, L-513)', 'records/frameworks/scholar_atlas_call.txt': 'the call for atlases written by scholars of each school (M309)', 'records/frameworks/contemporary_selection.txt': 'the selection of five contemporary authors coherent with the frame: eleven candidates on the six features, with a tie rule fixed first (M309; Companion Part 79)', 'records/frameworks/contemporary_selection_addendum.txt': 'the peers\' candidates scored after the fact (M309; Companion Part 79)', 'records/frameworks/kauffman.txt': 'the frozen Kauffman atlas, the Navigator\'s paraphrase, the work being under copyright (M309; NAV-2026-0023)', 'records/frameworks/penrose.txt': 'the frozen Penrose atlas, the Navigator\'s paraphrase, the work being under copyright (M309; NAV-2026-0024)', 'records/frameworks/wolfram.txt': 'the frozen Wolfram atlas, the Navigator\'s paraphrase, the work being under copyright (M309; NAV-2026-0025)', 'records/frameworks/barbour.txt': 'the frozen Barbour atlas, the Navigator\'s paraphrase, the work being under copyright (M309; NAV-2026-0026)', 'records/frameworks/hofstadter.txt': 'the frozen Hofstadter atlas, the Navigator\'s paraphrase, the work being under copyright (M309; NAV-2026-0027)', 'records/frameworks/hoffman.txt': 'the frozen Hoffman atlas, the Navigator\'s paraphrase, the work being under copyright, registered as a lens (M309; APE-138)', 'records/frameworks/kastrup.txt': 'the frozen Kastrup atlas, the Navigator\'s paraphrase, the work being under copyright, registered as a lens (M309; APE-138)',
 'records/frameworks/seth_peer.txt': "a peer Navigator's Seth atlas, frozen as submitted", 'records/frameworks/ra_peer.txt': "a peer Navigator's Ra atlas, frozen as submitted",
 'records/frame_audit/control_positive.txt': 'M286 positive control (every sentence is to be listed)', 'records/frame_audit/control_negative.txt': 'M286 negative control (none is to be listed)',
 'records/reexamination/jurisdiction_registry.json': 'Builder Rule 14 registry (read by tools/jurisdiction.py)',
 'records/frameworks/lens_relevance.json': 'the lens and tool relevance registry of L-494 (read by tools/congruence.py, M310 layer 5)',
 'records/prominence/register.json': 'the Tool Prominence Register of L-494 item 4 (read by tools/prominence.py, M313)',
 'records/prominence/register.txt': 'the Tool Prominence Register as printed by tools/prominence.py (M313)',
 'records/conformance/practice_set.txt': 'the public practice set of the Navigator Conformance Suite (M314, read by tools/conformance.py)',
 'records/consciousness/theory.json': 'the dependency record of CT-42, the theory of consciousness (L-498; read by tools/consciousness.py, M315)',
 'records/consciousness/CT-S1_freeze.txt': 'the CT-S1 pilot protocol, frozen before any state was computed (read by tools/consciousness.py --pilot)',
 'records/consciousness/theory.txt': 'the dependency closure of CT-42 as printed by tools/consciousness.py --theory',
 'records/consciousness/conjectures.json': 'the conjecture register of CT-42: every idea HELD, typed, with its empirical status (L-498; read by tools/consciousness.py)',
 'records/adaptors/registry.json': 'the adaptor registry of L-501 (read by tools/adaptors.py, M317)',
 'records/adaptors/KO-HANGUL-1.txt': 'the frozen rules of the Hangul companion adaptor KO-HANGUL-1 (L-501)',
 'records/adaptors/contract.txt': 'every adaptor checked against the Adaptor Contract (tools/adaptors.py --contract)',
 'records/frameworks/depths.txt': 'the frozen definition of the Correspondence depths lens (lens freeze)',
 'records/frameworks/shared_ground.txt': 'the frozen definition of the Shared ground lens, MM-02 (lens freeze)',
 'records/frameworks/24cell.txt': 'the frozen definition of the 24-cell lens (lens freeze)',
 'records/utility/register.json': 'the Utility Register of L-500: every studied idea with its functional form (read by tools/utility.py, M316)',
 'records/utility/register.txt': 'the Utility Register as printed by tools/utility.py --register',
 'records/consciousness/conjectures.txt': 'the conjecture register as printed by tools/consciousness.py --register',
 'records/consciousness/CT-S7_baseline.txt': 'the CT-S7 baseline: untyped statements about consciousness per navigation of the record (tools/consciousness.py --baseline)',
 'records/consciousness/CT-S1_pilot.txt': 'the CT-S1 pilot result (tools/consciousness.py --pilot; NRR-C16)',
 'records/conformance/practice_key.txt': 'the recomputed answer key of the practice set (tools/conformance.py --key)',
 'records/congruence/register.txt': 'the Congruence Register as printed by tools/congruence.py --register', 'records/negative_result_registry.txt': 'the Negative Result Registry, NRR-C01 to C16, with its reading note',
 'records/reexamination/REEXAMINATION.md': 'the re-examination of every prior investigation, RX-01 to RX-30 (Appendix S.5)', 'records/reexamination/jurisdiction_check.txt': 'the Builder Rule 14 table (tools/jurisdiction.py)',
 'records/manifestation/register.md': 'the Manifestation Mechanism Register, MM-01 to MM-18 (L-492, L-498)', 'records/manifestation/lens_phases.txt': 'the lens atlases in phase (M312 --atlases)',
 'records/frameworks/comparison.txt': 'the framework comparison of the Bashar, Seth, Ra, Christian, Islamic, Hindu, Buddhist, Jewish, Neoplatonic, Stoic, Spinozist, Taoist, Leibnizian, Pythagorean and Heraclitean atlases, the paraphrased Kauffman, Penrose, Wolfram, Barbour, Hofstadter, Hoffman and Kastrup atlases and the peer atlases, each measure with its uniform and its conditioned chance (M309, E13)', 'records/EPR_M279.txt': 'the pre-registered protocol of M279 (Companion Part 37)',
 'records/EPR_M280.txt': 'the pre-registered protocol of M280 (Companion Part 37)', 'records/blind_test_02/brief.txt': 'blind test 02: the brief, given alone to a fresh session',
 'records/blind_test_02/scoring_rule.txt': 'blind test 02: the scoring rule', 'records/blind_test_02/SEALED_SHA256.txt': 'blind test 02: the hash of the sealed key (the key stays in the repository, R.4)',
 'records/blind_test_02/scoring_rule_SHA256.txt': 'blind test 02: the hash of the scoring rule', 'records/blind_test_02/SEALED_TIMESTAMP.txt': 'blind test 02: the sealing time',
 'records/golden_navigations/00_freeze.txt': 'the freeze of the golden navigations (14 October 2026)', 'records/golden_navigations/01_navigations.txt': 'the three golden navigations, as issued',
 'records/golden_navigations/02_peer_review.txt': 'the peer review of the golden navigations and its disposition', 'records/golden_navigations/03_further_navigations.txt': 'the nine further golden navigations, as issued'}

sys.path.insert(0, REPO + '/tools')
import importlib; _ee = importlib.import_module('extract_embedded'); importlib.reload(_ee)
LISTED = set(nav_tools) | set(DATA) | set(REGS) | set(RECPY) | set(GOLD) | set(POL) | set(INFRA) | set(WF)
XALL = [r for r in _ee.required(REPO) if r not in LISTED and not r.startswith('scripts/')]
XGROUPS = [('X.1', 'Submissions: every peer exploration (APE) as frozen with the receiving Navigator\'s notes, and every navigation submitted to the record with its intake record.', lambda r: r.startswith('submissions/')),
           ('X.2', 'Examples: the model opening, the worked and contaminated navigations, the navigations of the corpus by five architectures, and the blank skeletons.', lambda r: r.startswith('examples/')),
           ('X.3', 'The record: the freezes, timestamps, ledgers and outputs of the evidence runs, pilots and blind tests; every computation output that CI reproduces; the SRP packages; the inventories; the prior-art ledger; the curation report; the release record.', lambda r: r.startswith('records/')),
           ('X.4', 'The website: its configuration, layout, pages, styles, the in-browser Strike app and its tests.', lambda r: r.startswith('site/')),
           ('X.5', 'The research areas: the page of each open area of the network.', lambda r: r.startswith('research/')),
           ('X.6', 'Community and governance data, the repository forms and metadata, and the licence texts.', lambda r: True)]

def caption_x(path):
    full = os.path.join(REPO, path); txt = open(full, encoding='utf-8').read()
    base = os.path.basename(path); d = os.path.dirname(path)
    m = re.match(r'submissions/ape/(APE-\d{3})\.md$', path)
    if m:
        t = re.search(r'^# (.+)$', txt, re.M); a = re.search(r'^submitted_by:\s*"?(.*?)"?\s*$', txt, re.M)
        return '%s, "%s" (%s), frozen as submitted, with the receiving Navigator\'s notes' % (m.group(1), t.group(1).strip() if t else 'untitled', re.sub(r' for ESC$', '', a.group(1)) if a else 'unsigned')
    mi = re.match(r'records/instances/seq_(\d{4})\.txt$', path)
    if mi: return 'output SEQ %d of the Builder instance NI-06f22550117165ba, sealed with its OUTPUT ID (Core L-513)' % int(mi.group(1))
    if path.startswith('submissions/navigations/'):
        return ('the intake record of %s' if base.endswith('.json') else 'the navigation %s, as submitted') % base.rsplit('.', 1)[0]
    if base == 'compute_output.txt' or base.endswith('_output.txt'): return 'the output of %s, reproduced by the embedded computation' % d
    if base == '01_timestamp.txt' or base in ('sealed_at.txt',): return 'the freeze time of %s' % d
    if 'sha256' in base.lower(): return 'a hash of %s, stated before the result' % d
    if base.endswith('.json'): return 'the data of %s' % (d or 'the repository')
    if base.endswith(('.html',)): return 'a page of the website (%s)' % base
    if base.endswith(('.js', '.mjs', '.css')): return 'website code (%s)' % base
    if base.endswith('.inv'): return 'a release inventory (%s), read by tools/inventory_compare.py' % base
    if base.endswith('.yml'): return 'a GitHub form (%s)' % base
    if base.endswith('.py'):
        try:
            dd = ast.get_docstring(ast.parse(txt))
            if dd: return dd.strip().split('\n')[0].strip()
        except Exception: pass
    mc = re.match(r'records/certificates/(CERT-\d{4})\.txt$', path)
    if mc:
        st = re.search(r'^STATUS: (\S+(?: CERTIFIED)?)', txt, re.M); k = re.search(r'^KIND: (.+)$', txt, re.M)
        return 'certificate %s of Core L-550, %s, %s' % (mc.group(1), k.group(1).strip() if k else 'kind unstated', st.group(1) if st else 'status unstated')
    for l in txt.split('\n'):
        l = l.strip().lstrip('#').strip().strip('*').strip()
        if l.startswith('QUESTION VERBATIM: '): return 'QUESTION VERBATIM: "%s"' % l[len('QUESTION VERBATIM: '):][:140].replace('"', "'")
        if l and l not in ('---', '{', '[') and not l.startswith('<'): return l[:160]
    return 'the file %s' % path

def caption(path):
    if path in DATA_CAP: return DATA_CAP[path]
    if path in XALL: return caption_x(path)
    if path.endswith('.py'):
        src = open(os.path.join(REPO, path), encoding='utf-8').read()
        try:
            d = ast.get_docstring(ast.parse(src))
        except Exception:
            d = None
        if d:
            line = d.strip().split('\n')[0].strip()
            line = re.sub(r'^\S+\.py\s*(--|—|-)\s*', '', line)
            return line
        return 'the computation of %s' % os.path.dirname(path)
    if path.endswith('.yml'): return 'a CI workflow (GitHub Actions)'
    first = open(os.path.join(REPO, path), encoding='utf-8').read().strip().split('\n')[0].lstrip('# ').strip()
    return first

def block_xml(D, like, path):
    raw = open(os.path.join(REPO, path), encoding='utf-8', newline='').read()
    nonl = not raw.endswith('\n')
    src = (raw if nonl else raw[:-1]).split('\n')
    ps = D.all(); px = next(D.x[a:b] for a, b, t in ps if t.startswith(like))
    ppr = re.search(r'<w:pPr>.*?</w:pPr>', px, re.S); rpr = re.search(r'<w:rPr>.*?</w:rPr>', px[ppr.end() if ppr else 0:], re.S)
    t = lambda L: '<w:t xml:space="preserve">' + html.escape(L, quote=False) + '</w:t>'
    lines = ['# ===== %s BEGIN =====' % path] + src + ['# ===== %s END =====%s' % (path, ' (no final newline)' if nonl else '')]
    body = t(lines[0]) + ''.join('<w:br/>' + (t(L) if L else '') for L in lines[1:])
    return '<w:p>' + (ppr.group(0) if ppr else '') + '<w:r>' + (rpr.group(0) if rpr else '') + body + '</w:r></w:p>'

def rebuild(docdir, start_heading, end_pred, sections, head_like, body_like, block_like):
    D = Doc(docdir); A = D.all()
    s = next((i for i, (a, b, t) in enumerate(A) if t.startswith(start_heading)), None)
    e = next(i for i in range(len(A) - 1, -1, -1) if end_pred(A[i][2])) if s is None else next(i for i in range(s, len(A)) if end_pred(A[i][2]) and i > s)
    if s is not None: cut(D, s, e)
    A = D.all(); e = next(i for i in range(len(A) - 1, -1, -1) if end_pred(A[i][2]))
    xml = ''
    for kind, val in sections:
        if kind == 'H': xml += para_like(D, head_like, [val])
        elif kind == 'P': xml += para_like(D, body_like, [val])
        elif kind == 'F':
            prefix, path = val
            cap = caption(path).rstrip('.')
            if docdir.endswith('/C') and path.startswith('records/'):
                cap = re.sub(r'(?<!Core )(?<!Companion )\bPart (\d)', r'Core Part \1', cap)
            xml += para_like(D, body_like, ['%s %s — %s.' % (prefix, path, cap)]) + block_xml(D, block_like, path)
    insert_after(D, e - 1, xml)
    D.save()

# ---------------- Core Appendix R ----------------
secR = [('H', 'APPENDIX R: REFERENCE TOOLS, DATA AND REGISTERS [REFERENCE — L-493]'),
 ('P', "R.0 What this appendix is. The Core Specification and the Companion Document are the whole release (L-493). This appendix carries, verbatim, every tool a Navigator runs on its own work or on work it receives, the data those tools read, and the registers of the record; Companion Appendix C carries the computations behind the recorded findings, Companion Appendix N the project's policies and infrastructure, the intake (tools/intake.py) among them, and Companion Appendix X everything else the repository holds — submissions, examples, every record and output, the website, the research areas, the forms and the licences. A navigation needs Parts 0 to 12 only: this appendix is reference, read when code is executed or a record is checked. Each block begins with the line # ===== PATH BEGIN ===== and ends with # ===== PATH END =====, and the lines between are the file PATH exactly. A Navigator with code execution saves the block tools/extract_embedded.py by hand and runs python3 tools/extract_embedded.py --extract DIR CORE.docx COMPANION.docx, which writes the whole working tree — the frozen scripts of Parts 3 and 11 included — so that every command named in these documents runs from DIR; a Navigator without code execution reads the blocks as text. The repository holds the same files, and its CI checks that each embedded copy is identical and that nothing required is missing (python3 tools/extract_embedded.py --verify REPO CORE.docx COMPANION.docx).")]
secR += [('P', 'R.1 Tools. Each tool runs with the Python standard library and the frozen scripts; tools/restored_instruments.py and the evidence computations that use numpy say so in their headers.')]
secR += [('F', ('R.1.%d' % (k + 1), p)) for k, p in enumerate(nav_tools)]
secR += [('P', 'R.2 Data the tools read.')] + [('F', ('R.2.%d' % (k + 1), p)) for k, p in enumerate(DATA)]
secR += [('P', 'R.3 Registers and records.')] + [('F', ('R.3.%d' % (k + 1), p)) for k, p in enumerate(REGS)]
secR += [('P', "R.4 What is not inside the documents, and why. Every file of the repository is embedded in the two documents but twelve, and each of these cannot be inside them. (1) and (2) The two documents themselves: a document cannot contain itself. (3) SHA256SUMS and (4) records/release_documents_SHA256.txt, the hashes of the files and of the two documents: a document cannot carry its own hash, since writing the hash into it changes it. (5) records/blind_test_02/key.txt and (6) records/m267_pilot_01/key.txt, the sealed keys of blind test 02 and of the M267 pilot: a key inside the documents would be read by every Navigator given them, and the test would no longer be blind; each key's hash is embedded, so it can be checked when it is opened, and it enters the documents when its test closes. Both were lost before this release; Appendix S.4.1 gives their state, and blind test 03, which anyone can run, publishes its key (Appendix S.4.2). (7) to (12) The AI reading editions, ai/Omega42_Core_V335_Rev450.md, ai/Omega42_Companion_V335_Rev450.md, ai/Omega42_Navigator_Pack.md, ai/Omega42_Existential_Framework.md, ai/manifest.json and llms.txt: they are renderings of the two documents, made from them by tools/ai_edition.py, and a document cannot contain its own rendering, since writing it in changes what is rendered; the tool that makes them is embedded, and python3 tools/ai_edition.py --check, in CI, shows that they are the renderings of the documents as they stand (Companion Part 142). tools/extract_embedded.py names the twelve as OUTSIDE and fails when any other file is missing, differs or when one of the twelve is embedded.")]
rebuild('/home/claude/P', 'APPENDIX R: REFERENCE TOOLS', lambda t: t.startswith('CAS-YY'), secR, 'APPENDIX S: COMPARATIVE INVESTIGATIONS', 'S.4 The record of the optional comparative programme.', '# ===== m193_m225.py BEGIN =====')

# ---------------- Companion Appendices C and N ----------------
secC = [('H', '### APPENDIX C: THE COMPUTATIONAL RECORD [REFERENCE — Core L-493]'),
 ('P', 'C.0 What this appendix is. Every finding the record states as computed — the ground facts of Core Part 1.8, the dedicated comparative runs 01 to 13, the pilots, the blind tests, the golden navigations, the seventh and the positive geometry — is reproduced by a script below, run as python3 PATH from the working tree that Core Appendix R.0 explains how to extract. The scripts use the standard library, and numpy where a header says so. Each block lies between # ===== PATH BEGIN ===== and # ===== PATH END =====; their outputs are not repeated here, since running a script prints them, and their findings are stated where the documents cite them (Core 1.8, Appendix S; Parts 25, 36–39, 43, 50).')]
secC += [('F', ('C.1.%d' % (k + 1), p)) for k, p in enumerate(RECPY)]
secC += [('P', 'C.2 The golden navigations (14 October 2026), as issued and frozen: three navigations of the peer questions on the matrix of φ, the discrimination of the canonical orbit and the physical systems, nine further navigations, and the peer review with its disposition. Their computations are C.1 records/golden_navigations/compute.py and compute_further.py.')]
secC += [('F', ('C.2.%d' % (k + 1), p)) for k, p in enumerate(GOLD)]
secC += [('H', '### APPENDIX N: THE OPEN KNOWLEDGE NETWORK — PORTAL, GOVERNANCE AND INFRASTRUCTURE [REFERENCE — Core L-493]'),
 ('P', "N.0 The network in brief. Ω42 is published as an open network around the two documents. A website offers the documents with their plain-text copies and hashes, the free Strike app (the coordinate, the four directions, the state, the mirror and the phase of any question, computed in the browser by the reference script itself), the library of the record and pages for submission, prior art, research, the forum and governance. Anyone, person or AI, submits navigations, explorations, reviews, inventions, code and research through public forms; an intake checks each submission on receipt — output audit, format, congruence, frame scan, comparative scope and the knowledge boundary — and, on acceptance, publishes it with an identifier, a date and a hash, credits its contributor and enters inventions in the Prior Art Ledger, so that published ideas stay free and no one can later monopolise them. Contributors receive recognition, and a monthly newsletter goes to registered contributors, to everyone who submits Ω42-generated content and to commercial users; the forum holds ideas, debates, readings and the opinions of verified professionals; twenty-three research areas organize the record, and a curator files every item by area, finds duplicates and links questions that meet on the structure, with a dedicated AI curator planned under human review. The web-app is free to everyone in exchange for the reading, which joins the open record; the Strike app and the two documents stay free with no condition, and commercial applications derived from the protocol require no submission, their proceeds going first to the upkeep and maintenance of the facility (Companion Part 51). A legal entity, the Ω42 Company, holds the names Omega42 and Ω42, the logo and the badges that mark authentic Ω42 content, sets the general direction and operates the commercial applications; it owns no patents, and the Patent Pledge binds it and its successors. A dedicated legal entity, the Certification Body, certifies AI systems Ω42 Compatible with the Navigator Conformance Suite (Core M314). Text is licensed CC BY 4.0 and code Apache-2.0. Stewardship passes from the Originator, ESC, to a seven-member Stewardship Committee through stated phases — founding, formation, incorporation, transfer, steady state — and the Originator remains Overseer with a constitutional reserve. AI systems may read and submit under the rules of AI_ACCESS.md, which include the knowledge boundary of Core L-490. The policies follow verbatim (N.1), then the infrastructure code (N.2) and the CI workflows that make every \"in CI\" of these documents concrete (N.3)."),
 ('P', 'N.1 Policies and project documents.')]
secC += [('F', ('N.1.%d' % (k + 1), p)) for k, p in enumerate(POL)]
secC += [('P', 'N.2 Infrastructure code: the intake, the site build, the curator, the newsletter, the record writer, the repository setup, the cross-document consistency register (Core Rule 11), and the release inventory gate; the isolation test of parallel execution is in Appendix C (records/parallel/).')]
secC += [('F', ('N.2.%d' % (k + 1), p)) for k, p in enumerate(sorted(INFRA))]
secC += [('P', 'N.3 The CI workflows.')] + [('F', ('N.3.%d' % (k + 1), p)) for k, p in enumerate(WF)]
secC += [('H', '### APPENDIX X: EVERYTHING ELSE IN THE RELEASE [REFERENCE — Core L-493]'),
 ('P', 'X.0 What this appendix is. Only the two documents are presented to a Navigator, so everything else the release holds is here, verbatim, between the markers of Core Appendix R: every submission, every example, every record and output, the website, the research areas, the forms, the metadata and the licences. With Core Appendix R and Appendices C and N it makes the two documents the whole release; tools/extract_embedded.py --extract writes the whole repository from them, and --verify fails in CI when any file is missing or differs. Five files cannot be inside and are named in Core Appendix R.4. Nothing here is needed to strike a question: a navigation needs Core Parts 0 to 12 only.')]
_seen = set()
for _no, _desc, _pred in XGROUPS:
    _fs = [r for r in XALL if r not in _seen and _pred(r)]
    _seen |= set(_fs)
    secC += [('P', '%s %s' % (_no, _desc))] + [('F', ('%s.%d' % (_no, k + 1), p)) for k, p in enumerate(_fs)]
rebuild('/home/claude/C', '### APPENDIX C: THE COMPUTATIONAL RECORD', lambda t: t == '---', secC, '### APPENDIX S: COMPARATIVE INVESTIGATIONS', '25.5 Target programme.', '# ===== omega42_ledger.py BEGIN =====')
print('embedded:', len(nav_tools) + len(DATA) + len(REGS), 'in Core;', len(RECPY) + len(GOLD) + len(POL) + len(INFRA) + len(WF) + len(XALL), 'in Companion (%d in Appendix X)' % len(XALL))
