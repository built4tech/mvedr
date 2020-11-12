# SECURITY LOGS

# The following document (see link bellow) has been followed in order to chose which event IDs to capture and their description
# MVEDR doesn't support other codes but UTF-8, transforming the original Event message (UTF16) to UTF 8 requires
# the creation of a temporal file, encoding to UTF8. 
# Additionally to the event description the collector also shows a quick hint, based on SANS document

# https://digital-forensics.sans.org/media/DFPS_FOR508_v4.3_12-18.pdf

# Hint of the events to be capured
$eventHint = @{}
$eventHint.add( '4624', 'SECURITY: Logon Type 3' )
$eventHint.add( '4648', 'SECURITY: Logon specifying alternate credentials' )
$eventHint.add( '4672', 'SECURITY: Logon by a user with administrative rights' )
$eventHint.add( '4697', 'SECURITY: Security records service install' )
$eventHint.add( '4698', 'SECURITY: Scheduled task created' )
$eventHint.add( '4699', 'SECURITY: Scheduled task deleted' )
$eventHint.add( '4700', 'SECURITY: Scheduled task enabled-disabled' )
$eventHint.add( '4701', 'SECURITY: Scheduled task enabled-disabled' )
$eventHint.add( '4702', 'SECURITY: Scheduled task updated' )
$eventHint.add( '5140', 'SECURITY: Share Access' )



$outfile = "$env:TEMP\utf8temp.tmp"
If (Test-Path $outfile){
	Remove-Item $outfile
}

$eventlogtype = "security"
$datestart = (Get-Date).AddDays(-1)
$dateend = (Get-Date)
$seclogs = Get-WinEvent -ErrorAction SilentlyContinue -FilterHashtable @{LogName=$eventlogtype; StartTime=$datestart; EndTime=$dateend; id=4624,4648,4672,4697,4698,4699,4700,4701,4702,5140} |Sort-Object -Property TimeCreated -Descending 

foreach ($log in $seclogs){
    $time     = $log.Timecreated.ToString("yyyy-MM-dd HH:mm:ss")
    $machine  = $log.MachineName
    # In the security event log type UserId is normally empty, information about the user is inside the description of the event
    $username = $log.UserId
    $source   = $log.ProviderName
    $id       = $log.Id   

    # The description of the event has a lot of information not suitable for a table
    $msg      = $log.Message
    $index    = $log.Message.IndexOf(".")
    $msg      = $msg.Substring(0, $index+1)
    # In case the msg has a comma replace it with a dot as MvEDR requires a comma separated table
    $msg      = $msg -replace ',','.' 

    $hint     = $eventHint[$id.ToString()]

    $line     = $time, $machine, $username, $source, $id, $msg, $hint -join ','

    write-output $line | out-file -FilePath $outfile -Append -Encoding utf8 
}
get-content -Path $outfile -Encoding UTF8 -ErrorAction SilentlyContinue


