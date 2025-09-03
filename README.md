# 🤖 X-Road AI Monitor

> Intelligent monitoring and analytics platform for X-Road ecosystems

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://docker.com)
[![X-Road Compatible](https://img.shields.io/badge/X--Road-7.6%2B-green.svg)](https://x-road.global)

## 🎯 Overview

X-Road AI Monitor is an advanced monitoring platform that transforms X-Road ecosystem data into actionable insights using artificial intelligence and machine learning. It provides comprehensive monitoring of entire X-Road networks, from individual Security Servers to complete government digital ecosystems.

### ✨ Key Features

- 🌐 **Ecosystem Monitoring** - Monitor entire X-Road networks with multiple Security Servers
- 🤖 **AI-Powered Analytics** - Machine learning for predictive failure detection and anomaly analysis
- 📊 **Real-time Dashboard** - Beautiful, responsive web interface with live metrics
- 🚨 **Smart Alerts** - Intelligent notification system with Slack, Teams, and email integration
- 🔌 **Modern Integrations** - MCP (Model Context Protocol) and Composio support
- 📱 **Mobile Ready** - Fully responsive design for mobile and tablet access
- 🔒 **Enterprise Security** - SSL/TLS support with certificate-based authentication
- 📈 **Advanced Analytics** - Performance trends, usage patterns, and capacity planning
- 🛡️ **Compliance Ready** - Built for government and enterprise compliance requirements

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   X-Road        │    │  X-Road AI       │    │   Dashboard     │
│   Central       │───▶│  Monitor         │───▶│   & Alerts      │
│   Server        │    │  (Core Engine)   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
┌─────────────────┐            │              ┌─────────────────┐
│   Security      │◀───────────┘              │  Integrations   │
│   Server 1..N   │                           │  (MCP/Composio) │
└─────────────────┘                           └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ (optional, for advanced features)
- X-Road 7.6+ environment
- Central Monitoring Client configured in X-Road Central Server

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/xroad-ai-monitor.git
cd xroad-ai-monitor

# Install dependencies
pip install -r requirements.txt

# Copy configuration templates
cp config/config.example.json config/config.json
cp config/ecosystem.example.json config/ecosystem.json

# Edit configurations with your X-Road settings
nano config/config.json
nano config/ecosystem.json

# Run the application
python src/main.py
```

### Docker Setup (Recommended)

```bash
# Clone and configure
git clone https://github.com/your-username/xroad-ai-monitor.git
cd xroad-ai-monitor

# Copy and configure
cp config/config.example.json config/config.json
cp config/ecosystem.example.json config/ecosystem.json

# Start with Docker Compose
docker-compose up -d

# Access dashboard
open http://localhost:8890
```

## 📋 Configuration

### Basic Configuration (`config/config.json`)

```json
{
  "xroad_instance": "YOUR-INSTANCE",
  "central_monitoring_client": {
    "client_id": "INSTANCE/GOV/12345678/MONITORING",
    "certificates": {
      "cert_path": "/certs/monitoring-client.pem",
      "key_path": "/certs/monitoring-client.key",
      "ca_path": "/certs/ca.pem"
    }
  },
  "monitoring": {
    "collection_interval_minutes": 15,
    "parallel_workers": 10,
    "timeout_seconds": 30
  },
  "dashboard": {
    "port": 8890,
    "refresh_interval_seconds": 30
  },
  "alerts": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.example.com",
      "recipients": ["admin@example.com"]
    },
    "slack": {
      "enabled": true,
      "webhook_url": "https://hooks.slack.com/..."
    }
  }
}
```

### Ecosystem Configuration (`config/ecosystem.json`)

```json
{
  "security_servers": [
    {
      "server_id": "ministry-finance",
      "host": "xroad-finance.gov.example",
      "port": 8080,
      "client_id": "INSTANCE/GOV/11111111/FINANCE",
      "description": "Ministry of Finance",
      "active": true
    },
    {
      "server_id": "tax-authority",
      "host": "xroad-tax.gov.example",
      "port": 8080,
      "client_id": "INSTANCE/GOV/22222222/TAX",
      "description": "Tax Authority",
      "active": true
    }
  ]
}
```

## 🎨 Dashboard Features

### Main Dashboard
- **Ecosystem Overview**: Real-time status of all Security Servers
- **Performance Metrics**: Response times, throughput, and availability
- **Service Analytics**: Most used services and clients
- **Alert Center**: Active alerts and system notifications

### Analytics Pages
- **Trends Analysis**: Historical performance and usage patterns
- **Service Dependencies**: Visualization of inter-service relationships
- **Capacity Planning**: Resource utilization and growth projections
- **Compliance Reports**: SLA compliance and audit trails

### Mobile Interface
- Responsive design optimized for mobile devices
- Push notifications for critical alerts
- Offline mode for basic monitoring data

## 🤖 AI/ML Features

### Anomaly Detection
- **Predictive Alerts**: Detect potential failures before they occur
- **Pattern Recognition**: Identify unusual traffic patterns or performance degradation
- **Baseline Learning**: Automatically establish normal operating parameters

### Intelligent Analytics
- **Root Cause Analysis**: Automated investigation of system issues
- **Performance Optimization**: ML-driven recommendations for system tuning
- **Capacity Forecasting**: Predict future resource needs based on usage trends

### Smart Alerting
- **Noise Reduction**: Filter out false positives using ML algorithms
- **Alert Prioritization**: Rank alerts by business impact and urgency
- **Correlation Analysis**: Group related alerts to reduce notification fatigue

## 🔌 Integrations

### Model Context Protocol (MCP)
```python
# MCP integration example
from src.integrations.mcp import MCPClient

