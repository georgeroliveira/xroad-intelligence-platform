#!/usr/bin/env python3
"""
Agente X-Road Integrado com X-Road Metrics Oficial
Versão avançada que utiliza as APIs oficiais do X-Road
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import sqlite3
import json
import logging
from typing import Dict, List, Optional
import time
from dataclasses import dataclass
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class XRoadOperationalData:
    """Dados operacionais do X-Road Metrics"""
    service_id: str
    client_id: str
    producer_id: str
    request_timestamp: datetime
    response_timestamp: Optional[datetime]
    request_size: int
    response_size: int
    success: bool
    error_message: Optional[str] = None
    request_duration: Optional[int] = None

class XRoadMetricsClient:
    """Cliente para X-Road Metrics oficial"""
    
    def __init__(self, config: dict):
        self.config = config
        self.xroad_server = config['xroad_server']
        self.client_id = config['client_id']
        self.timeout = config.get('timeout', 30)
        
        # Headers padrão para requisições X-Road
        self.soap_headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '',
            'X-Road-Client': self.client_id
        }
    
    def get_operational_data(self, records_from: datetime, records_to: datetime, 
                           client_filter: Optional[str] = None) -> List[XRoadOperationalData]:
        """
        Busca dados operacionais usando getSecurityServerOperationalData
        """
        soap_request = self._build_operational_data_request(records_from, records_to, client_filter)
        
        try:
            response = requests.post(
                self.xroad_server,
                data=soap_request,
                headers=self.soap_headers,
                timeout=self.timeout,
                verify=self.config.get('ssl_verify', True)
            )
            
            if response.status_code == 200:
                return self._parse_operational_data_response(response.text)
            else:
                logger.error(f"Erro ao buscar dados operacionais: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro na requisição de dados operacionais: {e}")
            return []
    
    def get_health_data(self, server_id: Optional[str] = None) -> Dict:
        """
        Busca dados de saúde usando getSecurityServerHealthData
        """
        soap_request = self._build_health_data_request(server_id)
        
        try:
            response = requests.post(
                self.xroad_server,
                data=soap_request,
                headers=self.soap_headers,
                timeout=self.timeout,
                verify=self.config.get('ssl_verify', True)
            )
            
            if response.status_code == 200:
                return self._parse_health_data_response(response.text)
            else:
                logger.error(f"Erro ao buscar dados de saúde: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro na requisição de dados de saúde: {e}")
            return {}
    
    def _build_operational_data_request(self, records_from: datetime, records_to: datetime, 
                                      client_filter: Optional[str] = None) -> str:
        """Constrói requisição SOAP para dados operacionais"""
        
        # Converte timestamps para Unix timestamp em segundos
        from_ts = int(records_from.timestamp())
        to_ts = int(records_to.timestamp())
        
        client_filter_xml = ""
        if client_filter:
            client_filter_xml = f"""
            <m:client>
                <id:xRoadInstance>{self.config.get('xroad_instance', 'DEV')}</id:xRoadInstance>
                <id:memberClass>{client_filter.split('/')[1]}</id:memberClass>
                <id:memberCode>{client_filter.split('/')[2]}</id:memberCode>
            </m:client>
            """
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope 
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:id="http://x-road.eu/xsd/identifiers" 
    xmlns:m="http://x-road.eu/xsd/monitoring" 
    xmlns:xrd="http://x-road.eu/xsd/xroad.xsd">
    <SOAP-ENV:Header>
        <xrd:client id:objectType="MEMBER">
            <id:xRoadInstance>{self.config.get('xroad_instance', 'DEV')}</id:xRoadInstance>
            <id:memberClass>{self.client_id.split('/')[1]}</id:memberClass>
            <id:memberCode>{self.client_id.split('/')[2]}</id:memberCode>
        </xrd:client>
        <xrd:service id:objectType="SERVICE">
            <id:xRoadInstance>{self.config.get('xroad_instance', 'DEV')}</id:xRoadInstance>
            <id:memberClass>GOV</id:memberClass>
            <id:memberCode>MONITORING</id:memberCode>
            <id:serviceCode>getSecurityServerOperationalData</id:serviceCode>
        </xrd:service>
        <xrd:id>{datetime.now().strftime('%Y%m%d%H%M%S')}</xrd:id>
        <xrd:protocolVersion>4.0</xrd:protocolVersion>
    </SOAP-ENV:Header>
    <SOAP-ENV:Body>
        <m:getSecurityServerOperationalData>
            <m:searchCriteria>
                <m:recordsFrom>{from_ts}</m:recordsFrom>
                <m:recordsTo>{to_ts}</m:recordsTo>
                {client_filter_xml}
            </m:searchCriteria>
        </m:getSecurityServerOperationalData>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""
    
    def _build_health_data_request(self, server_id: Optional[str] = None) -> str:
        """Constrói requisição SOAP para dados de saúde"""
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope 
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:id="http://x-road.eu/xsd/identifiers" 
    xmlns:m="http://x-road.eu/xsd/monitoring" 
    xmlns:xrd="http://x-road.eu/xsd/xroad.xsd">
    <SOAP-ENV:Header>
        <xrd:client id:objectType="MEMBER">
            <id:xRoadInstance>{self.config.get('xroad_instance', 'DEV')}</id:xRoadInstance>
            <id:memberClass>{self.client_id.split('/')[1]}</id:memberClass>
            <id:memberCode>{self.client_id.split('/')[2]}</id:memberCode>
        </xrd:client>
        <xrd:service id:objectType="SERVICE">
            <id:xRoadInstance>{self.config.get('xroad_instance', 'DEV')}</id:xRoadInstance>
            <id:memberClass>GOV</id:memberClass>
            <id:memberCode>MONITORING</id:memberCode>
            <id:serviceCode>getSecurityServerHealthData</id:serviceCode>
        </xrd:service>
        <xrd:id>{datetime.now().strftime('%Y%m%d%H%M%S')}</xrd:id>
        <xrd:protocolVersion>4.0</xrd:protocolVersion>
    </SOAP-ENV:Header>
    <SOAP-ENV:Body>
        <m:getSecurityServerHealthData/>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""
    
    def _parse_operational_data_response(self, response_xml: str) -> List[XRoadOperationalData]:
        """Parse da resposta XML de dados operacionais"""
        operational_data = []
        
        try:
            root = ET.fromstring(response_xml)
            
            # Namespace para parsing
            ns = {
                'm': 'http://x-road.eu/xsd/monitoring',
                'id': 'http://x-road.eu/xsd/identifiers'
            }
            
            records = root.findall('.//m:operationalDataRecords/m:operationalDataRecord', ns)
            
            for record in records:
                try:
                    service_elem = record.find('.//m:serviceXRoadRequestId', ns)
                    client_elem = record.find('.//m:clientXRoadRequestId', ns)
                    
                    request_ts_elem = record.find('.//m:requestInTs', ns)
                    response_ts_elem = record.find('.//m:responseOutTs', ns)
                    
                    request_size_elem = record.find('.//m:requestSize', ns)
                    response_size_elem = record.find('.//m:responseSize', ns)
                    
                    succeeded_elem = record.find('.//m:succeeded', ns)
                    fault_elem = record.find('.//m:faultString', ns)
                    
                    # Extrai dados
                    service_id = service_elem.text if service_elem is not None else "Unknown"
                    client_id = client_elem.text if client_elem is not None else "Unknown"
                    
                    request_ts = None
                    if request_ts_elem is not None:
                        request_ts = datetime.fromtimestamp(int(request_ts_elem.text) / 1000)
                    
                    response_ts = None
                    if response_ts_elem is not None:
                        response_ts = datetime.fromtimestamp(int(response_ts_elem.text) / 1000)
                    
                    request_size = int(request_size_elem.text) if request_size_elem is not None else 0
                    response_size = int(response_size_elem.text) if response_size_elem is not None else 0
                    
                    success = succeeded_elem.text.lower() == 'true' if succeeded_elem is not None else False
                    error_message = fault_elem.text if fault_elem is not None else None
                    
                    # Calcula duração
                    duration = None
                    if request_ts and response_ts:
                        duration = int((response_ts - request_ts).total_seconds() * 1000)
                    
                    operational_data.append(XRoadOperationalData(
                        service_id=service_id,
                        client_id=client_id,
                        producer_id="Unknown",  # Extrair do XML se disponível
                        request_timestamp=request_ts,
                        response_timestamp=response_ts,
                        request_size=request_size,
                        response_size=response_size,
                        success=success,
                        error_message=error_message,
                        request_duration=duration
                    ))
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar registro operacional: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse da resposta operacional: {e}")
        
        return operational_data
    
    def _parse_health_data_response(self, response_xml: str) -> Dict:
        """Parse da resposta XML de dados de saúde"""
        health_data = {}
        
        try:
            root = ET.fromstring(response_xml)
            
            ns = {'m': 'http://x-road.eu/xsd/monitoring'}
            
            # Dados gerais de saúde
            startup_ts_elem = root.find('.//m:monitoringStartupTimestamp', ns)
            if startup_ts_elem is not None:
                health_data['monitoringStartupTimestamp'] = int(startup_ts_elem.text)
            
            statistics_period_elem = root.find('.//m:statisticsPeriodSeconds', ns)
            if statistics_period_elem is not None:
                health_data['statisticsPeriodSeconds'] = int(statistics_period_elem.text)
            
            # Dados de serviços
            services = []
            service_events = root.findall('.//m:servicesEvents/m:serviceEvents', ns)
            
            for service_event in service_events:
                service_data = {}
                
                service_code_elem = service_event.find('.//m:serviceCode', ns)
                if service_code_elem is not None:
                    service_data['serviceCode'] = service_code_elem.text
                
                last_success_elem = service_event.find('.//m:lastSuccessfulRequestTimestamp', ns)
                if last_success_elem is not None:
                    service_data['lastSuccessfulRequestTimestamp'] = int(last_success_elem.text)
                
                last_failure_elem = service_event.find('.//m:lastUnsuccessfulRequestTimestamp', ns)
                if last_failure_elem is not None:
                    service_data['lastUnsuccessfulRequestTimestamp'] = int(last_failure_elem.text)
                
                # Estatísticas do último período
                stats_elem = service_event.find('.//m:lastPeriodStatistics', ns)
                if stats_elem is not None:
                    stats = {}
                    
                    success_count_elem = stats_elem.find('.//m:successfulRequestCount', ns)
                    if success_count_elem is not None:
                        stats['successfulRequestCount'] = int(success_count_elem.text)
                    
                    failure_count_elem = stats_elem.find('.//m:unsuccessfulRequestCount', ns)
                    if failure_count_elem is not None:
                        stats['unsuccessfulRequestCount'] = int(failure_count_elem.text)
                    
                    avg_duration_elem = stats_elem.find('.//m:requestMinDuration', ns)
                    if avg_duration_elem is not None:
                        stats['avgDuration'] = float(avg_duration_elem.text)
                    
                    service_data['lastPeriodStatistics'] = stats
                
                services.append(service_data)
            
            health_data['services'] = services
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse da resposta de saúde: {e}")
        
        return health_data

class EnhancedXRoadAgent:
    """Agente X-Road integrado com X-Road Metrics oficial"""
    
    def __init__(self, config_file: str = "xroad_metrics_config.json"):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.metrics_client = XRoadMetricsClient(self.config['xroad_metrics'])
        self.db_path = self.config.get('database', {}).get('path', 'xroad_enhanced.db')
        
        # Conecta com X-Road Metrics database se configurado
        self.postgres_config = self.config.get('xroad_metrics_db')
        self.postgres_conn = None
        if self.postgres_config:
            self._connect_to_xroad_metrics_db()
        
        self._init_local_database()
        
        logger.info("Enhanced X-Road Agent inicializado com X-Road Metrics")
    
    def _connect_to_xroad_metrics_db(self):
        """Conecta ao banco PostgreSQL do X-Road Metrics"""
        try:
            self.postgres_conn = psycopg2.connect(
                host=self.postgres_config['host'],
                database=self.postgres_config['database'],
                user=self.postgres_config['user'],
                password=self.postgres_config['password'],
                port=self.postgres_config.get('port', 5432)
            )
            logger.info("Conectado ao banco X-Road Metrics")
        except Exception as e:
            logger.error(f"Erro ao conectar com X-Road Metrics DB: {e}")
    
    def _init_local_database(self):
        """Inicializa banco local para cache e análises"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela para dados operacionais
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operational_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                client_id TEXT NOT NULL,
                producer_id TEXT,
                request_timestamp DATETIME,
                response_timestamp DATETIME,
                request_size INTEGER,
                response_size INTEGER,
                success BOOLEAN,
                error_message TEXT,
                request_duration INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para dados de saúde
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_code TEXT NOT NULL,
                last_successful_request DATETIME,
                last_unsuccessful_request DATETIME,
                successful_count INTEGER,
                unsuccessful_count INTEGER,
                avg_duration REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_operational_service ON operational_data(service_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_operational_timestamp ON operational_data(request_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_service ON health_data(service_code)')
        
        conn.commit()
        conn.close()
    
    def collect_operational_data(self, hours_back: int = 1):
        """Coleta dados operacionais das últimas N horas"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        logger.info(f"Coletando dados operacionais de {start_time} até {end_time}")
        
        # Busca dados via API oficial
        operational_data = self.metrics_client.get_operational_data(start_time, end_time)
        
        if operational_data:
            self._store_operational_data(operational_data)
            logger.info(f"Coletados {len(operational_data)} registros operacionais")
        else:
            logger.warning("Nenhum dado operacional coletado")
        
        return operational_data
    
    def collect_health_data(self):
        """Coleta dados de saúde atuais"""
        logger.info("Coletando dados de saúde")
        
        health_data = self.metrics_client.get_health_data()
        
        if health_data and 'services' in health_data:
            self._store_health_data(health_data['services'])
            logger.info(f"Coletados dados de saúde de {len(health_data['services'])} serviços")
        else:
            logger.warning("Nenhum dado de saúde coletado")
        
        return health_data
    
    def _store_operational_data(self, operational_data: List[XRoadOperationalData]):
        """Armazena dados operacionais no banco local"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for data in operational_data:
            cursor.execute('''
                INSERT OR IGNORE INTO operational_data 
                (service_id, client_id, producer_id, request_timestamp, response_timestamp,
                 request_size, response_size, success, error_message, request_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.service_id, data.client_id, data.producer_id,
                data.request_timestamp, data.response_timestamp,
                data.request_size, data.response_size, data.success,
                data.error_message, data.request_duration
            ))
        
        conn.commit()
        conn.close()
    
    def _store_health_data(self, services: List[Dict]):
        """Armazena dados de saúde no banco local"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for service in services:
            stats = service.get('lastPeriodStatistics', {})
            
            cursor.execute('''
                INSERT INTO health_data 
                (service_code, last_successful_request, last_unsuccessful_request,
                 successful_count, unsuccessful_count, avg_duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                service.get('serviceCode'),
                datetime.fromtimestamp(service.get('lastSuccessfulRequestTimestamp', 0) / 1000) 
                    if service.get('lastSuccessfulRequestTimestamp') else None,
                datetime.fromtimestamp(service.get('lastUnsuccessfulRequestTimestamp', 0) / 1000) 
                    if service.get('lastUnsuccessfulRequestTimestamp') else None,
                stats.get('successfulRequestCount', 0),
                stats.get('unsuccessfulRequestCount', 0),
                stats.get('avgDuration', 0.0)
            ))
        
        conn.commit()
        conn.close()
    
    def get_service_analytics(self, service_id: str = None, days: int = 7) -> Dict:
        """Gera analytics de um serviço ou todos os serviços"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(days=days)
        
        if service_id:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_requests,
                    AVG(request_duration) as avg_duration,
                    MIN(request_duration) as min_duration,
                    MAX(request_duration) as max_duration,
                    AVG(request_size) as avg_request_size,
                    AVG(response_size) as avg_response_size
                FROM operational_data 
                WHERE service_id = ? AND request_timestamp > ?
            ''', (service_id, since))
        else:
            cursor.execute('''
                SELECT 
                    service_id,
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_requests,
                    AVG(request_duration) as avg_duration
                FROM operational_data 
                WHERE request_timestamp > ?
                GROUP BY service_id
                ORDER BY total_requests DESC
            ''', (since,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def start_monitoring_loop(self, interval_minutes: int = 15):
        """Inicia loop de monitoramento contínuo"""
        logger.info(f"Iniciando loop de monitoramento (intervalo: {interval_minutes} min)")
        
        while True:
            try:
                # Coleta dados operacionais das últimas 2 horas
                self.collect_operational_data(hours_back=2)
                
                # Coleta dados de saúde atuais
                self.collect_health_data()
                
                # Aguarda próximo ciclo
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Interrompendo monitoramento...")
                break
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente

def main():
    """Função principal"""
    agent = EnhancedXRoadAgent()
    
    # Teste inicial
    logger.info("Executando coleta de teste...")
    operational_data = agent.collect_operational_data(hours_back=24)
    health_data = agent.collect_health_data()
    
    # Analytics de exemplo
    analytics = agent.get_service_analytics(days=1)
    logger.info(f"Analytics: {analytics}")
    
    # Inicia monitoramento contínuo
    agent.start_monitoring_loop()

if __name__ == "__main__":
    main()
