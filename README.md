___

    Date: 17th of November 2020
    Author: Carlos Munoz
    Email: carlos_munozgarrido@mcafee.com

___
# mvedr-search.py

Tool that allows to execute queries to Mvision EDR from command line, showing the response in the console screen or in a file, supporting CSV and JSON format.

Queries files are stored in xml format on the ./hunting folder, the query defines the collectors, conditions and aggregation parameters, the query file is parsed and transformed into a Mvision EDR standard format query.

Queries files are organized in folders according with its category (for example network, processes or users categories), the -i parameter can point to the query file to be executed but it can also points to the folder category so all query files in the folder will be executed secuencially.

By default the output of the tool is the console screen in json format, -o parameter can be set to file in order to store the result of the query in a file, the location of the file and the name of the file is set in code, being the folder ./output and a combination of date and query name for the file name. In case the -o parameter is set to file the default format will be changed to csv, the -f parameter only applies when the output of the query is sent to a file, allowing to force the output format to CSV o JSON.

Some of the queries, in the hunting folder requires a custom collector to be used, the folder collectors shows the process to add two new collectors to Mvision EDR in charge of collecting logs events from the event viewer fo the systems.

For more information read the Readme file of collectors and hunting folders

## Command Line

python \nmvedr-search.py -u Username -p Password -i file_name or folder [-c datacenter US|EU] [-o output file|screen] 
[-f output format csv|json] 

Required parameters

-u Username: Mvision EDR Username
-p Password: Mvision EDR Password
-i Input value: It can be a query xml file or a folder, if it's a folder the script will execute all query xml found secuencially.

Optional parameters

-c Datacenter: Datacenter where Mvision EDR tenant is located, possible values are EU and US. Default value EU
-o output: Where the information returned will be shown, possible values are file or screen. If file is chosen a folder call output on the root of the project will be created, output files will be created there. Default value screen
-f format: Only applies when -o equals file, possible values are json and csv. Default value csv

## Installation

* Step 1: Clone the repository. 

git clone https://github.com/built4tech/mvedr.git

* Step 2: Add non standar modules, with the exception of the module requests, the rest of the modules used by this tool are part of the standard library

pip install -r requirements.txt

* Step 3: Execute the tool, see the examples section for help.

## Examples


* **Sample 1**, Query all incoming connections, showing the information on the console

