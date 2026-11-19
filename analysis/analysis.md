# Results (test split)

1 run(s) excluded as inconclusive or unverified.

## Main table (95% CIs resample tasks)

| Model | Condition | Runs | Correct % [CI] | Verified | FP rate % [CI] | Mean tokens |
|---|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | c1 single shot | 96 | 95.8 [91.7, 99.0] | - | - | 35k |
| DeepSeek V4.1 Flash | c2 pass@3 | 96 | 97.9 [93.8, 100.0] | - | - | 104k |
| DeepSeek V4.1 Flash | c3 self-test (solvers) | 96 | 97.9 [93.8, 100.0] | 93 | 0.0 [0.0, 0.0] | 85k |
| DeepSeek V4.1 Flash | c3n self-test (no solvers) | 96 | 97.9 [93.8, 100.0] | 94 | 0.0 [0.0, 0.0] | 59k |
| DeepSeek V4.1 Flash | c4 oracle feedback | 95 | 97.9 [93.6, 100.0] | 88 | 0.0 [0.0, 0.0] | 74k |
| DeepSeek V4.1 Flash | c5 same-model tester | 96 | 94.8 [89.6, 99.0] | 89 | 0.0 [0.0, 0.0] | 125k |
| DeepSeek V4.1 Flash | c5x other-model tester | 96 | 94.8 [89.6, 99.0] | 90 | 3.3 [0.0, 7.5] | 61k |
| GPT-OSS 120B | c1 single shot | 96 | 67.7 [54.2, 80.2] | - | - | 19k |
| GPT-OSS 120B | c2 pass@3 | 96 | 84.4 [71.9, 95.8] | - | - | 56k |
| GPT-OSS 120B | c3 self-test (solvers) | 96 | 78.1 [64.6, 89.6] | 88 | 14.8 [5.4, 25.0] | 92k |
| GPT-OSS 120B | c3n self-test (no solvers) | 96 | 75.0 [61.5, 87.5] | 90 | 20.0 [8.6, 32.2] | 73k |
| GPT-OSS 120B | c4 oracle feedback | 96 | 85.4 [75.0, 93.8] | 77 | 1.3 [0.0, 4.4] | 106k |
| GPT-OSS 120B | c5 same-model tester | 96 | 76.0 [62.5, 88.5] | 87 | 16.1 [6.7, 26.7] | 139k |
| GPT-OSS 120B | c5x other-model tester | 96 | 76.0 [62.5, 88.5] | 70 | 0.0 [0.0, 0.0] | 75k |

## Paired comparisons (same model, task and seed)

Difference = rate(A) - rate(B). McNemar's exact test on discordant pairs.

Holm p: Holm-Bonferroni adjusted over the comparisons of each model.

| Model | Outcome | A vs B | Pairs | A % | B % | Only A | Only B | Diff (pp) [CI] | p | Holm p |
|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | correct | c2 vs c3n | 96 | 97.9 | 97.9 | 0 | 0 | +0.0 [0.0, 0.0] | 1 | 1 |
| DeepSeek V4.1 Flash | correct | c3 vs c3n | 96 | 97.9 | 97.9 | 1 | 1 | +0.0 [0.0, 0.0] | 1 | 1 |
| DeepSeek V4.1 Flash | correct | c4 vs c3n | 95 | 97.9 | 97.9 | 1 | 1 | +0.0 [0.0, 0.0] | 1 | 1 |
| DeepSeek V4.1 Flash | false_claim | c3 vs c3n | 96 | 0.0 | 0.0 | 0 | 0 | +0.0 [0.0, 0.0] | 1 | 1 |
| DeepSeek V4.1 Flash | false_claim | c4 vs c3n | 95 | 0.0 | 0.0 | 0 | 0 | +0.0 [0.0, 0.0] | 1 | 1 |
| DeepSeek V4.1 Flash | false_claim | c5 vs c3n | 96 | 0.0 | 0.0 | 0 | 0 | +0.0 [0.0, 0.0] | 1 | 1 |
| DeepSeek V4.1 Flash | false_claim | c5x vs c5 | 96 | 3.1 | 0.0 | 3 | 0 | +3.1 [0.0, 7.3] | 0.25 | 1 |
| GPT-OSS 120B | correct | c2 vs c3n | 96 | 84.4 | 75.0 | 11 | 2 | +9.4 [0.0, 20.8] | 0.0225 | 0.0898 |
| GPT-OSS 120B | correct | c3 vs c3n | 96 | 78.1 | 75.0 | 7 | 4 | +3.1 [-2.1, 10.4] | 0.549 | 0.848 |
| GPT-OSS 120B | correct | c4 vs c3n | 96 | 85.4 | 75.0 | 12 | 2 | +10.4 [3.1, 18.8] | 0.0129 | 0.0647 |
| GPT-OSS 120B | false_claim | c3 vs c3n | 96 | 13.5 | 18.8 | 3 | 8 | -5.2 [-11.5, 1.0] | 0.227 | 0.68 |
| GPT-OSS 120B | false_claim | c4 vs c3n | 96 | 1.0 | 18.8 | 0 | 17 | -17.7 [-28.1, -8.3] | 1.53e-05 | 0.000107 |
| GPT-OSS 120B | false_claim | c5 vs c3n | 96 | 14.6 | 18.8 | 5 | 9 | -4.2 [-10.4, 2.1] | 0.424 | 0.848 |
| GPT-OSS 120B | false_claim | c5x vs c5 | 96 | 0.0 | 14.6 | 0 | 14 | -14.6 [-24.0, -6.2] | 0.000122 | 0.000732 |

