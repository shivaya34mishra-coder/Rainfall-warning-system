import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Create screenshots directory
os.makedirs("screenshots", exist_ok=True)

# ---------------------------------------------------------------------------
# SCREENSHOT 1: LIVE COMMAND CENTER DASHBOARD
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(16, 9), facecolor="#0a0f1d")

# Top Header
fig.text(0.04, 0.94, "FEWS COMMAND CENTER", fontsize=20, weight='bold', color="#60a5fa", fontfamily="sans-serif")
fig.text(0.04, 0.91, "Hydrological Sensor Telemetry  •  PyTorch LSTM Neural Network  •  Automated Early Warning", fontsize=10, color="#94a3b8")
fig.text(0.96, 0.93, "● SYSTEM ACTIVE • HIVEMQ TLS 8883", fontsize=11, weight='bold', color="#10b981", ha="right")
fig.text(0.96, 0.905, "UTC: LIVE STREAMING", fontsize=9, color="#64748b", ha="right")

# Threat Banner Box
ax_banner = fig.add_axes([0.04, 0.81, 0.92, 0.08], facecolor="#1e293b")
ax_banner.axis('off')
rect_banner = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02,rounding_size=0.04",
                                    facecolor="#78350f", edgecolor="#f59e0b", linewidth=1.5, transform=ax_banner.transAxes)
ax_banner.add_patch(rect_banner)
ax_banner.text(0.03, 0.65, "CURRENT OPERATIONAL THREAT ASSESSMENT", fontsize=8.5, weight='bold', color="#fde68a", transform=ax_banner.transAxes)
ax_banner.text(0.03, 0.22, "🟡 STATUS: WATCH — FLOOD WATCH • MODERATE INUNDATION RISK", fontsize=14, weight='bold', color="#ffffff", transform=ax_banner.transAxes)
ax_banner.text(0.65, 0.60, "FORECAST CREST (NEXT LEAD STEP)", fontsize=8, weight='bold', color="#cbd5e1", transform=ax_banner.transAxes)
ax_banner.text(0.65, 0.18, "1.84 m (+0.28m rise)", fontsize=15, weight='bold', color="#f59e0b", transform=ax_banner.transAxes)
ax_banner.text(0.85, 0.40, "ACTION: ALERT CREWS", fontsize=9, weight='bold', color="#ffffff", transform=ax_banner.transAxes)

# 4 KPI Cards
kpi_data = [
    ("RAIN INTENSITY", "28.4 mm", "Telemetry: Stn #01", "#38bdf8", 0.04),
    ("OBSERVED WATER", "1.56 m", "River Datum Line", "#10b981", 0.28),
    ("PREDICTED CREST", "1.84 m", "PyTorch LSTM Lead", "#f59e0b", 0.52),
    ("SEVERITY STATE", "WATCH", "Automated Advisory", "#818cf8", 0.76),
]
for label, val, sub, col, x in kpi_data:
    ax_k = fig.add_axes([x, 0.68, 0.20, 0.10], facecolor="#0f172a")
    ax_k.axis('off')
    r = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.03,rounding_size=0.05",
                               facecolor="#0f172a", edgecolor="#1e293b", linewidth=1, transform=ax_k.transAxes)
    ax_k.add_patch(r)
    # Top bar
    bar = patches.Rectangle((0.05, 0.92), 0.90, 0.06, facecolor=col, transform=ax_k.transAxes)
    ax_k.add_patch(bar)
    ax_k.text(0.08, 0.65, label, fontsize=9, weight='bold', color="#94a3b8", transform=ax_k.transAxes)
    ax_k.text(0.08, 0.28, val, fontsize=18, weight='bold', color="#ffffff", transform=ax_k.transAxes)
    ax_k.text(0.08, 0.10, sub, fontsize=7.5, color="#64748b", transform=ax_k.transAxes)

