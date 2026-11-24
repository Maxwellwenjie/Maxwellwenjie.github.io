---
title: Using LLMs to Triage Vehicle Logs
date: 2026-11-12
summary: A practical prompt pattern for turning 200k-line CAN logs into a shortlist of suspects.
tags: LLM, Diagnostics
---

A vehicle log is too big to read and too unstructured to query. This is the pattern I use.

## Step 1 — Reduce before you ask

Never paste a raw log into a model. Pre-aggregate first:

```python
# frame counts per ID, first and last timestamp
df.groupby('id').agg(count=('id','size'), t0=('t','min'), t1=('t','max'))
```

## Step 2 — Ask about *anomalies*, not about *causes*

Bad prompt:

> What is wrong with this log?

Good prompt:

> These are frame counts per CAN ID across 6 ignition cycles. Which IDs change behaviour
> between cycles, and what are the most likely explanations?

## Step 3 — Verify by re-querying the log

The model gives you hypotheses. The log gives you facts. Keep them separate.
