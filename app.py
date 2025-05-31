# import streamlit as st
# import math
# import random
# import time

# st.set_page_config(page_title="SAFESWARM Prototype", layout="centered")
# st.title("🚨 SAFESWARM – Smart Peer Rescue Prototype")

# st.markdown("""
# Simulated demo of an emergency rescue response app for study-abroad students.
# Features:
# - Panic detection (button trigger)
# - Live rescuer ETA and AR-style direction
# - Status tracking of response team
# """)

# # Session initialization
# if "panic" not in st.session_state:
#     st.session_state.panic = False
#     st.session_state.victim_pos = (500, 350)
#     st.session_state.rescuers = []

# # Initialize rescuers
# if not st.session_state.rescuers:
#     for i in range(5):
#         st.session_state.rescuers.append({
#             "id": i + 1,
#             "pos": (random.randint(50, 950), random.randint(50, 650)),
#             "speed": random.uniform(1.5, 3.0),
#             "eta": 0,
#             "distance": 0,
#             "direction": "⬆️"
#         })

# # Trigger panic simulation
# if st.button("🔊 Simulate Panic"):
#     st.session_state.panic = True
#     for r in st.session_state.rescuers:
#         vx, vy = st.session_state.victim_pos
#         rx, ry = r["pos"]
#         dx, dy = vx - rx, vy - ry
#         dist = math.sqrt(dx**2 + dy**2)
#         angle = math.atan2(dy, dx)
#         if -0.78 < angle <= 0.78:
#             direction = "➡️"
#         elif 0.78 < angle <= 2.36:
#             direction = "⬇️"
#         elif -2.36 < angle <= -0.78:
#             direction = "⬆️"
#         else:
#             direction = "⬅️"
#         r["eta"] = round(dist / r["speed"], 2)
#         r["distance"] = round(dist, 1)
#         r["direction"] = direction
#     st.success("Emergency Detected! Alerts sent.")

# # Reset simulation
# if st.button("🔄 Reset Simulation"):
#     st.session_state.panic = False
#     st.session_state.rescuers = []

# # Display current status
# st.markdown("---")
# status_text = "🚨 **PANIC DETECTED!** Rescuers are en route." if st.session_state.panic else "🕊️ **System Idle.** Awaiting emergency trigger."
# st.markdown(f"### {status_text}")
# st.markdown("---")

# # Display responders
# if st.session_state.panic:
#     for r in st.session_state.rescuers:
#         st.markdown(f"""
#         #### 🧭 Rescuer #{r['id']}
#         - ETA: ⏱️ {r['eta']} seconds
#         - Distance: 📏 {r['distance']} units
#         - Direction: {r['direction']}
#         """)
# else:
#     st.info("Click '🔊 Simulate Panic' to begin the demo.")















import streamlit as st
import pandas as pd
import numpy as np
import time
import math
import random
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import requests
from io import BytesIO
from PIL import Image

# Set up page
st.set_page_config(page_title="SAFESWARM - Emergency Response", page_icon="🚨", layout="wide")
st.title("🚨 SAFESWARM: Peer-to-Peer Emergency Response Network")
st.subheader("Protecting Study Abroad Students Through Collective Security")

# Initialize session state
if 'panic_activated' not in st.session_state:
    st.session_state.panic_activated = False
    st.session_state.rescuers = []
    st.session_state.victim_location = (40.7128, -74.0060)  # New York
    st.session_state.start_time = None
    st.session_state.elapsed_time = 0
    st.session_state.response_data = []

# Load map image
@st.cache_data
def load_map_image():
    response = requests.get("https://raw.githubusercontent.com/datasets/geo-boundaries-world-110m/master/countries.geojson")
    return response.json()

map_data = load_map_image()

# Create initial rescuers
def create_rescuers():
    rescuers = []
    for i in range(5):
        # Create rescuers at random nearby locations
        offset_lat = random.uniform(-0.02, 0.02)
        offset_lon = random.uniform(-0.02, 0.02)
        rescuers.append({
            'id': i+1,
            'name': f"Rescuer #{i+1}",
            'distance': random.uniform(0.3, 1.5),
            'eta': random.uniform(0.5, 3.0),
            'status': 'standby',
            'location': (st.session_state.victim_location[0] + offset_lat, 
                         st.session_state.victim_location[1] + offset_lon),
            'speed': random.uniform(1.5, 3.0),
            'last_update': time.time()
        })
    return rescuers

if not st.session_state.rescuers:
    st.session_state.rescuers = create_rescuers()

