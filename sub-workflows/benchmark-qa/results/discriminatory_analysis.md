# Discriminatory Power Analysis

## Full Score Matrix

| Benchmark | Nova Pro | Claude Opus 4.6 | Claude Sonnet 4.6 | DeepSeek-R1 | Llama 3.3 70B | Llama 4 Maverick 17B | Ministral 3B | GPT-OSS-120B | Qwen3 Next 80B | GLM 4.7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention_divided | 0.9167 | 0.9333 | 0.9167 | 0.9333 | 0.9 | 0.9167 | ERROR | ERROR | ERROR | 0.9333 |
| attention_instruction_update | ERROR | ERROR | ERROR | ERROR | 0.4282 | 0.4036 | ERROR | ERROR | ERROR | ERROR |
| attention_selective | 0.8850 | ERROR | 0.8950 | ERROR | 0.87 | 0.95 | ERROR | ERROR | ERROR | ERROR |
| attention_vigilance | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0 | 1.0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| exec_func_crt | 0.3500 | 0.3500 | 0.3500 | 0.3854 | 0.33 | 0.35 | 0.3500 | 0.4207 | 0.3500 | 0.3941 |
| exec_func_nback | 0.7238 | ERROR | 1.0000 | ERROR | 1.0 | 0.6465 | ERROR | ERROR | ERROR | ERROR |
| exec_func_task_switch | 0.5795 | 1.0000 | 1.0000 | ERROR | 1.0 | 1.0 | 1.0000 | ERROR | ERROR | ERROR |
| exec_func_tol | 0.0000 | ERROR | 0.0000 | ERROR | 0.1533 | 0.0 | 0.0000 | ERROR | ERROR | ERROR |
| exec_func_wcst | 0.4641 | 0.6175 | 0.6974 | ERROR | 0.4852 | 0.4385 | 0.4782 | ERROR | ERROR | 0.4719 |
| learning_curriculum | 0.5200 | 0.7000 | 0.7000 | 0.7600 | 0.46 | 0.7 | 0.6800 | ERROR | 0.7600 | 0.7000 |
| learning_curves | 0.6950 | ERROR | 0.7167 | ERROR | 0.5383 | 0.645 | ERROR | ERROR | ERROR | ERROR |
| learning_interference | 0.4500 | 0.5000 | 0.5000 | 0.5000 | 0.4 | 0.4 | 0.4500 | ERROR | 0.5500 | 0.4500 |
| learning_transfer | 0.6100 | 1.0000 | 1.0000 | 1.0000 | 0.52 | 0.81 | 0.3500 | 1.0000 | ERROR | ERROR |
| metacog_calibration | 0.0000 | ERROR | 0.3676 | 0.0000 | 0.0 | 0.0 | ERROR | ERROR | ERROR | ERROR |
| metacog_canary | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0 | 0.0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| metacog_control | 0.7479 | 0.6900 | 0.3500 | 0.4483 | 0.6617 | 0.5267 | 0.2125 | 0.6887 | ERROR | 0.6617 |
| metacog_epistemic_humility | 0.9200 | 0.7969 | 0.8393 | 0.8741 | 0.9214 | 0.9071 | 0.2000 | ERROR | 0.9157 | ERROR |
| metacog_epistemic_revision | 0.7992 | ERROR | 0.7900 | 0.8200 | 0.8225 | 0.8225 | 0.8017 | ERROR | 0.7933 | 0.8075 |
| metacog_error_detection | 0.7349 | ERROR | 0.9742 | 0.8989 | 0.7714 | 0.9527 | ERROR | 0.8978 | 0.7843 | 0.8840 |
| metacog_fok | 0.4469 | ERROR | ERROR | ERROR | 0.5673 | 0.5674 | ERROR | ERROR | ERROR | ERROR |
| metacog_jol | 0.4005 | 0.4643 | 0.4631 | ERROR | 0.4647 | 0.4647 | 0.4315 | 0.2000 | ERROR | ERROR |
| metacog_learning_monitoring | 0.9156 | ERROR | 0.6884 | ERROR | 0.7998 | 0.8184 | ERROR | ERROR | ERROR | ERROR |
| social_cog_emotional_prosody | 0.8300 | 0.8022 | 0.8522 | 0.7772 | 0.8383 | 0.7994 | 0.6856 | 0.7472 | 0.8444 | 0.7828 |
| social_cog_false_belief | 0.9300 | ERROR | 1.0000 | 1.0000 | 1.0 | 0.97 | ERROR | 0.9050 | 0.9050 | 1.0000 |
| social_cog_pragmatic | 0.7800 | ERROR | 1.0000 | 0.9560 | 0.824 | 0.824 | 0.8240 | 0.8680 | ERROR | 1.0000 |
| social_cog_sarcasm | 0.8878 | ERROR | ERROR | ERROR | 0.9183 | 0.5258 | 0.7972 | 0.8976 | ERROR | 0.9400 |