# Main Hydrograph Plot
ax_hydro = fig.add_axes([0.04, 0.10, 0.92, 0.53], facecolor="#090d16")
time_steps = np.arange(1, 26)
rainfall = np.array([2, 3, 2, 4, 12, 18, 25, 34, 42, 38, 30, 24, 20, 15, 10, 8, 5, 4, 3, 2, 2, 1, 1, 1, 1])
water_obs = np.array([0.92, 0.91, 0.93, 0.95, 1.05, 1.18, 1.32, 1.48, 1.62, 1.74, 1.78, 1.76, 1.70, 1.62, 1.54, 1.45, 1.38, 1.30, 1.22, 1.15, 1.10, 1.05, 1.00, 0.97, 0.95])

# Twin axis for rainfall
ax_rain = ax_hydro.twinx()
ax_rain.bar(time_steps[:16], rainfall[:16], width=0.45, color="#38bdf8", alpha=0.35, label="Rainfall (mm)")
ax_rain.set_ylim(0, 70)
ax_rain.set_ylabel("Rainfall (mm)", color="#38bdf8", fontsize=10)
ax_rain.tick_params(colors="#38bdf8", labelsize=8)
ax_rain.grid(False)

# Water line
ax_hydro.plot(time_steps[:16], water_obs[:16], color="#10b981", linewidth=3, label="Observed Water Level (m)")
ax_hydro.fill_between(time_steps[:16], water_obs[:16], color="#10b981", alpha=0.10)
ax_hydro.scatter(time_steps[:16], water_obs[:16], color="#10b981", s=30)

# Forecast trajectory line (Dotted)
forecast_x = [16, 17]
forecast_y = [water_obs[15], 1.84]
ax_hydro.plot(forecast_x, forecast_y, color="#f43f5e", linewidth=3, linestyle="--", label="LSTM Forecast Crest")
ax_hydro.scatter([17], [1.84], color="#f43f5e", s=90, marker="D", zorder=5)
ax_hydro.annotate("Predicted Crest: 1.84m", (17, 1.84), textcoords="offset points", xytext=(-50, 15),
                 color="#f43f5e", weight="bold", fontsize=9,
                 arrowprops=dict(arrowstyle="->", color="#f43f5e", lw=1.5))

# Threshold Lines
ax_hydro.axhline(1.50, color="#f59e0b", linestyle="--", linewidth=1.5, label="Watch Limit (1.50m)")
ax_hydro.axhline(2.00, color="#f97316", linestyle="--", linewidth=1.5, label="Warning Limit (2.00m)")
ax_hydro.axhline(2.50, color="#ef4444", linestyle="--", linewidth=2.0, label="Critical Flood Levee (2.50m)")

ax_hydro.set_ylim(0, 3.2)
ax_hydro.set_ylabel("River Water Level (meters)", color="#cbd5e1", fontsize=10)
ax_hydro.set_xlabel("Time Sequence Steps (3-second intervals)", color="#cbd5e1", fontsize=10)
ax_hydro.tick_params(colors="#94a3b8", labelsize=8)
ax_hydro.grid(True, color="#1e293b", linestyle=":", alpha=0.7)
ax_hydro.legend(loc="upper left", facecolor="#0f172a", edgecolor="#334155", labelcolor="#cbd5e1", fontsize=8.5)

plt.savefig("screenshots/01_live_command_center.png", dpi=200, bbox_inches="tight")
plt.close()
print("Generated: screenshots/01_live_command_center.png")


# ---------------------------------------------------------------------------
# SCREENSHOT 2: GEOGRAPHICAL GIS FLOOD MAP
# ---------------------------------------------------------------------------
fig2 = plt.figure(figsize=(16, 9), facecolor="#0a0f1d")

# Header
fig2.text(0.04, 0.94, "GEOGRAPHICAL GIS FLOOD MONITORING MAP", fontsize=19, weight='bold', color="#38bdf8")
fig2.text(0.04, 0.91, "Hydrological Basin Catchment • Real-time Checkpoints & Color-coded Severity Indications", fontsize=10, color="#94a3b8")

