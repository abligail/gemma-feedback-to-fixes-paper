# Original uncertainty analyses and post-hoc missing-result bounds

Generated from existing analyses. These figures/tables are supporting material, not additional experiments.

Study A retains all repeats per task; its cross-batch analysis was specified after R01/R02 outcomes. Study B conditions on normal paired scores, including graded empty patches. Neither handles repository correlation or multiple comparisons.

| Study A scope/policy | Pairs | V5/policy passes | Difference pp | Original exploratory 95% interval |
|---|---:|---:|---:|---|
| official54 / trigger_probe_v1 | 162 | 75/77 | +1.23 | [-3.70, +6.17] |
| official54 / trigger_reuse_v2 | 108 | 48/47 | -0.93 | [-7.41, +5.56] |
| old_external29 / trigger_probe_v1 | 87 | 48/47 | -1.15 | [-9.20, +8.05] |
| old_external29 / trigger_reuse_v2 | 58 | 33/32 | -1.72 | [-13.79, +10.34] |
| new_scope12 / trigger_probe_v1 | 24 | 13/14 | +4.17 | [+0.00, +12.50] |
| new_scope12 / trigger_reuse_v2 | 24 | 13/12 | -4.17 | [-16.67, +8.33] |

| Study B batch | Normal C/F pairs | Gain/loss | Original exploratory 95% interval pp | Loose missing-result bounds pp |
|---|---:|---:|---|---|
| R01 | 52 | 0/2 | [-9.62, +0.00] | [-7.41, +0.00] |
| R02 | 51 | 2/1 | [-3.92, +7.84] | [-3.70, +7.41] |
| R03 | 52 | 1/1 | [-5.77, +5.77] | [-3.70, +3.70] |
| R04 | 51 | 1/2 | [-9.80, +3.92] | [-5.56, +3.70] |

R01 has zero observed gains and two losses. Its percentile bootstrap upper limit is zero because resampling the observed pairs cannot generate a gain; it does not rule out a positive population effect.

Loose bounds assign unresolved score outcomes independently to pass/fail to bound full-list F-C. They are post-hoc identification bounds, not confidence intervals; same patch identity does not force equal unknown judgments. All original official judgments are preserved.

The review's post-hoc exact discordance diagnostics are 0.5, 1, 1, 1; these emphasize sparse information, not confirmatory evidence or equivalence.
