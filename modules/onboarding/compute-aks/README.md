# AKS — run the same app with Deployment, Pod and Service

English | [한국어](./README-ko.md)

Reuse the shared image and Kubernetes manifest while learning Azure cluster, kubelet and workload identity boundaries. This is a new AKS deployment, not an actual EKS migration.

## 1. Learning objectives and module boundaries

Choose manifest reading (about 30 minutes) or an approved Azure lab (90–120 minutes plus cluster/role preparation). Inputs are the manifest/app contract or the same digest image, registry ID and cluster permissions. No VM/Container Apps/Functions/DB/Blob/Terraform completion is required. Shared image steps 4.1–4.2 are sufficient; do not create a Container Apps pull identity for AKS.

**Resources for this step**

- [Container image](../../../shared/container-image/README.md)

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [What is aks](https://learn.microsoft.com/en-us/azure/aks/what-is-aks)
- [Container registry intro](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-intro)
- [Overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Workload identity overview](https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview)
- [Overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Concepts network azure cni overlay](https://learn.microsoft.com/en-us/azure/aks/concepts-network-azure-cni-overlay)
- [Overview](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)

### Why this teaching cluster?

AKS Automatic is a production-ready option to evaluate, but this lab chooses Standard/base with an explicitly readable node pool. Free means no control-plane SLA, not no node/disk/network charges. Keep the documented two-node system-pool minimum; do not reduce it to an unsupported one-node/B-series example. Putting the tiny app in the system pool is a teaching simplification, not production workload isolation. GPU, extra user pools, zone HA and paid telemetry are outside scope.

## 3. Prerequisites, permissions and cost

Use local PowerShell 7.4+/Azure CLI/kubectl/kubelogin from the root. Match kubectl's supported version skew and approved Kubernetes patch. The teaching choice is AKS Standard/base Free tier, not a free VM service: the system pool requires at least two nodes and at least 4 vCPU/4 GB per node. The example uses two D4s_v5 nodes with upgrade-surge quota headroom. Approve nodes, managed disks, outbound load balancer/IP and cluster access separately. Use Entra/Azure RBAC with local accounts disabled, a private lab kubeconfig and RBAC-mode ACR. Cluster-scoped RBAC Cluster Admin is a lab simplification for namespace/node learning; AcrPull belongs to kubelet, not the app Pod. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [Aks](https://learn.microsoft.com/en-us/cli/azure/aks#az-aks-install-cli)
- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Read the manifest without cloud resources

Inspect Deployment selector, Pod labels, Service selector, named port and /health readiness/liveness probes. Requests 100m CPU/128Mi and limits 250m/256Mi have different purposes. One replica and Recreate match process-memory learning: updates interrupt service and reset state, not HA/zero downtime. The app does not call Kubernetes APIs, so no service-account token is mounted. Enabling Workload ID does not grant this Pod data access.

```text
Deployment: 1 replica → Pod: image + HTTP 8080 + /health probes
Service: ClusterIP 8080 → http port on Pods labelled app=workshop
kubectl port-forward → local 127.0.0.1:8080
```

**Resources for this step**

- [Deployment and Service manifest](./lab/app.yaml)
- [Sample app](../../../sample-app/README.md)

### 4.2. Confirm the selected cluster and client inputs

The command branch below is restricted public API access from one approved IPv4 /32. Validate the version, approved RSA public key, registry/subscription and immutable digest. SSH is not the access method here; only a public key input is used. Confirm tenant/Enabled, client egress, quota and costs. If VPN egress changes, seek an approved update, never 0.0.0.0/0. Private API access is a separate branch in step 4.7.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
az version
kubectl version --client
kubelogin --version
az login
$SubscriptionId = "<sandbox-subscription-id>"
$Location = "<approved-region>"
$KubernetesVersion = "<approved-supported-patch-version>"
$ApiServerCidr = "<approved-public-admin-ip>/32"
$NodeSshPublicKeyFile = "<approved-RSA-public-key-file>"
$RegistryServer = "<approved-registry-login-server>"
$RegistryId = "<approved-registry-resource-id>"
$ContainerImage = "<approved-registry-login-server>/workshop/app@sha256:<digest>"
$ParsedId = [guid]::Empty
$ParsedAddress = [System.Net.IPAddress]::None
if (-not [guid]::TryParse($SubscriptionId, [ref]$ParsedId) -or
    [string]::IsNullOrWhiteSpace($Location) -or $Location -like "<*" -or
    $KubernetesVersion -notmatch "^\d+\.\d+\.\d+$" -or
    $ApiServerCidr -notmatch "^\d{1,3}(\.\d{1,3}){3}/32$" -or
    -not [System.Net.IPAddress]::TryParse(($ApiServerCidr -split "/")[0], [ref]$ParsedAddress) -or
    -not (Test-Path -LiteralPath $NodeSshPublicKeyFile -PathType Leaf) -or
    [string]::IsNullOrWhiteSpace($RegistryServer) -or $RegistryServer -like "<*" -or
    [string]::IsNullOrWhiteSpace($RegistryId) -or $RegistryId -like "<*" -or
    $ContainerImage -notmatch "^[a-z0-9.-]+/[a-z0-9._/-]+@sha256:[a-f0-9]{64}$") {
    throw "Set the approved cluster inputs, public admin IP, public SSH key and image."
}
if (-not $RegistryId.StartsWith("/subscriptions/$SubscriptionId/", [System.StringComparison]::OrdinalIgnoreCase) -or
    -not $ContainerImage.StartsWith("$RegistryServer/", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "This lab expects the registry in the approved subscription and the selected image."
}
$NodeSshPublicKey = (Get-Content -Raw -LiteralPath $NodeSshPublicKeyFile).Trim()
if ($NodeSshPublicKey -notlike "ssh-rsa *") { throw "Provide an approved RSA public key, not a private key." }
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
az aks get-versions --location $Location --subscription $SubscriptionId --output table
$LabId = [guid]::NewGuid().ToString("N").Substring(0, 8)
$ResourceGroupName = "rg-amw-aks-$LabId"
$NodeGroupName = "rg-amw-aksnodes-$LabId"
$ClusterName = "aks-amw-$LabId"
$Namespace = "amw-$LabId"
$LabDirectory = Join-Path (Join-Path $PWD "lab-output") "aks-$LabId"
$KubeConfigPath = Join-Path $LabDirectory "kubeconfig"
$ManifestPath = Join-Path $LabDirectory "app.yaml"
[pscustomobject]@{ Subscription = $SubscriptionId; Region = $Location; Group = $ResourceGroupName; Nodes = $NodeGroupName; Cluster = $ClusterName; AdminCidr = $ApiServerCidr; Image = $ContainerImage } | Format-List
```

### 4.3. Create the fresh cluster after approval

Reject existing lab and node groups. Create the cluster with the explicit two-node pool, CNI Overlay/Cilium, distinct Pod/Service ranges, Entra/Azure RBAC and local accounts disabled. Inspect actual pool count/size, provisioning and node-group identity. There is no app Pod yet. Control-plane MI, kubelet pull and application Workload ID are separate; this app needs no federation/data grants.

```powershell
foreach ($Name in @($ResourceGroupName, $NodeGroupName)) {
    $Exists = az group exists --name $Name --subscription $SubscriptionId --output tsv
    if ($Exists -ne "false") { throw "Use fresh lab and node groups." }
}
New-Item -ItemType Directory -Path $LabDirectory -ErrorAction Stop | Out-Null
az group create --name $ResourceGroupName --location $Location --subscription $SubscriptionId --tags Workshop=azure-migration-aks LabId=$LabId --output table
az aks create --name $ClusterName --resource-group $ResourceGroupName --node-resource-group $NodeGroupName --location $Location --sku base --tier free --kubernetes-version $KubernetesVersion --node-count 2 --node-vm-size Standard_D4s_v5 --node-osdisk-type Managed --node-osdisk-size 32 --os-sku AzureLinux3 --max-pods 30 --network-plugin azure --network-plugin-mode overlay --network-dataplane cilium --pod-cidr 10.244.0.0/16 --service-cidr 10.50.0.0/16 --dns-service-ip 10.50.0.10 --outbound-type loadBalancer --api-server-authorized-ip-ranges $ApiServerCidr --enable-managed-identity --enable-aad --enable-azure-rbac --disable-local-accounts --enable-oidc-issuer --enable-workload-identity --ssh-key-value $NodeSshPublicKeyFile --subscription $SubscriptionId --output table
$Cluster = az aks show --name $ClusterName --resource-group $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
if ($Cluster.provisioningState -ne "Succeeded" -or $Cluster.nodeResourceGroup -ne $NodeGroupName -or
    @($Cluster.agentPoolProfiles).Count -ne 1 -or $Cluster.agentPoolProfiles[0].count -ne 2 -or
    $Cluster.agentPoolProfiles[0].vmSize -ne "Standard_D4s_v5") {
    throw "The cluster does not match the approved lab configuration."
}
$ClusterId = $Cluster.id
$KubeletObjectId = $Cluster.identityProfile.kubeletidentity.objectId
$ParticipantObjectId = az ad signed-in-user show --query id --output tsv
if (-not $ClusterId -or -not $KubeletObjectId -or -not $ParticipantObjectId) { throw "Cluster or identity IDs are missing." }
[pscustomobject]@{ ClusterScope = $ClusterId; RegistryScope = $RegistryId; Kubelet = $KubeletObjectId; Participant = $ParticipantObjectId } | Format-List
```

### 4.4. Administrator: grant two distinct permissions

Grant kubelet AcrPull at registry scope and the participant's lab-only Kubernetes RBAC role at new cluster scope separately. Save each exact assignment ID immediately even if the next assignment fails. Record them in this lab directory and verify prefixes before continuing. Do not remove or treat preexisting roles as new lab grants. Allow propagation and do not accept 403 as success.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$AcrPullAssignmentId = az role assignment create --assignee-object-id $KubeletObjectId --assignee-principal-type ServicePrincipal --role AcrPull --scope $RegistryId --subscription $SubscriptionId --query id --output tsv
if ([string]::IsNullOrWhiteSpace($AcrPullAssignmentId)) { throw "The kubelet role assignment ID was not returned." }
$AcrPullAssignmentId
```

```powershell
$ClusterAccessAssignmentId = az role assignment create --assignee-object-id $ParticipantObjectId --assignee-principal-type User --role "Azure Kubernetes Service RBAC Cluster Admin" --scope $ClusterId --subscription $SubscriptionId --query id --output tsv
if ([string]::IsNullOrWhiteSpace($ClusterAccessAssignmentId)) { throw "The cluster role assignment ID was not returned." }
$ClusterAccessAssignmentId
```

```powershell
if ([string]::IsNullOrWhiteSpace($AcrPullAssignmentId) -or
    -not $AcrPullAssignmentId.StartsWith("$RegistryId/providers/Microsoft.Authorization/roleAssignments/", [System.StringComparison]::OrdinalIgnoreCase) -or
    [string]::IsNullOrWhiteSpace($ClusterAccessAssignmentId) -or
    -not $ClusterAccessAssignmentId.StartsWith("$ClusterId/providers/Microsoft.Authorization/roleAssignments/", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Record only the role assignments created for this lab."
}
Set-Content -LiteralPath (Join-Path $LabDirectory "acr-grant-id.txt") -Value $AcrPullAssignmentId -Encoding utf8NoBOM
Set-Content -LiteralPath (Join-Path $LabDirectory "cluster-grant-id.txt") -Value $ClusterAccessAssignmentId -Encoding utf8NoBOM
```

### 4.5. Use only this lab's kubeconfig, namespace and manifest

Do not overwrite the default kubeconfig. Download user credentials to the dedicated path, convert with kubelogin, and require the expected context. Confirm two Ready nodes. Render the template with exact namespace/digest, reject remaining placeholders and apply only there. Expect Deployment 1/1 and a ClusterIP Service; distinguish node, Pod and Service addresses.

```powershell
if (Test-Path -LiteralPath $KubeConfigPath) { throw "Do not overwrite an existing kubeconfig." }
az aks get-credentials --name $ClusterName --resource-group $ResourceGroupName --file $KubeConfigPath --context $ClusterName --subscription $SubscriptionId
kubelogin convert-kubeconfig --login azurecli --kubeconfig $KubeConfigPath
$Context = kubectl --kubeconfig $KubeConfigPath config current-context
if ($Context -ne $ClusterName) { throw "Unexpected Kubernetes context." }
kubectl --kubeconfig $KubeConfigPath --context $ClusterName get nodes
kubectl --kubeconfig $KubeConfigPath --context $ClusterName create namespace $Namespace
kubectl --kubeconfig $KubeConfigPath --context $ClusterName label namespace $Namespace workshop=azure-migration-aks lab-id=$LabId
$Template = Get-Content -Raw -LiteralPath .\modules\onboarding\compute-aks\lab\app.yaml
$Rendered = $Template.Replace("<namespace>", $Namespace).Replace("<container-image>", $ContainerImage)
if ($Rendered.Contains("<namespace>") -or $Rendered.Contains("<container-image>")) { throw "Manifest placeholders remain." }
Set-Content -LiteralPath $ManifestPath -Value $Rendered -Encoding utf8NoBOM
kubectl --kubeconfig $KubeConfigPath --context $ClusterName apply --namespace $Namespace --filename $ManifestPath
kubectl --kubeconfig $KubeConfigPath --context $ClusterName rollout status deployment/workshop --namespace $Namespace --timeout=180s
kubectl --kubeconfig $KubeConfigPath --context $ClusterName get deployment,pods,services --namespace $Namespace
```

### 4.6. Port-forward and verify the shared HTTP contract

In a second local PowerShell terminal maintain localhost port-forward with this kubeconfig/context/namespace. Do not create public ingress or an app LoadBalancer. Use matching localhost requests in the first terminal. For a fresh single-process application, expect GET /health to return 200 with status ok, two initial items, POST /items to return 201, and the new item to appear on read-back. Invalid input returns 422 without changing the data. Restarting resets the in-memory dataset. A running resource or container is not enough: observe the actual HTTP responses and relevant logs. Inspect Pod request logs; Pod Running alone is not enough.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$KubeConfigPath = "<path-to-this-lab-kubeconfig>"
$ClusterName = "<this-lab-cluster-name>"
$Namespace = "<this-lab-namespace>"
kubectl --kubeconfig $KubeConfigPath --context $ClusterName port-forward --namespace $Namespace service/workshop 8080:8080 --address 127.0.0.1
```

```powershell
$BaseUrl = "http://127.0.0.1:8080"
$Health = Invoke-RestMethod "$BaseUrl/health"
$Before = @(Invoke-RestMethod "$BaseUrl/items")
if ($Health.status -ne "ok" -or $Before.Count -ne 2) { throw "Expected a healthy fresh app with two seed items." }
$Created = Invoke-RestMethod "$BaseUrl/items" -Method Post -ContentType "application/json" -Body '{"name":"aks-workshop-item"}' -StatusCodeVariable PostStatus
$After = @(Invoke-RestMethod "$BaseUrl/items")
if ($PostStatus -ne 201 -or $After.Count -ne 3 -or
    -not ($After | Where-Object { $_.id -eq $Created.id -and $_.name -eq "aks-workshop-item" })) {
    throw "Write/read verification failed."
}
$Invalid = Invoke-WebRequest "$BaseUrl/items" -Method Post -ContentType "application/json" -Body '{"name":""}' -SkipHttpErrorCheck
if ($Invalid.StatusCode -ne 422 -or @(Invoke-RestMethod "$BaseUrl/items").Count -ne 3) {
    throw "Invalid input changed the data or did not return 422."
}
kubectl --kubeconfig $KubeConfigPath --context $ClusterName logs deployment/workshop --namespace $Namespace --tail=20
```

### 4.7. Alternative: private API and approved private client

In the Portal, open **AKS Overview → Node pools** and inspect the system pool's management status, scaling mode and target node count. The example shows **Succeeded / Running / Manual / target 2**.

![AKS system node-pool management status and manual target of two nodes](./images/portal-aks-node-pool.png)

*The target count is desired capacity. A dash in Ready nodes leaves Kubernetes readiness unknown from that view. Nodes/Workloads reads require the browser/client to reach the private Kubernetes API through appropriate route/DNS and have the required Kubernetes authorization. Use the supplied private client's `kubectl get nodes`, Pod readiness, logs and HTTP checks for runtime results; keep the private endpoint configuration unchanged.*

Choose this instead of public API /32 access. Supply a dedicated node subnet, explicit outbound, private DNS and a reachable approved client. Do not apply public authorized-IP flags to the private branch. The control identity may need precisely scoped VNet/DNS/NAT rights; kubelet still needs registry pull. A diagnostic VM MI can use kubelogin --login msi with a newly scoped cluster role, whereas the local user branch uses azurecli. Verify actual kubectl authorization, two Ready nodes and the same namespace/manifest/localhost HTTP contract. The instructor prepares tools, DNS, TCP 443 and diagnostics; do not modify source DB engines. Record every new external-scope grant for cleanup.

## 5. Verification and common failures

Read scoped Pod descriptions/events on failures. Check quota/patch/system-pool support, approved API reachability, Entra/RBAC/propagation/client version, kubelet registry role/mode/digest, node readiness/scheduling and app port/probes/limits. Never use --admin or open the API globally as a shortcut. Restart/Recreate resets memory. Free fixed two-node operation is not an HA assessment.

```powershell
kubectl --kubeconfig $KubeConfigPath --context $ClusterName describe pods --namespace $Namespace --selector app=workshop
kubectl --kubeconfig $KubeConfigPath --context $ClusterName get events --namespace $Namespace --sort-by=.lastTimestamp
```

## 6. Cleanup and ownership

Own the new cluster and its managed node group, this namespace and precise consumer-added grants. In private mode account for owned control UAI/DNS/subnet and grants on shared VNet/NAT/registry without deleting those inputs. Handle only resources actually created after partial failures. The image publisher cleans up after the final consumer.

### 6.1. Namespace and this lab's role assignments

End port-forward, inspect namespace name and lab labels plus its resources, then approve namespace deletion. An administrator inspects the saved exact registry and cluster grant IDs/principals before separately approving their removal. Revoke consumer-added grants, not registry resources or existing assignments.

```powershell
$Ns = kubectl --kubeconfig $KubeConfigPath --context $ClusterName get namespace $Namespace --output json | ConvertFrom-Json
if ($Namespace -ne "amw-$LabId" -or $Ns.metadata.labels.workshop -ne "azure-migration-aks" -or $Ns.metadata.labels.'lab-id' -ne $LabId) {
    throw "The namespace is not this lab."
}
[pscustomobject]@{ Cluster = $ClusterName; Namespace = $Namespace; Labels = $Ns.metadata.labels } | Format-List
kubectl --kubeconfig $KubeConfigPath --context $ClusterName get deployment,pods,services --namespace $Namespace
```

```powershell
kubectl --kubeconfig $KubeConfigPath --context $ClusterName delete namespace $Namespace --wait=true
```

```powershell
$AcrPullAssignmentId = (Get-Content -Raw -LiteralPath (Join-Path $LabDirectory "acr-grant-id.txt")).Trim()
$ClusterAccessAssignmentId = (Get-Content -Raw -LiteralPath (Join-Path $LabDirectory "cluster-grant-id.txt")).Trim()
if (-not $AcrPullAssignmentId.StartsWith("$RegistryId/providers/Microsoft.Authorization/roleAssignments/", [System.StringComparison]::OrdinalIgnoreCase) -or
    -not $ClusterAccessAssignmentId.StartsWith("$ClusterId/providers/Microsoft.Authorization/roleAssignments/", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Unexpected role assignment scopes."
}
az role assignment list --scope $RegistryId --subscription $SubscriptionId --query "[?id=='$AcrPullAssignmentId'].{id:id,principal:principalId,scope:scope}" --output table
az role assignment list --scope $ClusterId --subscription $SubscriptionId --query "[?id=='$ClusterAccessAssignmentId'].{id:id,principal:principalId,scope:scope}" --output table
```

```powershell
az role assignment delete --ids $AcrPullAssignmentId --subscription $SubscriptionId
az role assignment delete --ids $ClusterAccessAssignmentId --subscription $SubscriptionId
```

### 6.2. Inspect cluster and managed node groups

Confirm the current cluster's node-resource-group matches this lab. List both groups before approval to delete the owner group, then verify both disappear. If managed cleanup leaves a group, investigate rather than force-delete it blindly. Remove only kubeconfig, rendered manifest and the two grant files after cleanup is confirmed; preserve other files/shared image inputs.

```powershell
$Group = az group show --name $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
$CurrentCluster = az aks show --name $ClusterName --resource-group $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
az resource list --resource-group $ResourceGroupName --subscription $SubscriptionId --query "[].{name:name,type:type}" --output table
az resource list --resource-group $NodeGroupName --subscription $SubscriptionId --query "[].{name:name,type:type}" --output table
if ($ResourceGroupName -ne "rg-amw-aks-$LabId" -or $Group.tags.Workshop -ne "azure-migration-aks" -or
    $Group.tags.LabId -ne $LabId -or $CurrentCluster.nodeResourceGroup -ne "rg-amw-aksnodes-$LabId") {
    throw "The cluster groups do not match this lab."
}
az group delete --name $ResourceGroupName --subscription $SubscriptionId
foreach ($Name in @($ResourceGroupName, $NodeGroupName)) {
    $ExistsAfter = az group exists --name $Name --subscription $SubscriptionId --output tsv
    if ($ExistsAfter -ne "false") { throw "A lab or node group remains; investigate before claiming cleanup." }
}
```

```powershell
Remove-Item -LiteralPath $KubeConfigPath
Remove-Item -LiteralPath $ManifestPath
Remove-Item -LiteralPath (Join-Path $LabDirectory "acr-grant-id.txt")
Remove-Item -LiteralPath (Join-Path $LabDirectory "cluster-grant-id.txt")
Remove-Item -LiteralPath $LabDirectory
```

**Resources for this step**

- [Container image](../../../shared/container-image/README.md#6-cleanup-and-ownership)

## 7. Additional considerations for a real migration

Review EKS add-ons, ingress/PVC/storage, CRDs/policies/DNS and version compatibility. Compare IRSA/Pod Identity with Workload ID, separate kubelet and app permissions, and plan IP/egress/private API, minimum namespace access, user pools, PDBs, deployment strategy, durable data/backups and operational cutover.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.

**Resources for this step**

- [Use system pools](https://learn.microsoft.com/en-us/azure/aks/use-system-pools)
- [Cluster container registry integration](https://learn.microsoft.com/en-us/azure/aks/cluster-container-registry-integration)
- [Manage azure rbac](https://learn.microsoft.com/en-us/azure/aks/manage-azure-rbac)
- [Kubelogin authentication](https://learn.microsoft.com/en-us/azure/aks/kubelogin-authentication)
- [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Service](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Configure liveness readiness startup probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
