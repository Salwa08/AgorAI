"""Generate EXP002 result tables from completed, verified evidence."""
import argparse
import json
from pathlib import Path
import pandas as pd
from .analysis import B_ARMS,E_ARMS,interval

BASE=Path(__file__).resolve().parent


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str,r))+' |' for r in rows])+'\n'


def ci(row,scale=1,digits=1):
    return f'{row.estimate*scale:,.{digits}f} [{row.ci_low*scale:,.{digits}f}, {row.ci_high*scale:,.{digits}f}]'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,required=True)
    args=parser.parse_args();p=args.results
    verified=json.loads((p/'verification.json').read_text())
    assert verified['exp001_seed_summaries_exact'] and verified['verified_outcome_rows']==960000
    levels=pd.read_csv(p/'levels.csv');effects=pd.read_csv(p/'contrasts.csv')
    diag=pd.read_csv(p/'B_diagnostics.csv');groups=pd.read_csv(p/'harm_groups.csv')
    exploration=pd.read_csv(p/'exploration_comparisons.csv')
    pairs=pd.read_csv(p/'B_crop_contributions.csv')
    tests=json.loads((BASE/'test_results.json').read_text())
    meta=json.loads((p/'metadata.json').read_text())
    out=['# EXP002 — mechanisms of harmful social information','',
         'Completed simulation diagnostics: **20 seeds (0–19), 100 matched farmers, 30 seasons, 16 arms; 960,000 farmer-season outcomes**. '
         'The research plan was committed before implementation. EXP001 A–D seed summaries reproduce exactly, including '
         'the +35,238.72 MAD information-only mean effect, 26.5% harmed, and ARID mean effect −5,911.02 MAD with a small positive gross-yield effect.','',
         '**Interpretation rule:** these are interventions within FarmSwarm, not empirical causal evidence. '
         'Negative profit differences alone do not establish environmental negative transfer. '
         'All intervals are 95% seed-level t intervals, with seasons averaged within farmers first. '
         'Intervals are unadjusted; the 48 prespecified endpoint/contrast/stratum tests receive Holm-adjusted p-values separately.','',
         '## Absolute outcomes and harm versus original A','',
         'Profit is MAD/farmer/season; median profit is the median across farmer mean profits within each seed, then averaged over seeds. '
         'Harm compares each matched identity with A. Negative-part loss averages losses over everyone (zero for unhurt farmers). '
         'Switching excludes season one. All rows below have 20 seed replicates.','']
    rows=[]
    for arm in ['A','B','C','D',*E_ARMS,*B_ARMS]:
        g=levels[(levels.arm==arm)&(levels.zone=='ALL')].set_index('metric')
        rows.append([arm,ci(g.loc['mean_profit']),ci(g.loc['median_profit']),ci(g.loc['harmed_A'],100),
                     ci(g.loc['negative_part_loss']),ci(g.loc['switch_rate'],100)])
    out += [table(['Arm','Mean profit [CI]','Median profit [CI]','Harmed % [CI]','Negative-part loss [CI]','Switch % [CI]'],rows),'',
            '## Controlled intervention contrasts','',
            'Each intervention changes one mechanism. B-based rows compare against B; epsilon rows compare against A. '
            'Harm differences are percentage-point changes in the fraction harmed relative to original A. '
            'Holm p-values cover the complete family of 48 tests (12 contrasts × 2 endpoints × ALL/ARID).','']
    for zone in ['ALL','ARID']:
        rows=[]
        for arm,ref in [(x,'B') for x in B_ARMS]+[(x,'A') for x in E_ARMS]:
            g=effects[(effects.zone==zone)&(effects.arm==arm)&(effects.reference==ref)].set_index('metric')
            pr=g.loc['mean_profit'];ha=g.loc['harmed_A']
            rows.append([f'{arm} − {ref}',ci(pr),f'{pr.p_holm:.4g}',ci(ha,100),f'{ha.p_holm:.4g}'])
        out += ['### '+zone,'',table(['Contrast','Profit change [CI]','Holm p','Harm change, pp [CI]','Holm p'],rows),'']
    out += ['## Exploration changes the comparison baseline','',
            'B is held fixed. The following compares B with the contemporaneous exploratory A, including newly paired harm fractions '
            'computed against that exploratory baseline (not differences between two A-relative harm rates). These comparisons are exploratory.','']
    rows=[]
    for zone in ['ALL','ARID']:
        for ref in E_ARMS:
            g=exploration[(exploration.zone==zone)&(exploration.reference==ref)].set_index('metric')
            rows.append([zone,'B − '+ref,ci(g.loc['mean_profit_effect']),ci(g.loc['harmed'],100),ci(g.loc['negative_part_loss'])])
    out += [table(['Stratum','Comparison','Mean profit effect [CI]','B harmed % [CI]','Negative-part loss [CI]'],rows),'',
            'Exploration can improve average independent performance while harming some identities. Uniform exploration continues throughout the horizon '
            'and is not a learning-optimal policy. No epsilon was selected for favorable results.','',
            '## Zone heterogeneity and severity','',
            'These additional zone/endpoints are exploratory; all six zones occur in all 20 seeds.','']
    rows=[]
    for zone in sorted(z for z in levels.zone.unique() if z!='ALL'):
        g=levels[(levels.arm=='B')&(levels.zone==zone)].set_index('metric')
        rows.append([zone,ci(g.loc['effect_A']),ci(g.loc['harmed_A'],100),ci(g.loc['conditional_harmed_loss']),
                     int(g.loc['conditional_harmed_loss','n']),ci(g.loc['q10_effect_A'])])
    out += [table(['Zone','B−A mean profit [CI]','Harmed % [CI]','Loss among harmed [CI]','Severity seeds','10th percentile effect [CI]'],rows),'',
            '## Decision evidence and accounting decomposition','',
            'All source observations in default B originate within the receiver\'s zone. Source ages are at least one season in decision traces. '
            'Current-season candidate potential profit is computed only after every decision and is labeled analyst-only. '
            'The decomposition below is an accounting identity, not causal mediation.','']
    rows=[]
    metrics=['score_conflict_among_losses','yield_gain_among_losses','mean_yield_component','mean_price_component',
             'mean_cost_component','mean_neighbor_duplicates','neighbor_duplicate_fraction','received_experience','cross_channel_duplicates','mean_age']
    for metric in metrics:
        g=diag[diag.metric==metric].set_index('zone')
        rows.append([metric,ci(g.loc['ALL']),ci(g.loc['ARID'])])
    out += [table(['Metric','ALL [CI]','ARID [CI]'],rows),'',
            'Conflict and tradeoff quantities are fractions, not percentages. Duplication counts are appearances of immutable harvest IDs, '
            'not equality of numeric values; cross-channel duplication intentionally includes an event used by different weighted channels. '
            'Experience received counts refer to observations originating at another farmer. Neighbor duplicate fraction conditions on a nonempty neighbor pool.','',
            '### Harmed versus benefited farmers (descriptive)','',
            'Groups are defined by their realized 30-season average B−A effect. These associations are outcome-selected and not causal tests. '
            'Numbers are means of seed-specific group summaries; missing groups are omitted and n is reported.','']
    rows=[]
    b=groups[groups.arm=='B']
    for zone in ['ARID','IRRIGATED_SOUSS','SEMI_ARID_WARM']:
        for status in ['harmed','benefited','unchanged']:
            g=b[(b.zone==zone)&(b.group==status)]
            if not len(g):continue
            rows.append([zone,status,len(g),f'{g.mean_land.mean():.2f}',f'{100*g.switch_rate.mean():.2f}',
                         f'{g.mean_delta.mean():,.1f}',f'{g.received_experience.mean():.1f}',f'{g.neighbor_duplicates.mean():.1f}'])
    out += [table(['Zone','Group','Seeds','Land ha','Switch %','Profit delta','Received experience','Neighbor duplicates'],rows),'',
            '### ARID crop substitutions contributing to paired profit loss','',
            'Each seed/zone contribution divides the substitution\'s total profit difference by all farmer-season observations in that zone. '
            'Absent substitutions receive zero before averaging seeds; contributions therefore sum to the zone effect. '
            'These are A-crop versus B-crop substitutions, distinct from actual temporal switches recorded in switch_transitions.csv.','']
    rows=[]
    for r in pairs[pairs.zone=='ARID'].sort_values('estimate').head(8).itertuples():
        rows.append([r.baseline_crop+' → '+r.crop,r.n_rows,ci(r)])
    out += [table(['A crop → B crop','Farmer-season rows','Mean contribution, MAD [CI]'],rows),'',
            'Actual transitions and their distributions, season-by-zone harm profiles, source statistics, paired rescue rates and '
            'all non-primary zone contrasts are retained in the machine-readable evidence. No farmer-season counts are used as independent replicates.','',
            '## Competing hypotheses and EXP003 recommendation','',
            'The strongest controlled contribution is the zone scoring mixture: profit-only zone scoring raises mean profit by 21,364 MAD and reduces harm from 26.5% to 9.8%. Default cross-zone exposure is zero. Deduplication and per-hectare profit normalization show no clear average benefit; mixed-memory scoring can cause individual losses even though its removal does not clearly improve the mean. Exploration strengthens some baselines but does not remove the overall information advantage. These conclusions concern the modeled environment only.', '',
            'See [INTERPRETATION.md](INTERPRETATION.md) for hypothesis-by-hypothesis evidence, a post-hoc causal decision case, contradictory findings, and a prioritized EXP003 proposal. The priority is a prespecified objective-mixture × memory-separation factorial with an exploration comparator; the water correction belongs in a separate sensitivity. No EXP003 implementation is included.','',
            '## Validation and reproducibility','',
            f"Tests: **{tests['passed']} passed**, {tests['failed']} failed; command `{tests['command']}`. "
            'Coverage includes tracing-on/off exact parity, all four committed EXP001 seed-zero regressions, prospective identity/deduplication, '
            'past-only evidence, context rules including ultimate-source bypass prevention, normalization, intervention independence, pairing, accounting, '
            'seed-level inference and the 48-test Holm family. EXP001\'s tests also pass unchanged.','',
            'The complete 20-seed A–D reproduction table matches EXP001 committed seed summaries exactly. All 320 seed/arm environment hashes pair; '
            '960,000 outcome rows passed count, identity uniqueness, finite-value and accounting checks. Default B has zero cross-zone observations. '
            'Saved execution-source, input and output hashes were verified. The test environment emits a Requests dependency warning; no test or simulation failed.','',
            'Software: '+meta['python'].split('\n')[0]+'. Platform: '+meta['platform']+'. Packages: '+str(meta['packages'])+'.',
            'The execution metadata records the pre-implementation plan commit and uncommitted implementation state plus exact source hashes; '
            'this is not presented as execution from a later commit. Metadata UTC completion: '+meta['timestamp_utc']+'.','',
            'Actual commands (repository root):','',
            '```powershell',
            'python -m experiments.exp002.runner --config experiments/exp002/configs/smoke.json --output experiments/exp002/results/smoke',
            'python -m experiments.exp002.runner --config experiments/exp002/configs/full.json --output experiments/exp002/results/full',
            'python -m pytest experiments/exp001/tests experiments/exp002/tests -q',
            'python -m experiments.exp002.diagnose --results experiments/exp002/results/full',
            'python -m experiments.exp002.report --results experiments/exp002/results/full',
            '```','',
            'For reproduction in a fresh clone use new results/replay directories as documented in README.md. '
            'Raw compressed decisions, observations and outcomes remain local; compact summaries and provenance are committed. '
            'Existing V1 notebook, EXP001 implementation and agricultural data remain unchanged.','',
            '## Scientific limits','',
            'Seed uncertainty excludes parameter, observational and structural uncertainty. Holm correction covers only the designated 48 tests. '
            'Other results are explicitly exploratory. Within-zone farmers share environmental parameters, so same-zone filtering cannot test '
            'unmodeled microclimates. Ecological filtering changes only one cross-zone pair under current inputs. Deduplication leaves cross-channel '
            'reuse and cannot identify all contamination mechanisms. Exploration and profit-only zone weighting are narrow diagnostics, not policy recommendations. '
            'The 500-mm fallback, uncoupled irrigation/yield, static prices and climate, non-profit agent goals, unconstrained budgets and immediate perennial '
            'switching remain limitations. No sustainability benefit or real-world agricultural improvement is claimed.']
    (BASE/'RESULTS.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
    print('Wrote RESULTS.md from verified full evidence')

if __name__=='__main__':main()
