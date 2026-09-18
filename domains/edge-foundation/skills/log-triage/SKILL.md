---
id: log-triage
version: 1.0.0
owner_kind: capability
owner: embedded.debug-reliability
max_action_level: A2_GENERATE
inputs: [raw-logs, source-identity, device-context]
outputs: [diagnostic-evidence]
---
# Log Triage

## Purpose
Convert raw logs into a provenance-preserving timeline and diagnostic evidence set while strictly separating observed events, inference and confirmed facts.

## Use When
- Initial defect/incident triage with raw logs.
- Correlating multi-process/kernel/MCU/device logs around the first abnormal event.
- Determining what additional capture is needed before deeper diagnosis.

## Do Not Use For
- Declaring root cause solely from a final error code or repeated message.
- Rewriting/truncating logs in a way that loses original context.
- Using logs from a different build/device as target proof.

## Required Inputs
- Raw logs or durable references to the original capture.
- Exact source/firmware identity where available.
- Device/environment/run context relevant to collection.

## Optional Inputs
- Clock synchronization information and multi-source traces.
- Known-good baseline logs.
- Hashes, capture command and collector/run IDs.

## Method
1. Bind logs to exact source/firmware/device/environment identity or mark identity gaps.
2. Preserve original context around the first abnormal event, not just the terminal error.
3. Build a time-ordered timeline across relevant sources and note clock uncertainty.
4. Classify each material statement as Observed, Inferred or Confirmed.
5. Identify missing context and specify the smallest next capture that discriminates leading hypotheses.

## Outputs
- Diagnostic evidence timeline with provenance.
- Observed/Inferred/Confirmed separation and evidence gaps.
- Next discriminating log/trace capture request.

## Evidence Rules
- Raw capture remains authoritative; summaries must link back to it.
- Timestamp correlation must account for clock/source uncertainty.
- Repeated log messages can support frequency/sequence claims but not a causal root cause by themselves.

## BLOCK Conditions
- Logs are truncated or untraceable where raw context is required.
- Build/device identity is unknown and materially affects interpretation.
- Timestamp/source inconsistency prevents the requested causal ordering.

## Verification / Review Handoff
- Debug/Reliability hands normalized diagnostic evidence to deeper Skills/capabilities.
- Engineering must not treat an inferred log interpretation as a confirmed fix target.
- Verification uses independent reproduction evidence rather than the triage label.

## Evaluation
- Positive case: raw logs yield a stable first-abnormal-event timeline.
- Negative case: final error line alone does not produce root cause.
- Identity case: mismatched build/device log remains an evidence gap.

## Known Limits / Change Notes
- Log triage does not replace crash, memory, storage or performance-specific analysis.
- Version 1.0.0 is definition hardening only.
