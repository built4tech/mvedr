import requests
import json
import sys
import os
import time
import xml.etree.ElementTree as ET
import argparse
import glob
from common import logger

# Definition of Global variables

# Current Path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Maximum number of returned lines per page
PAGE_SIZE = 25

class MvEDR():
    def __init__(self, region, user, password):
        self.api_endpoints = {
                             'login': '/identity/v1/login',
                             'rt_search': '/active-response/api/v1/searches',
                             'rt_status': '/active-response/api/v1/searches/{}/status',
                             'rt_getdata': '/active-response/api/v1/searches/{}/results?$offset={}&$limit={}'
                             }
        if region == 'EU':
            self.base_endpoint = 'https://api.soc.eu-central-1.mcafee.com'
        elif region =='US':
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

def parse_xml(xml_file):

    def sanitize(line):       
        line = ' '.join(line.split())
        return line

    try:
        tree  = ET.parse(xml_file)
        query_structure = tree.getroot()

        query = {}

        query_name        = query_structure.find('name').text
        query_description = query_structure.find('description').text

        projections = sanitize(query_structure.find('projections').text)
        condition  = sanitize(query_structure.find('condition').text)
        aggregated  = query_structure.find('aggregated').text

        query['projections'] = json.loads(projections)
        query['condition']  = json.loads(condition)
        query['aggregated']  = json.loads(aggregated)

    except Exception as error:
        raise

    return (query_name, query_description, query)

def parseargs():
    '''
    Description: Function in charge of the CLI parameters
    Input:       No input
    Output:      Parsed arguments
    '''
    description = 'Set parameters for McAfee Mvision EDR search'
    prog = 'mvedr-search.py'
    usage = '\nmvedr-search.py -u Username -p Password -i file_name or folder [-o output format]'
    epilog = 'Carlos Munoz (carlos.munozgarrido@mcafee.com)\n%(prog)s 1.0 (13/11/2020)'

    parser = argparse.ArgumentParser(epilog=epilog, usage=usage, prog=prog, description=description, formatter_class=argparse.RawTextHelpFormatter)

    auth_group = parser.add_argument_group("Required parameters")

    
    arg_help = "Username for Mvision EDR platform"
    auth_group.add_argument('-u', required=True, action='store', dest='username', help=arg_help, metavar="")

    arg_help = "Password for Mvision EDR platform"
    auth_group.add_argument('-p', required=True, action='store', dest='password', help=arg_help, metavar="")

    arg_help = "Path to file or folder"
    auth_group.add_argument('-i', required=True, default="", action='store', dest='input', help=arg_help,
                        metavar="")

    arg_help = "Output format"
    parser.add_argument('-o', required=False, default="json", action='store', dest='output', choices=['json', 'csv', 'pdf'], 
                        help=arg_help, metavar="")

    arg_help = "Data Center Location"
    parser.add_argument('-c', required=False, default="EU", action='store', dest='datacenter', choices=['EU', 'US'], 
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

def check_query_status(id, mvedr):

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
            query_value = mvedr.query_status(id)
            status = query_value['status']
            if status == "FINISHED" or error_count == 3:
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

    return query_value



def main():
    option = parseargs()

    datacenter = option.datacenter
    username = option.username
    password = option.password

    input_value = option.input 

    
    if input_value.endswith('\\') or input_value.endswith('/'):
        input_value = input_value[:-1]

    output_value = option.output

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

    logger.info('[+] Autenticación realizada')


    if is_folder(input_value):
        xml_files = glob.glob(input_value + os.sep + '*.xml')
    else:
        xml_files = [input_value]
    
    for xml_file in xml_files:
        logger.info('[+] Processing file query {}'.format(xml_file))

        # Parsing XML file if Exception continue with next file in folder
        try:
            (query_name, query_description, query) = parse_xml(xml_file)
        except Exception as error:
            logger.error ('[¡] Error parsing query file, check format')
            continue
            
        # Sending query to Mvision EDR if Exception continue with next file in folder
        logger.info('[+] Sending query {} to Mvision EDR'.format(query_name))
        logger.info('[+] Query Description: \n\t{}'.format(query_description))

        try:
            query_request = mvedr.query(query)
        except Exception as error:
            logger.error('[!] Error sending query to Mvision EDR')
            continue

        # Obtaining query Identificator if Exception continue with next file in folder
        try:
            id = query_request['id']
        except Exception as error:
            logger.error('[¡] Error obtaining the identificator of the query')
            continue

        # Checking status of the query if Exceptioncontinue with next file in folder
        try:
            query_value = check_query_status(id, mvedr)
        except Exception as error:
            logger.error(error)
            continue

        logger.info('[+] Query finish')
    
        logger.info('[+] Getting information')

        # Getting the total number of returned lines
        total_lines = query_value['results']

        # Code to go through the returned content
        for i in range(0, int(total_lines), PAGE_SIZE):
            offset = i
            limit  = offset + page
            try:
                results = mvedr.getQueryData(id, offset=i, limit=limit)
            except Exception as error:
                logger.error(error)
                break

            logger.info("[+] Query result - values from {} to {}".format(offset, limit))
            logger.info(results)

        logger.info('[+] End process for query')

if __name__ == '__main__':
    main()