import streamlit as st
import requests
import time
import pandas as pd
import numpy as np
from collections import deque

# -----------------------
# CONFIG
# -----------------------
BASE_URL = "http://127.0.0.1:8000"
REFRESH_INTERVAL = 2
MAX_HISTORY = 60

st.set_page_config(page_title="Incident AI Resolver", layout="wide")

# -----------------------
# UI STYLE
# -----------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# HEADER
# -----------------------
st.title("🚀 Incident AI Resolver Dashboard")
st.caption("AI-powered real-time incident monitoring system")
st.markdown("---")

# -----------------------
# INCIDENT SWITCH
# -----------------------
colA, colB = st.columns([2, 1])

incident = colA.selectbox("⚙️ Incident Level", ["easy", "medium", "hard"])

if colB.button("Apply"):
    try:
        requests.get(f"{BASE_URL}/set_incident?level={incident}")
        st.success(f"Switched to {incident}")
    except:
        st.error("Backend not reachable")

# -----------------------
# SESSION STATE
# -----------------------
if "history" not in st.session_state:
    st.session_state.history = deque(maxlen=MAX_HISTORY)

# -----------------------
# FETCH DATA
# -----------------------
def fetch_data():
    try:
        res = requests.get(f"{BASE_URL}/live_monitor", timeout=2)
        data = res.json()
        if "error" in data:
            return None, data["error"]
        return data, None
    except Exception as e:
        return None, str(e)

# -----------------------
# HELPERS
# -----------------------
def detect_zscore(values):
    if len(values) < 10:
        return False, 0
    mean = np.mean(values[:-1])
    std = np.std(values[:-1]) + 1e-5
    z = (values[-1] - mean) / std
    return abs(z) > 2.5, z

def simulate(prev, new):
    if prev is None:
        return new
    return int(prev + (new - prev) * 0.5 + np.random.randint(-3, 4))

def predict(values):
    if len(values) < 5:
        return values
    trend = np.mean(np.diff(values[-5:]))
    next_val = values[-1] + trend
    return values + [next_val]

def generate_narration(cpu, memory, db, action, anomaly, info):
    confidence = info.get("confidence", 0)

    if action == "scale_up":
        return f"🚀 CPU spiked to {cpu}%. AI scaled system proactively. Confidence {confidence}"

    elif action == "check_database":
        return f"🛢️ Database latency at {db} ms. AI checking DB bottleneck."

    elif action == "restart_service":
        return f"♻️ Memory usage at {memory}%. AI restarted service to prevent crash."

    elif anomaly:
        return f"🔥 Unexpected anomaly detected. System behavior abnormal."

    else:
        return f"✅ System stable. No intervention needed."

# -----------------------
# FETCH + VALIDATE
# -----------------------
data, error = fetch_data()

if error:
    st.error(f"Backend error: {error}")
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

# 🔴 HARD VALIDATION (NO MORE CRASHES)
if not data:
    st.error("Empty response from backend")
    st.stop()

if "metrics" not in data:
    st.error(f"Invalid response (missing metrics): {data}")
    st.stop()

if "action" not in data:
    st.error(f"Invalid response (missing action): {data}")
    st.stop()

# -----------------------
# SAFE EXTRACTION
# -----------------------
metrics = data.get("metrics", {})
action = data.get("action", "unknown")
info = data.get("info", {})

cpu_raw = metrics.get("cpu", 0)
memory_raw = metrics.get("memory", 0)
db_raw = metrics.get("db_latency", 0)

# -----------------------
# SIMULATION
# -----------------------
prev = st.session_state.history[-1] if st.session_state.history else None

cpu = simulate(prev["cpu"] if prev else None, cpu_raw)
memory = simulate(prev["memory"] if prev else None, memory_raw)
db_latency = simulate(prev["db_latency"] if prev else None, db_raw)

# -----------------------
# STORE HISTORY
# -----------------------
st.session_state.history.append({
    "cpu": cpu,
    "memory": memory,
    "db_latency": db_latency,
    "action": action,
    "confidence": info.get("confidence", 0),
    "reason": info.get("reason", "unknown")
})

latest = st.session_state.history[-1]

# -----------------------
# METRICS DISPLAY
# -----------------------
st.subheader("📊 System Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("CPU", f"{cpu}%")
c2.metric("Memory", f"{memory}%")
c3.metric("DB Latency", f"{db_latency} ms")
c4.metric("Action", action)

st.progress(min(cpu, 100) / 100)

# -----------------------
# ANOMALY DETECTION
# -----------------------
st.markdown("### 🚨 System Intelligence")

cpu_vals = [h["cpu"] for h in st.session_state.history]
db_vals = [h["db_latency"] for h in st.session_state.history]

cpu_anomaly, cpu_z = detect_zscore(cpu_vals)
db_anomaly, db_z = detect_zscore(db_vals)

if cpu_anomaly:
    st.error(f"🔥 CPU anomaly (Z-score: {cpu_z:.2f})")
elif db_anomaly:
    st.error(f"🔥 DB anomaly (Z-score: {db_z:.2f})")
elif cpu > 85 or memory > 85:
    st.warning("⚠️ High resource usage")
else:
    st.success("✅ System stable")

# -----------------------
# AI EXPLANATION
# -----------------------
st.markdown("---")
st.subheader("🧠 AI Decision Explanation")

st.info(f"""
Reason: {latest['reason']}

Confidence: {latest['confidence']}

Action: {latest['action']}
""")

# -----------------------
# NARRATION
# -----------------------
st.markdown("---")
st.subheader("🗣️ AI Live Narration")

narration = generate_narration(
    cpu,
    memory,
    db_latency,
    action,
    cpu_anomaly or db_anomaly,
    info
)

placeholder = st.empty()
typed = ""

for char in narration:
    typed += char
    placeholder.markdown(f"### {typed}")
    time.sleep(0.01)

# -----------------------
# DECISION BREAKDOWN
# -----------------------
st.markdown("### ⚙️ Decision Breakdown")

scores = info.get("scores", {})

if scores:
    df_scores = pd.DataFrame(list(scores.items()), columns=["Action", "Score"])
    st.bar_chart(df_scores.set_index("Action"))

# -----------------------
# CHARTS
# -----------------------
st.markdown("---")
st.subheader("📈 Live Trends")

df = pd.DataFrame(st.session_state.history)

col1, col2, col3 = st.columns(3)

col1.line_chart(df["cpu"])
col2.line_chart(df["memory"])
col3.line_chart(df["db_latency"])

# -----------------------
# PREDICTION
# -----------------------
st.markdown("---")
st.subheader("🔮 Future Forecast")

cpu_pred = predict(cpu_vals)

st.line_chart(cpu_pred)

if len(cpu_pred) > 1:
    next_val = cpu_pred[-1]
    st.write(f"Predicted CPU: **{next_val:.2f}%**")

    if next_val > 90:
        st.warning("⚠️ Critical spike predicted")

# -----------------------
# LOGS
# -----------------------
st.markdown("---")
st.subheader("📜 Activity Log")

for h in list(st.session_state.history)[-10:][::-1]:
    st.write(h)

# -----------------------
# AUTO REFRESH
# -----------------------
time.sleep(REFRESH_INTERVAL)
st.rerun()