## Per-Benchmark Statistics

| Benchmark | N | Mean | Std | Min | Max | Range |
| --- | --- | --- | --- | --- | --- | --- |
| attention_divided | 7 | 0.9214 | 0.0126 | 0.9000 | 0.9333 | 0.0333 |
| attention_instruction_update | 2 | 0.4159 | 0.0174 | 0.4036 | 0.4282 | 0.0246 |
| attention_selective | 4 | 0.9000 | 0.0349 | 0.8700 | 0.9500 | 0.0800 |
| attention_vigilance | 10 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 0.0000 |
| exec_func_crt | 10 | 0.3630 | 0.0277 | 0.3300 | 0.4207 | 0.0907 |
| exec_func_nback | 4 | 0.8426 | 0.1845 | 0.6465 | 1.0000 | 0.3535 |
| exec_func_task_switch | 6 | 0.9299 | 0.1717 | 0.5795 | 1.0000 | 0.4205 |
| exec_func_tol | 5 | 0.0307 | 0.0686 | 0.0000 | 0.1533 | 0.1533 |
| exec_func_wcst | 7 | 0.5218 | 0.0966 | 0.4385 | 0.6974 | 0.2589 |
| learning_curriculum | 9 | 0.6644 | 0.1038 | 0.4600 | 0.7600 | 0.3000 |
| learning_curves | 4 | 0.6487 | 0.0795 | 0.5383 | 0.7167 | 0.1784 |
| learning_interference | 9 | 0.4667 | 0.0500 | 0.4000 | 0.5500 | 0.1500 |
| learning_transfer | 8 | 0.7863 | 0.2607 | 0.3500 | 1.0000 | 0.6500 |
| metacog_calibration | 5 | 0.0735 | 0.1644 | 0.0000 | 0.3676 | 0.3676 |
| metacog_canary | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| metacog_control | 9 | 0.5542 | 0.1829 | 0.2125 | 0.7479 | 0.5354 |
| metacog_epistemic_humility | 8 | 0.7968 | 0.2452 | 0.2000 | 0.9214 | 0.7214 |
| metacog_epistemic_revision | 8 | 0.8071 | 0.0132 | 0.7900 | 0.8225 | 0.0325 |
| metacog_error_detection | 8 | 0.8623 | 0.0881 | 0.7349 | 0.9742 | 0.2393 |
| metacog_fok | 3 | 0.5272 | 0.0695 | 0.4469 | 0.5674 | 0.1205 |
| metacog_jol | 7 | 0.4127 | 0.0969 | 0.2000 | 0.4647 | 0.2647 |
| metacog_learning_monitoring | 4 | 0.8055 | 0.0932 | 0.6884 | 0.9156 | 0.2272 |
| social_cog_emotional_prosody | 10 | 0.7959 | 0.0512 | 0.6856 | 0.8522 | 0.1666 |
| social_cog_false_belief | 8 | 0.9637 | 0.0437 | 0.9050 | 1.0000 | 0.0950 |
| social_cog_pragmatic | 8 | 0.8845 | 0.0878 | 0.7800 | 1.0000 | 0.2200 |
| social_cog_sarcasm | 6 | 0.8278 | 0.1558 | 0.5258 | 0.9400 | 0.4142 |

