# ============================================================
# AGRO-VATORS VECTOR DIAGRAMS (Pure SVG)
# ============================================================

SYSTEM_ARCHITECTURE_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 620" width="100%" height="auto" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px;">
  <defs>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.1"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#15803d"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#0284c7"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>
    </marker>
  </defs>

  <!-- TITLE -->
  <text x="480" y="30" text-anchor="middle" font-family="-apple-system, Segoe UI, sans-serif" font-size="16" font-weight="bold" fill="#14532d">AGRO-VATORS: Quad-Tier Autonomous Edge System Architecture</text>
  <text x="480" y="48" text-anchor="middle" font-family="-apple-system, Segoe UI, sans-serif" font-size="11" fill="#64748b">Zero-Cloud Local Hotspot Topology with Independent Edge Compute Tiers</text>

  <!-- TIER 1: PHYSICAL ROVER -->
  <rect x="20" y="70" width="440" height="525" rx="8" fill="#ffffff" stroke="#16a34a" stroke-width="2" filter="url(#shadow)"/>
  <rect x="20" y="70" width="440" height="32" rx="8" fill="#15803d"/>
  <rect x="20" y="94" width="440" height="8" fill="#15803d"/>
  <text x="240" y="92" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#ffffff">TIER 1: PHYSICAL ROVER HARDWARE (ESP32 Master + ESP32-CAM)</text>

  <!-- ESP32 Master Box -->
  <rect x="35" y="115" width="230" height="180" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>
  <text x="150" y="135" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">ESP32 DevKit V1 (Master)</text>
  <text x="150" y="150" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#475569">240MHz Dual-Core | FreeRTOS</text>
  <text x="45" y="172" font-family="sans-serif" font-size="9" fill="#1e293b">• WebServer on Port 80 (REST API)</text>
  <text x="45" y="190" font-family="sans-serif" font-size="9" fill="#1e293b">• 600ms Failsafe Drive Watchdog</text>
  <text x="45" y="208" font-family="sans-serif" font-size="9" fill="#1e293b">• Smooth Servo Slew Interpolator</text>
  <text x="45" y="226" font-family="sans-serif" font-size="9" fill="#1e293b">• 3.3V Active-LOW Relay Inversion</text>
  <text x="45" y="244" font-family="sans-serif" font-size="9" fill="#1e293b">• Multi-Sensor ADC Sampling (12-bit)</text>
  <text x="45" y="262" font-family="sans-serif" font-size="9" fill="#1e293b">• IP: 192.168.93.164 (STA Mode)</text>
  <text x="45" y="280" font-family="sans-serif" font-size="9" font-weight="bold" fill="#15803d">Status: Verified &amp; Operational</text>

  <!-- ESP32-CAM Box -->
  <rect x="280" y="115" width="165" height="180" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5"/>
  <text x="362" y="135" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1e40af">ESP32-CAM (Vision)</text>
  <text x="362" y="150" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#475569">AI-Thinker OV2640 2MP</text>
  <text x="290" y="172" font-family="sans-serif" font-size="9" fill="#1e293b">• MJPEG Streamer (:80)</text>
  <text x="290" y="190" font-family="sans-serif" font-size="9" fill="#1e293b">• JPEG Frame Capture</text>
  <text x="290" y="208" font-family="sans-serif" font-size="9" fill="#1e293b">• 4MB External PSRAM</text>
  <text x="290" y="226" font-family="sans-serif" font-size="9" fill="#1e293b">• 240x240 @ 15-20 FPS</text>
  <text x="290" y="244" font-family="sans-serif" font-size="9" fill="#1e293b">• IP: 192.168.93.28</text>
  <text x="290" y="262" font-family="sans-serif" font-size="9" fill="#1e293b">• RFC-Compliant HTTP</text>
  <text x="290" y="280" font-family="sans-serif" font-size="9" font-weight="bold" fill="#0284c7">Node: Camera Worker</text>

  <!-- Actuators & Peripherals Box -->
  <rect x="35" y="310" width="410" height="270" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
  <text x="240" y="330" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#334155">Rover Actuators, Sensors &amp; Display Hardware</text>

  <!-- Motor Block -->
  <rect x="45" y="345" width="190" height="65" rx="4" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
  <text x="140" y="362" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0f172a">4WD DC Motors (300 RPM)</text>
  <text x="140" y="378" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">L298N Dual H-Bridge Driver</text>
  <text x="140" y="394" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#166534">IN1:26 | IN2:27 | IN3:14 | IN4:12</text>

  <!-- Servo Block -->
  <rect x="245" y="345" width="190" height="65" rx="4" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
  <text x="340" y="362" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0f172a">SG90 Soil Probe Servo</text>
  <text x="340" y="378" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">50Hz Hardware PWM | GPIO 25</text>
  <text x="340" y="394" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#166534">20° (Tuck Up) ⇄ 160° (Ground In)</text>

  <!-- Relay & Pump Block -->
  <rect x="45" y="420" width="190" height="65" rx="4" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
  <text x="140" y="437" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0f172a">Submersible Water Pump</text>
  <text x="140" y="453" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">1-Ch Opto Relay | GPIO 33</text>
  <text x="140" y="469" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#166534">Batt(+) → COM → NO → Pump(+)</text>

  <!-- Sensor Block -->
  <rect x="245" y="420" width="190" height="65" rx="4" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
  <text x="340" y="437" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0f172a">Environmental Sensors</text>
  <text x="340" y="453" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">DHT11 (GPIO 4: Temp &amp; Humidity)</text>
  <text x="340" y="469" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#166534">Soil: GPIO 34 | LDR: GPIO 35</text>

  <!-- OLED & Battery Block -->
  <rect x="45" y="495" width="190" height="70" rx="4" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
  <text x="140" y="514" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0f172a">0.96" SSD1306 OLED (I2C)</text>
  <text x="140" y="530" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">SDA: GPIO 21 | SCL: GPIO 22</text>
  <text x="140" y="546" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#166534">Real-Time IP &amp; Probe HUD</text>

  <rect x="245" y="495" width="190" height="70" rx="4" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
  <text x="340" y="514" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0f172a">Power Architecture</text>
  <text x="340" y="530" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">12V Li-ion Battery Pack</text>
  <text x="340" y="546" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#166534">L298N 5V Buck + AMS1117 3.3V</text>

  <!-- TIER 2: LOCAL NETWORK -->
  <rect x="480" y="70" width="460" height="95" rx="8" fill="#ffffff" stroke="#0284c7" stroke-width="2" filter="url(#shadow)"/>
  <rect x="480" y="70" width="460" height="28" rx="8" fill="#0284c7"/>
  <rect x="480" y="90" width="460" height="8" fill="#0284c7"/>
  <text x="710" y="89" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#ffffff">TIER 2: PRIVATE 2.4 GHz WIRELESS HOTSPOT (ZERO CLOUD)</text>
  <text x="710" y="118" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#0f172a">SSID: "phone1" | Password: "12345678" | Subnet: 192.168.93.0/24</text>
  <text x="710" y="135" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#475569">High-throughput, low-latency field mesh binding Rover, Laptop Core, and Phone Controller</text>
  <text x="710" y="150" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#0369a1">No Internet Gateway Required | Operates 100% Offline in Deep Agricultural Fields</text>

  <!-- TIER 3: LAPTOP AI CORE -->
  <rect x="480" y="180" width="460" height="225" rx="8" fill="#ffffff" stroke="#7c3aed" stroke-width="2" filter="url(#shadow)"/>
  <rect x="480" y="180" width="460" height="28" rx="8" fill="#7c3aed"/>
  <rect x="480" y="200" width="460" height="8" fill="#7c3aed"/>
  <text x="710" y="199" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#ffffff">TIER 3: LAPTOP AI ENGINE &amp; FLASK BACKEND (PORT 5001)</text>

  <!-- Python Flask Server -->
  <rect x="495" y="220" width="210" height="170" rx="6" fill="#faf5ff" stroke="#d8b4fe" stroke-width="1.5"/>
  <text x="600" y="238" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#6b21a8">Flask REST API (app.py)</text>
  <text x="505" y="258" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Background Camera Worker Thread</text>
  <text x="505" y="274" font-family="sans-serif" font-size="8.5" fill="#1e293b">• RFC-Compliant MJPEG Stream Proxy</text>
  <text x="505" y="290" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Telemetry Ingestion &amp; Caching</text>
  <text x="505" y="306" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Inverted Relay Signal Routing</text>
  <text x="505" y="322" font-family="sans-serif" font-size="8.5" fill="#1e293b">• SQLite3 Database Logger</text>
  <text x="505" y="338" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Agronomic Decision Rule Engine</text>
  <text x="505" y="354" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Multilingual String Tables</text>
  <text x="505" y="372" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#7c3aed">Host IP: 192.168.93.173:5001</text>

  <!-- YOLOv8 & Computer Vision -->
  <rect x="715" y="220" width="210" height="170" rx="6" fill="#faf5ff" stroke="#d8b4fe" stroke-width="1.5"/>
  <text x="820" y="238" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#6b21a8">Vision &amp; YOLOv8 Engine</text>
  <text x="725" y="258" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Ultralytics YOLOv8n (yolov8n.pt)</text>
  <text x="725" y="274" font-family="sans-serif" font-size="8.5" fill="#1e293b">• 640x480 CLAHE Contrast Filtering</text>
  <text x="725" y="290" font-family="sans-serif" font-size="8.5" fill="#1e293b">• LAB / HSV Spectral Color Masks</text>
  <text x="725" y="306" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Chlorophyll Vigor Index (Hue 25-88)</text>
  <text x="725" y="322" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Necrotic Lesion Profiler (Hue 8-18)</text>
  <text x="725" y="338" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Powdery Mildew Detector (Gray)</text>
  <text x="725" y="354" font-family="sans-serif" font-size="8.5" fill="#1e293b">• 8 Crop Pathology Classifiers</text>
  <text x="725" y="372" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#7c3aed">Latency: ~40ms per frame</text>

  <!-- TIER 4: ANDROID MOBILE OPERATOR CONSOLE -->
  <rect x="480" y="420" width="460" height="175" rx="8" fill="#ffffff" stroke="#ea580c" stroke-width="2" filter="url(#shadow)"/>
  <rect x="480" y="420" width="460" height="28" rx="8" fill="#ea580c"/>
  <rect x="480" y="440" width="460" height="8" fill="#ea580c"/>
  <text x="710" y="439" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#ffffff">TIER 4: MOBILE OPERATOR CONSOLE (NATIVE ANDROID APK)</text>

  <rect x="495" y="460" width="430" height="120" rx="6" fill="#fff7ed" stroke="#fdba74" stroke-width="1.5"/>
  <text x="710" y="478" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#c2410c">Native Android App: com.agrovators.agrirover (Poco F1: 192.168.93.175)</text>
  <text x="510" y="498" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Touch Directional D-Pad (Forward, Backward, Left, Right, Immediate Release-to-Stop)</text>
  <text x="510" y="514" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Real-Time Soil Probe Servo Slider (20° Retracted Drive Safe ⇄ 160° Ground Insertion Depth)</text>
  <text x="510" y="530" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Rewired Water Pump Toggles ([▶ Pump ON] in Green &amp; [⏹ Pump OFF] in Red) + Real-Time Badge</text>
  <text x="510" y="546" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Zero-Latency Double-Buffered Video Viewer with Real-Time YOLO Bounding Boxes &amp; Crop Health HUD</text>
  <text x="510" y="562" font-family="sans-serif" font-size="8.5" fill="#1e293b">• Dual-Mode: Full AI Mode via Laptop (:5001) OR Standalone Direct Rover Control (:80)</text>
  <text x="510" y="574" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#c2410c">Multilingual Localization: English | हिंदी (Hindi) | বাংলা (Bengali)</text>

  <!-- INTERCONNECT ARROWS -->
  <!-- Rover to Hotspot -->
  <line x1="240" y1="70" x2="240" y2="40" stroke="#0284c7" stroke-width="2"/>
  <line x1="240" y1="40" x2="600" y2="40" stroke="#0284c7" stroke-width="2"/>
  <line x1="600" y1="40" x2="600" y2="70" stroke="#0284c7" stroke-width="2" marker-end="url(#arrow-blue)"/>

  <!-- Hotspot to Laptop -->
  <line x1="650" y1="165" x2="650" y2="180" stroke="#7c3aed" stroke-width="2" marker-end="url(#arrow-purple)"/>

  <!-- Laptop to Android -->
  <line x1="710" y1="405" x2="710" y2="420" stroke="#ea580c" stroke-width="2" marker-end="url(#arrow)"/>
