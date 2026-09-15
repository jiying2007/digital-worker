# Edge Foundation Runtime Assets

This directory is the target runtime/control surface for Edge Foundation. It is provider-neutral and must not encode legacy `1+7` expert identities.

Canonical responsibilities remain in `domain.yaml`, `coordination.yaml`, `experts/**`, `assurance/**`, `gate-policy.yaml`, `skills.yaml`, and `evaluation/**`.

Runtime files here define execution mechanics only:

- `task-modes.yaml`: task type → allowed execution modes plus target Expert/Capability/Assurance routing metadata;
- `workflow.yaml`: lifecycle, gates, transitions, recovery and responsibility owners;
- `action-policy.yaml`: A0–A7 action authority;
- `material-requirements.yaml`: task-scoped material readiness requirements.

Product Pilot maturity is evaluated separately. Runtime migration/legacy retirement must not imply Production Ready, Device/HIL PASS, or Release Approval.
