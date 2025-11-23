# Metrics Logging Helper Script
param(
    [Parameter(Position = 0)]
    [ValidateSet('registry', 'agent')]
    [string]$Type = 'registry',
    
    [Parameter(Mandatory = $false)]
    [double]$Duration = 0,
    
    [Parameter(Mandatory = $false)]
    [int]$FileCount = 0,
    
    [Parameter(Mandatory = $false)]
    [string]$AgentName = "",
    
    [Parameter(Mandatory = $false)]
    [bool]$Success = $true
)

$ApexRoot = Split-Path -Parent $PSScriptRoot

Push-Location $ApexRoot
try {
    if ($Type -eq 'registry') {
        python -c @"
from agent_app.metrics_logger import log_registry_scan
log_registry_scan($Duration, $FileCount)
print('Registry scan metric logged: {0}ms, {1} files' -f $Duration, $FileCount)
"@
    }
    elseif ($Type -eq 'agent') {
        $successStr = if ($Success) { 'True' } else { 'False' }
        python -c @"
from agent_app.metrics_logger import log_agent_execution
log_agent_execution('$AgentName', $Duration, $successStr)
print('Agent execution metric logged: {0}, {1}ms, success={2}' -f '$AgentName', $Duration, $successStr)
"@
    }
}
finally {
    Pop-Location
}