</svg>
"""

WORKFLOW_DIAGRAM_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 760" width="100%" height="auto" style="background:#ffffff; border:1px solid #cbd5e1; border-radius:8px;">
  <defs>
    <filter id="wf-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.08"/>
    </filter>
    <marker id="wf-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#15803d"/>
    </marker>
    <marker id="wf-arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#b91c1c"/>
    </marker>
  </defs>

  <!-- TITLE -->
  <text x="480" y="30" text-anchor="middle" font-family="-apple-system, Segoe UI, sans-serif" font-size="16" font-weight="bold" fill="#14532d">AGRO-VATORS: End-to-End Operational Workflow &amp; Execution Flowchart</text>
  <text x="480" y="48" text-anchor="middle" font-family="-apple-system, Segoe UI, sans-serif" font-size="11" fill="#64748b">Complete Lifecycle from Power-On to Edge AI Diagnosis, Soil Insertion, and Micro-Irrigation</text>

  <!-- STEP 1: INITIALIZATION -->
  <rect x="360" y="70" width="240" height="42" rx="21" fill="#15803d" stroke="#14532d" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="480" y="96" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#ffffff">1. SYSTEM POWER-ON</text>

  <line x1="480" y1="112" x2="480" y2="135" stroke="#15803d" stroke-width="2" marker-end="url(#wf-arrow)"/>

  <!-- STEP 2: HOTSPOT CONNECTION -->
  <rect x="340" y="135" width="280" height="50" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="480" y="156" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">2. Local 2.4 GHz Hotspot Bind</text>
  <text x="480" y="172" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#475569">ESP32, ESP32-CAM &amp; Laptop bind to "phone1"</text>

  <line x1="480" y1="185" x2="480" y2="210" stroke="#15803d" stroke-width="2" marker-end="url(#wf-arrow)"/>

  <!-- STEP 3: PERIPHERAL INIT -->
  <rect x="330" y="210" width="300" height="52" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="480" y="231" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">3. Peripheral Failsafe Initialization</text>
  <text x="480" y="248" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#475569">Motors STOP | Soil Servo @ 55° (Retracted) | Pump OFF</text>

  <line x1="480" y1="262" x2="480" y2="285" stroke="#15803d" stroke-width="2" marker-end="url(#wf-arrow)"/>

  <!-- STEP 4: NAVIGATION -->
  <rect x="330" y="285" width="300" height="52" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="480" y="306" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e40af">4. Tele-Operated Crop Navigation</text>
  <text x="480" y="323" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#475569">Operator drives via D-Pad (600ms Watchdog Active)</text>

  <line x1="480" y1="337" x2="480" y2="360" stroke="#15803d" stroke-width="2" marker-end="url(#wf-arrow)"/>

  <!-- STEP 5: PROBE DEPLOYMENT -->
  <rect x="320" y="360" width="320" height="52" rx="6" fill="#fef3c7" stroke="#fcd34d" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="480" y="381" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#b45309">5. Soil Probe Deployment (GPIO 25)</text>
  <text x="480" y="398" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#78350f">Operator taps "Deploy" → SG90 slews 55° → 135° into earth</text>

  <line x1="480" y1="412" x2="480" y2="435" stroke="#15803d" stroke-width="2" marker-end="url(#wf-arrow)"/>

  <!-- STEP 6: DUAL DATA SAMPLING (SPLIT) -->
  <rect x="180" y="435" width="280" height="58" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="320" y="455" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#166534">6A. Multi-Sensor Acquisition</text>
  <text x="320" y="471" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">Soil Moisture (ADC1: 34), Temp &amp; Hum (DHT11),</text>
  <text x="320" y="484" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">Ambient Light (LDR: 35) → Displayed on OLED</text>

  <rect x="500" y="435" width="280" height="58" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="640" y="455" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#1e40af">6B. ESP32-CAM Leaf Capture</text>
  <text x="640" y="471" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">High-definition foliage snapshot captured</text>
  <text x="640" y="484" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">and streamed to Laptop AI Server (:5001)</text>

  <!-- Connect 5 to 6A and 6B -->
  <line x1="420" y1="412" x2="320" y2="435" stroke="#15803d" stroke-width="1.5" marker-end="url(#wf-arrow)"/>
  <line x1="540" y1="412" x2="640" y2="435" stroke="#15803d" stroke-width="1.5" marker-end="url(#wf-arrow)"/>

  <!-- STEP 7: YOLO + CV ANALYSIS -->
  <rect x="300" y="520" width="360" height="56" rx="6" fill="#faf5ff" stroke="#d8b4fe" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="480" y="541" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#6b21a8">7. Edge YOLOv8 &amp; Spectral HSV Analysis</text>
  <text x="480" y="557" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">YOLOv8 Bounding Boxes + LAB CLAHE + HSV Chlorophyll/Lesion Segmentation</text>
  <text x="480" y="569" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#6b21a8">Classifies Healthy Leaf, Blight, Rust, Septoria, Mildew, or Chlorosis</text>

  <line x1="320" y1="493" x2="440" y2="520" stroke="#15803d" stroke-width="1.5" marker-end="url(#wf-arrow)"/>
  <line x1="640" y1="493" x2="520" y2="520" stroke="#15803d" stroke-width="1.5" marker-end="url(#wf-arrow)"/>

  <line x1="480" y1="576" x2="480" y2="600" stroke="#15803d" stroke-width="2" marker-end="url(#wf-arrow)"/>

  <!-- STEP 8: DECISION DIAMOND -->
  <polygon points="480,600 580,635 480,670 380,635" fill="#fef3c7" stroke="#f59e0b" stroke-width="2" filter="url(#wf-shadow)"/>
  <text x="480" y="632" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#92400e">Irrigation</text>
  <text x="480" y="646" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#92400e">Needed?</text>

  <!-- DECISION BRANCH: YES -->
  <line x1="580" y1="635" x2="680" y2="635" stroke="#15803d" stroke-width="2" marker-end="url(#wf-arrow)"/>
  <text x="630" y="628" font-family="sans-serif" font-size="9" font-weight="bold" fill="#15803d">YES (Dry / ADC &gt; 3000)</text>

  <rect x="680" y="612" width="220" height="46" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="790" y="632" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#166534">8A. Trigger Pump ON</text>
  <text x="790" y="647" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">Relay GPIO 33 active → Hydrate root zone</text>

  <!-- DECISION BRANCH: NO -->
  <line x1="380" y1="635" x2="280" y2="635" stroke="#b91c1c" stroke-width="2" marker-end="url(#wf-arrow-red)"/>
  <text x="330" y="628" font-family="sans-serif" font-size="9" font-weight="bold" fill="#b91c1c">NO (Moist / Normal)</text>

  <rect x="60" y="612" width="220" height="46" rx="6" fill="#fee2e2" stroke="#fca5a5" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="170" y="632" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#991b1b">8B. Pump Remains OFF</text>
  <text x="170" y="647" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#475569">Prevents root rot and pathogen spread</text>

  <!-- MERGE TO COMPLETION -->
  <line x1="790" y1="658" x2="790" y2="700" stroke="#15803d" stroke-width="1.5"/>
  <line x1="790" y1="700" x2="580" y2="700" stroke="#15803d" stroke-width="1.5"/>

  <line x1="170" y1="658" x2="170" y2="700" stroke="#15803d" stroke-width="1.5"/>
  <line x1="170" y1="700" x2="380" y2="700" stroke="#15803d" stroke-width="1.5"/>

  <line x1="480" y1="670" x2="480" y2="710" stroke="#15803d" stroke-width="2" marker-end="url(#wf-arrow)"/>

  <!-- STEP 9: RETRACT PROBE & LOG -->
  <rect x="300" y="710" width="360" height="42" rx="6" fill="#15803d" stroke="#14532d" stroke-width="1.5" filter="url(#wf-shadow)"/>
  <text x="480" y="728" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#ffffff">9. Retract Probe to 55° (Drive Safe) &amp; Log to DB</text>
  <text x="480" y="742" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#bbf7d0">Telemetry and diagnosis stored in agrivise.db | Ready for next plant</text>
</svg>
"""