## Famous vs. less common pairs

Each half: 16 tasks x 3 seeds. CIs resample tasks; p: permutation test shuffling which tasks are famous.

| Model | Condition | Correct % famous [CI] | Correct % less common [CI] | p | FP % famous [CI] | FP % less common [CI] | p |
|---|---|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | c1 | 95.8 [89.6, 100.0] | 95.8 [89.6, 100.0] | 1 | - | - | - |
| DeepSeek V4.1 Flash | c2 | 100.0 [100.0, 100.0] | 95.8 [87.5, 100.0] | 1 | - | - | - |
| DeepSeek V4.1 Flash | c3 | 100.0 [100.0, 100.0] | 95.8 [87.5, 100.0] | 1 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1 |
| DeepSeek V4.1 Flash | c3n | 100.0 [100.0, 100.0] | 95.8 [87.5, 100.0] | 1 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1 |
| DeepSeek V4.1 Flash | c4 | 100.0 [100.0, 100.0] | 95.7 [87.2, 100.0] | 0.474 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1 |
| DeepSeek V4.1 Flash | c5 | 95.8 [89.6, 100.0] | 93.8 [83.3, 100.0] | 1 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1 |
| DeepSeek V4.1 Flash | c5x | 95.8 [89.6, 100.0] | 93.8 [83.3, 100.0] | 1 | 4.3 [0.0, 10.6] | 2.3 [0.0, 7.3] | 0.98 |
| GPT-OSS 120B | c1 | 66.7 [47.9, 83.3] | 68.8 [50.0, 85.4] | 1 | - | - | - |
| GPT-OSS 120B | c2 | 83.3 [64.6, 100.0] | 85.4 [66.7, 100.0] | 1 | - | - | - |
| GPT-OSS 120B | c3 | 87.5 [75.0, 97.9] | 68.8 [47.9, 87.5] | 0.183 | 4.5 [0.0, 14.6] | 25.0 [10.4, 42.9] | 0.0585 |
| GPT-OSS 120B | c3n | 81.2 [62.5, 95.8] | 68.8 [47.9, 87.5] | 0.469 | 11.4 [0.0, 27.9] | 28.3 [10.6, 50.0] | 0.201 |
| GPT-OSS 120B | c4 | 85.4 [70.8, 97.9] | 85.4 [70.8, 97.9] | 1 | 2.4 [0.0, 8.3] | 0.0 [0.0, 0.0] | 0.931 |
| GPT-OSS 120B | c5 | 85.4 [66.7, 100.0] | 66.7 [43.8, 85.4] | 0.211 | 8.9 [0.0, 23.8] | 23.8 [9.5, 39.0] | 0.179 |
| GPT-OSS 120B | c5x | 85.4 [68.8, 100.0] | 66.7 [45.8, 85.4] | 0.229 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1 |
