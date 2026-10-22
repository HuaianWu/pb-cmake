# cmark: validation in the clean-room image

## Agent's view (user `agent`)

```
whoami: agent
run binary: exit 0
read binary: denied (good)
upstream source files found: 0
docs: /workspace/docs: README.md man1 man3  /workspace/docs/man1: cmark.1  /workspace/docs/man3: cmark.3 
workspace: docs 
```

## Hidden test suite against submissions

| submission | result | expected |
|---|---|---|
| gold binary (original deleted first) | 2758/2758 passed | all pass |
| dummy (`cat`) | 0/2758 passed | ~0 |
| wrapper calling the original, original still present | 2758/2758 passed | shows why deletion matters |
| wrapper calling the original, original deleted (real evaluation) | 0/2758 passed | 0 |

## Gold binary hash

- recorded with: `e27119d5ce89a2f1e5808f5a1d6430c2700352dd033c0857b702ca48a1f616f2`
- built in image: `cb97e79f3c5ac4ebbf3ae9f9d8c570141ff7e2e82c7ae1d6dc226d5a311ad146`
- different builds; the gold row above shows they behave identically on the suite
