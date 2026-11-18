# ============================================================
# AGRO-VATORS: 100 TECHNICAL QUESTIONS & ANSWERS
# Comprehensive Viva, Defense & Engineering Reference
# ============================================================

QUESTIONS_AND_ANSWERS = [
    # ------------------------------------------------------------
    # DOMAIN 1: PROJECT OVERVIEW & SYSTEM PHILOSOPHY (Q1 - Q10)
    # ------------------------------------------------------------
    {
        "q": "1. What is the core problem AGRO-VATORS solves compared to traditional farming methods?",
        "a": "Traditional agriculture relies on manual visual crop inspection and broad-spectrum chemical spraying, leading to delayed disease detection, pesticide overuse, soil degradation, and water waste. AGRO-VATORS replaces manual labor with an autonomous edge robotic platform that performs sub-surface soil moisture logging, localized AI leaf disease diagnosis, and targeted root-zone micro-irrigation without requiring cloud connectivity."
    },
    {
        "q": "2. Why does the system use a Quad-Tier Architecture rather than a centralized cloud architecture?",
        "a": "Agricultural fields in rural regions often suffer from poor or non-existent 4G/5G cellular connectivity. A cloud-dependent system suffers from high latency, dropped connections, and bandwidth costs when streaming video. The Quad-Tier Architecture partitions responsibilities across Tier 1 (Real-time robotics MCU), Tier 2 (Local 2.4 GHz Wi-Fi hotspot), Tier 3 (Edge laptop AI server), and Tier 4 (Android mobile console), achieving zero-cloud independence with sub-50ms latency."
    },
    {
        "q": "3. Why are there two separate ESP32 microcontrollers instead of just one?",
        "a": "The ESP32-CAM's camera driver (OV2640 with DMA) and JPEG compression demand substantial memory bandwidth and DMA channels. Running 4 high-frequency PWM motor channels, servo PWM, analog ADC sampling, I2C OLED updating, and multi-client web serving on the same chip causes CPU starvation, frame dropping, and erratic motor pulsing. Separating vision (ESP32-CAM) from real-time robotics (ESP32 DevKit V1) guarantees deterministic, stutter-free performance."
    },
    {
        "q": "4. Why were the Ultrasonic sensor (HC-SR04) and GPS module decoupled in the final build?",
        "a": "The legacy code utilized blocking pulseIn() calls on the ultrasonic echo pin which held the CPU for up to 30ms per measurement, causing noticeable motor stutter. Furthermore, the echo pin was physically mapped to GPIO 33, causing a direct electrical conflict with the water pump relay. GPS UART2 polling introduced serial buffer latency while providing negligible benefit for localized furrow-level navigation. Decoupling them eliminated all CPU freezes and pin contention."
    },
    {
        "q": "5. What are the primary operating modes of the rover?",
        "a": "The rover operates in two modes: (1) Connected AI Mode, where the mobile app communicates through the laptop Flask server (port 5001) for live YOLOv8 bounding boxes and automated sensor logging; and (2) Standalone Direct Mode, where the mobile app connects directly to the master ESP32 (port 80) for full manual driving, servo probe deployment, and pump irrigation if the laptop is absent."
    },
    {
        "q": "6. How does the rover handle safety during communication loss?",
        "a": "The firmware implements a hardware-level FreeRTOS watchdog timer (DRIVE_WATCHDOG_MS = 600ms). If the rover is actively moving and does not receive a valid directional keep-alive packet within 600ms, the ESP32 automatically executes stopMotor(), cutting power to all H-bridge channels to prevent runaway collisions."
    },
    {
        "q": "7. What makes AGRO-VATORS cost-effective compared to commercial agricultural robots?",
        "a": "Commercial agricultural robots (such as John Deere See & Spray or FarmWise) utilize expensive RTK-GPS, LiDAR, and industrial IPCs costing $10,000–$50,000+. AGRO-VATORS leverages commercial off-the-shelf (COTS) microcontrollers (ESP32), standard 12V DC geared motors, lightweight YOLOv8 nano models, and an operator's existing Android smartphone, reducing the total bill of materials to under $100."
    },
    {
        "q": "8. What is the spatial resolution and working distance of the rover's camera?",
        "a": "The OV2640 sensor is configured for 240x240 / 320x240 native acquisition, upscaled and CLAHE-filtered to 640x480 on the laptop. Its focal length is calibrated for an optimal working distance of 15 cm to 45 cm from the crop foliage, providing sufficient pixel density to identify micro-lesions as small as 2 mm in diameter."
    },
    {
        "q": "9. How is the rover powered in the field?",
        "a": "The chassis is powered by a central 12V rechargeable Lithium-ion battery pack. The 12V rail directly feeds the L298N motor driver for high-torque wheel actuation. The L298N onboard 5V buck regulator steps down the voltage to 5V to power the ESP32 VIN, servo rails, and relay coil, while the ESP32 onboard AMS1117 regulator supplies clean 3.3V to the sensors and OLED display."
    },
    {
        "q": "10. What crops can AGRO-VATORS monitor out of the box?",
        "a": "The visual pathology engine and soil algorithms are pre-calibrated for solanaceous crops (tomatoes, potatoes, eggplants), leafy greens, chili peppers, cucurbits, and cereal crops (wheat, rice), detecting both broad fungal blights and specific nutrient deficiencies common across all broad-leaf vegetation."
    },

    # ------------------------------------------------------------
    # DOMAIN 2: HARDWARE ARCHITECTURE & MICROCONTROLLERS (Q11 - Q20)
    # ------------------------------------------------------------
    {
        "q": "11. What are the key architectural specifications of the ESP32 DevKit V1?",
        "a": "The ESP32 DevKit V1 features a Tensilica Xtensa Dual-Core 32-bit LX6 microprocessor operating at 240 MHz, 520 KB SRAM, 448 KB ROM, 4 MB external SPI flash, integrated 2.4 GHz 802.11 b/g/n Wi-Fi, dual-mode Bluetooth (classic and BLE), hardware PWM timers (LEDC), and two 12-bit SAR analog-to-digital converters (ADC1 and ADC2)."
    },
    {
        "q": "12. Why are all analog sensors connected specifically to ADC1 on the ESP32?",
        "a": "On the ESP32, ADC2 (GPIOs 0, 2, 4, 12, 13, 14, 15, 25, 26, 27) is shared with the internal Wi-Fi subsystem. When Wi-Fi is active in station or AP mode, any call to analogRead() on an ADC2 pin fails or returns invalid zero/overflow data. Therefore, the soil sensor (GPIO 34) and LDR (GPIO 35) are strictly mapped to ADC1, which operates independently of the Wi-Fi hardware."
    },
    {
        "q": "13. What is the role of the CP2102 chip on the ESP32 board?",
        "a": "The Silicon Labs CP2102 is a USB-to-UART bridge controller that converts USB communication from a PC into asynchronous serial TTL signals (TX/RX) on GPIO 1 and GPIO 3. It also controls the RTS and DTR lines to automatically toggle GPIO 0 and the EN (Reset) pin, allowing hands-free flashing from the Arduino CLI."
    },
    {
        "q": "14. What happens if the ESP32 auto-reset circuit fails during code upload?",
        "a": "On some ESP32 DevKit boards, the timing capacitor on the EN line is slightly out of tolerance. If the board fails to enter download mode (displaying 'Connecting........_____'), holding down the physical BOOT button on the ESP32 pulls GPIO 0 to ground upon reset, forcing the ROM bootloader into serial flashing mode."
    },
    {
        "q": "15. What are the memory and hardware limitations of the ESP32-CAM module?",
        "a": "The ESP32-CAM module lacks an onboard USB-to-serial chip (requiring an external FTDI adapter for programming) and has only a limited number of exposed GPIOs. However, it integrates 4MB of external pseudo-static RAM (PSRAM), which is critical for buffering high-resolution uncompressed JPEG camera frames before transmission."
    },
    {
        "q": "16. How does the 0.96-inch SSD1306 OLED communicate with the ESP32?",
        "a": "The SSD1306 OLED communicates over the I2C serial protocol using GPIO 21 (SDA) and GPIO 22 (SCL) at a 400 kHz Fast-Mode clock speed. The default 7-bit slave address is 0x3C. The display draws only ~20mA because OLED pixels emit their own light without requiring a backlight."
    },
    {
        "q": "17. What information is displayed on the onboard OLED during rover operation?",
        "a": "The OLED renders a multi-line diagnostic HUD showing: (1) Current Wi-Fi Connection & IP Address, (2) Ambient Temperature (°C) and Humidity (%), (3) Soil Moisture raw ADC value, (4) SG90 Soil Probe current angle, and (5) Water Pump operational status (ON/OFF)."
    },
    {
        "q": "18. What is FreeRTOS and how does the ESP32 firmware leverage it?",
        "a": "FreeRTOS is a real-time preemptive operating system built into the ESP32 Arduino framework. The ESP32 distributes tasks across Core 0 (which handles Wi-Fi stacks and TCP/IP networking) and Core 1 (which handles user loop execution, motor timing, sensor polling, and display updates), preventing network delays from locking the robot's physical actuation."
    },
    {
        "q": "19. Why is GPIO 33 an appropriate choice for controlling the pump relay?",
        "a": "GPIO 33 is an RTC-capable, general-purpose digital input/output pin on ADC1. Unlike strapping pins (GPIO 0, 2, 5, 12, 15), GPIO 33 has no boot-mode configuration requirements during power-up, meaning the relay will not glitch or falsely toggle during an MCU restart."
    },
    {
        "q": "20. What is brownout detection on the ESP32 and how is it prevented in AGRO-VATORS?",
        "a": "The ESP32 features an internal brownout detector that triggers a hardware reset if the supply voltage drops below 2.8V. When 4 DC motors start simultaneously, their inductive inrush current can cause a temporary voltage dip on the battery. This is prevented by using a high-discharge Li-ion battery and placing a 1000uF electrolytic capacitor across the power rails to smooth transient voltage sags."
    },

    # ------------------------------------------------------------
    # DOMAIN 3: ACTUATORS, MOTOR DRIVING & POWER ELECTRONICS (Q21 - Q30)
    # ------------------------------------------------------------
    {
        "q": "21. How does the L298N Dual H-Bridge motor driver work?",
        "a": "The L298N contains two full-bridge drivers comprising eight high-power bipolar transistors. By switching diagonal transistor pairs (e.g., Q1 and Q4 ON, Q2 and Q3 OFF), current is forced through the DC motor coils in one direction (Forward). Reversing the pair switches current flow (Backward). Setting both inputs to LOW stops the motor by disconnecting power."
    },
    {
        "q": "22. What is the truth table for the 4WD motor system on the rover?",
        "a": "The 4 motors are paired into Left (IN1, IN2) and Right (IN3, IN4) channels: Forward = [IN1=1, IN2=0, IN3=1, IN4=0]; Backward = [IN1=0, IN2=1, IN3=0, IN4=1]; Pivot Left = [IN1=0, IN2=1, IN3=1, IN4=0]; Pivot Right = [IN1=1, IN2=0, IN3=0, IN4=1]; Stop = [IN1=0, IN2=0, IN3=0, IN4=0]."
    },
    {
        "q": "23. Why did we avoid using analogWrite() or PWM on GPIO 26?",
        "a": "On the ESP32 Arduino Core v3.x, legacy analogWrite() calls on certain strapping/output pins conflict with the new LEDC hardware channel allocator. Using high-speed digital switching (digitalWrite) provides 100% full-voltage torque directly to the geared wheels, which is essential for pushing through uneven, high-friction field furrows without motor stalling."
    },
    {
        "q": "24. What is the role of the 5V jumper on the L298N driver board?",
        "a": "The L298N board contains an onboard 78M05 linear voltage regulator. When the jumper is installed and the motor supply is 12V (below the 12V limit for the regulator), the 78M05 steps down the 12V battery input to provide a clean 5V output on the screw terminal, which is routed to power the ESP32 VIN pin."
    },
    {
        "q": "25. Why is a common ground strictly necessary between the battery, L298N, and ESP32?",
        "a": "Voltage is a relative difference in electrical potential. If the ESP32 logic ground is not physically bonded to the L298N driver ground, the 3.3V control signals on IN1–IN4 have no return path. This causes floating logic, erratic motor behavior, or complete failure of the driver to register digital HIGH signals."
    },
    {
        "q": "26. What are flyback diodes and why are they critical in the L298N driver?",
        "a": "DC motors are inductive loads. When a motor is abruptly stopped or reversed, its collapsing magnetic field generates a massive reverse voltage spike (back-EMF) that can exceed 50V. The L298N module includes 8 onboard Schottky flyback diodes that clamp these spikes safely to the power rails, protecting the driver transistors from breakdown."
    },
    {
        "q": "27. What is skid-steering and why was it chosen over Ackermann steering?",
        "a": "Skid-steering (tank-style steering) rotates the rover by driving the left and right wheels in opposite directions at the same time. This enables zero-radius turning (pivoting on the spot), allowing the rover to turn around within narrow 50 cm crop rows without requiring complex mechanical steering knuckles, tie rods, or rack-and-pinion linkages."
    },
    {
        "q": "28. What gear ratio and torque do the DC geared motors provide?",
        "a": "The rover utilizes four yellow TT-style DC geared motors with a 1:48 reduction gearbox. At 12V input, they deliver approximately 300 RPM unloaded and ~1.5 kg·cm of stall torque per wheel, providing sufficient mechanical advantage to propel the 2.5 kg rover over loose dirt, mulch, and small pebbles."
    },
    {
        "q": "29. How does the software prevent shoot-through in the H-bridge?",
        "a": "Shoot-through occurs when both high-side and low-side transistors in an H-bridge leg conduct simultaneously, creating a direct short circuit across the battery. In our firmware, directional transitions always execute an explicit intermediate stopMotor() call with a 10ms delay before reversing polarity, ensuring the conducting transistors have fully turned off."
    },
    {
        "q": "30. What is the power consumption of the rover during active driving?",
        "a": "During steady driving on flat ground, each motor draws approximately 180–250mA, totaling ~800mA to 1.0A for all four motors. Under stall conditions (e.g., hitting a furrow wall), current can peak at 2.4A. The 12V 2600mAh Li-ion battery pack provides approximately 2.5 to 3.5 hours of continuous field scouting."
    },

    # ------------------------------------------------------------
    # DOMAIN 4: SOIL PROBE MECHANISM & SERVO DYNAMICS (Q31 - Q40)
    # ------------------------------------------------------------
    {
        "q": "31. Why is the soil moisture probe mounted on a motorized servo arm rather than fixed rigidly?",
        "a": "If the soil probe were fixed permanently below the chassis, it would drag through weeds, catch on rocks, and bend or snap while the rover travels between rows. Furthermore, dragging a live electrical probe creates furrow ruts and causes rapid galvanic corrosion. Motorizing the probe allows it to stay safely retracted during travel and deploy only when taking a reading."
    },
    {
        "q": "32. What servo motor is used and what pin controls it?",
        "a": "The probe mechanism is driven by a TowerPro SG90 micro servo attached to ESP32 GPIO 25. The SG90 operates on 5V power and receives a 50 Hz pulse-width modulated (PWM) control signal generated by the ESP32's hardware LEDC timer peripheral."
    },
    {
        "q": "33. What is the calibrated mechanical angle range of the soil probe arm?",
        "a": "The firmware restricts the servo motion to a calibrated range between TILT_MIN = 20° and TILT_MAX = 160°. An angle of 20°–55° corresponds to the 'Tuck Up / Retracted' transport position, while 135°–160° drives the probe vertically downward into the soil profile to a depth of approximately 5–7 cm."
    },
    {
        "q": "34. How does the firmware achieve smooth servo movement without blocking the CPU?",
        "a": "Instead of executing a blocking for-loop with delay(), the firmware uses a non-blocking slew-rate interpolator in loop(). Every 20ms, it compares the current tiltAngle to the targetTilt. If they differ, it steps the angle by 5° toward the target. This provides smooth physical motion, eliminates current spikes, and leaves the CPU free to handle HTTP requests."
    },
    {
        "q": "35. How does the operator control the soil probe from the Android app?",
        "a": "The Android UI features an interactive touch slider that allows continuous angle adjustment from 20° to 160°, along with two quick-action buttons: '[⬆ Retract (Drive)]' which commands 55° (safe travel), and '[⬇ Deploy (Soil)]' which commands 135° (standard insertion depth)."
    },
    {
        "q": "36. What endpoints does the ESP32 expose for soil probe articulation?",
        "a": "The ESP32 REST server exposes: (1) /probe/deploy (sets target to 135°), (2) /probe/retract (sets target to 55°), (3) /probe/angle?val=X (sets target to angle X), and legacy aliases /servoUp and /servoDown."
    },
    {
        "q": "37. What mechanical linkage connects the SG90 servo horn to the soil probe?",
        "a": "The soil probe is affixed to a 3D-printed lightweight acrylic swing-arm fastened to the single-arm nylon horn of the SG90 servo. The arm geometry converts 110° of angular servo rotation into 6.5 cm of vertical linear displacement into the root zone."
    },
    {
        "q": "38. What prevents the SG90 servo from stripping its gears if it encounters a stone?",
        "a": "The nylon gears of the SG90 are rated for 1.8 kg·cm of torque. In the event that the probe encounters an impenetrable rock or compacted hardpan, the mechanical swing-arm incorporates a compliant flexible mounting tab that deflects before the gear teeth exceed their shear stress threshold."
    },
    {
        "q": "39. Why does the ESP32 Servo library use LEDC hardware timers?",
        "a": "Standard Arduino servo libraries rely on software timer interrupts that can introduce jitter when Wi-Fi interrupts fire. The ESP32Servo library attaches to the ESP32's dedicated LEDC (LED Control) hardware PWM channels, generating crystal-stable 50 Hz pulses with 16-bit resolution completely in hardware."
    },
    {
        "q": "40. How long does the rover pause for the probe to stabilize before reading soil moisture?",
        "a": "After commanding deployment to 135°, the operator or automated routine pauses for 1.5 seconds. This allows mechanical motion to cease and allows the capacitive/conductive soil interfaces to establish stable electrical contact with the surrounding soil water film before sampling ADC1."
    },

    # ------------------------------------------------------------
    # DOMAIN 5: WATER PUMP RELAY & FLUID ELECTRONICS (Q41 - Q50)
    # ------------------------------------------------------------
    {
        "q": "41. What type of relay module is used for the water pump?",
        "a": "The system uses a single-channel Songle 5V electromagnetic relay module (SRD-05VDC-SL-C) featuring an onboard optocoupler, protective freewheeling diode, transistor driver, and dual status LEDs (Red for power, Green for relay coil trigger status)."
    },
    {
        "q": "42. Explain the classic '3.3V ESP32 vs 5V Relay Voltage Trap' that was diagnosed and resolved.",
        "a": "The 5V relay module's optocoupler is referenced to 5V VCC. When powered by 5V and controlled by a 3.3V ESP32 GPIO, setting the GPIO to HIGH (3.3V) results in a voltage differential across the optocoupler of 5.0V - 3.3V = 1.7V. Because 1.7V exceeds the forward voltage of the optocoupler LED (~1.2V), current never stops flowing! The relay remains permanently stuck ON with both LEDs glowing. Moving the relay's VCC to 3.3V eliminates this potential difference (3.3V - 3.3V = 0V), enabling complete shutoff."
    },
    {
        "q": "43. What is the difference between an Active-HIGH and Active-LOW relay module?",
        "a": "An Active-HIGH relay energizes its coil when its input pin receives a positive voltage (HIGH / 3.3V/5V) relative to ground. An Active-LOW relay energizes its coil when its input pin is pulled down to 0V (GND), creating current flow from VCC through the optocoupler into the sinking GPIO pin."
    },
    {
        "q": "44. Why did shaking or tapping the relay make it click before the fix?",
        "a": "When the relay was receiving an indeterminate floating signal or experiencing borderline coil voltage, the electromagnetic coil lacked the full magnetic flux required to overcome the internal mechanical return spring. Physically shaking or tapping the module provided mechanical momentum, allowing the magnetic armature to temporarily snap shut."
    },
    {
        "q": "45. How is the water pump relay configured in the final firmware?",
        "a": "The relay trigger pin is defined on GPIO 33. The firmware utilizes Active-LOW logic (relayActiveLow = true) powered by the 3.3V rail. In the web dashboard and backend, the endpoints are mapped so that pressing 'Pump ON' sinks GPIO 33 to GND (energizing the pump), while pressing 'Pump OFF' drives GPIO 33 to 3.3V (releasing the pump)."
    },
    {
        "q": "46. What are the screw terminals on the relay module (COM, NO, NC)?",
        "a": "COM = Common contact terminal. NO = Normally Open (disconnected from COM when relay is unpowered; connects to COM when coil energizes). NC = Normally Closed (connected to COM when unpowered; disconnects when coil energizes). The pump is wired across COM and NO."
    },
    {
        "q": "47. Why must the water pump power be isolated from the ESP32 power rail?",
        "a": "DC water pumps contain electric motors with rotating brushes that generate significant electromagnetic interference (EMI) and heavy inductive current surges (up to 800mA stall). If powered directly from the ESP32 3.3V or 5V regulator, the voltage drop would cause an immediate ESP32 brownout reset and freeze the CPU."
    },
    {
        "q": "48. What type of water pump is used and what is its flow rate?",
        "a": "The system utilizes a 3V–5V DC mini submersible centrifugal water pump with a flow rate of approximately 80 to 120 liters per hour (L/h) and a static lift head of 30 to 50 cm. It connects to 6mm flexible food-grade silicone tubing routed to an adjustable drip emitter positioned over the plant root zone."
    },
    {
        "q": "49. What software safety feature prevents continuous flooding if a client disconnects?",
        "a": "The backend Flask controller implements an irrigation safety timer (PUMP_RUN_SECONDS = 10s). When automated irrigation triggers, a background Python threading.Timer automatically dispatches a /pumpOff command after 10 seconds, followed by an enforced 5-minute cooldown (PUMP_COOLDOWN_SECONDS = 300s) to prevent overwatering."
    },
    {
        "q": "50. What endpoints on the Flask server control the water pump?",
        "a": "The Flask server exposes: (1) /pump/on (starts the pump), (2) /pump/off (stops the pump), (3) /pump/test (executes a 1.2-second diagnostic pulse), and (4) /pump/invert (toggles Active-HIGH / Active-LOW logic in RAM for on-the-fly polarity calibration)."
    },

    # ------------------------------------------------------------
    # DOMAIN 6: ENVIRONMENTAL SENSORS & ANALOG TELEMETRY (Q51 - Q60)
    # ------------------------------------------------------------
    {
        "q": "51. What sensors are integrated into the AGRO-VATORS environmental subsystem?",
        "a": "The environmental subsystem comprises: (1) A DHT11 digital sensor for ambient air temperature and relative humidity, (2) An analog soil moisture probe measuring soil volumetric water content, and (3) A photoresistor (LDR) measuring ambient solar radiation intensity."
    },
    {
        "q": "52. How does the DHT11 sensor communicate with the ESP32 on GPIO 4?",
        "a": "The DHT11 uses a proprietary single-wire bi-directional digital protocol. The ESP32 initiates communication by pulling GPIO 4 LOW for 18ms and then releasing it. The DHT11 responds with an 80us LOW signal followed by 40 bits of serial data (16 bits humidity, 16 bits temperature, 8 bits checksum). The firmware polls it at non-blocking 2-second intervals."
    },
    {
        "q": "53. What are the measurement ranges and accuracy of the DHT11 sensor?",
        "a": "Temperature range: 0°C to 50°C with ±2°C accuracy. Humidity range: 20% to 90% RH with ±5% accuracy. While not laboratory-grade, it provides rapid, dependable relative readings for detecting microclimate humidity spikes that facilitate fungal spore germination."
    },
    {
        "q": "54. How does the analog soil moisture probe work and how are its raw values interpreted?",
        "a": "The soil probe measures soil electrical conductivity between two PCB prongs. The onboard comparator outputs an analog voltage sampled by ESP32 ADC1 on GPIO 34 (12-bit, 0–4095). A raw reading of ~4095 indicates open-circuit air (completely dry); 2500–3500 represents semi-dry soil needing irrigation; and 1400–2200 represents thoroughly saturated, healthy root-zone soil."
    },
    {
        "q": "55. Why is galvanic corrosion a concern with resistive soil probes and how does the rover mitigate it?",
        "a": "Continuous DC current flowing through moist soil causes rapid electrolytic oxidation (galvanic corrosion) of copper probe traces, destroying the probe within weeks. AGRO-VATORS mitigates this by: (1) Mechanically lifting the probe out of the soil during driving, and (2) Sampling the analog pin only intermittently during inspection stops."
    },
    {
        "q": "56. How is the Light Dependent Resistor (LDR) circuit constructed on GPIO 35?",
        "a": "The LDR is configured in a voltage divider circuit with a 10kΩ fixed pull-up resistor connected between 3.3V and GND. As ambient sunlight increases, the LDR resistance drops (from ~1MΩ in total darkness to ~1kΩ in bright sun), causing the analog voltage on GPIO 35 to drop toward zero. The 12-bit ADC converts this into an ambient light value."
    },
    {
        "q": "57. How does the firmware prevent sensor reading jitter on the analog pins?",
        "a": "In updateSensorCache(), analogRead() values on GPIO 34 and GPIO 35 are passed through a rolling software low-pass filter (averaging 5 consecutive samples spaced 2ms apart) to filter out high-frequency electrical noise generated by the motor H-bridge."
    },
    {
        "q": "58. What is the update frequency of the rover's sensor cache?",
        "a": "The main loop executes updateSensorCache() every 1000 milliseconds (SENSOR_INTERVAL = 1000ms), while the DHT11 is polled every 2000 milliseconds (DHT_INTERVAL = 2000ms). This prevents I/O bus contention while keeping the JSON /data payload fresh for web and mobile clients."
    },
    {
        "q": "59. How is sensor telemetry serialized and sent to the laptop and mobile app?",
        "a": "When an HTTP GET request hits the ESP32 endpoint /data, the handleData() function serializes the cached sensor variables into a standard JSON string: {\"temperature\":27.4,\"humidity\":75.4,\"soil\":4095,\"light\":234,\"pump\":\"OFF\",\"probeAngle\":55,\"mode\":\"MANUAL\"}."
    },
    {
        "q": "60. How does the system handle sensor failures (e.g., if the DHT11 disconnects)?",
        "a": "The firmware uses isnan() validation checks. If dht.readTemperature() returns NaN due to a disconnected jumper wire, the firmware preserves the last known valid temperature in cachedTemperature rather than broadcasting corrupt data or crashing the web server."
    },

    # ------------------------------------------------------------
    # DOMAIN 7: CAMERA STREAMING & ESP32-CAM ARCHITECTURE (Q61 - Q70)
    # ------------------------------------------------------------
    {
        "q": "61. What camera sensor is used on the ESP32-CAM and what resolution does it capture?",
        "a": "The ESP32-CAM uses an OmniVision OV2640 2-megapixel CMOS image sensor supporting native resolutions from QQVGA (160x120) up to UXGA (1600x1200). For real-time low-latency field streaming, the rover firmware sets the sensor to 240x240 (QVGA cropped), which optimizes frame throughput over 2.4 GHz Wi-Fi."
    },
    {
        "q": "62. How does the camera stream video over HTTP?",
        "a": "The ESP32-CAM streams video as a Motion JPEG (MJPEG) stream over HTTP. The server returns an HTTP response with Content-Type: multipart/x-mixed-replace; boundary=frame. Individual JPEG frames are continuously streamed across the open TCP socket separated by boundary headers."
    },
    {
        "q": "63. Why did the video stream initially show a black screen on the Android app, and how was it solved?",
        "a": "Android's native WebView rendering engine requires strict RFC-compliant HTTP multipart headers, including Content-Type: image/jpeg and a valid Content-Length: [bytes] header for each individual boundary frame. The legacy code omitted Content-Length, causing Android's Chromium decoder to discard frames as incomplete. Adding Content-Length and implementing background double-buffering (new Image()) on the frontend completely fixed the stream."
    },
    {
        "q": "64. What is the role of the centralized camera worker thread in app.py?",
        "a": "In multi-client environments, having both the browser, phone, and AI inference loop connect directly to the ESP32-CAM saturates its single-core lightweight HTTP server, causing dropped connections. In app.py, a single background daemon thread (cam_worker_thread) polls the ESP32-CAM at ~18 FPS, runs YOLOv8 and OpenCV overlays, and stores the latest frame in a thread-safe memory buffer (camera_lock)."
    },
    {
        "q": "65. What framerate and latency does the video pipeline achieve?",
        "a": "The camera streaming pipeline achieves 16 to 20 frames per second (FPS) over the local phone1 Wi-Fi hotspot with an end-to-end glass-to-glass latency of approximately 45–65 milliseconds, providing responsive visual feedback for real-time manual driving."
    },
    {
        "q": "66. How does the ESP32-CAM handle challenging outdoor lighting conditions?",
        "a": "Outdoor field lighting varies from harsh direct sunlight to heavy canopy shadows. In app.py, incoming frames are converted to the LAB color space, where Contrast Limited Adaptive Histogram Equalization (CLAHE) is applied to the L (Luminance) channel before converting back to BGR. This normalizes lighting across leaves without distorting color hue."
    },
    {
        "q": "67. How does the camera pan servo work?",
        "a": "The camera module is mounted on an SG90 micro servo connected to ESP32 GPIO 13. The operator can pan the camera horizontally across a 30° to 150° viewing arc using on-screen pan controls, allowing inspection of crop foliage on either side of the rover without needing to rotate the rover chassis."
    },
    {
        "q": "68. What happens if the ESP32-CAM disconnects or loses power?",
        "a": "The camera worker thread in app.py catches connection timeouts (CAMERA_TIMEOUT = 3s). If the camera drops offline, make_offline_frame() dynamically generates a synthetic 640x480 test card with a dark gray background and clear yellow text: 'CAMERA OFFLINE - CHECKING 192.168.93.28', preventing UI crashes."
    },
    {
        "q": "69. What are the IP addresses of the camera and master controller on the network?",
        "a": "On the phone1 local hotspot subnet (192.168.93.0/24): (1) Master ESP32 DevKit V1 = 192.168.93.164, (2) ESP32-CAM Vision Node = 192.168.93.28, (3) Laptop AI Core = 192.168.93.173, and (4) Android Phone Controller = 192.168.93.175."
    },
    {
        "q": "70. What is the JPEG compression quality setting on the ESP32-CAM?",
        "a": "The JPEG compression quality is configured to jpeg_quality = 12 (on a scale where 0 is highest quality and 63 is lowest). A setting of 12 provides sharp leaf vein detail with average frame sizes of ~8–12 KB, maximizing Wi-Fi packet transfer efficiency."
    },

    # ------------------------------------------------------------
    # DOMAIN 8: ARTIFICIAL INTELLIGENCE, YOLOV8 & COMPUTER VISION (Q71 - Q80)
    # ------------------------------------------------------------
    {
        "q": "71. What deep learning model does AGRO-VATORS use for leaf detection?",
        "a": "The system runs Ultralytics YOLOv8 Nano (yolov8n.pt), a state-of-the-art single-stage convolutional object detection network featuring an anchor-free split head, C2f feature extraction modules, and mosaic data augmentation, optimized for low-latency edge CPU and GPU execution."
    },
    {
        "q": "72. Why was YOLOv8 Nano selected over YOLOv8 Small, Medium, or Large?",
        "a": "YOLOv8 Nano has only 3.2 million parameters and requires just 8.7 GFLOPs of computation. This allows it to run at 20+ FPS on a standard laptop CPU without requiring an expensive dedicated NVIDIA GPU, making the entire setup portable and battery-efficient in the field."
    },
    {
        "q": "73. Explain the Dual-Stage Hybrid Computer Vision Pipeline.",
        "a": "Stage 1 uses YOLOv8 to localize and bound candidate plant leaves, filtering out soil, chassis wheels, and weeds. Stage 2 extracts the pixel Region of Interest (ROI) and applies biochemical HSV color space thresholding and contour morphological analysis to quantify chlorosis, necrotic lesion area, and fungal pustules, merging deep learning with domain-specific plant pathology."
    },
    {
        "q": "74. What is the HSV color space and why is it superior to RGB for plant pathology?",
        "a": "In RGB color space, chromaticity and luminance are intertwined; a shadow completely shifts R, G, and B values. In HSV (Hue, Saturation, Value), Hue represents the pure color wavelength independent of illumination. This allows the system to isolate chlorophyll green (Hue 25–88), chlorosis yellow (Hue 18–28), and necrotic lesion brown (Hue 8–18) regardless of sunlight or cloud cover."
    },
    {
        "q": "75. How does the system calculate the leaf disease severity percentage?",
        "a": "The system segments the total leaf area into green chlorophyll pixels (G), chlorotic yellow pixels (Y), and necrotic brown lesion pixels (B). Severity is mathematically computed as: Severity (%) = (B / (G + Y + B)) * 100 for fungal blights, or (Y / (G + Y + B)) * 100 for nutrient chlorosis."
    },
    {
        "q": "76. How does the system distinguish between a single large lesion and many small spots?",
        "a": "The system applies OpenCV findContours() on the necrotic binary mask. It calculates max_spot_area = max([cv2.contourArea(c) for c in contours]) and spot_count = len([c for c in contours if cv2.contourArea(c) > 25]). A large contiguous area (>400 px) indicates Late Blight, whereas numerous small scattered spots (>8 spots) indicate Septoria Leaf Spot."
    },
    {
        "q": "77. How does the vision engine identify Powdery Mildew?",
        "a": "Powdery mildew produces white or light gray fungal mycelium on the leaf surface. The algorithm creates a brightness mask in HSV (Hue 0–180, Saturation 0–45, Value 185–255) and performs a bitwise-AND with the segmented plant foliage mask, isolating white patches located specifically on the leaf blade."
    },
    {
        "q": "78. How are bounding boxes and disease classifications rendered on the video feed?",
        "a": "In app.py, cv2.rectangle() draws dynamic color-coded bounding boxes on the output frame: Vibrant Green for healthy foliage, Yellow/Gold for chlorosis/deficiency, and Bold Red for active fungal blights. A filled banner with anti-aliased text displays the condition name and confidence percentage."
    },
    {
        "q": "79. What is the role of CLAHE in the preprocessing pipeline?",
        "a": "Contrast Limited Adaptive Histogram Equalization (CLAHE) divides the image into small contextual tiles (8x8 pixels) and equalizes local contrast while clipping histogram amplification. This eliminates harsh glare on waxy crop leaves and illuminates shaded lesions under dense canopies."
    },
    {
        "q": "80. What is the inference time of the combined YOLOv8 + OpenCV diagnostic pipeline?",
        "a": "On an Intel Core i5/i7 laptop CPU, YOLOv8 Nano inference takes approximately 28–35ms per frame, while the OpenCV HSV morphological pipeline takes ~8ms, yielding a total processing latency of ~36–43ms per frame (~23 FPS)."
    },

    # ------------------------------------------------------------
    # DOMAIN 9: PLANT PATHOLOGY, DISEASES & TREATMENT PROTOCOLS (Q81 - Q90)
    # ------------------------------------------------------------
    {
        "q": "81. List all 8 plant conditions detected by the AGRO-VATORS pathology engine.",
        "a": "The 8 conditions are: (1) Early Blight (Alternaria solani), (2) Late Blight (Phytophthora infestans), (3) Crop Leaf Rust (Puccinia spp.), (4) Septoria Leaf Spot (Septoria spp.), (5) Powdery Mildew (Erysiphales), (6) Nitrogen Deficiency, (7) Iron Deficiency (Interveinal Chlorosis), and (8) Healthy Foliage."
    },
    {
        "q": "82. What are the symptoms and treatment for Early Blight (Alternaria solani)?",
        "a": "Symptoms: Concentric dark brown or black target-pattern rings surrounded by a chlorotic yellow halo on older lower leaves. Chemical Treatment: Foliar spray of Copper Oxychloride (2.5g/L water) or Mancozeb 75 WP (2g/L). Cultural Action: Prune lower infected leaves; apply organic mulch to prevent fungal spore splash from the soil."
    },
    {
        "q": "83. What are the symptoms and treatment for Late Blight (Phytophthora infestans)?",
        "a": "Symptoms: Rapidly enlarging water-soaked dark brown or black lesions with pale chlorotic margins, capable of destroying an entire field in days. High-Urgency Treatment: Apply systemic Metalaxyl + Mancozeb (Ridomil Gold MZ @ 2g/L) immediately. Preventive Action: Improve field furrow drainage, widen crop row spacing for airflow, and destroy cull piles."
    },
    {
        "q": "84. What are the symptoms and treatment for Crop Leaf Rust (Puccinia spp.)?",
        "a": "Symptoms: Raised reddish-brown, orange, or copper-colored fungal spore pustules rupturing the epidermis on the lower leaf surface. Treatment: Foliar application of Triazole fungicides (Propiconazole 25 EC or Tebuconazole @ 1ml/L water). Prevention: Plant certified rust-resistant seed cultivars; eradicate alternative weed hosts."
    },
    {
        "q": "85. What are the symptoms and treatment for Septoria Leaf Spot (Septoria spp.)?",
        "a": "Symptoms: Numerous small (2–4mm) circular necrotic spots with dark brown margins and sunken gray centers containing tiny black pycnidia. Treatment: Apply protective Chlorothalonil or Bio-fungicide (Bacillus subtilis). Prevention: Implement a 3-year crop rotation; clear all solanaceous crop debris post-harvest."
    },
    {
        "q": "86. What are the symptoms and treatment for Powdery Mildew (Erysiphales)?",
        "a": "Symptoms: White, talcum-powder-like fungal patches across the upper leaf lamina, causing leaves to curl, brown, and senesce prematurely. Treatment: Spray Wettable Sulfur (2g/L) or cold-pressed emulsified Neem Oil (5ml/L). Prevention: Maximize sunlight canopy penetration; avoid excessive high-nitrogen feeding."
    },
    {
        "q": "87. How does the system differentiate Nitrogen Deficiency from Iron Deficiency?",
        "a": "Both cause chlorosis (yellowing). Nitrogen is a mobile nutrient: deficiency causes uniform pale yellowing starting from the leaf tip and older lower foliage. Iron is an immobile nutrient: deficiency causes interveinal chlorosis on young upper leaves where the leaf blade turns yellow while the primary and secondary veins remain distinctly dark green."
    },
    {
        "q": "88. What is the recommended treatment for Nitrogen and Iron deficiencies?",
        "a": "Nitrogen: Top-dress with Urea (46% N) at 50 kg/ha or Calcium Ammonium Nitrate (CAN); apply compost tea foliar spray. Iron: Apply a foliar spray of Chelated Iron (Fe-EDDHA or Fe-EDTA @ 1g/L water) in the cool early morning; correct alkaline soil with elemental sulfur."
    },
    {
        "q": "89. How does multi-modal telemetry fusion enhance disease diagnosis?",
        "a": "Visuals alone cannot assess environmental risk. The system cross-references camera detections with live telemetry: (1) If Blight is spotted and ambient humidity >75%, it issues an Accelerated Spore Germination Warning; (2) If Blight is spotted and soil ADC <2200 (waterlogged), it blocks irrigation to prevent root-zone fungal multiplication; (3) If Chlorosis is spotted but soil ADC >3800 (drought), it warns to hydrate before fertilizing to avoid root chemical burn."
    },
    {
        "q": "90. How does the system define a 'Healthy Leaf'?",
        "a": "A leaf is classified as Healthy when chlorophyll green coverage exceeds 75% of the segmented foliage, necrotic lesion area is below 5%, and chlorotic yellowing is below 10%, indicating high photosynthetic efficiency and cellular turgidity."
    },

    # ------------------------------------------------------------
    # DOMAIN 10: ANDROID APP, FLASK BACKEND & NETWORKING (Q91 - Q100)
    # ------------------------------------------------------------
    {
        "q": "91. What is the architecture of the native Android application (AgriRover)?",
        "a": "The Android app is built in Java (package com.agrovators.agrirover) using an optimized Hardware-Accelerated WebView container backed by a native WebAppInterface. It features dual-mode URL switching: loading http://192.168.93.173:5001/ when the laptop is online, or falling back to file:///android_asset/index.html for direct ESP32 control."
    },
    {
        "q": "92. How does the WebAppInterface JavaScript bridge operate?",
        "a": "The JavaScript bridge exposes Java methods (sendCommand(), fetchUrl(), showToast()) to the client-side JavaScript running in the WebView. Using the @JavascriptInterface annotation, touch events on the web D-pad trigger asynchronous background Java worker threads via HttpURLConnection, achieving zero UI thread stutter."
    },
    {
        "q": "93. How is the SQLite3 database structured and what data is logged?",
        "a": "The SQLite database (database/agrivise.db) contains a readings table with fields: id (INTEGER PRIMARY KEY), timestamp (DATETIME), temperature (FLOAT), humidity (FLOAT), soil (INTEGER), distance (FLOAT), pump (TEXT), mode (TEXT), latitude (FLOAT), and longitude (FLOAT). New readings are saved at regular intervals."
    },
    {
        "q": "94. What REST API endpoints does the Flask server expose?",
        "a": "Key endpoints include: (1) /video_feed (MJPEG video stream with YOLO overlays), (2) /current_frame.jpg (single JPEG polling fallback), (3) /sensor_data (JSON telemetry), (4) /scan (triggers high-resolution leaf pathology scan), (5) /pump/on and /pump/off (pump controls), (6) /probe/angle (probe servo), and (7) /api/sensors/history (historical telemetry)."
    },
    {
        "q": "95. How does the frontend implement double-buffering for the video stream?",
        "a": "In static/script.js, instead of binding the &lt;img&gt; src directly to the stream (which causes mobile rendering drops), a background worker creates a new Image() object in memory. Once the new JPEG is fully downloaded, it swaps the DOM image source instantaneously, guaranteeing flicker-free video."
    },
    {
        "q": "96. How is internationalization (i18n) implemented in the dashboard?",
        "a": "static/script.js contains a dictionary with translation maps for English, Hindi (हिंदी), and Bengali (বাংলা). All UI text elements carry a data-i18n attribute. When the operator changes the language dropdown, applyTranslations() traverses the DOM and swaps all text content instantly without reloading the page."
    },
    {
        "q": "97. How does the installer package (install.bat) simplify setup on a new laptop?",
        "a": "install.bat automates deployment: (1) Checks for Python 3.10+ in system PATH, (2) Creates an isolated Python virtual environment (venv), (3) Upgrades pip, (4) Installs all dependencies from requirements.txt (Flask, Ultralytics, OpenCV, NumPy), and (5) Creates desktop shortcuts to start_rover.bat."
    },
    {
        "q": "98. What does start_rover.bat do when launched?",
        "a": "start_rover.bat activates the Python virtual environment, sets environment variables (ESP32_MAIN_IP=192.168.93.164, ESP32_CAM_IP=192.168.93.28), launches app.py on port 5001, pauses 2 seconds for server initialization, and automatically opens the dashboard in the default web browser."
    },
    {
        "q": "99. What are the key troubleshooting steps if the rover fails to move?",
        "a": "Check: (1) 12V battery charge state and switch position; (2) L298N power LED is lit and common ground jumper is intact; (3) ESP32 is connected to phone1 hotspot (verify IP on OLED); (4) Drive watchdog has not timed out; (5) Motor wires are firmly screwed into the L298N terminal blocks."
    },
    {
        "q": "100. What are the future research and commercial expansion possibilities for AGRO-VATORS?",
        "a": "Future enhancements include: (1) Integrating micro-LiDAR or stereo-depth cameras for full autonomous row-following without human tele-operation; (2) Adding a multi-nozzle chemical micro-dosing spray boom with selective solenoid valves for targeted weed and blight spraying; (3) Upgrading to an onboard NVIDIA Jetson Orin Nano for embedded deep learning; and (4) Incorporating an RTK-GNSS module for autonomous centimeter-accurate geofenced field mapping."
    }
]
