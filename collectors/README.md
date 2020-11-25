___

    Date: 13th of November 2020
    Author: Carlos Munoz
    Email: carlos_munozgarrido@mcafee.com

___
# Mvision EDR - Custom Collectors

## Event Log Security and System Events

### Description

The Sans institute in its Digital Forensics & Incident Response poster publication [https://digital-forensics.sans.org/media/DFPS_FOR508_v4.3_12-18.pdf] stress the importance to monitor certain data sources like Event Logs, registry and File system to identify how attackers move arround the victim network.

McAfee Mvision EDR doesn't include, by default, a Log viewer collector. 
_Getsecurityevents.ps1 and _Getsystemevents.ps1 are two custom collectors that allow to get this information.

The amount of information that can be stored on the event viewer of each workstation can be huge, because of this both custom collectors limit the information obtained to the last 24 hours, and the event IDs to the list of Event IDs publised on the Sans Digital Forensic & Incident Response publication. Even taking into consideration this filter, it is recommended to use these collectors with additionally filters like hostname or specific event ID that allow to limit further the amount of information obtained.

### Event IDs collected  and basic explanation of each event:

* **_Getsystemevents.ps1:** 7034, 7035, 7036, 7040, 7045

Event ID | Brief Description
--- | --- 
7034 | Service crashed unexpectedly
7035 | Service sent a Start Stop control
7036 | Service started or stopped
7040 | Service Start type changed
7045 | A service was installed on the system

* **_Getsecurityevents.ps1:** 4624,4648,4672,4697,4698,4699,4700,4701,4702,5140

Event ID | Brief Description
--- | --- 
4624 | Logon Type 3
4648 | Logon specifying alternate credentials
4672 | Logon by a user with administrative rights
4697 | Security records service install
4698 | Scheduled task created
4699 | Scheduled task deleted
4700 | Scheduled task enabled-disabled
4701 | Scheduled task enabled-disabled
4702 | Scheduled task updated
5140 | Share Access

For more detail information of each event take a look to the mentioning Sans publication or google the id of the event.

### Setup

* Logon into Mvision EDR
* Go to Menu / Catalog /Collectors
* Add a new Custom Collector 
* Give it a name, it must start with _ (For instance _Getsystemevents.ps1)
* In collector content chose Windows Execute PowerShell Script
* Paste the content of _Getsystemevents.ps1 
* In the collector output be sure that you define the following 6 properties, the name of the properties and the Show by default check is your decision. 

Name | Type | Show by Default
--- | --- | ---
date | Time stamp | Yes
hostname | String | Yes
username | String | No
source | String | No
eventid | String | Yes
msg | String | Yes

* Repeat the same instructions in order to create the second custom collector (_Getsecurityevents.ps1) the collector output is exactly the same so you can use the same structure as before.

### Real Time Search

Go to Menu / Real-time Search and start using your new collectors, I have been able to test the collectors on Windows 7, Windows 8.1 and Windows 10.

**Query example:**

* _Getsecuritylogs date, hostname, eventid, msg, hint where _Getsecuritylogs hostname equals Windows10 and _Getsecuritylogs eventid equals 4648

A user connects to a server or runs a program locally using alternate credentials.  For instance a user maps a drive to a server but specifies a different user's credentials or opens a shortcut under RunAs by shift-control-right-clicking on the shortcut, selecting Run as..., and then filling in a different user's credentials in the dialog box that appears

This event is also logged when a process logs on as a different account such as when the Scheduled Tasks service starts a task as the specified user. Logged on user: specifies the original user account.

* _Getsystemlogs date, hostname, eventid, msg, hint where _Getsystemlogs hostname equals Windows10 and _Getsystelogs eventid equals 7045

Shows new services installed on the system

## GeoLocation information

### Description

McAfee Mvision EDR doesn't include, by default, a collector in charge of showing Geolocation information of the EDR clients. 

_publicipinfo.ps1 is a Custom collector that uses a public service https://ipinfo.io/ to collect this information.

When you use it it's interesting to analyze the count of systems, due to the agregation capability that Mvision EDR provides.

### Setup

* Logon into Mvision EDR
* Go to Menu / Catalog /Collectors
* Add a new Custom Collector 
* Give it a name, it must start with _ (For instance _Getpublicip.ps1)
* In collector content chose Windows Execute PowerShell Script
* Paste the content of _publicipinfo.ps1 
* In the collector output be sure that you define the following properties, the name of the properties and the Show by default check is your decision. 

Name | Type | Show by Default
--- | --- | ---
ip_address | IP | Yes
country | String | Yes
city | String | No
location | String | No
asn | String | Yes
postal | String | Yes
region | String | Yes
timezone | String | Yes

**Query example:**

* HostInfo hostname and _GetPublic_IP ip_address, country, city, region, postal, timezone, location, asn

![MvEDR Real Time Search Image](../images/mvedr_getpublicip.jpg)

