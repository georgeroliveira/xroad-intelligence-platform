#!/usr/bin/env python3
"""
Agente de IA Básico para Monitoramento X-Road
Versão inicial focada em health checks e alertas
"""

import requests
import sqlite3
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from dataclasses import dataclass

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceStatus:
    """Representa o status de um serviço X-Road"""
    subsystem: str
    service: str
    status: str  # 'UP', 'DOWN', 'SLOW'
    response_time: float
    timestamp: datetime
    error_message: Optional[str] = None

class XRoadMonitor:
    """Monitor básico para serviços X-Road"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.db_path = "xroad_monitoring.db"
        self._init_database()
        
    def _load_config(self, config_file: str) -> dict:
        """Carrega configurações do arquivo JSON"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Configurações padrão"""
        return {
            "xroad_server": "http://localhost:8080",
            "services": [
                {
                    "subsystem": "GOV/12345678/TestSystem",
                    "service": "testService"
                }
            ],
            "check_interval": 60,  # segundos
            "alert_threshold": 5000,  # ms
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your-email@gmail.com",
                "password": "your-password",
                "to_addresses": ["admin@yourorg.com"]
            }
        }
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subsystem TEXT NOT NULL,
                service TEXT NOT NULL,
                status TEXT NOT NULL,
                response_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")

class XRoadHealthChecker:
    """Realiza health checks nos serviços X-Road"""
    
    def __init__(self, xroad_server: str):
        self.xroad_server = xroad_server
        self.timeout = 10  # segundos
    
    def check_service(self, subsystem: str, service: str) -> ServiceStatus:
        """Verifica o status de um serviço específico"""
        start_time = time.time()
        
        try:
            # Exemplo de chamada para listMethods (ajuste conforme sua API)
            url = f"{self.xroad_server}/r1/{subsystem}/{service}/listMethods"
            
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={
                    'Accept': 'application/json',
                    'X-Road-Client': 'DEV/12345678/MonitoringAgent'
                }
            )
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                status = 'SLOW' if response_time > 3000 else 'UP'
                return ServiceStatus(
                    subsystem=subsystem,
                    service=service,
                    status=status,
                    response_time=response_time,
                    timestamp=datetime.now()
                )
            else:
                return ServiceStatus(
                    subsystem=subsystem,
                    service=service,
                    status='DOWN',
                    response_time=response_time,
                    timestamp=datetime.now(),
                    error_message=f"HTTP {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            return ServiceStatus(
                subsystem=subsystem,
                service=service,
                status='DOWN',
                response_time=self.timeout * 1000,
                timestamp=datetime.now(),
                error_message="Timeout"
            )
        except Exception as e:
            return ServiceStatus(
                subsystem=subsystem,
                service=service,
                status='DOWN',
                response_time=0,
                timestamp=datetime.now(),
                error_message=str(e)
            )

class AlertManager:
    """Gerencia alertas e notificações"""
    
    def __init__(self, config: dict):
        self.config = config
        self.email_config = config.get('email', {})
    
    def send_alert(self, alert_type: str, message: str):
        """Envia alerta por email se configurado"""
        logger.warning(f"ALERT [{alert_type}]: {message}")
        
        if self.email_config.get('enabled', False):
            self._send_email(alert_type, message)
    
    def _send_email(self, alert_type: str, message: str):
        """Envia email de alerta"""
        try:
            msg = MIMEText(f"X-Road Alert: {message}")
            msg['Subject'] = f"X-Road {alert_type} Alert"
            msg['From'] = self.email_config['username']
            msg['To'] = ', '.join(self.email_config['to_addresses'])
            
            server = smtplib.SMTP(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            )
            server.starttls()
            server.login(
                self.email_config['username'],
                self.email_config['password']
            )
            server.send_message(msg)
            server.quit()
            logger.info("Alert email sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

class XRoadAgent:
    """Agente principal que coordena todas as atividades"""
    
    def __init__(self, config_file: str = "config.json"):
        self.monitor = XRoadMonitor(config_file)
        self.health_checker = XRoadHealthChecker(
            self.monitor.config['xroad_server']
        )
        self.alert_manager = AlertManager(self.monitor.config)
        self.running = False
    
    def start(self):
        """Inicia o agente de monitoramento"""
        logger.info("Starting X-Road AI Agent...")
        self.running = True
        
        while self.running:
            try:
                self._monitoring_cycle()
                time.sleep(self.monitor.config['check_interval'])
            except KeyboardInterrupt:
                logger.info("Stopping agent...")
                self.running = False
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                time.sleep(10)  # Espera antes de tentar novamente
    
    def _monitoring_cycle(self):
        """Executa um ciclo completo de monitoramento"""
        logger.info("Starting monitoring cycle...")
        
        for service_config in self.monitor.config['services']:
            status = self.health_checker.check_service(
                service_config['subsystem'],
                service_config['service']
            )
            
            # Salva no banco
            self._save_status(status)
            
            # Verifica se precisa alertar
            self._check_alerts(status)
            
            logger.info(
                f"Service {status.service}: {status.status} "
                f"({status.response_time:.2f}ms)"
            )
    
    def _save_status(self, status: ServiceStatus):
        """Salva status no banco de dados"""
        conn = sqlite3.connect(self.monitor.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO service_status 
            (subsystem, service, status, response_time, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            status.subsystem,
            status.service,
            status.status,
            status.response_time,
            status.error_message
        ))
        
        conn.commit()
        conn.close()
    
    def _check_alerts(self, status: ServiceStatus):
        """Verifica se deve disparar alertas"""
        threshold = self.monitor.config['alert_threshold']
        
        if status.status == 'DOWN':
            self.alert_manager.send_alert(
                'SERVICE_DOWN',
                f"Service {status.service} is DOWN. Error: {status.error_message}"
            )
        elif status.status == 'SLOW':
            self.alert_manager.send_alert(
                'SLOW_RESPONSE',
                f"Service {status.service} is slow: {status.response_time:.2f}ms"
            )
    
    def get_dashboard_data(self) -> dict:
        """Retorna dados para dashboard"""
        conn = sqlite3.connect(self.monitor.db_path)
        cursor = conn.cursor()
        
        # Status atual dos serviços
        cursor.execute('''
            SELECT subsystem, service, status, response_time, timestamp
            FROM service_status
            WHERE id IN (
                SELECT MAX(id)
                FROM service_status
                GROUP BY subsystem, service
            )
        ''')
        current_status = cursor.fetchall()
        
        # Estatísticas das últimas 24h
        yesterday = datetime.now() - timedelta(days=1)
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM service_status
            WHERE timestamp > ?
            GROUP BY status
        ''', (yesterday,))
        stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'current_status': current_status,
            'stats_24h': dict(stats),
            'last_update': datetime.now().isoformat()
        }

def main():
    """Função principal"""
    agent = XRoadAgent()
    agent.start()

if __name__ == "__main__":
    main()
