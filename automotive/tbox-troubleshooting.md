---
title: T-Box Troubleshooting Notes
date: 2026-11-18
summary: Country code mismatch, Wi-Fi provisioning and network registration issues in the field.
tags: T-Box, OTA
---

Field notes from a batch of T-Box units that failed to register on the mobile network
after delivery.

## Symptom

Unit boots, Wi-Fi hotspot comes up, but no cellular registration. `AT+COPS?` returns
an empty operator list.

## Root causes found

- **Country code mismatch** — the unit was provisioned for the wrong market region.
- **Wi-Fi provisioning** — the hotspot SSID was blocking the provisioning APN retry loop.
- **Stale SIM profile** — the eSIM profile had not been activated for the destination carrier.

## Diagnostic order

Check the country code *first*. It is a one-line query and it explains the majority of
"No Service" tickets that look like hardware failures.

```text
AT+CGDCONT?
AT+COPS=?
AT+CSQ
```

## Fix

A firmware-side guard that refuses to boot the modem when the provisioned country does not
match the SIM's MCC, surfacing a clear error instead of silent retries.