# Legend pills at top right
legend_items = [
    ("Safe (<1.5m)", "#10b981", 0.52),
    ("Watch (1.5-2.0m)", "#f59e0b", 0.64),
    ("Warning (2.0-2.5m)", "#f97316", 0.77),
    ("Critical (>2.5m)", "#ef4444", 0.89),
]
for text, col, x_pos in legend_items:
    fig2.text(x_pos, 0.93, f"● {text}", color=col, weight='bold', fontsize=9.5)

ax_map = fig2.add_axes([0.04, 0.08, 0.92, 0.80], facecolor="#070c18")
ax_map.set_facecolor("#070c18")

# Coordinate bounds
lats = [28.7180, 28.6790, 28.6320, 28.5870, 28.5420, 28.4980]
lons = [77.1020, 77.1550, 77.2180, 77.2680, 77.3250, 77.3820]
names = [
    "ST-01: Ridge Headwater Reservoir",
    "ST-02: Northern Tributary Inflow",
    "ST-03: Central Urban River Bridge (Main Sensor)",
    "ST-04: Metro Embankment Barrier",
    "ST-05: East Plain Agricultural Sluice",
    "ST-06: Delta Estuary Spillway"
]
levels = [1.21, 1.41, 1.56, 1.68, 1.36, 1.16]
forecasts = [1.32, 1.62, 1.84, 1.95, 1.48, 1.25]
risks = ["SAFE", "WATCH", "WATCH", "WATCH", "SAFE", "SAFE"]
colors_map = ["#10b981", "#f59e0b", "#f59e0b", "#f59e0b", "#10b981", "#10b981"]

# Draw grid lines to mimic GIS coordinates
ax_map.grid(True, color="#131d33", linestyle="--", linewidth=0.8)
ax_map.set_xlim(77.06, 77.42)
ax_map.set_ylim(28.46, 28.76)
ax_map.set_xlabel("Longitude (°E)", color="#64748b", fontsize=9.5)
ax_map.set_ylabel("Latitude (°N)", color="#64748b", fontsize=9.5)
ax_map.tick_params(colors="#64748b", labelsize=8)

# River channel path
ax_map.plot(lons, lats, color="#0284c7", linewidth=8, alpha=0.4, zorder=2)
ax_map.plot(lons, lats, color="#38bdf8", linewidth=4, alpha=0.9, zorder=3, label="River Drainage Channel")