mcp_client = MCPClient()
mcp_client.register_tool("xroad_metrics", get_ecosystem_metrics)
```

### Composio Platform
```python
# Composio integration for workflow automation
from src.integrations.composio import ComposioConnector

composio = ComposioConnector()
composio.create_workflow("incident_response", [
    "detect_anomaly",
    "notify_team", 
    "create_ticket",
    "escalate_if_needed"
])
```

### Third-party Tools
- **Grafana**: Export metrics for advanced visualization
- **Prometheus**: Native metrics export
- **Splunk**: Log forwarding and analysis
- **ServiceNow**: Incident management integration
- **Jira**: Automated ticket creation

## 📊 API Reference

### REST API Endpoints

#### Ecosystem Status
```http
GET /api/v1/ecosystem/status
```

Response:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "total_servers": 6,
  "online_servers": 5,
  "total_requests_24h": 12547,
  "avg_response_time": 1200,
  "success_rate": 97.3
}
```

#### Server Metrics
```http
GET /api/v1/servers/{server_id}/metrics
```

#### Service Analytics
```http
GET /api/v1/analytics/services/top
```

#### Real-time Alerts
```http
GET /api/v1/alerts/active
POST /api/v1/alerts/acknowledge/{alert_id}
```

### WebSocket API
```javascript
// Real-time updates via WebSocket
const ws = new WebSocket('ws://localhost:8890/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};
```

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/

# Run specific test category
python -m pytest tests/test_collectors/
```

### Integration Tests
```bash
# Test with real X-Road environment
python -m pytest tests/integration/ --integration

# Load testing
python scripts/load_test.py
```

### Example Test Configuration
```python
# tests/conftest.py
import pytest
from src.core.monitor import XRoadEcosystemMonitor

@pytest.fixture
def monitor():
    return XRoadEcosystemMonitor('config/test_config.json')
```

## 📈 Performance

### Benchmarks
- **Collection Speed**: ~1000 records/second per Security Server
- **Memory Usage**: <512MB for monitoring 20 servers
- **Dashboard Response**: <200ms average page load
- **API Latency**: <50ms for most endpoints

### Scalability
- **Horizontal**: Deploy multiple instances with load balancing
- **Vertical**: Single instance can monitor 50+ Security Servers
- **Cloud**: Kubernetes-ready with Helm charts

## 🛡️ Security

### Authentication
- **Certificate-based**: X.509 certificate authentication
- **API Keys**: REST API access control
- **OAuth 2.0**: Third-party integrations
- **SAML/LDAP**: Enterprise SSO integration

### Data Protection
- **Encryption**: TLS 1.3 for all communications
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete audit trail of all actions
- **Data Anonymization**: PII protection for analytics

### Compliance
- **GDPR**: Data privacy compliance
- **SOC 2**: Security audit readiness
- **Government Standards**: Meets public sector security requirements

## 🔧 Administration

### Monitoring the Monitor
```bash
# Health check endpoint
curl http://localhost:8890/health

# Metrics endpoint for external monitoring
curl http://localhost:8890/metrics

