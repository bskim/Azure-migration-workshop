# Shared preparation — the private Blob execution path

English | [한국어](./README-ko.md)

**Sample configuration:** the provided Blob examples use private endpoints/DNS, public network Disabled, Entra data authentication, Shared Key/anonymous access disabled, bypass None and no resource-instance exceptions. Use the selected lab's approved identity/network inputs and check applicable policies with the administrator. Keep the supplied configuration and TLS checks unchanged; an alternative needs its own supported scenario and approval. Authentication and network access are independent.


Supply reusable private network/DNS/client inputs for Blob basics and AzCopy. This is not app, ACR, Docker or AKS preparation and does not require completing a compute track.

**Resources for this step**

- [Storage](../../modules/onboarding/storage/README.md)
- [Objects](../../modules/migration/objects/README.md)

## 1. Learning objectives and module boundaries

Choose concept reading, reuse of existing approved private accounts/endpoints/DNS/client/data identity, or a separately approved instructor diagnostic fixture. With no network input, use a walkthrough or instructor-provided environment. WSL, ordinary Cloud Shell and Portal account-management sign-in do not automatically provide private Blob data connectivity. The Blob default is public network Disabled, firewall default Deny and bypass None, HTTPS/TLS, anonymous Blob access disabled and Shared Key disabled. Entra/RBAC does not replace network isolation. Use an approved private client, Approved Blob Private Endpoints, canonical hostname DNS and routes to the selected accounts; never reopen public access to resolve a failure.

Previously configured resource-instance or trusted-service exceptions may remain effective even with public network Disabled; read the [Storage network limitations](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-limitations). [Resource-instance rules](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-resource-instances) govern **public endpoint network access**, do not grant data permissions and are **not Private Endpoints**. The provided samples use bypass None and empty resourceAccessRules. Adding such exceptions is neither approved here nor a private-compliant workaround.

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Private endpoint overview](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview)
- [Storage private endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [Virtual networks overview](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview)
- [Private dns overview](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview)
- [Overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/overview)
- [Run command](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/run-command)
- [Nat overview](https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview)

## 3. Reuse existing approved inputs first

The administrator confirms account owner/resource ID, Approved blob endpoint, private zone/link, client route/NSG and data identity. Use the canonical Blob hostname, not an IP or privatelink URL. Check actual public Disabled and data requests separately from DNS/TCP/role assignment output. For two-account server-to-server copy confirm the official restricted-network topology: a hub client with endpoints in different spokes can encounter CannotVerifyCopySource. Mover's native identity/topology support must be assessed separately from AzCopy.

**Resources for this step**

- [Copy blobs between storage accounts network restriction](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/blobs/connectivity/copy-blobs-between-storage-accounts-network-restriction)

## 4. Instructor alternative: a small diagnostic fixture

If inputs are unavailable, the instructor prepares only an approved fixture group/VNet, separate client/endpoint subnets, required account PEs and private DNS links. Existing accounts remain with their original owners. An optional small x64 Linux VM has no public NIC IP or SSH inbound and uses management Run Command, MI data roles and approved explicit outbound. NAT public IP is outbound only, not Blob public access. Validate SKU/image/quota/cost and guest-agent/tool requirements; broad HTTP/HTTPS port rules are not an FQDN allowlist. Install only official/approved CLI/AzCopy. Blob-only learners do not install a DB or take VM+Docker; diagnostic recovery and timing details belong to the instructor guide.

**Resources for this step**

- [Tutorial private endpoint storage portal](https://learn.microsoft.com/en-us/azure/private-link/tutorial-private-endpoint-storage-portal)

## 5. Execute data operations and read actual guest evidence

Use the user Entra private PowerShell branch or VM Bash/MI branch, not copied human login caches. The linked Blob script uses original upload/list/download/20-byte SHA-256 checks; object preparation seeds source only and official AzCopy performs copy. Python only interprets job JSON and small hash comparisons. Require the appropriate final PASS and reject guest error/traceback/FAIL even if outer Run Command says Enable succeeded. Managed output is limited, so protect full logs/job/diagnostics on the fixture. Pass synthetic base64 as explicit name=value parameters; never send customer data or secrets that way.

**Resources for this step**

- [Private data verification](../../modules/onboarding/storage/verify/verify-private.sh)
- [Prepare the private synthetic source](../../modules/migration/objects/verify/prepare-private.sh)
- [Private data verification](../../modules/migration/objects/verify/verify-private.sh)

## 6. Costs, owners and cleanup

Approve current VM/disk/NAT/IP/PE/DNS/data-processing costs from the calculator rather than treating the fixture as free. Storage/Objects own their new accounts/data/grants; fixture owns only its new VM/MI/NIC/disk/VNet/NSG/NAT/IP/PE/DNS and exact added grants. Do not delete the fixture while consumers remain. Revoke exact external account-scope grants before removing the owned fixture; preserve accounts/data/app/ACR and existing client/DNS/roles. A removed PE and a removed account are different effects; a retained public-disabled account still needs an access path.

**Resources for this step**

- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
