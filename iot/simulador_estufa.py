# ============================================================
# PBL1 — Simulador de Sensores de Estufa
# Disciplina: Programação Multiplataforma
# Professor: André Souza
#
# Este script substitui o ESP32/Wokwi como dispositivo IoT.
# Publica dados simulados de sensores via MQTT a cada 5s.
# ============================================================

# Instalar dependência (rodar no Google Colab)
# !pip install paho-mqtt

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# ── CONFIGURAÇÕES ────────────────────────────────────────────
# Atualizar com o IP atual da instância EC2 ao reiniciar
MQTT_BROKER = "IP_DA_EC2"
MQTT_PORT   = 1883
MQTT_TOPIC  = "fatec/pbl01"
INTERVALO_S = 5  # segundos entre cada envio

# ── FAIXAS SIMULADAS DOS SENSORES ────────────────────────────
# Baseadas nas condições reais de uma estufa agrícola
FAIXAS = {
    "temperatura":  (20.0, 30.0),   # °C  — ideal: 18 a 28°C
    "umidade":      (40.0, 70.0),   # %   — ideal: 50 a 70%
    "luminosidade": (100.0, 1000.0),# lux — ideal: 200 a 800 lux
    "qualidade_ar": (100, 500),     # ppm — ideal: 400 a 600 ppm (CO2)
}

# ── CALLBACKS MQTT ───────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Conectado ao broker {MQTT_BROKER}:{MQTT_PORT}")
    else:
        print(f"[MQTT] Falha na conexão — código: {rc}")

def on_publish(client, userdata, mid):
    pass  # confirmação silenciosa de publicação

# ── INICIALIZACAO ────────────────────────────────────────────
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish  = on_publish

print(f"[INFO] Conectando ao broker MQTT em {MQTT_BROKER}...")
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
client.loop_start()

print(f"[INFO] Simulador iniciado. Publicando em '{MQTT_TOPIC}' a cada {INTERVALO_S}s")
print("[INFO] Pressione Ctrl+C ou interrompa a célula para parar.\n")

# ── LOOP PRINCIPAL ───────────────────────────────────────────
try:
    contador = 0
    while True:
        contador += 1

        # Gera dados simulados dentro das faixas configuradas
        dados = {
            "temperatura":  round(random.uniform(*FAIXAS["temperatura"]), 2),
            "umidade":      round(random.uniform(*FAIXAS["umidade"]), 2),
            "luminosidade": round(random.uniform(*FAIXAS["luminosidade"]), 2),
            "qualidade_ar": random.randint(*FAIXAS["qualidade_ar"]),
            "timestamp":    datetime.now().strftime("%Y%m%d%H%M%S"),
        }

        # Serializa e publica via MQTT
        payload = json.dumps(dados)
        result  = client.publish(MQTT_TOPIC, payload, qos=0)

        # Log formatado para acompanhamento
        hora = datetime.now().strftime("%H:%M:%S")
        status = "OK" if result.rc == 0 else f"ERRO ({result.rc})"
        print(
            f"[{hora}] #{contador:04d} | "
            f"Temp: {dados['temperatura']:5.1f}°C | "
            f"Umid: {dados['umidade']:5.1f}% | "
            f"Lux: {dados['luminosidade']:6.1f} | "
            f"CO2: {dados['qualidade_ar']:4d}ppm | "
            f"{status}"
        )

        time.sleep(INTERVALO_S)

except KeyboardInterrupt:
    print("\n[INFO] Simulação encerrada pelo usuário.")
    client.loop_stop()
    client.disconnect()
    print("[INFO] Conexão MQTT encerrada.")