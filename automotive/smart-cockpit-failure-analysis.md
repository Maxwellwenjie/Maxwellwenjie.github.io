---
title: Smart Cockpit Failure Analysis
date: 2026-11-24
summary: Root-cause methodology for intermittent display and audio faults on LEAP 3.5 platforms.
tags: Smart Cockpit, Diagnostics
---

Intermittent faults are the hardest class of problem in vehicle electronics: they never
show up when the diagnostic tool is connected.

## The problem

On the LEAP 3.5 platform we saw display flicker and audio dropouts that appeared only at
certain temperatures and only after 40+ minutes of driving.

## Approach

1. Reproduce with a logged bus — never chase a symptom you cannot record.
2. Correlate timestamps across CAN, Ethernet and the kernel log.
3. Narrow the window until one ECU remains.

> A fault you cannot reproduce on demand is a fault you do not yet understand.

## What the traces showed

The dropout aligned with a periodic re-enumeration on the internal USB path. The root cause
was a power-sequencing race in the cockpit domain controller, not the display itself.

## Takeaway

Always validate the *power* path before the *signal* path. Signal integrity problems get the
attention because they look technical; power sequencing problems cause most of them.