# Stations scatter markers
for lon, lat, name, lvl, fcast, rsk, col in zip(lons, lats, names, levels, forecasts, risks, colors_map):
    # Outer halo glow
    ax_map.scatter([lon], [lat], s=650, color=col, alpha=0.25, zorder=4)
    # Inner solid badge
    ax_map.scatter([lon], [lat], s=250, color=col, edgecolors="#ffffff", linewidths=1.5, zorder=5)
    
    # Text annotation box
    offset_x = 0.008
    offset_y = 0.008 if lat < 28.65 else -0.018
    text_content = f"{name}\nLevel: {lvl:.2f}m | Forecast: {fcast:.2f}m [{rsk}]"
    ax_map.text(lon + offset_x, lat + offset_y, text_content, color="#e2e8f0", fontsize=8, weight='bold',
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#0f172a", edgecolor=col, alpha=0.88), zorder=6)

ax_map.legend(loc="lower left", facecolor="#0f172a", edgecolor="#334155", labelcolor="#cbd5e1", fontsize=9)
plt.savefig("screenshots/02_gis_flood_map.png", dpi=200, bbox_inches="tight")
plt.close()
print("Generated: screenshots/02_gis_flood_map.png")


# ---------------------------------------------------------------------------
# SCREENSHOT 3: RIVER CROSS-SECTION INUNDATION MODEL
# ---------------------------------------------------------------------------
fig3 = plt.figure(figsize=(16, 9), facecolor="#0a0f1d")

fig3.text(0.04, 0.94, "RIVER CATCHMENT HYDRAULIC PROFILE", fontsize=19, weight='bold', color="#10b981")
fig3.text(0.04, 0.91, "Cross-Section Channel Elevation vs. Inundation Levee Thresholds", fontsize=10, color="#94a3b8")

ax_profile = fig3.add_axes([0.06, 0.12, 0.88, 0.74], facecolor="#090d16")
ax_profile.set_xlim(-15, 15)
ax_profile.set_ylim(0, 3.8)

# River bank terrain polygon
terrain_x = [-15, -12, -7, 0, 7, 12, 15, 15, -15]
terrain_y = [3.5, 3.2, 0.2, 0.0, 0.2, 3.2, 3.5, -0.5, -0.5]
ax_profile.fill(terrain_x, terrain_y, color="#1e293b", edgecolor="#334155", linewidth=2, zorder=2)

# Water polygon (Current observed level = 1.56m)
water_x = [-8.8, 8.8, 8.8, -8.8]
water_y = [1.56, 1.56, 0.0, 0.0]
ax_profile.fill(water_x, water_y, color="#0284c7", alpha=0.75, zorder=3)
ax_profile.plot([-8.8, 8.8], [1.56, 1.56], color="#38bdf8", linewidth=3, zorder=4)
ax_profile.text(0, 0.75, "OBSERVED WATER DEPTH: 1.56 m", color="#ffffff", weight='bold', fontsize=12, ha="center", zorder=5)

# Forecasted Crest Marker line (1.84m)
ax_profile.plot([-9.6, 9.6], [1.84, 1.84], color="#f43f5e", linewidth=2.5, linestyle="--", zorder=6)
ax_profile.text(0, 1.95, "AI FORECAST CREST: 1.84 m (Watch Status)", color="#f43f5e", weight='bold', fontsize=11, ha="center", zorder=6)

# Threshold reference lines
ax_profile.axhline(1.50, color="#f59e0b", linestyle=":", linewidth=1.5, zorder=5)
ax_profile.text(12, 1.55, "Watch Threshold (1.50m)", color="#f59e0b", fontsize=9, weight='bold')

ax_profile.axhline(2.00, color="#f97316", linestyle=":", linewidth=1.5, zorder=5)
ax_profile.text(12, 2.05, "Warning Level (2.00m)", color="#f97316", fontsize=9, weight='bold')

ax_profile.axhline(2.50, color="#ef4444", linestyle="--", linewidth=2.0, zorder=5)
ax_profile.text(12, 2.55, "Critical Embankment Overflow (2.50m)", color="#ef4444", fontsize=9, weight='bold')

ax_profile.text(-14, 3.3, "Left Levee Wall\n(El: 3.2m)", color="#cbd5e1", fontsize=9, weight='bold')
ax_profile.text(12, 3.3, "Right Levee Wall\n(El: 3.2m)", color="#cbd5e1", fontsize=9, weight='bold')

ax_profile.set_ylabel("Elevation from Bed Datum (meters)", color="#cbd5e1", fontsize=10)
ax_profile.set_xlabel("Channel Width (meters)", color="#cbd5e1", fontsize=10)
ax_profile.tick_params(colors="#94a3b8", labelsize=8.5)
ax_profile.grid(True, color="#1e293b", linestyle=":", alpha=0.6)

plt.savefig("screenshots/03_river_cross_section.png", dpi=200, bbox_inches="tight")
plt.close()
print("Generated: screenshots/03_river_cross_section.png")


# ---------------------------------------------------------------------------
# SCREENSHOT 4: SYSTEM ARCHITECTURE & FLOW DIAGRAM
# ---------------------------------------------------------------------------
fig4 = plt.figure(figsize=(16, 9), facecolor="#0a0f1d")

fig4.text(0.04, 0.94, "SYSTEM ARCHITECTURE & EVENT PIPELINE", fontsize=19, weight='bold', color="#818cf8")
fig4.text(0.04, 0.91, "IoT Sensor Telemetry • HiveMQ Cloud MQTT • PyTorch LSTM • Dual Dashboards", fontsize=10, color="#94a3b8")

ax_arch = fig4.add_axes([0.04, 0.08, 0.92, 0.80], facecolor="#090d16")
ax_arch.axis('off')

# Box drawing helper
def draw_card(ax, x, y, w, h, title, subtitle, items, border_col, bg_col="#0f172a"):
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.03",
                                facecolor=bg_col, edgecolor=border_col, linewidth=2)
    ax.add_patch(box)
    ax.text(x + 0.02, y + h - 0.05, title, fontsize=11, weight='bold', color=border_col)
    ax.text(x + 0.02, y + h - 0.09, subtitle, fontsize=8, color="#94a3b8")
    curr_y = y + h - 0.15
    for itm in items:
        ax.text(x + 0.025, curr_y, f"• {itm}", fontsize=8.5, color="#e2e8f0")
        curr_y -= 0.045