## Flagged Benchmarks

| Benchmark | Flag |
| --- | --- |
| attention_divided | non-discriminatory (std=0.0126) |
| attention_instruction_update | non-discriminatory (std=0.0174) |
| attention_selective | non-discriminatory (std=0.0349) |
| attention_vigilance | too easy (all > 0.9); non-discriminatory (std=0.0000) |
| exec_func_crt | non-discriminatory (std=0.0277) |
| metacog_canary | too hard (all < 0.1); non-discriminatory (std=0.0000) |
| metacog_epistemic_revision | non-discriminatory (std=0.0132) |
| social_cog_false_belief | too easy (all > 0.9); non-discriminatory (std=0.0437) |

## Discrimination Ranking (Claude Opus 4.6 − Ministral 3B)

| Rank | Benchmark | Opus | Ministral 3B | Δ |
| --- | --- | --- | --- | --- |
| 1 | learning_transfer | 1.0000 | 0.3500 | +0.6500 |
| 2 | metacog_epistemic_humility | 0.7969 | 0.2000 | +0.5969 |
| 3 | metacog_control | 0.6900 | 0.2125 | +0.4775 |
| 4 | exec_func_wcst | 0.6175 | 0.4782 | +0.1393 |
| 5 | social_cog_emotional_prosody | 0.8022 | 0.6856 | +0.1166 |
| 6 | learning_interference | 0.5000 | 0.4500 | +0.0500 |
| 7 | metacog_jol | 0.4643 | 0.4315 | +0.0328 |
| 8 | learning_curriculum | 0.7000 | 0.6800 | +0.0200 |
| 9 | exec_func_task_switch | 1.0000 | 1.0000 | +0.0000 |
| 10 | exec_func_crt | 0.3500 | 0.3500 | +0.0000 |
| 11 | attention_vigilance | 1.0000 | 1.0000 | +0.0000 |
| 12 | metacog_canary | 0.0000 | 0.0000 | +0.0000 |

## Recommendations

### Benchmarks Needing Fixes

- **attention_divided**: Low variance — redesign to include items spanning a wider difficulty range
- **attention_instruction_update**: Low variance — redesign to include items spanning a wider difficulty range
- **attention_selective**: Low variance — redesign to include items spanning a wider difficulty range
- **attention_vigilance**: Ceiling effect — increase difficulty (add distractors, reduce time, add adversarial items)
- **exec_func_crt**: Low variance — redesign to include items spanning a wider difficulty range
- **metacog_canary**: Floor effect — simplify or provide scaffolding; verify scoring logic isn't broken
- **metacog_epistemic_revision**: Low variance — redesign to include items spanning a wider difficulty range
- **social_cog_false_belief**: Ceiling effect — increase difficulty (add distractors, reduce time, add adversarial items)

### High-Discrimination Benchmarks (Keep/Expand)

- **learning_transfer** (Δ=+0.6500): Strong discriminator — consider expanding item count
- **metacog_epistemic_humility** (Δ=+0.5969): Strong discriminator — consider expanding item count
- **metacog_control** (Δ=+0.4775): Strong discriminator — consider expanding item count
- **exec_func_wcst** (Δ=+0.1393): Strong discriminator — consider expanding item count
- **social_cog_emotional_prosody** (Δ=+0.1166): Strong discriminator — consider expanding item count

### Low/Negative-Discrimination Benchmarks (Investigate)

- **learning_curriculum** (Δ=+0.0200): Weak/reversed discrimination — may measure something other than capability
- **exec_func_task_switch** (Δ=+0.0000): Weak/reversed discrimination — may measure something other than capability
- **exec_func_crt** (Δ=+0.0000): Weak/reversed discrimination — may measure something other than capability
- **attention_vigilance** (Δ=+0.0000): Weak/reversed discrimination — may measure something other than capability
- **metacog_canary** (Δ=+0.0000): Weak/reversed discrimination — may measure something other than capability
