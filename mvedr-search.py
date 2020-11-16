import requests
import json
import sys
import os
import time
import xml.etree.ElementTree as ET
import argparse
import glob
from common import logger
import errno

# Definition of Global variables

# Current Path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# If the information is showed on screen it is paged, PAGE_SIZE is the Maximum number of returned lines per page
PAGE_SIZE = 25

# If the information is stores on a file, these files are stored on this path
OUTPUT_FOLDER = CURRENT_DIR + os.sep + 'output' + os.sep

class MvEDR():
    def __init__(self, region, user, password):
        self.api_endpoints = {
                             'login': '/identity/v1/login',
                             'rt_search': '/active-response/api/v1/searches',
                             'rt_status': '/active-response/api/v1/searches/{}/status',
                             'rt_getdata': '/active-response/api/v1/searches/{}/results?$offset={}&$limit={}'
                             }
        if region.upper() == 'EU':
            self.base_endpoint = 'https://api.soc.eu-central-1.mcafee.com'
        elif region.upper() =='US':
            self.base_endpoint = 'https://api.soc.mcafee.com'
        else:
            raise ValueError('[¡] Error región no soportada, seleccione US o EU')
        
        self.credentials = (user, password)
        self.auth_header = self.auth()
    
    def auth(self):
        try:
            r = requests.get(self.base_endpoint + self.api_endpoints['login'], auth=(self.credentials))
        except Exception as error:
            logger.error('[¡] Error en la conexión con la enpoint API')
            raise 

        if r.status_code == 200:            
            try:
                response = r.json()
                token = response['AuthorizationToken']
                return {'Authorization': 'Bearer {}'.format(token), 'content-type': 'application/json'}
            except Exception as error:
                logger.error('[¡] Error transformando la respuesta del proceso de autenticación a formato json ')
                raise
        else:
            raise ConnectionError('[¡] Error en el proceso de autenticación, status code {}'.format(r.status_code))

    def query(self, query):

        logger.debug("[Debug] Consulta realizada: \t {}".format(json.dumps(query)))

        try:
            r = requests.post(self.base_endpoint + self.api_endpoints['rt_search'], headers = self.auth_header, data = json.dumps(query))
        except Exception as error:
            logger.error('[¡] Error en la conexión con la enpoint API')
            raise

        if r.status_code == 200:
            try:
                response = r.json()
                return response
            except Exception as error:
                logger.error('[¡] Error transformando la respuesta de la consulta a formato json')
                raise
        else:
            raise ConnectionError('[¡] Error al realizar la consulta, status code {}'.format(r.status_code))
    
    def query_status(self, id):
        api_endpoint_rt_status= self.api_endpoints['rt_status']
        api_endpoint = self.base_endpoint + api_endpoint_rt_status.format(id)

        try:
            r = requests.get(api_endpoint, headers=self.auth_header)
        except Exception as error:
            logger.error('[¡] Error en la conexión con la enpoint API')
            raise


        if r.status_code == 200:
            try:
                response = r.json()
                return response
            except Exception as error:
                logger.error('[¡] Error transformando el estado de la consulta a formato json')
                raise
        else:
            raise ConnectionError('[¡] Error al comprobar el estado de la consulta, status code {}'.format(r.status_code))
    
    def getQueryData(self, id, offset=0, limit=50):
        api_endpoint_rt_getdata= self.api_endpoints['rt_getdata']
        api_endpoint = self.base_endpoint + api_endpoint_rt_getdata.format(id, offset, limit)

        try:
            r = requests.get(api_endpoint, headers=self.auth_header)
        except Exception as error:
            logger.error('[¡] Error en la conexión con la enpoint API')
            raise

        if r.status_code == 200:
            try:
                response = r.json()
                return response
            except Exception as error:
                logger.error('[¡] Error transformando los datos retornados por la consulta a formato json')
                raise
        else:
            raise ConnectionError('[¡] Error al obtener la información consultada, status code {}'.format(r.status_code))

