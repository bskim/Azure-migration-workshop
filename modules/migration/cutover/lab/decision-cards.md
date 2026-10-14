# Cutover decision cards — synthetic scenarios

English | [한국어](./decision-cards-ko.md)

These are fictional learning inputs, not actual migration jobs, writer events or recovery results. T0/T1 indicate ordering, not measured timestamps. Use with the [cutover module](../README.md) and [runbook template](./runbook.csv).

## Card A — ready to switch a read client

Assume the source owner has stopped writers and saved the final baseline, the required native completion/sync condition is met, and target schema/content/representative reads match. A new approved read client is available. No new business writes have occurred on target (native migration writes are different). Source, backups, original profile, return method and approver are retained.

**Discuss:** Which actual evidence and approval would justify GO? Why must read-client switching and enabling writers be separate decisions? Assumptions on this card alone cannot authorize a real switch.

## Card B — connection fails after switching; no new writes

Assume a target read profile fails due to connection/TLS/wrong DB. Source remains protected, actual evidence confirms no new business writes on target, and original profile/rights/baseline and a responsible source owner remain available.

**Discuss:** When is a personal read-profile return appropriate? Who separately authorizes source read acceptance and writer resume? Does a working connection authorize native job cancellation or target deletion? It does not.

## Card C — mismatch after new target writes

Assume target accepted LAB-WRITE-001 and source lacks it, then target develops an error. Both databases and backups are retained.

**Discuss:** What is lost by simply reconnecting to source? Identify writer-stop, difference/reconciliation/restore, allowable loss/RPO and recovery approval responsibilities. This card does not authorize write SQL, reverse copy or a rollback program.

## Card D — target write state unknown

Target has errors, but writers, logs and data have not been inspected. Your own test was read-only; other clients/jobs/queues are unknown.

**Discuss:** Why is this not Card B? Keep unknown as unknown, choose NO-GO or wait for recovery approval, and request actual writer/log/data evidence from owners.

## Learning outcome

For one card record GO, NO-GO, awaiting return approval or data recovery plan required, with rationale, unknowns, owner, source/target retention and next evidence. No automated or operational transition is performed.
