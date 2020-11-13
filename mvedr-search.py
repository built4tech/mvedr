import requests
import json
import sys
import os
import time
import logging
import xml.etree.ElementTree as ET
from credenciales import user, password

# Path actual
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Fichero con consulta XML
XMLFILE = 'hunting' + os.sep + 'service_crashed.xml'

# Configure local logger
# Enable logging, this will also direct built-in DXL log messages.
# See - https://docs.python.org/2/howto/logging-cookbook.html
log_formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


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
            print(r.json())
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
        logger.error ('[¡] Error parseando el fichero xml de consulta')
        logger.error(error)
        sys.exit()

    return (query_name, query_description, query)

if __name__ == '__main__':
 
    xmlfile_path = CURRENT_DIR + os.sep + XMLFILE
    (query_name, query_description, query) = parse_xml(xmlfile_path)

    try:
        EDR = MvEDR('EU', user, password)
    except ValueError as error:
        logger.error(error)
        sys.exit()
    except Exception as error:
        logger.error(error)
        sys.exit()

    logger.info('[+] Autenticación realizada')

    try:
        query_request = EDR.query(query)
    except Exception as error:
        logger.error(error)
        sys.exit()

    logger.info('[+] Ejecutando consulta {}'.format(query_name))
    logger.info('[+] Descripción \t{}'.format(query_description))
    logger.info(query_request)

    try:
        id = query_request['id']
    except Exception as error:
        logger.error('[¡] Error al obtener el identificador de la consulta')
        logger.error(error)
        sys.exit()
    
    error_count = 0
    while True:        
        try:
            query_value = EDR.query_status(id)
            status = query_value['status']
            if status == "FINISHED" or error_count == 3:
                break
            else:
                logger.info("[+] Consulta en proceso")
                logger.info(query_value)
                time.sleep(10)
        except Exception as error:
            logger.error(error)
            error_count += 1
            #sys.exit()

    if error_count == 3:
        logger.error('[!] Demasidados errores detectados al comprobar el estado de la consulta')
        sys.exit()

    logger.info('[+] Consulta finalizada')
    logger.info(query_value)
    logger.info('[+] Obteniendo information')
    # Obteniendo el volumen de lineas devueltas
    total_lines = query_value['results']

    # Rutina para recorrer el total de lineas de forma paginas 
    page = 25
    for i in range(0, int(total_lines), page):
        offset = i
        limit  = offset + page
        try:
            results = EDR.getQueryData(id, offset=i, limit=limit)
        except Exception as error:
            logger.error(error)

        logger.info("[+] Resultados - valores desde {} a {}".format(offset, limit))
        logger.info(results)

    logger.info('[+] Fin del proceso')

 