class Query():

    def __init__(self, mvedr_object: MvEDR) -> None:
        self.projections = None
        self.condition = None
        self.agregated = None
        self.query_name = None
        self.query_description = None

        self.mvedr = mvedr_object
        
        self.query_id = None
        self.query_execute_metadata = None
        self.query_status_metadata = None

        self.query_data = None
    
    def parse_xml(self, xml_file: str) -> None:

        def sanitize(line):       
            line = ' '.join(line.split())
            return line

        try:
            tree  = ET.parse(xml_file)
            query_structure = tree.getroot()

            self.query_name        = query_structure.find('name').text
            self.query_description = query_structure.find('description').text

            self.projections = sanitize(query_structure.find('projections').text)
            self.condition   = sanitize(query_structure.find('condition').text)
            self.aggregated  = query_structure.find('aggregated').text

        except Exception as error:
            raise
    
    def execute_query(self):

        if not self.projections or not self.condition or not self.aggregated:
            raise ValueError("[¡] projections, conditions or aggregated value not set")

        built_query = {}

        built_query['projections'] = json.loads(self.projections)
        built_query['condition']   = json.loads(self.condition)
        built_query['aggregated']  = json.loads(self.aggregated)

        try:
            query_request = self.mvedr.query(built_query)
            self.query_execute_metadata = query_request
            self.query_id = query_request['id']
        except Exception as error:
            raise
    
    def get_query_id(self) -> str:
        if not self.query_id:
            raise ValueError("[¡] Query id not set")
        else:
            return self.query_id

    def get_query_status(self) -> str:
        try:
            id = self.get_query_id()

            query_status_metadata = self.mvedr.query_status(id)
            status = query_status_metadata['status']
            if status == "FINISHED":
                msg = "READY"
                self.query_status_metadata = query_status_metadata
            else:
                msg = "NOT READY"
        except Exception as error:
            raise

        return msg

    def get_query_lines(self) -> str:
        if not self.query_status_metadata:
            raise ValueError("[¡] Query status metadata not obtained")

        return self.query_status_metadata['results']

    def get_offset_query_data(self, offset=None, limit=None) -> str:
        try:
            if not offset:
                offset = 0
            if not limit:
                limit = self.get_query_lines()
            
            results = self.mvedr.getQueryData(self.query_id, offset, limit )

        except Exception as error:
            raise        
      
        return results
    
    def obtain_query_data(self):
        try:
            offset = 0
            limit = self.get_query_lines()            
            results = self.mvedr.getQueryData(self.query_id, offset, limit )

        except Exception as error:
            raise
        
        self.query_data = results


    def get_query_data(self, format):
        import csv

        # If the output folder where the datafiles will be created doen't exist create it.
        # check de Exception, if it's different that folder already exists raise it.
        try:
            os.makedirs(OUTPUT_FOLDER)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

        def _get_json_query_data(): 
            return self.query_data
        
        def _get_csv_query_data():
            data = self.query_data

            # Getting columns available
            columns = []
            if data["totalItems"] != 0:
                for each_column in data['items'][0]['output']:
                    columns.append(each_column)

                columns.append('created_at')
                columns.append('count')

                # Getting rows
                rows = []
                for each_item in data['items']:
                    data_dict = {}
                    data_dict['created_at'] = each_item['created_at']
                    data_dict['count'] = each_item['count']
                    for column in each_item['output'].keys():
                        data_dict[column] = each_item['output'][column]
                    
                    rows.append(data_dict)
            else:
                columns = None
                rows = None

            return (columns, rows)

        if not self.query_data:
            raise ValueError("[¡] Query data not obtained")

        filename = time.strftime("%Y%m%d%H%M%S")
        filename = filename + "_" + "_".join(self.query_name.split()) + '.' + format

        if format.upper() == "JSON":
            results = _get_json_query_data()
            try:
                with open(OUTPUT_FOLDER + filename, 'w+') as jsonfile:
                    jsonfile.write(json.dumps(results))
            except IOError:
                raise

        elif format.upper() == "CSV":
            csv_columns, dict_data = _get_csv_query_data()
            if csv_columns and dict_data:
                try:
                    with open(OUTPUT_FOLDER + filename, 'w+', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                        writer.writeheader()
                        for data in dict_data:
                            writer.writerow(data)
                except IOError:
                    raise
            else:
                try:
                    with open(OUTPUT_FOLDER + filename, 'w+') as f:
                        f.write("No system responded as a result of this query")
                except IOError:
                    raise
        else:
            raise ValueError("[¡] Query data format not supported, supported values (json and csv)")


def parseargs():
    '''
    Description: Function in charge of the CLI parameters
    Input:       No input
    Output:      Parsed arguments
    '''
    description = 'Set parameters for McAfee Mvision EDR search'
    prog = 'mvedr-search.py'
    usage = '\nmvedr-search.py -u Username -p Password -i file_name or folder [-f output format csv|json] [-o output file|screen] [-c datacenter US|EU]'
    epilog = 'Carlos Munoz (carlos.munozgarrido@mcafee.com)\n%(prog)s 1.0 (13/11/2020)'

    parser = argparse.ArgumentParser(epilog=epilog, usage=usage, prog=prog, description=description, formatter_class=argparse.RawTextHelpFormatter)

    required_group = parser.add_argument_group("Required parameters")

    
    arg_help = "Username for Mvision EDR platform"
    required_group.add_argument('-u', required=True, action='store', dest='username', help=arg_help, metavar="")

    arg_help = "Password for Mvision EDR platform"
    required_group.add_argument('-p', required=True, action='store', dest='password', help=arg_help, metavar="")

    arg_help = "Path to hunting file or folder"
    required_group.add_argument('-i', required=True, default="", action='store', dest='input', help=arg_help,
                        metavar="")

    arg_help = "Output format JSON or CSV, only applies if information output (-o) is set to file"
    parser.add_argument('-f', required=False, default="csv", action='store', dest='format', choices=['json','JSON','csv','CSV'], 
                        help=arg_help, metavar="")

    arg_help = "Data Center Location EU or US"
    parser.add_argument('-c', required=False, default="EU", action='store', dest='datacenter', choices=['eu','EU','us','US'], 
                        help=arg_help, metavar="")

    arg_help = "Information output screen or file"
    parser.add_argument('-o', required=False, default="screen", action='store', dest='output', choices=['screen', 'SCREEN', 'file', 'FILE'], 
                        help=arg_help, metavar="")

    parser.add_argument('--version', action='version', version='Carlos Munoz (carlos.munozgarrido@mcafee.com)\n%(prog)s 1.0 (13/11/2020)')

    return parser.parse_args()

def is_folder(input_value):
        # Check if input_value is folder or file
        if os.path.isdir(input_value):
            is_folder = True
        else:
            is_folder = False

        return is_folder

def check_query_status(query):

    def spinner(seconds):
        now = time.time()
        future = now + seconds
        char = "*"
        i = 0
        while time.time() < future:
            print('[{:50s}]'.format(char*i), end="\r")
            i += 1
            time.sleep(0.20)
        print('[{:50s}]'.format(" "*i), end="\r")
        return

    error_count = 0
    logger.info("[+] Proccesing query")
    while True:        
        try:
            status = query.get_query_status()
            if status == "READY" or error_count == 3:
                break
            else:
                #logger.info("[+] Proccesing query")
                #logger.info(query_value)
                spinner(10)
                #time.sleep(10)
        except Exception as error:
            error_count += 1

    if error_count == 3:
        raise ValueError('[!] Too many detected errors when checking status of the query')

    return query.get_query_lines()

def main():
    option = parseargs()

    datacenter = option.datacenter
    username = option.username
    password = option.password

    input_value = option.input 

    
    if input_value.endswith('\\') or input_value.endswith('/'):
        input_value = input_value[:-1]

    output_format = option.format
    output_stdout = option.output

    if not os.path.exists(input_value):
        logger.error("[¡] input value (file or folder) doesn't exists")
        sys.exit()

    try:
        mvedr = MvEDR(datacenter, username, password)
    except ValueError as error:
        logger.error(error)
        sys.exit()
    except Exception as error:
        logger.error(error)
        sys.exit()

    logger.info('[+] Successful authentication')


    if is_folder(input_value):
        xml_files = glob.glob(input_value + os.sep + '*.xml')
    else:
        xml_files = [input_value]
    
    for xml_file in xml_files:
        logger.info('[+] Processing file query {}'.format(xml_file))

        query = Query(mvedr)

        try:
            query.parse_xml(xml_file)
            logger.info(f'[+] Query name: {query.query_name}')
            logger.info(f'[+] Query Description: {query.query_description}')
        except Exception as error:
            logger.error ('[¡] Error parsing query file, check format')
            logger.error(error)
            continue
  
        try:
            query.execute_query()
        except Exception as error:
            logger.error('[!] Error sending query to Mvision EDR')
            logger.error(error)
            continue

 
        # Checking status of the query if Exception continue with next file in folder
        try:
            total_lines = check_query_status(query)
        except Exception as error:
            logger.error('[!] Error checking the status of the query')
            logger.error(error)
            continue


        logger.info('[+] Getting information')

        if output_stdout.upper() == "SCREEN":
            # If the choice is to show the information in the screen the format is always json
            if total_lines == 0:
                print('\n No system responded as a result of this query \n')
            else:
                for i in range(0, int(total_lines), PAGE_SIZE):
                    offset = i
                    limit  = offset + PAGE_SIZE
                    try:
                        results = query.get_offset_query_data(offset=i, limit=limit)
                    except Exception as error:
                        logger.error('[!] Error getting the query data')
                        logger.error(error)
                        break

                    logger.info("[+] Query result - values from {} to {}".format(offset, limit))
                    print
                    print('\n' + json.dumps(results) + '\n')

            logger.info('[+] End process for query')

        elif output_stdout.upper() == "FILE":
            # if the choice is to store the information on file the format can be json or csv
            try:
                query.obtain_query_data()
            except Exception as error:
                logger.error('[!] Error getting the query data')
                logger.error(error)
                continue

            try:
                query.get_query_data(output_format)
            except Exception as error:
                logger.error('[!] Error writting information to file')
                logger.error(error)
                continue

if __name__ == '__main__':
    main()