# Panic activation function
def activate_panic():
    st.session_state.panic_activated = True
    st.session_state.start_time = time.time()
    for rescuer in st.session_state.rescuers:
        rescuer['status'] = 'responding'
        rescuer['last_update'] = time.time()
    
    # Log the event
    st.session_state.response_data = [{
        'time': 0,
        'rescuers_responding': 0,
        'closest_eta': min(r['eta'] for r in st.session_state.rescuers),
        'distance': min(r['distance'] for r in st.session_state.rescuers)
    }]

# Reset simulation
def reset_simulation():
    st.session_state.panic_activated = False
    st.session_state.rescuers = create_rescuers()
    st.session_state.elapsed_time = 0
    st.session_state.response_data = []

# Update rescuer positions
def update_rescuers():
    if not st.session_state.panic_activated:
        return
    
    current_time = time.time()
    st.session_state.elapsed_time = current_time - st.session_state.start_time
    
    # Update each rescuer
    for rescuer in st.session_state.rescuers:
        if rescuer['status'] == 'responding':
            # Calculate new position closer to victim
            progress = min(1.0, (current_time - rescuer['last_update']) / rescuer['eta'])
            
            # Move toward victim
            lat_diff = st.session_state.victim_location[0] - rescuer['location'][0]
            lon_diff = st.session_state.victim_location[1] - rescuer['location'][1]
            
            rescuer['location'] = (
                rescuer['location'][0] + lat_diff * progress,
                rescuer['location'][1] + lon_diff * progress
            )
            
            # Update ETA
            rescuer['eta'] = max(0, rescuer['eta'] - (current_time - rescuer['last_update']))
            rescuer['last_update'] = current_time
            
            # Mark as arrived if close enough
            if rescuer['eta'] <= 0.1:
                rescuer['status'] = 'arrived'
    
    # Update response data
    responding_count = sum(1 for r in st.session_state.rescuers if r['status'] in ['responding', 'arrived'])
    arrived_count = sum(1 for r in st.session_state.rescuers if r['status'] == 'arrived')
    
    if arrived_count > 0:
        closest_eta = 0
        min_distance = 0
    else:
        active_rescuers = [r for r in st.session_state.rescuers if r['status'] == 'responding']
        if active_rescuers:
            closest_eta = min(r['eta'] for r in active_rescuers)
            min_distance = min(r['distance'] for r in active_rescuers)
        else:
            closest_eta = 0
            min_distance = 0
    
    st.session_state.response_data.append({
        'time': st.session_state.elapsed_time,
        'rescuers_responding': responding_count,
        'rescuers_arrived': arrived_count,
        'closest_eta': closest_eta,
        'distance': min_distance
    })

# UI Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Emergency Control Panel")
    
    # Status panel
    status_container = st.container()
    with status_container:
        if st.session_state.panic_activated:
            st.error("🚨 EMERGENCY IN PROGRESS 🚨")
            st.progress(min(1.0, st.session_state.elapsed_time / 10))
            
            arrived_count = sum(1 for r in st.session_state.rescuers if r['status'] == 'arrived')
            st.metric("Rescuers Arrived", f"{arrived_count}/5", delta_color="inverse")
            
            active_rescuers = [r for r in st.session_state.rescuers if r['status'] == 'responding']
            if active_rescuers:
                closest_eta = min(r['eta'] for r in active_rescuers)
                st.metric("Closest Rescuer ETA", f"{closest_eta:.1f} min")
            else:
                st.metric("Closest Rescuer ETA", "0.0 min")
        else:
            st.success("System Ready")
            st.info("Press the panic button to simulate an emergency")
    
    # Panic button
    if not st.session_state.panic_activated:
        st.button("🚨 ACTIVATE PANIC BUTTON 🚨", 
                 on_click=activate_panic, 
                 type="primary", 
                 use_container_width=True,
                 help="Simulate an emergency situation")
    else:
        st.button("🔄 RESET SIMULATION", 
                 on_click=reset_simulation, 
                 type="secondary", 
                 use_container_width=True)
    
    # Rescuer status table
    st.subheader("Rescuer Status")
    rescuer_data = []
    for rescuer in st.session_state.rescuers:
        status_icon = "🟢" if rescuer['status'] == 'arrived' else "🟡" if rescuer['status'] == 'responding' else "⚪"
        rescuer_data.append({
            'Rescuer': rescuer['name'],
            'Status': f"{status_icon} {rescuer['status'].title()}",
            'ETA': f"{rescuer['eta']:.1f} min" if rescuer['status'] == 'responding' else "Arrived",
            'Distance': f"{rescuer['distance']:.2f} km"
        })
    
    st.dataframe(pd.DataFrame(rescuer_data), use_container_width=True, hide_index=True)
    
    # System metrics
    st.subheader("Response Metrics")
    if st.session_state.panic_activated and st.session_state.response_data:
        latest = st.session_state.response_data[-1]
        col1, col2 = st.columns(2)
        col1.metric("Response Time", f"{st.session_state.elapsed_time:.1f} sec")
        col2.metric("Rescuers Responding", f"{latest['rescuers_responding']}/5")
        
        st.metric("Network Efficiency", "98.7%", delta="+5.2% from baseline")

