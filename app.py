import streamlit as st
import math
import random
import time

st.set_page_config(page_title="SAFESWARM Prototype", layout="centered")
st.title("🚨 SAFESWARM – Smart Peer Rescue Prototype")

st.markdown("""
Simulated demo of an emergency rescue response app for study-abroad students.
Features:
- Panic detection (button trigger)
- Live rescuer ETA and AR-style direction
- Status tracking of response team
""")

# Session initialization
if "panic" not in st.session_state:
    st.session_state.panic = False
    st.session_state.victim_pos = (500, 350)
    st.session_state.rescuers = []

# Initialize rescuers
if not st.session_state.rescuers:
    for i in range(5):
        st.session_state.rescuers.append({
            "id": i + 1,
            "pos": (random.randint(50, 950), random.randint(50, 650)),
            "speed": random.uniform(1.5, 3.0),
            "eta": 0,
            "distance": 0,
            "direction": "⬆️"
        })

# Trigger panic simulation
if st.button("🔊 Simulate Panic"):
    st.session_state.panic = True
    for r in st.session_state.rescuers:
        vx, vy = st.session_state.victim_pos
        rx, ry = r["pos"]
        dx, dy = vx - rx, vy - ry
        dist = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)
        if -0.78 < angle <= 0.78:
            direction = "➡️"
        elif 0.78 < angle <= 2.36:
            direction = "⬇️"
        elif -2.36 < angle <= -0.78:
            direction = "⬆️"
        else:
            direction = "⬅️"
        r["eta"] = round(dist / r["speed"], 2)
        r["distance"] = round(dist, 1)
        r["direction"] = direction
    st.success("Emergency Detected! Alerts sent.")

# Reset simulation
if st.button("🔄 Reset Simulation"):
    st.session_state.panic = False
    st.session_state.rescuers = []

# Display current status
st.markdown("---")
status_text = "🚨 **PANIC DETECTED!** Rescuers are en route." if st.session_state.panic else "🕊️ **System Idle.** Awaiting emergency trigger."
st.markdown(f"### {status_text}")
st.markdown("---")

# Display responders
if st.session_state.panic:
    for r in st.session_state.rescuers:
        st.markdown(f"""
        #### 🧭 Rescuer #{r['id']}
        - ETA: ⏱️ {r['eta']} seconds
        - Distance: 📏 {r['distance']} units
        - Direction: {r['direction']}
        """)
else:
    st.info("Click '🔊 Simulate Panic' to begin the demo.")















            