```
 python .\mvedr-search.py -u "USER_NAME" -p "PASSWORD" -i .\hunting\network\incoming_connections.xml

2020-11-17 09:09:30,675 root - INFO - [+] Successful authentication
2020-11-17 09:09:30,676 root - INFO - [+] Processing file query .\hunting\network\incoming_connections.xml
2020-11-17 09:09:30,705 root - INFO - [+] Query name: Incoming connections
2020-11-17 09:09:30,705 root - INFO - [+] Query Description: HostInfo hostname, ip_address and  NetworkFlow  src_ip, dst_port where NetworkFlow direction EQUALS in and NetworkFlow status EQUALS CONNECTED
2020-11-17 09:09:31,020 root - INFO - [+] Proccesing query
2020-11-17 09:11:44,936 root - INFO - [+] Getting information
2020-11-17 09:11:45,175 root - INFO - [+] Query result - values from 0 to 25

{"startIndex": 0, "itemsPerPage": 25, "currentItemCount": 12, "totalItems": 12, "items": [{"output": {"HostInfo|hostname": "WINDOWS81", "HostInfo|ip_address": "10.0.0.8", "NetworkFlow|src_ip": "10.0.0.7", "NetworkFlow|dst_port": 139}, "count": 48, "created_at": "2020-11-17T08:10:00.013Z", "id": "939e156e4d8d3276abe8ee70572159c1"}, {"output": {"HostInfo|hostname": "WINDOWS10", "HostInfo|ip_address": "10.0.0.10", "NetworkFlow|src_ip": "10.0.0.8", "NetworkFlow|dst_port": 5357}, "count": 20, "created_at": "2020-11-17T08:10:01.013Z", "id": "11a231b57ba461da0386e17d6d32c901"}, {"output": {"HostInfo|hostname": "WINDOWS7", "HostInfo|ip_address": "10.0.0.7", "NetworkFlow|src_ip": "10.0.0.8", "NetworkFlow|dst_port": 139}, "count": 18, "created_at": "2020-11-17T08:10:00.926Z", "id": "94c2754658de4960e9a5a2c913dba08a"}, {"output": {"HostInfo|hostname": "WINDOWS7", "HostInfo|ip_address": "10.0.0.7", "NetworkFlow|src_ip": "10.0.0.8", "NetworkFlow|dst_port": 5357}, "count": 15, "created_at": "2020-11-17T08:10:00.926Z", "id": "ecc71348be9a3f55ce81b56e18163bdf"}, {"output": {"HostInfo|hostname": "WINDOWS81", "HostInfo|ip_address": "10.0.0.8", "NetworkFlow|src_ip": "10.0.0.10", "NetworkFlow|dst_port": 5357}, "count": 12, "created_at": "2020-11-17T08:10:00.013Z", "id": "b9bd58c953af4c9ddcf045bd75a2fada"}, {"output": {"HostInfo|hostname": "WINDOWS7", "HostInfo|ip_address": "10.0.0.7", "NetworkFlow|src_ip": "10.0.0.10", "NetworkFlow|dst_port": 5357}, "count": 11, "created_at": "2020-11-17T08:10:00.926Z", "id": "cac813fc480fefc1b199b3d2f9bd7a31"}, {"output": {"HostInfo|hostname": "WINDOWS10", "HostInfo|ip_address": "10.0.0.10", "NetworkFlow|src_ip": "10.0.0.7", "NetworkFlow|dst_port": 8081}, "count": 10, "created_at": "2020-11-17T08:10:01.013Z", "id": "f43eca115e24a8d604b34c29901c93ed"}, {"output": {"HostInfo|hostname": "WINDOWS7", "HostInfo|ip_address": "10.0.0.7", "NetworkFlow|src_ip": "10.0.0.8", "NetworkFlow|dst_port": 8081}, "count": 6, "created_at": "2020-11-17T08:10:00.926Z", "id": "6fb73c92adb777535f00a46613989a77"}, {"output": {"HostInfo|hostname": "WINDOWS10", "HostInfo|ip_address": "10.0.0.10", "NetworkFlow|src_ip": "10.0.0.8", "NetworkFlow|dst_port": 8081}, "count": 5, "created_at": "2020-11-17T08:10:01.013Z", "id": "8894d397bcd8aa43e6539d1c0ec8ca56"}, {"output": {"HostInfo|hostname": "WINDOWS10", "HostInfo|ip_address": "10.0.0.10", "NetworkFlow|src_ip": "10.0.0.7", "NetworkFlow|dst_port": 445}, "count": 1, "created_at": "2020-11-17T08:10:01.013Z", "id": "ba537fa9f8fd71d5d2d39adb4e66ee3b"}, {"output": {"HostInfo|hostname": "WINDOWS81", "HostInfo|ip_address": "10.0.0.8", "NetworkFlow|src_ip": "10.0.0.7", "NetworkFlow|dst_port": 8081}, "count": 1, "created_at": "2020-11-17T08:10:00.013Z", "id": "5f388b1e11236c3991836ca42db48052"}, {"output": {"HostInfo|hostname": "WINDOWS81", "HostInfo|ip_address": "10.0.0.8", "NetworkFlow|src_ip": "10.0.0.7", "NetworkFlow|dst_port": 445}, "count": 1, "created_at": "2020-11-17T08:10:00.013Z", "id": "6599e00911bdedefaf02384622aa3ab9"}]}
```

* **Sample 2**, Query all users related queries, showing the information on the console

