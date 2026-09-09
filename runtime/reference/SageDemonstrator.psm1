Set-StrictMode -Version Latest

function Invoke-SageDemonstrator {
    param([Parameter(Mandatory)]$Request)
    $risk = if (@($Request.unknowns).Count -ge 3) { 'R2' } else { 'R1' }
    $questions = @($Request.unknowns | ForEach-Object { [pscustomobject]@{ question=$_; blocking=$true } })
    [pscustomobject]@{
        record_type='sage_demonstrator_result'; schema_version='sage-demonstrator/0.8'; request_id=$Request.request_id; status='CLARIFY_REQUIRED'; risk_level=$risk
        intake=[pscustomobject]@{ objective=$Request.raw_request; constraints=@($Request.known_constraints); non_goals=@($Request.non_goals) }
        clarification=[pscustomobject]@{ questions=$questions; blocking_count=$questions.Count }
        plan=[pscustomobject]@{ stages=@('CLARIFY','CLASSIFY','MODEL','ARCHITECT','PLAN','REVIEW','IMPLEMENT','VERIFY'); deliverables=@('Goal Contract','Architecture Model','Task Plan','Evidence Plan') }
        architecture=[pscustomobject]@{ source_of_truth='approved_model'; model_provider='provider-neutral'; domains=@('mobile-client','location-service','map-provider-adapter','place-storage','privacy-boundary'); relationships=@('mobile-client->location-service','mobile-client->map-provider-adapter','mobile-client->place-storage') }
        routing=[pscustomobject]@{ agents=@('requirements-agent','architecture-agent','security-agent','implementation-agent','verification-agent'); tools=@('schema-validator','architecture-policy-checker','test-runner'); external_execution='NOT_AUTHORIZED' }
        evidence_plan=@('clarification answers','architecture review','permission/privacy tests','offline behavior test','targeted regression')
    }
}

Export-ModuleMember -Function Invoke-SageDemonstrator
