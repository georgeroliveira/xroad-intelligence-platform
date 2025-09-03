# Agente de IA para Monitoramento X-Road

## Pré-requisitos

```bash
# Instalar Python 3.8+
python3 --version

# Instalar dependências
pip install requests flask sqlite3
```

## Instalação

1. **Crie o diretório do projeto:**
```bash
mkdir xroad-ai-agent
cd xroad-ai-agent
```

2. **Salve os arquivos:**
   - `agent.py` - Código principal do agente
   - `dashboard.py` - Dashboard web
   - `config.json` - Configurações

3. **Configure o arquivo `config.json`:**
   - Ajuste `xroad_server` com seu servidor X-Road
   - Configure os `services` que deseja monitorar
   - Configure alertas por email se necessário

## Como usar

### 1. Iniciar o Agente de Monitoramento

```bash
python3 agent.py
```

O agente irá:
- Verificar serviços a cada 60 segundos (configurável)
- Salvar dados no SQLite (`xroad_monitoring.db`)
- Enviar alertas quando serviços ficam offline ou lentos

### 2. Iniciar o Dashboard (em outro terminal)

```bash
python3 dashboard.py
```

Acesse: http://localhost:8888

### 3. Estrutura de Arquivos

```
xroad-ai-agent/
├── agent.py              # Agente principal
├── dashboard.py           # Interface web
├── config.json            # Configurações
├── xroad_monitoring.db    # Banco de dados (criado automaticamente)
└── requirements.txt       # Dependências Python
```

## Funcionalidades Básicas Implementadas

### ✅ Health Check Automatizado
- Verifica se serviços respondem
- Mede tempo de resposta
- Detecta timeouts e erros

### ✅ Banco de Dados
- Histórico de status dos serviços
- Métricas de performance
- Log de alertas

### ✅ Sistema de Alertas
- Alertas por email (opcional)
- Logs detalhados
- Categorização de problemas

### ✅ Dashboard Web
- Status em tempo real
- Estatísticas das últimas 24h
- Interface responsiva

## Configuração Avançada

### Alertas por Email
```json
"email": {
  "enabled": true,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "username": "monitor@empresa.com",
  "password": "senha-app-gmail",
  "to_addresses": ["admin@empresa.com"]
}
```

### Múltiplos Serviços
```json
"services": [
  {
    "subsystem": "GOV/12345678/Sistema1",
    "service": "consultarDados"
  },
  {
    "subsystem": "GOV/87654321/Sistema2", 
    "service": "validarDocumento"
  }
]
```

## Próximos Passos (Expansões Futuras)

### 🔄 Funcionalidades Intermediárias
- Dashboard com gráficos históricos
- Integração com Slack
- Monitoramento de certificados
- Testes de carga automáticos

### 🚀 Funcionalidades Avançadas
- Machine Learning para previsão de falhas
- Descoberta automática de novos serviços
- Otimização automática de performance
- Integração com ferramentas de DevOps

## Troubleshooting

### Problemas Comuns

**1. Erro de conexão com X-Road:**
- Verifique se o servidor X-Road está acessível
- Confirme as URLs dos serviços
- Verifique permissões de rede

**2. Banco de dados não criado:**
- Verifique permissões de escrita no diretório
- Confirme instalação do SQLite

**3. Alertas não enviados:**
- Verifique configuração SMTP
- Use senhas de aplicativo (Gmail)
- Teste conectividade com servidor email

### Logs e Debug

```bash
# Ver logs em tempo real
tail -f xroad_agent.log

# Verificar banco de dados
sqlite3 xroad_monitoring.db
.tables
SELECT * FROM service_status ORDER BY timestamp DESC LIMIT 10;
```

## Arquitetura do Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   X-Road        │◄──►│  Agente de IA    │◄──►│   Dashboard     │
│   Servers       │    │  (Monitor)       │    │   Web           │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  SQLite Database │
                       │  + Alert System  │
                       └──────────────────┘
```

Este é um agente básico mas funcional. À medida que você usar, pode identificar necessidades específicas e expandir gradualmente as funcionalidades!
