# SYSTEM EVENTS

# The following document (see link bellow) has been followed in order to chose which event IDs to capture and their description
# MVEDR doesn't support other codes but UTF-8, transforming the original Event message (UTF16) to UTF 8 requires
# the creation of a temporal file, encoding to UTF8. 
# Additionally to the event description the collector also shows a quick hint, based on SANS document

# https://digital-forensics.sans.org/media/DFPS_FOR508_v4.3_12-18.pdf

# Hint of the events to be capured
$eventHint = @{}
$eventHint.add( '7045', 'SYSTEM: A service was installed on the system' )
$eventHint.add( '7040', 'SYSTEM: Service Start type changed' )
$eventHint.add( '7036', 'SYSTEM: Service started or stopped' )
$eventHint.add( '7035', 'SYSTEM: Service sent a Start Stop control' )
$eventHint.add( '7034', 'SYSTEM: Service crashed unexpectedly' )

$eventlogtype = "system"
$datestart = (Get-Date).AddDays(-1)
$dateend = (Get-Date)

$systemlogs = Get-WinEvent -ErrorAction SilentlyContinue -FilterHashtable @{LogName=$eventlogtype; StartTime=$datestart; EndTime=$dateend; id=7034,7035,7036,7040,7045} |Sort-Object -Property TimeCreated -Descending 

$outfile = "$env:TEMP\utf8temp.tmp"
If (Test-Path $outfile){
	Remove-Item $outfile
}

foreach ($log in $systemlogs){
    $time     = $log.Timecreated.ToString("yyyy-MM-dd HH:mm:ss")
    $machine  = $log.MachineName
    $username = $log.UserId
    $source   = $log.ProviderName
    $id       = $log.Id   
    $msg      = $log.Message 
    # In case the msg has a comma replace it with a dot as MvEDR requires a comma separated table
    $msg      = $msg -replace ',','.'
    $hint     = $eventHint[$id.ToString()]
    $line     = $time, $machine, $username, $source, $id, $msg, $hint -join ','
    write-output $line | out-file -FilePath $outfile -Append -Encoding utf8    
}
get-content -Path $outfile -Encoding UTF8 -ErrorAction SilentlyContinue
