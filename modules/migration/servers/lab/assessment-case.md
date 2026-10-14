# Synthetic Azure Migrate assessment case

English | [한국어](./assessment-case-ko.md)

This is not a real server inventory, AWS discovery result or completed Azure assessment, and is not an upload-ready CSV. Use the [server module](../README.md) and the service's current official template.

For a separate import exercise, [synthetic-inventory.csv](./synthetic-inventory.csv) is the shared 27-column Portal-template asset with one fictional server. The card below explains assumptions and unknowns; the CSV is an Azure Migrate import input, not the planning scenario table or a replication source.

## Preservation requirement

The fictional server-sample is Windows Server 2019 x64 on EC2, with an OS/disk/service/local-state preservation goal. The assumed downtime objective is 60 minutes, not an achieved result. No source VM, data, account or appliance was constructed. Service names, ports, paths, dependencies and boot evidence remain unknown.

## Candidate synthetic template values

| Meaning | Candidate | Evidence |
|---|---|---|
| Unique name | srv-amw-<lab-id>.example.invalid | Fictional lab-only name |
| Cores | 4 | Invented capacity |
| Memory in MB | 8192 | Invented capacity |
| OS | Windows Server 2019 | Assumption; match current recognized values |
| Architecture | x64 | Assumption |
| Disk 1 in GB | 64 | Invented size, not actual usage |
| CPU/memory utilization | Unknown | Do not fill zero or invented measurements |
| Disk IOPS/throughput/network | Unknown | No performance collection |
| Boot type/source IP | Unknown | Needs actual evidence |
| Hypervisor | Unknown/not applicable | Do not put AWS into a VMware/Hyper-V field |

Use the downloaded template's supported names, units, required fields and unknown handling. Give the item and assessment a unique synthetic lab label; reimporting a shared name can update another item.

## Questions for interpreting results

1. Why is import success different from actual discovery?
2. Which fictional inputs drive as-is sizing?
3. Without performance history, why is this not measured performance-based rightsizing?
4. Why does OS readiness not establish app/service/data/boot compatibility?
5. Why can CSV-imported inventory not itself be replicated?
6. What actual supported source, separate replication appliance, Mobility service, network and roles would a demo require?

## Completion and stop criteria

Complete when you can distinguish invented capacity from unknowns and explain output limits. Stop on unavailable current template/UI, permission/format/OS-recognition errors or risk of overwriting existing project inventory. Do not prefill Ready, a real SKU/cost or migration success; actual service output needs its own input evidence, conditions and observation time.