DATA_FLOW_DIAGRAM_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 620" width="100%" height="auto" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px;">
  <defs>
    <filter id="dfd-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.08"/>
    </filter>
    <marker id="dfd-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#0369a1"/>
    </marker>
  </defs>

  <!-- TITLE -->
  <text x="480" y="30" text-anchor="middle" font-family="-apple-system, Segoe UI, sans-serif" font-size="16" font-weight="bold" fill="#0f172a">AGRO-VATORS: Data Flow Diagram (DFD Level 1)</text>
  <text x="480" y="48" text-anchor="middle" font-family="-apple-system, Segoe UI, sans-serif" font-size="11" fill="#64748b">Mapping Entity Interactions, Transformations, Data Stores, and Multi-Modal Agronomic Feedback</text>

  <!-- EXTERNAL ENTITIES -->
  <!-- Entity 1: Operator / Farmer -->
  <rect x="25" y="80" width="150" height="80" rx="4" fill="#f1f5f9" stroke="#475569" stroke-width="2" filter="url(#dfd-shadow)"/>
  <text x="100" y="115" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0f172a">FARMER /</text>
  <text x="100" y="132" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0f172a">OPERATOR</text>

  <!-- Entity 2: Crop & Soil Environment -->
  <rect x="25" y="470" width="150" height="80" rx="4" fill="#f1f5f9" stroke="#475569" stroke-width="2" filter="url(#dfd-shadow)"/>
  <text x="100" y="505" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0f172a">CROP &amp; SOIL</text>
  <text x="100" y="522" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0f172a">ENVIRONMENT</text>

  <!-- PROCESS 1.0: Touch Control Handling -->
  <circle cx="280" cy="120" r="45" fill="#e0f2fe" stroke="#0284c7" stroke-width="2" filter="url(#dfd-shadow)"/>
  <text x="280" y="115" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#0369a1">1.0</text>
  <text x="280" y="130" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="bold" fill="#0f172a">Touch Input</text>
  <text x="280" y="142" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#475569">UI Dispatch</text>

  <!-- PROCESS 2.0: Motor & Actuator Control -->
  <circle cx="490" cy="120" r="45" fill="#e0f2fe" stroke="#0284c7" stroke-width="2" filter="url(#dfd-shadow)"/>
  <text x="490" y="115" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#0369a1">2.0</text>
  <text x="490" y="130" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="bold" fill="#0f172a">Motor &amp; Servo</text>
  <text x="490" y="142" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#475569">Failsafe Loop</text>

  <!-- PROCESS 3.0: Sensor Acquisition -->
  <circle cx="280" cy="400" r="45" fill="#e0f2fe" stroke="#0284c7" stroke-width="2" filter="url(#dfd-shadow)"/>
  <text x="280" y="395" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#0369a1">3.0</text>
  <text x="280" y="410" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="bold" fill="#0f172a">Sensor ADC</text>
  <text x="280" y="422" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#475569">Sampling</text>

  <!-- PROCESS 4.0: Video Stream Proxy -->
  <circle cx="490" cy="270" r="45" fill="#e0f2fe" stroke="#0284c7" stroke-width="2" filter="url(#dfd-shadow)"/>
  <text x="490" y="265" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#0369a1">4.0</text>
  <text x="490" y="280" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="bold" fill="#0f172a">MJPEG Stream</text>
  <text x="490" y="292" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#475569">Proxy Server</text>

  <!-- PROCESS 5.0: YOLO & CV Diagnostics -->
  <circle cx="700" cy="270" r="45" fill="#e0f2fe" stroke="#0284c7" stroke-width="2" filter="url(#dfd-shadow)"/>
  <text x="700" y="265" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#0369a1">5.0</text>
  <text x="700" y="280" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="bold" fill="#0f172a">YOLOv8 &amp; HSV</text>
  <text x="700" y="292" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#475569">Pathology</text>

  <!-- PROCESS 6.0: Irrigation Decision -->
  <circle cx="700" cy="450" r="45" fill="#e0f2fe" stroke="#0284c7" stroke-width="2" filter="url(#dfd-shadow)"/>
  <text x="700" y="445" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#0369a1">6.0</text>
  <text x="700" y="460" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="bold" fill="#0f172a">Agronomic</text>
  <text x="700" y="472" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#475569">Decision Engine</text>

  <!-- DATA STORES -->
  <!-- D1: ESP32 RAM Cache -->
  <line x1="390" y1="400" x2="470" y2="400" stroke="#334155" stroke-width="2"/>
  <line x1="390" y1="430" x2="470" y2="430" stroke="#334155" stroke-width="2"/>
  <text x="430" y="420" text-anchor="middle" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#334155">D1: ESP32 RAM</text>

  <!-- D2: SQLite DB -->
  <line x1="840" y1="360" x2="940" y2="360" stroke="#334155" stroke-width="2"/>
  <line x1="840" y1="390" x2="940" y2="390" stroke="#334155" stroke-width="2"/>
  <text x="890" y="380" text-anchor="middle" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#334155">D2: agrivise.db</text>

  <!-- D3: YOLOv8 Weights -->
  <line x1="840" y1="210" x2="940" y2="210" stroke="#334155" stroke-width="2"/>
  <line x1="840" y1="240" x2="940" y2="240" stroke="#334155" stroke-width="2"/>
  <text x="890" y="230" text-anchor="middle" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#334155">D3: yolov8n.pt</text>

  <!-- DATA FLOWS (ARROWS & LABELS) -->
  <!-- Farmer -> 1.0 -->
  <line x1="175" y1="120" x2="235" y2="120" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="205" y="112" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">Touch D-Pad</text>

  <!-- 1.0 -> 2.0 -->
  <line x1="325" y1="120" x2="445" y2="120" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="385" y="112" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">HTTP /forward, etc.</text>

  <!-- 2.0 -> Physical Actuators -->
  <line x1="490" y1="75" x2="490" y2="60" stroke="#0369a1" stroke-width="1.5"/>
  <line x1="490" y1="60" x2="100" y2="60" stroke="#0369a1" stroke-width="1.5"/>
  <line x1="100" y1="60" x2="100" y2="80" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="295" y="55" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">PWM &amp; GPIO Signals (Motors, Servo, Pump)</text>

  <!-- Environment -> 3.0 (Sensors) -->
  <line x1="175" y1="480" x2="245" y2="425" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="210" y="465" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">Physical Signals</text>

  <!-- 3.0 -> D1 (RAM Cache) -->
  <line x1="325" y1="405" x2="390" y2="405" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="357" y="398" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">ADC Raw</text>

  <!-- D1 -> 6.0 -->
  <line x1="470" y1="415" x2="655" y2="450" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="560" y="425" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">JSON /data</text>

  <!-- Environment -> 4.0 (Camera) -->
  <line x1="175" y1="510" x2="460" y2="295" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="320" y="360" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">Light / Photons → OV2640</text>

  <!-- 4.0 -> 5.0 (Frames) -->
  <line x1="535" y1="270" x2="655" y2="270" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="595" y="262" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">Raw JPEG Frames</text>

  <!-- D3 -> 5.0 (Weights) -->
  <line x1="840" y1="235" x2="745" y2="260" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="800" y="240" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">Neural Weights</text>

  <!-- 5.0 -> 6.0 (Pathology) -->
  <line x1="700" y1="315" x2="700" y2="405" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="705" y="360" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">Disease Labels</text>

  <!-- 6.0 -> D2 (Log) -->
  <line x1="745" y1="435" x2="840" y2="385" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="800" y="415" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">Store Diagnostic</text>

  <!-- 5.0 -> Farmer (Annotated Video & HUD) -->
  <line x1="700" y1="225" x2="700" y2="180" stroke="#0369a1" stroke-width="1.5"/>
  <line x1="700" y1="180" x2="160" y2="180" stroke="#0369a1" stroke-width="1.5"/>
  <line x1="160" y1="180" x2="160" y2="160" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="430" y="175" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">Annotated MJPEG Video + Disease Prescriptions + Telemetry Cards</text>

  <!-- 6.0 -> 2.0 (Relay trigger) -->
  <line x1="700" y1="495" x2="700" y2="580" stroke="#0369a1" stroke-width="1.5"/>
  <line x1="700" y1="580" x2="520" y2="580" stroke="#0369a1" stroke-width="1.5"/>
  <line x1="520" y1="580" x2="520" y2="165" stroke="#0369a1" stroke-width="1.5" marker-end="url(#dfd-arrow)"/>
  <text x="610" y="575" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#0369a1">Automated Irrigation Trigger (/pumpOn /pumpOff)</text>
</svg>
"""
