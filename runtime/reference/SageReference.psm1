Set-StrictMode -Version Latest

function Read-SageJson {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Contract file not found: $Path" }
    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json -Depth 100 -DateKind String
}

function Test-SageArchitectureModel {
    param([Parameter(Mandatory)]$Model)
    $errors = [System.Collections.Generic.List[string]]::new()
    if ($Model.record_type -ne 'architecture_model') { $errors.Add('record_type must be architecture_model') }
    $ids = @($Model.elements | ForEach-Object { [string]$_.architecture_id })
    if (($ids | Sort-Object -Unique).Count -ne $ids.Count) { $errors.Add('architecture element IDs must be unique') }
    $known = @{}; foreach ($id in $ids) { $known[$id] = $true }
    foreach ($rel in @($Model.relationships)) {
        if (-not $known.ContainsKey([string]$rel.from)) { $errors.Add("relationship endpoint missing: $($rel.from)") }
        if (-not $known.ContainsKey([string]$rel.to)) { $errors.Add("relationship endpoint missing: $($rel.to)") }
    }
    [pscustomobject]@{ valid = ($errors.Count -eq 0); errors = @($errors); model_id = [string]$Model.model_id; model_version = [string]$Model.model_version }
}

function Compare-SageArchitectureModels {
    param([Parameter(Mandatory)]$Approved, [Parameter(Mandatory)]$Observed)
    $approvedCheck = Test-SageArchitectureModel $Approved
    $observedCheck = Test-SageArchitectureModel $Observed
    $findings = [System.Collections.Generic.List[object]]::new()
    if (-not $approvedCheck.valid) { throw "Approved model invalid: $($approvedCheck.errors -join '; ')" }
    if (-not $observedCheck.valid) { throw "Observed model invalid: $($observedCheck.errors -join '; ')" }
    $approvedEdges = @($Approved.relationships | ForEach-Object { "$(($_.from))|$(($_.to))|$(($_.kind))" })
    $observedEdges = @($Observed.relationships | ForEach-Object { "$(($_.from))|$(($_.to))|$(($_.kind))" })
    foreach ($edge in $observedEdges) {
        if ($approvedEdges -notcontains $edge) {
            $parts = $edge -split '\|', 3
            $findings.Add([pscustomobject]@{ finding_id = "drift.$($findings.Count + 1)"; kind = 'UNEXPECTED_RUNTIME_RELATIONSHIP'; severity = 'HIGH'; edge = $edge; evidence_refs = @('reference-runtime:observed-graph') })
        }
    }
    $status = if ($findings.Count -eq 0) { 'CONVERGED' } else { 'NOT_CONVERGED' }
    [pscustomobject]@{ comparison_id = "comparison.$([guid]::NewGuid().ToString('N'))"; approved_model_version = [string]$Approved.model_version; observed_model_version = [string]$Observed.model_version; status = $status; findings = @($findings) }
}

Export-ModuleMember -Function Read-SageJson, Test-SageArchitectureModel, Compare-SageArchitectureModels
