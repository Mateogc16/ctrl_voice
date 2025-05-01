import os
import time
import glob
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import paho.mqtt.client as paho
import json
from gtts import gTTS
from io import BytesIO

# ----------------------------------------
# Estética Medieval
# ----------------------------------------
st.set_page_config(page_title="🔮 Control Arcano por Voz", page_icon="🧙‍♂️", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&display=swap');

    html, body, [class*="css"] {
        background-color: #0b032d;
        color: #d0caff;
        font-family: 'UnifrakturCook', cursive;
    }
    .stButton>button {
        background: linear-gradient(145deg, #6a00ff, #9c4dff);
        border: 1px solid #d6b3ff;
        color: #ffffff;
        border-radius: 10px;
        padding: 0.6em 1.2em;
        font-weight: bold;
        box-shadow: 0 0 10px #a463ff;
        font-family: 'UnifrakturCook', cursive;
    }
    .stSidebar {
        background-color: #120a3b;
        color: #dcd6f7;
    }
    h1, h2, h3 {
        color: #cba6f7;
        text-shadow: 0 0 5px #b892ff, 0 0 10px #8f43f8;
        font-family: 'UnifrakturCook', cursive;
    }
    .stMarkdown p, .css-1v0mbdj p {
        font-family: 'Georgia', serif;
        color: #e0dfff;
    }
    .block-container {
        background-color: rgba(18, 10, 59, 0.8);
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------
# MQTT Setup
# ----------------------------------------
def on_publish(client, userdata, result):
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(1)
    message_received = message.payload.decode('utf-8')
    st.success(f"🪞 Espejo Arcano responde: {message_received}")

broker = "157.230.214.127"
port = 1883

auth_client = paho.Client("Voice_Control_Client")
auth_client.on_message = on_message

# Sidebar información
st.sidebar.title("📜 Panel de Hechicería")
st.sidebar.write("Ajusta parámetros o revisa el registro de conjuros enviados.")

# Título principal
st.title("🔮 Control Arcano por Voz")

image = Image.open('voice_ctrl.jpg') if os.path.exists('voice_ctrl.jpg') else None
if image:
    st.image(image, width=200)

st.markdown("***")
st.write("🗣️ Pulsa el sello encantado y pronuncia tu conjuro:")

# Botón de inicio de voz
stt_button = Button(label="Iniciar Conjuro por Voz", width=250)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# Captura el comando y publica
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="voice_listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    command = result.get("GET_TEXT").strip()
    st.markdown(f"**🔊 Hechizo Utillizado:** *{command}*")
    # Conexión MQTT
    auth_client.connect(broker, port)
    auth_client.loop_start()
    auth_client.subscribe("voice_ctrl")
    payload = json.dumps({"Act1": command})
    auth_client.publish("voice_ctrl", payload)
    time.sleep(1)
    auth_client.loop_stop()

# Limpiar archivos temporales generados por TTS
try:
    os.mkdir("temp")
except FileExistsError:
    pass

# Pie de página
st.markdown("***")
st.caption("🏰 Desarrollado por los alquimistas digitales del reino.")