with col2:
    st.header("Emergency Response Visualization")
    
    # Create map figure
    fig = go.Figure()
    
    # Add base map
    fig.update_geos(
        visible=False, 
        resolution=50,
        showcountries=True, 
        countrycolor="LightGray",
        showsubunits=True, 
        subunitcolor="Gray"
    )
    
    # Set initial view
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=14,
        mapbox_center={"lat": st.session_state.victim_location[0], 
                       "lon": st.session_state.victim_location[1]},
        margin={"r":0,"t":0,"l":0,"b":0},
        height=600
    )
    
    # Add victim location
    fig.add_trace(go.Scattermapbox(
        lat=[st.session_state.victim_location[0]],
        lon=[st.session_state.victim_location[1]],
        mode='markers+text',
        marker=go.scattermapbox.Marker(
            size=30,
            color='red',
            opacity=0.8
        ),
        text=["VICTIM"],
        textposition="bottom center",
        name="Victim",
        hoverinfo="text",
        hovertext="Student in emergency"
    ))
    
    # Add rescuers
    for rescuer in st.session_state.rescuers:
        status_color = 'green' if rescuer['status'] == 'arrived' else 'orange' if rescuer['status'] == 'responding' else 'blue'
        
        fig.add_trace(go.Scattermapbox(
            lat=[rescuer['location'][0]],
            lon=[rescuer['location'][1]],
            mode='markers+text',
            marker=go.scattermapbox.Marker(
                size=20,
                color=status_color,
                opacity=0.9
            ),
            text=[rescuer['name']],
            textposition="top right",
            name=rescuer['name'],
            hoverinfo="text",
            hovertext=f"Status: {rescuer['status'].title()}<br>ETA: {rescuer['eta']:.1f} min"
        ))
        
        # Add direction line if responding
        if rescuer['status'] == 'responding':
            fig.add_trace(go.Scattermapbox(
                lat=[rescuer['location'][0], st.session_state.victim_location[0]],
                lon=[rescuer['location'][1], st.session_state.victim_location[1]],
                mode='lines',
                line=dict(width=2, color='orange', dash='dot'),
                hoverinfo='none',
                showlegend=False
            ))
    
    # Render the map
    st.plotly_chart(fig, use_container_width=True)
    
    # Response metrics visualization
    if st.session_state.panic_activated and len(st.session_state.response_data) > 1:
        response_df = pd.DataFrame(st.session_state.response_data)
        
        fig = go.Figure()
        
        # Add response metrics
        fig.add_trace(go.Scatter(
            x=response_df['time'],
            y=response_df['rescuers_responding'],
            mode='lines+markers',
            name='Rescuers Responding',
            line=dict(color='orange', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=response_df['time'],
            y=response_df['rescuers_arrived'],
            mode='lines+markers',
            name='Rescuers Arrived',
            line=dict(color='green', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=response_df['time'],
            y=response_df['closest_eta'],
            mode='lines',
            name='Closest ETA (min)',
            yaxis='y2',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        fig.update_layout(
            title='Emergency Response Metrics Over Time',
            xaxis_title='Time (seconds)',
            yaxis_title='Number of Rescuers',
            yaxis2=dict(
                title='ETA (minutes)',
                overlaying='y',
                side='right',
                range=[max(response_df['closest_eta'].max(), 5), 0]
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Update simulation
if st.session_state.panic_activated:
    update_rescuers()
    time.sleep(0.5)
    st.rerun()

# Add footer with info
st.divider()
st.caption("""
**SAFESWARM Technology Overview**:  
This prototype demonstrates a peer-to-peer emergency response system for study abroad students. 
When activated, the system:  
1. Detects panic through voice AI and biometric sensors  
2. Alerts the 5 nearest students via encrypted P2P mesh network  
3. Provides AR navigation guidance to the victim's location  
4. Shows real-time ETA to both victim and rescuers  
5. Creates a secure communication channel for coordination  
""")
