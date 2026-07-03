$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatchPath = Join-Path $ScriptDir "run_bot.bat"

# Trigger 1: Morning 8:30 AM
$Trigger1 = New-ScheduledTaskTrigger -Daily -At 8:30AM

# Trigger 2: Evening 5:30 PM
$Trigger2 = New-ScheduledTaskTrigger -Daily -At 5:30PM

# Combine triggers
$Triggers = @($Trigger1, $Trigger2)

# Action to run the batch file
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatchPath`"" -WorkingDirectory $ScriptDir

# Settings: Allow run on battery power and run as soon as possible if missed
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$TaskName = "Naukri_Auto_Apply_Bot"
$Description = "Automates Naukri profile updates and SAP Security job applications twice daily."

# Register Task (overwriting if exists)
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Output "Unregistered existing scheduled task: $TaskName"
}

Register-ScheduledTask -TaskName $TaskName -Trigger $Triggers -Action $Action -Settings $Settings -Description $Description -ErrorAction Stop

Write-Output "Successfully registered scheduled task: $TaskName"
Write-Output "It will run twice daily at 8:30 AM and 5:30 PM."
