"""Streamlit dashboard. Run with:  streamlit run app.py"""
import time
import pandas as pd
import streamlit as st

from simulator import SimulatedSource, WATER_PROFILES
from classifier import classify

st.set_page_config(page_title="Water Quality Monitor", page_icon="💧", layout="wide")
st.title("💧 Smart Drinking Water Quality Monitor")
st.caption("Phase 1: simulated data. Readings are indicative, not a substitute for lab testing.")

# ---- sidebar controls ----
water_type = st.sidebar.selectbox("Water type (simulated)", list(WATER_PROFILES))
auto = st.sidebar.toggle("Auto-update", value=False)
interval = st.sidebar.slider("Update interval (sec)", 1, 10, 2)
if st.sidebar.button("Clear history"):
    st.session_state.history = []

if "history" not in st.session_state:
    st.session_state.history = []

# ---- get a new reading (swap SimulatedSource for a real source in Phase 2) ----
source = SimulatedSource(water_type)
if auto or st.sidebar.button("Take reading") or not st.session_state.history:
    reading = source.read()
    statuses, overall = classify(reading)
    reading.update({"status": overall})
    st.session_state.history.append(reading)
    st.session_state.history = st.session_state.history[-50:]  # keep last 50

latest = st.session_state.history[-1]
statuses, overall = classify(latest)

# ---- overall status banner ----
icons = {"Safe": "✅", "Caution": "⚠️", "Unsafe": "❌"}
msg = f"{icons[overall]} Water status: **{overall}**  ({latest['water_type']}, {latest['time']})"
{"Safe": st.success, "Caution": st.warning, "Unsafe": st.error}[overall](msg)

# ---- live readings ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("TDS (mg/L)", latest["tds"], statuses["tds"])
c2.metric("Turbidity (NTU)", latest["turbidity"], statuses["turbidity"])
c3.metric("pH", latest["ph"], statuses["ph"])
c4.metric("Temperature (°C)", latest["temp"])

# ---- history ----
df = pd.DataFrame(st.session_state.history)
st.subheader("History")
left, right = st.columns(2)
left.line_chart(df.set_index("time")[["tds"]])
right.line_chart(df.set_index("time")[["turbidity", "ph"]])
st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)

# ---- auto-refresh loop ----
if auto:
    time.sleep(interval)
    st.rerun()