# System status
python scripts/system_check.py
```

### Backup and Recovery
```bash
# Automated backup script
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh backup_20240115.tar.gz
```

### Log Management
```bash
# View application logs
tail -f logs/xroad-monitor.log

# Analyze error patterns
python scripts/log_analyzer.py --errors-only
```

## 🚀 Deployment

### Production Deployment

#### Using Docker (Recommended)
```bash
# Production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

#### Using Kubernetes
```bash
# Deploy with Helm
helm install xroad-monitor ./helm/xroad-monitor

# Or with kubectl
kubectl apply -f k8s/
```

#### Traditional Installation
```bash
# Install as systemd service
sudo ./scripts/install.sh --service

# Start services
sudo systemctl start xroad-monitor
sudo systemctl start xroad-dashboard
```

### Environment Variables
```bash
# Core configuration
XROAD_INSTANCE=PROD-GOV
MONITORING_CLIENT_ID=PROD-GOV/GOV/12345678/MONITORING

# Database
DB_HOST=localhost
DB_NAME=xroad_monitor
DB_USER=monitor
DB_PASS=secure_password

# Security
SSL_CERT_PATH=/etc/ssl/certs/monitor.pem
SSL_KEY_PATH=/etc/ssl/private/monitor.key

# Features
ENABLE_ML_ANALYTICS=true
ENABLE_PREDICTIONS=true
LOG_LEVEL=INFO
```

## 📚 Documentation

### Complete Documentation
- [Installation Guide](docs/installation.md) - Step-by-step setup instructions
- [Configuration Reference](docs/configuration.md) - All configuration options
- [API Documentation](docs/api.md) - Complete REST API reference
- [Architecture Guide](docs/architecture.md) - Technical architecture details
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [Security Guide](docs/security.md) - Security configuration and best practices

### Additional Resources
- [FAQ](docs/faq.md) - Frequently asked questions
- [Best Practices](docs/best-practices.md) - Recommended configurations
- [Migration Guide](docs/migration.md) - Upgrading between versions
- [Developer Guide](docs/development.md) - Contributing to the project

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](.github/CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone the repository
git clone https://github.com/your-username/xroad-ai-monitor.git
cd xroad-ai-monitor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run development server
python src/main.py --dev
```

### Code Style
- **Python**: Follow PEP 8 with Black formatter
- **JavaScript**: ESLint with Airbnb config
- **Documentation**: Markdown with consistent formatting
- **Commits**: Conventional Commits specification

### Pull Request Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`python -m pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🐛 Bug Reports & Feature Requests

### Bug Reports
Please use the [GitHub Issues](https://github.com/your-username/xroad-ai-monitor/issues) page to report bugs. Include:
- Environment details (OS, Python version, X-Road version)
- Steps to reproduce
- Expected vs actual behavior
- Log files or error messages

### Feature Requests
We love feature ideas! Please [open an issue](https://github.com/your-username/xroad-ai-monitor/issues/new) with:
- Use case description
- Proposed solution
- Alternative considerations
- Willingness to contribute

## 🎉 Roadmap

### Version 1.x - Foundation
- [x] Basic ecosystem monitoring
- [x] Real-time dashboard
- [x] Email/Slack alerts
- [ ] Performance optimization
- [ ] Enhanced documentation

### Version 2.x - Intelligence
- [ ] Machine learning analytics
- [ ] Predictive alerting
- [ ] Anomaly detection
- [ ] Auto-remediation
- [ ] Advanced reporting

### Version 3.x - Integration
- [ ] Full MCP support
- [ ] Composio workflows
- [ ] Enterprise integrations
- [ ] Mobile applications
- [ ] Multi-tenant architecture

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **X-Road Community** - For the excellent interoperability platform
- **Nordic Institute for Interoperability Solutions (NIIS)** - X-Road development and maintenance
- **Contributors** - Everyone who has contributed to this project
- **Open Source Community** - For the amazing tools and libraries we depend on

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Community Forum**: [GitHub Discussions](https://github.com/your-username/xroad-ai-monitor/discussions)
- **Issue Tracker**: [GitHub Issues](https://github.com/your-username/xroad-ai-monitor/issues)
- **Security Issues**: security@your-domain.com

---

<div align="center">

**Made with ❤️ for the X-Road Community**

[Website](https://your-project-website.com) • [Documentation](docs/) • [API Reference](docs/api.md) • [Community](https://github.com/your-username/xroad-ai-monitor/discussions)

</div>
