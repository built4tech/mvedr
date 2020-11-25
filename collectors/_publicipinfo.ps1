$outfile = "$env:TEMP\utf8temp.tmp"
If (Test-Path $outfile){
	Remove-Item $outfile
}

$ip_info = Invoke-RestMethod -Method Get -Uri 'https://ipinfo.io/'

$city       = $ip_info.city
$ip         = $ip_info.ip
$loc        = $ip_info.loc   
$org        = $ip_info.org 
$postal     = $ip_info.postal 
$region     = $ip_info.region 
$timezone   = $ip_info.timezone 
$country    = $ip_info.country

# Mvision EDR requires collectors to generate a CSV file, location information has a comma between its coordenades
# the following line use scape characters to surround it between quote marks
$loc = "`"$loc`""
$org = "`"$org`""
$region = "`"$region`""

$line     = $ip, $country, $city, $loc, $org, $postal, $region, $timezone -join ','

# MVEDR doesn't support other codes but UTF-8, transforming the original Event message (UTF16) to UTF 8 requires
# the creation of a temporal file, encoding to UTF8. 
write-output $line | out-file -FilePath $outfile -Append -Encoding utf8   

get-content -Path $outfile -Encoding UTF8 -ErrorAction SilentlyContinue
