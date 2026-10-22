# cmark: test-suite report

- candidate cases: 2857
- kept tests: **2758**
- gold sha256: `e27119d5ce89a2f1e5808f5a1d6430c2700352dd033c0857b702ca48a1f616f2`

## Dropped

| reason | count |
|---|---|
| duplicate input | 1 |
| uninformative (dummy passes) | 98 |

uninformative (dummy passes) examples: spec_017_commonmark, spec_021_commonmark, spec_149_commonmark, spec_153_commonmark, spec_157_commonmark, spec_161_commonmark, spec_165_commonmark, spec_173_commonmark, spec_181_commonmark, spec_189_commonmark, spec_207, spec_219_latex, spec_265_commonmark, spec_333_commonmark, spec_347_latex

## Kept by group

| group | tests |
|---|---|
| breaks | 124 |
| cli | 44 |
| fuzz | 494 |
| input_bytes | 63 |
| pathological | 25 |
| regression | 46 |
| render_commonmark | 9 |
| render_html | 13 |
| render_latex | 13 |
| render_man | 13 |
| render_xml | 13 |
| safety | 122 |
| smart | 123 |
| sourcepos | 61 |
| spec_commonmark | 129 |
| spec_html | 651 |
| spec_latex | 154 |
| spec_man | 163 |
| spec_xml | 163 |
| width | 335 |

## Kept by source

| source | tests |
|---|---|
| fuzz | 494 |
| harvested | 1391 |
| probe | 873 |

## Exit codes

| exit code | tests |
|---|---|
| 0 | 2745 |
| 1 | 13 |

## Coverage of the gold source by the kept suite

Columns: regions, missed, cover | functions, missed, executed | lines, missed, cover | branches, missed, cover

```
TOTAL                                    13933              7105    49.01%         271                35    87.08%       14811              6935    53.18%       10120              5590    44.76%
```

Per-file numbers: `coverage/summary.txt`; uncovered lines: `coverage/uncovered.txt`.
