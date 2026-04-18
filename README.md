# 🌱 PBL1 — Sistema de Monitoramento de Estufa

Monitoramento inteligente de ambientes agrícolas em tempo real usando a Stack MING + Stack Web.

> **Problema:** Pequenas variações de temperatura, umidade ou luminosidade podem comprometer toda uma produção vegetal. Este sistema monitora continuamente 4 variáveis ambientais e dispara alertas automáticos quando qualquer valor sai da faixa segura para as plantas.

---

## 📋 Sumário

- [Stack utilizada](#stack-utilizada)
- [Arquitetura](#arquitetura)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Variáveis monitoradas](#variáveis-monitoradas)
- [Como executar](#como-executar)
- [Endpoints da API](#endpoints-da-api)
- [Fluxo de dados](#fluxo-de-dados)

---

## Stack utilizada

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| IoT | Google Colab + Python | Simula sensores ESP32 via MQTT |
| Mensageria | Eclipse Mosquitto | Broker MQTT :1883 |
| Orquestração | Node-RED | Processa MQTT e grava no InfluxDB |
| Time series | InfluxDB 2.x | Armazena leituras brutas dos sensores |
| Monitoramento | Grafana | Dashboard em tempo real |
| Backend | Node.js + Express | API REST + consolidação + alertas |
| Banco relacional | MySQL 8.4 | Dados consolidados e alertas |
| Frontend | React + TypeScript | Dashboard do produtor |
| Infraestrutura | AWS EC2 + Docker | Hospeda a Stack MING |

---

## Arquitetura

```
[Google Colab — simula ESP32]
        |
        | MQTT (fatec/pbl01)
        ↓
[Eclipse Mosquitto :1883]  ← EC2
        |
        ↓
[Node-RED :8082]           ← EC2
        |
        ↓
[InfluxDB :8083]           ← EC2
        |
        ├──→ [Grafana :8084]         ← tempo real
        |
        └──→ [Backend :8080]         ← consolida a cada 30s
                    |
                    ↓
               [MySQL :3307]
                    |
                    ↓
             [Frontend :3000]        ← atualiza a cada 5s
```

---

## Estrutura do repositório

```
StackMingWeb/
├── /iot
│   └── simulador_estufa.ipynb   # Simulador de sensores (substitui ESP32/Wokwi)
│
├── /nodered
│   └── flows.json               # Fluxo exportado do Node-RED
│
├── /backend
│   ├── src/
│   │   ├── index.js             # Entry point
│   │   ├── app.js               # Express + middlewares
│   │   ├── db/
│   │   │   ├── influx.js        # Queries Flux ao InfluxDB
│   │   │   ├── migrate.js       # Criação das tabelas MySQL
│   │   │   └── seed.js          # Inserção inicial de sensores
│   │   ├── routes/
│   │   │   ├── sensors.js       # CRUD de sensores
│   │   │   ├── metrics.js       # Consulta de métricas
│   │   │   └── alerts.js        # Gerenciamento de alertas
│   │   └── jobs/
│   │       └── consolidation.js # Job de consolidação + alertas automáticos
│   └── package.json
│
├── /frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx         # Painel principal IoT
│   │   │   └── GrafanaDashboard.tsx  # Iframe Grafana
│   │   ├── components/               # MetricCard, SensorTable, AlertFeed, Sparkline
│   │   ├── hooks/
│   │   │   └── useIoTData.ts         # Polling automático a cada 5s
│   │   └── services/
│   │       └── api.ts                # Chamadas REST ao backend
│   └── package.json
│
├── /docs
│   └── PBL1_Monitoramento_Estufa_Final.docx  # Documentação completa
│
└── docker-compose.yml           # Orquestração da Stack MING na EC2
```

---

## Variáveis monitoradas

| Variável | Faixa ideal | Alerta | Crítico | Impacto fora da faixa |
|----------|-------------|--------|---------|----------------------|
| Temperatura | 18 a 28 °C | > 28 °C | > 35 °C | Estresse térmico, queima de folhas |
| Umidade | 50 a 70% | > 70% | > 80% | Fungos, podridão de raízes |
| Luminosidade | 200 a 800 lux | > 1500 lux | > 1800 lux | Fotoinibição ou etiolamento |
| Qualidade do ar (CO₂) | 400 a 600 ppm | > 600 ppm | > 800 ppm | Fotossíntese limitada |

---

## Como executar

### Pré-requisitos

- AWS EC2 com Ubuntu 22.04 + Docker + Docker Compose
- Node.js v18+ na máquina local
- Google Colab para o simulador

### 1. EC2 — Stack MING

```bash
git clone https://github.com/profAndreSouza/StackMingWeb.git
cd StackMingWeb
docker-compose up -d
```

### 2. Local — Backend

Criar `backend/.env`:

```env
INFLUX_URL=http://IP_DA_EC2:8083
INFLUX_TOKEN=seu_token_aqui
INFLUX_ORG=my-org
INFLUX_BUCKET=iot-sensors
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_DATABASE=iot_consolidated
MYSQL_USER=iot_user
MYSQL_PASSWORD=iot_pass
USE_MOCK=false
CONSOLIDATION_CRON=*/30 * * * * *
CONSOLIDATION_WINDOW_MINUTES=5
```

```bash
cd backend
npm install
npm run seed   # apenas na primeira execução
npm start
```

### 3. Local — Frontend

Criar `frontend/.env`:

```env
VITE_API_URL=http://localhost:8080
```

```bash
cd frontend
npm install
npm start
```

### 4. Google Colab — Simulador

Abrir `/iot/simulador_estufa.ipynb`, atualizar o IP do broker e rodar todas as células.

> ⚠️ **Ao reiniciar a EC2** o IP público muda. Atualizar: `backend/.env`, `frontend/.env`, `GrafanaDashboard.tsx` e o Colab.

---

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/health` | Status da API |
| GET | `/api/sensors` | Lista todos os sensores |
| GET | `/api/sensors/:id` | Detalhe de um sensor |
| PATCH | `/api/sensors/:id` | Atualiza nome/localização |
| GET | `/api/metrics` | Resumo das métricas (última janela 5min) |
| GET | `/api/metrics/:metric/trend` | Série histórica para sparklines |
| GET | `/api/alerts` | Lista alertas (`?resolved=false\|true\|all`) |
| PATCH | `/api/alerts/:id/resolve` | Resolve um alerta |

---

## Fluxo de dados

### Dados enviados pelo simulador (JSON via MQTT)

```json
{
  "temperatura": 24.7,
  "umidade": 58.3,
  "luminosidade": 642.5,
  "qualidade_ar": 387,
  "timestamp": "20260417092519"
}
```

**Tópico:** `fatec/pbl01` | **Intervalo:** 5 segundos | **QoS:** 0

### Pipeline Node-RED → InfluxDB

O Node-RED assina `fatec/pbl01`, converte o payload JSON e grava no InfluxDB com:

```
_measurement = iot-sensors
_field       = temperatura | umidade | luminosidade | qualidade_ar
_value       = número float
_time        = timestamp UTC automático
```

### Backend → MySQL (job de consolidação)

A cada 30 segundos o backend:
1. Busca leituras dos últimos 5 minutos no InfluxDB
2. Calcula avg/min/max por sensor + métrica
3. Persiste em `metrics_consolidated` no MySQL
4. Verifica thresholds e gera alertas automáticos
5. Atualiza status dos sensores

---

## Portas na EC2

| Serviço | Porta |
|---------|-------|
| MQTT | 1883 |
| Node-RED | 8082 |
| InfluxDB | 8083 |
| Grafana | 8084 |
| Backend API | 8080 |
| MySQL | 3307 |
| Frontend | 80 |

---

*Programação Multiplataforma — Prof. André Souza — PBL1 2026*
