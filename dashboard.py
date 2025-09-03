#!/usr/bin/env python3
"""
Dashboard Web para Monitoramento X-Road
Interface simples para visualizar status dos serviços
"""

from flask import Flask, render_template, jsonify
import json
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

class DashboardData:
    def __init__(self, db_path="xroad_monitoring.db"):
        self.db_path = db_path
    
    def get_current_status(self):
        """Retorna status atual de todos os serviços"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s1.subsystem, s1.service, s1.status, s1.response_time, 
                   s1.timestamp, s1.error_message
            FROM service_status s1
            INNER JOIN (
                SELECT subsystem, service, MAX(timestamp) as max_timestamp
                FROM service_status
                GROUP BY subsystem, service
            ) s2 ON s1.subsystem = s2.subsystem 
                 AND s1.service = s2.service 
                 AND s1.timestamp = s2.max_timestamp
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        services = []
        for row in results:
            services.append({
                'subsystem': row[0],
                'service': row[1],
                'status': row[2],
                'response_time': row[3],
                'last_check': row[4],
                'error_message': row[5]
            })
        
        return services
    
    def get_stats_24h(self):
        """Estatísticas das últimas 24 horas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        yesterday = datetime.now() - timedelta(days=1)
        
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM service_status
            WHERE timestamp > ?
            GROUP BY status
        ''', (yesterday,))
        
        stats = dict(cursor.fetchall())
        conn.close()
        
        return stats
    
    def get_response_time_history(self, hours=24):
        """Histórico de tempo de resposta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT service, timestamp, response_time
            FROM service_status
            WHERE timestamp > ? AND status != 'DOWN'
            ORDER BY timestamp
        ''', (since,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Agrupa por serviço
        history = {}
        for service, timestamp, response_time in results:
            if service not in history:
                history[service] = []
            history[service].append({
                'timestamp': timestamp,
                'response_time': response_time
            })
        
        return history

dashboard_data = DashboardData()

@app.route('/')
def index():
    """Página principal do dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint para status atual"""
    services = dashboard_data.get_current_status()
    stats = dashboard_data.get_stats_24h()
    
    return jsonify({
        'services': services,
        'stats_24h': stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/history')
def api_history():
    """API endpoint para histórico"""
    history = dashboard_data.get_response_time_history()
    return jsonify(history)

# Template HTML inline (normalmente seria um arquivo separado)
@app.route('/template')
def get_template():
    """Retorna template HTML (para desenvolvimento)"""
    template_html = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>X-Road Monitor Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; margin-bottom: 10px; }
        .stat-label { color: #666; }
        .services { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .service-header { padding: 20px; border-bottom: 1px solid #eee; }
        .service-item { padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .service-item:last-child { border-bottom: none; }
        .service-name { font-weight: bold; }
        .service-subsystem { color: #666; font-size: 0.9em; }
        .status { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
        .status.UP { background: #d4edda; color: #155724; }
        .status.DOWN { background: #f8d7da; color: #721c24; }
        .status.SLOW { background: #fff3cd; color: #856404; }
        .response-time { color: #666; }
        .last-update { text-align: center; color: #666; margin-top: 20px; }
        .error-message { color: #dc3545; font-size: 0.9em; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>X-Road Monitor Dashboard</h1>
            <p>Monitoramento em tempo real dos serviços X-Road</p>
        </div>
        
        <div class="stats" id="stats">
            <!-- Stats serão inseridas via JavaScript -->
        </div>
        
        <div class="services">
            <div class="service-header">
                <h2>Status dos Serviços</h2>
            </div>
            <div id="services-list">
                <!-- Serviços serão inseridos via JavaScript -->
            </div>
        </div>
        
        <div class="last-update" id="last-update">
            Última atualização: --
        </div>
    </div>

    <script>
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    updateStats(data.stats_24h);
                    updateServices(data.services);
                    document.getElementById('last-update').textContent = 
                        'Última atualização: ' + new Date(data.timestamp).toLocaleString('pt-BR');
                })
                .catch(error => {
                    console.error('Erro ao carregar dados:', error);
                });
        }
        
        function updateStats(stats) {
            const statsHtml = `
                <div class="stat-card">
                    <div class="stat-number" style="color: #28a745;">${stats.UP || 0}</div>
                    <div class="stat-label">Serviços Online</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #dc3545;">${stats.DOWN || 0}</div>
                    <div class="stat-label">Serviços Offline</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #ffc107;">${stats.SLOW || 0}</div>
                    <div class="stat-label">Serviços Lentos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${(stats.UP || 0) + (stats.DOWN || 0) + (stats.SLOW || 0)}</div>
                    <div class="stat-label">Total de Checks (24h)</div>
                </div>
            `;
            document.getElementById('stats').innerHTML = statsHtml;
        }
        
        function updateServices(services) {
            const servicesHtml = services.map(service => {
                const errorHtml = service.error_message ? 
                    `<div class="error-message">Erro: ${service.error_message}</div>` : '';
                
                return `
                    <div class="service-item">
                        <div>
                            <div class="service-name">${service.service}</div>
                            <div class="service-subsystem">${service.subsystem}</div>
                            ${errorHtml}
                        </div>
                        <div style="text-align: right;">
                            <div class="status ${service.status}">${service.status}</div>
                            <div class="response-time">
                                ${service.response_time ? service.response_time.toFixed(2) + 'ms' : '--'}
                            </div>
                            <div style="font-size: 0.8em; color: #999;">
                                ${new Date(service.last_check).toLocaleTimeString('pt-BR')}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            
            document.getElementById('services-list').innerHTML = servicesHtml;
        }
        
        // Atualiza a cada 30 segundos
        updateDashboard();
        setInterval(updateDashboard, 30000);
    </script>
</body>
</html>
    """
    return template_html

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888)
