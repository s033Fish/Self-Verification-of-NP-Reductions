# False claims: causes and spec gaps (49 claims)

## Cause by condition

| Model | Condition | Claims | shortcut | blowup | gadget |
|---|---|---|---|---|---|
| GPT-OSS | c3 | 13 | 8 | 4 | 1 |
| GPT-OSS | c3n | 18 | 15 | 2 | 1 |
| GPT-OSS | c4 | 1 | 0 | 0 | 1 |
| GPT-OSS | c5 | 14 | 8 | 4 | 2 |
| DeepSeek | c5x | 3 | 0 | 0 | 3 |
| **all** |  | 49 | **31** | **10** | **8** |

## What the agent's check left out (spec gap; a claim can have several)

| Model | Condition | Claims | poly_time | large_instances | no_instances | none |
|---|---|---|---|---|---|---|
| GPT-OSS | c3 | 13 | 8 | 12 | 0 | 1 |
| GPT-OSS | c3n | 18 | 15 | 15 | 3 | 0 |
| GPT-OSS | c4 | 1 | 0 | 0 | 1 | 0 |
| GPT-OSS | c5 | 14 | 9 | 12 | 2 | 0 |
| DeepSeek | c5x | 3 | 0 | 0 | 3 | 0 |
| **all** |  | 49 | **32** | **39** | **9** | **1** |

## Cause by pair type (all claims)

| Pairs | Claims | shortcut | blowup | gadget |
|---|---|---|---|---|
| famous | 14 | 9 | 0 | 5 |
| less common | 35 | 22 | 10 | 3 |

Shortcuts whose docstring admits the brute force or the small-instance assumption: 29 of 31.