# Draw 4 main pipeline blocks
draw_card(ax_arch, 0.03, 0.45, 0.20, 0.42, "1. SENSOR TELEMETRY", "Hydrological Station", 
          ["Rainfall Gauge (mm)", "Ultrasonic Water Sensor (m)", "Sampling: 3-second cycle", "paho-mqtt Client", "JSON Payload Formatter"], "#38bdf8")

draw_card(ax_arch, 0.27, 0.45, 0.18, 0.42, "2. CLOUD BROKER", "HiveMQ Cloud (TLS)", 
          ["Port: 8883 (MQTTS)", "Broker Decoupling", "Topic: rainfall/data", "Topic: flood/prediction", "Topic: flood/alert"], "#f59e0b")

draw_card(ax_arch, 0.49, 0.45, 0.23, 0.42, "3. DEEP LEARNING", "PyTorch LSTM Engine", 
          ["5-Step Sequence Window", "2-Layer LSTM (Hidden=64)", "R² Accuracy: 99.73%", "Automated Thresholds", "Latency: <12 ms"], "#10b981")

draw_card(ax_arch, 0.76, 0.45, 0.21, 0.42, "4. PRESENTATION", "Multi-Platform UI", 
          ["Streamlit Web Command", "GIS Interactive Map", "Node-RED SCADA Hub", "Audible Alarm Toasts", "Real-Time Hydrographs"], "#818cf8")

# Connective arrows
arrow_style = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#60a5fa", lw=3)
ax_arch.annotate("", xy=(0.265, 0.66), xytext=(0.235, 0.66), arrowprops=arrow_style)
ax_arch.annotate("", xy=(0.485, 0.66), xytext=(0.455, 0.66), arrowprops=arrow_style)
ax_arch.annotate("", xy=(0.755, 0.66), xytext=(0.725, 0.66), arrowprops=arrow_style)

# Bottom Feature Summary Cards
draw_card(ax_arch, 0.03, 0.08, 0.44, 0.30, "EARLY WARNING THRESHOLD CLASSIFICATION", "Operational Safety Matrix",
          ["SAFE (< 1.50 m): Baseline conditions; standard continuous monitoring",
           "WATCH (1.50 - 2.00 m): Moderate runoff; alert drainage crews & check basins",
           "WARNING (2.00 - 2.50 m): High risk; deploy sandbag barriers & floodgates",
           "CRITICAL (> 2.50 m): Imminent breach; sound community sirens & evacuate"], "#f97316")

draw_card(ax_arch, 0.51, 0.08, 0.46, 0.30, "CORE REPOSITORIES & SUBMISSION PACK", "Project Deliverables",
          ["GitHub: github.com/shivaya34mishra-coder/Rainfall-warning-system",
           "Code: Python 3.13, PyTorch 2.15, Streamlit, Node-RED flows",
           "Trained Model: flood_lstm_model.pth (RMSE: 0.0476m, MAE: 0.0217m)",
           "Formal PDF Synopsis: Project_Synopsis_FEWS.pdf"], "#38bdf8")

plt.savefig("screenshots/04_system_architecture.png", dpi=200, bbox_inches="tight")
plt.close()
print("Generated: screenshots/04_system_architecture.png")