```
python .\mvedr-search.py -u "USER_NAME" -p "PASSWORD" -i .\hunting\users\

2020-11-17 09:16:42,509 root - INFO - [+] Successful authentication
2020-11-17 09:16:42,512 root - INFO - [+] Processing file query .\hunting\users\admin_connection.xml
2020-11-17 09:16:42,526 root - INFO - [+] Query name: Admin  connection
2020-11-17 09:16:42,526 root - INFO - [+] Query Description: _Getsecuritylogs hostname, eventid, msg where _Getsecuritylogs eventid equals 4672
2020-11-17 09:16:42,811 root - INFO - [+] Proccesing query
2020-11-17 09:18:15,266 root - INFO - [+] Getting information
2020-11-17 09:18:15,461 root - INFO - [+] Query result - values from 0 to 25

{"startIndex": 0, "itemsPerPage": 25, "currentItemCount": 3, "totalItems": 3, "items": [{"output": {"_Getsecuritylogs|hostname": "windows10", "_Getsecuritylogs|eventid": "4672", "_Getsecuritylogs|msg": "Special privileges assigned to new logon."}, "count": 232, "created_at": "2020-11-17T08:17:16.977Z", "id": "8a1135c0f3eb63bb96b96807f51631b1"}, {"output": {"_Getsecuritylogs|hostname": "windows81", "_Getsecuritylogs|eventid": "4672", "_Getsecuritylogs|msg": "Special privileges assigned to new logon."}, "count": 221, "created_at": "2020-11-17T08:17:15.287Z", "id": "f117dc0f62c18cde31750247e1a245b2"}, {"output": {"_Getsecuritylogs|hostname": "windows7", "_Getsecuritylogs|eventid": "4672", "_Getsecuritylogs|msg": "Special privileges assigned to new logon."}, "count": 89, "created_at": "2020-11-17T08:17:12.050Z", "id": "a3841d2563994357d5770314c86e1944"}]}

2020-11-17 09:18:15,468 root - INFO - [+] End process for query
2020-11-17 09:18:15,468 root - INFO - [+] Processing file query .\hunting\users\loggedin_users.xml
2020-11-17 09:18:15,482 root - INFO - [+] Query name: Loggedin Users
2020-11-17 09:18:15,482 root - INFO - [+] Query Description: LoggedInUsers username and HostInfo hostname
2020-11-17 09:18:15,696 root - INFO - [+] Proccesing query
2020-11-17 09:19:48,210 root - INFO - [+] Getting information
2020-11-17 09:19:48,401 root - INFO - [+] Query result - values from 0 to 25

{"startIndex": 0, "itemsPerPage": 25, "currentItemCount": 3, "totalItems": 3, "items": [{"output": {"LoggedInUsers|username": "5Y5TEM_UPDATES", "HostInfo|hostname": "WINDOWS81"}, "count": 1, "created_at": "2020-11-17T08:18:40.995Z", "id": "4f333023ffa6f8a4bbf045bfbad5793a"}, {"output": {"LoggedInUsers|username": "5Y5TEM_UPDATES", "HostInfo|hostname": "WINDOWS7"}, "count": 1, "created_at": "2020-11-17T08:18:41.068Z", "id": "72e735aa500c6320938bd4bc04381b0f"}, {"output": {"LoggedInUsers|username": "5Y5TEM_UPDATES", "HostInfo|hostname": "WINDOWS10"}, "count": 1, "created_at": "2020-11-17T08:18:42.069Z", "id": "22caeeb7c236cdc4766dc9dbe795af22"}]}

2020-11-17 09:19:48,408 root - INFO - [+] End process for query
```

* **Sample 3**, Query all users related queries, storing the information obtained on files in csv format

```

python .\mvedr-search.py -u "USER_NAME" -p "PASSWORD" -i .\hunting\users\ -o file -f csv

2020-11-17 09:22:00,438 root - INFO - [+] Successful authentication
2020-11-17 09:22:00,441 root - INFO - [+] Processing file query .\hunting\users\admin_connection.xml
2020-11-17 09:22:00,443 root - INFO - [+] Query name: Admin  connection
2020-11-17 09:22:00,443 root - INFO - [+] Query Description: _Getsecuritylogs hostname, eventid, msg where _Getsecuritylogs eventid equals 4672
2020-11-17 09:22:00,695 root - INFO - [+] Proccesing query
2020-11-17 09:23:33,235 root - INFO - [+] Getting information
2020-11-17 09:23:33,452 root - INFO - [+] Processing file query .\hunting\users\loggedin_users.xml
2020-11-17 09:23:33,452 root - INFO - [+] Query name: Loggedin Users
2020-11-17 09:23:33,452 root - INFO - [+] Query Description: LoggedInUsers username and HostInfo hostname
2020-11-17 09:23:33,690 root - INFO - [+] Proccesing query
2020-11-17 09:25:06,584 root - INFO - [+] Getting information

**Output folder content**

    Directory: .\output


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a---l       17/11/2020      9:23            349 20201117092333_Admin_connection.csv
-a---l       17/11/2020      9:25            217 20201117092506_Loggedin_Users.csv

**File content**

type .\output\20201117092333_Admin_connection.csv

_Getsecuritylogs|hostname,_Getsecuritylogs|eventid,_Getsecuritylogs|msg,created_at,count
windows10,4672,Special privileges assigned to new logon.,2020-11-17T08:22:45.329Z,233
windows81,4672,Special privileges assigned to new logon.,2020-11-17T08:22:46.021Z,225
windows7,4672,Special privileges assigned to new logon.,2020-11-17T08:22:41.329Z,90
```