import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, Response, jsonify, request, redirect, send_from_directory
from ultralytics import YOLO
import cv2
import urllib.request
import numpy as np
import requests
import time
import threading
import base64
from datetime import datetime

from plant_health import scan_plant
from intercrop_engine import recommend_intercrops
from database import init_database, save_sensor_reading, get_sensor_history

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__)
# DATABASE DISABLED FOR CURRENT VERSION (init_database not called)

# ============================================================
# ESP32 CONFIG
# ============================================================
ESP32_CAM_IP = os.getenv("ESP32_CAM_IP", "192.168.93.28")
ESP32_MAIN_IP = os.getenv("ESP32_MAIN_IP", "192.168.93.164")
ESP32_URL = f"http://{ESP32_CAM_IP}/capture"
ESP32_DATA_URL = f"http://{ESP32_MAIN_IP}/data"
ESP32_CONTROL_URL = f"http://{ESP32_MAIN_IP}"
REQUEST_TIMEOUT = 3
CAMERA_TIMEOUT = 3

# ============================================================
# DATABASE (disabled — future: historical sensor graphs)
# ============================================================
last_database_save = 0
DATABASE_SAVE_INTERVAL = 5

# ============================================================
# AUTOMATIC IRRIGATION
# ============================================================
AUTO_IRRIGATION = True
PUMP_RUN_SECONDS = 10          # pump runs for 10s
PUMP_COOLDOWN_SECONDS = 300    # then waits 5 min before running again
last_pump_run = 0
pump_running_until = 0
pump_timer = None
pump_lock = threading.Lock()

# ============================================================
# YOLO MODEL
# ============================================================
model = YOLO("models/yolov8n.pt")
last_detection = "None"

# ============================================================
# SENSOR / STATE
# ============================================================
OFFLINE_SENSOR = {
    "temperature": "--", "humidity": "--", "soil": "--",
    "distance": "--", "pump": "OFF", "relayMode": "ACTIVE_LOW", "mode": "--",
    "lat": "--", "lon": "--", "pan": 90, "tilt": 90, "probeAngle": 90
}
last_sensor_data = dict(OFFLINE_SENSOR)
esp32_online = False
health_status = "Waiting for Scan..."
health_details = {
    "disease_name": "Waiting for Scan...",
    "treatment": "Hold a crop leaf in front of the camera and click Scan Plant.",
    "severity": 0
}

weather_location = {
    "available": False, "latitude": None, "longitude": None,
    "accuracy": None, "source": "Waiting for laptop location", "updated": None
}

weather_data = {
    "available": False, "temperature": "--", "humidity": "--",
    "condition": "Waiting for laptop location", "rain_probability": "--",
    "precipitation": "--", "wind_speed": "--", "forecast_max": "--",
    "forecast_min": "--", "rain_forecast": "--", "latitude": "--",
    "longitude": "--", "location_source": "Laptop location unavailable"
}
last_weather_update = 0
WEATHER_CACHE_TIME = 300

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail"
}


# ============================================================
# ESP32 COMMUNICATION
# ============================================================
def get_sensor_data():
    """Poll ESP32 for latest sensor readings, cache them, and log to DB."""
    global last_sensor_data, esp32_online, last_database_save

    try:
        response = requests.get(ESP32_DATA_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        for key in OFFLINE_SENSOR:
            if key in data and data[key] is not None:
                val = data[key]
                if key == "pump":
                    # Invert reported state so badge accurately displays physical relay/pump state
                    val = "ON" if str(val).upper() == "OFF" else "OFF"
                last_sensor_data[key] = val
        esp32_online = True

        now = time.time()
        if now - last_database_save >= DATABASE_SAVE_INTERVAL:
            save_sensor_reading(
                temperature=data.get("temperature"),
                humidity=data.get("humidity"),
                soil=data.get("soil"),
                distance=data.get("distance"),
                pump=data.get("pump"),
                mode=data.get("mode"),
                latitude=data.get("lat"),
                longitude=data.get("lon")
            )
            last_database_save = now

        return dict(last_sensor_data)

    except Exception as e:
        print("ESP32 sensor error:", e)
        esp32_online = False
        return dict(last_sensor_data)


def esp32_command(path):
    """Send a GET command to the ESP32 control endpoint."""
    try:
        url = f"{ESP32_CONTROL_URL}{path}"
        print("ESP32 COMMAND:", url)
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        print("ESP32 RESPONSE:", response.text)
        return True
    except Exception as e:
        print("ESP32 COMMAND ERROR:", e)
        return False


def weather_description(code):
    try:
        code = int(code)
    except (TypeError, ValueError):
        return "Unknown"
    return WEATHER_CODES.get(code, "Unknown")


# ============================================================
# LAPTOP LOCATION / WEATHER
# ============================================================
@app.route("/set_weather_location", methods=["POST"])
def set_weather_location():
    global weather_location, last_weather_update
    try:
        data = request.get_json()
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])

        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("Invalid coordinates")

        weather_location = {
            "available": True,
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": data.get("accuracy"),
            "source": "Laptop browser location",
            "updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        last_weather_update = 0
        print("Laptop weather location:", latitude, longitude)

        return jsonify({"success": True, "latitude": latitude, "longitude": longitude})

    except Exception as e:
        print("Location error:", e)
        return jsonify({"success": False, "error": str(e)}), 400


def get_weather():
    """Fetch current + forecast weather from Open-Meteo, cached for WEATHER_CACHE_TIME."""
    global weather_data, last_weather_update

    if not weather_location["available"]:
        return dict(weather_data)

    now = time.time()
    if weather_data["available"] and now - last_weather_update < WEATHER_CACHE_TIME:
        return dict(weather_data)

    lat = weather_location["latitude"]
    lon = weather_location["longitude"]
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
        "&hourly=temperature_2m,precipitation_probability,precipitation"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&forecast_days=2&timezone=auto"
    )

    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        hourly = data["hourly"]
        daily = data["daily"]

        probabilities = hourly.get("precipitation_probability", [])[:12]
        rain_probability = max(probabilities) if probabilities else 0

        weather_data = {
            "available": True,
            "temperature": current.get("temperature_2m", "--"),
            "humidity": current.get("relative_humidity_2m", "--"),
            "condition": weather_description(current.get("weather_code", 0)),
            "rain_probability": rain_probability,
            "precipitation": current.get("precipitation", "--"),
            "wind_speed": current.get("wind_speed_10m", "--"),
            "forecast_max": daily.get("temperature_2m_max", ["--"])[0],
            "forecast_min": daily.get("temperature_2m_min", ["--"])[0],
            "rain_forecast": daily.get("precipitation_sum", ["--"])[0],
            "latitude": lat,
            "longitude": lon,
            "location_source": "Laptop browser location"
        }
        last_weather_update = now
        print("Weather updated. Rain probability:", rain_probability)
        return dict(weather_data)

    except Exception as e:
        print("Weather API error:", e)
        return dict(weather_data)


# ============================================================
# AGRICULTURAL INTELLIGENCE
# ============================================================
def agricultural_decision(sensor, weather):
    """Combine soil, weather and temperature readings into an irrigation decision."""
    SOIL_DRY_THRESHOLD = 3000

    try:
        soil = float(sensor.get("soil", 0))
    except (TypeError, ValueError):
        return {
            "state": "WAITING", "irrigation": "WAIT",
            "reason": "Waiting for valid soil data.",
            "heat_risk": "UNKNOWN", "rain_risk": "UNKNOWN",
            "flood_risk": "UNKNOWN", "risk": "UNKNOWN"
        }

    soil_is_dry = soil >= SOIL_DRY_THRESHOLD

    try:
        rain_probability = float(weather.get("rain_probability", 0))
    except (TypeError, ValueError):
        rain_probability = 0

    try:
        field_temperature = float(sensor.get("temperature", 0))
    except (TypeError, ValueError):
        field_temperature = 0

    try:
        weather_temperature = float(weather.get("temperature", 0))
    except (TypeError, ValueError):
        weather_temperature = 0

    # --- Irrigation decision ---
    if soil_is_dry:
        if rain_probability >= 60:
            state, irrigation = "RAIN_EXPECTED", "DELAY"
            reason = (f"Soil is dry (sensor {soil:.0f}), but rain probability is "
                       f"{rain_probability:.0f}%. Delay irrigation.")
        else:
            state, irrigation = "IRRIGATION_REQUIRED", "RECOMMENDED"
            reason = (f"Soil is dry (sensor {soil:.0f}) and rain probability is "
                       f"{rain_probability:.0f}%. Irrigation is recommended.")
    else:
        state, irrigation = "SOIL_SUFFICIENT", "NOT REQUIRED"
        reason = f"Soil moisture is currently sufficient (sensor {soil:.0f})."

    # --- Heat risk ---
    max_temperature = max(field_temperature, weather_temperature)
    if max_temperature >= 38:
        heat_risk = "HIGH"
    elif max_temperature >= 33:
        heat_risk = "MODERATE"
    else:
        heat_risk = "LOW"

    # --- Rain risk ---
    if rain_probability >= 70:
        rain_risk = "HIGH"
    elif rain_probability >= 40:
        rain_risk = "MODERATE"
    else:
        rain_risk = "LOW"

    # --- Flood / waterlogging risk (overrides irrigation) ---
    try:
        rain_forecast_mm = float(weather.get("rain_forecast", 0))
    except (TypeError, ValueError):
        rain_forecast_mm = 0

    if rain_forecast_mm >= 50:
        flood_risk = "HIGH"
        irrigation = "SUSPENDED"
        state = "FLOOD_RISK"
        reason = (f"Heavy rain forecast ({rain_forecast_mm:.0f}mm). "
                  f"Irrigation suspended to reduce waterlogging risk.")
    elif rain_forecast_mm >= 20:
        flood_risk = "MODERATE"
    else:
        flood_risk = "LOW"

    # --- Overall risk summary ---
    if flood_risk == "HIGH":
        overall_risk = "FLOOD / WATERLOGGING RISK"
    elif soil_is_dry and rain_probability >= 70:
        overall_risk = "HEAVY RAIN / DRY SOIL"
    elif soil_is_dry and heat_risk == "HIGH":
        overall_risk = "DROUGHT / HEAT RISK"
    elif rain_probability >= 70:
        overall_risk = "HEAVY RAIN RISK"
    elif heat_risk == "MODERATE":
        overall_risk = "HEAT RISK"
    else:
        overall_risk = "LOW"

    return {
        "state": state, "irrigation": irrigation, "reason": reason,
        "heat_risk": heat_risk, "rain_risk": rain_risk,
        "flood_risk": flood_risk, "risk": overall_risk,
        "soil": soil, "rain_probability": rain_probability
    }


# ============================================================
# AUTOMATIC IRRIGATION
# ============================================================
def automatic_pump_off():
    global pump_running_until, pump_timer
    with pump_lock:
        print("AUTOMATIC IRRIGATION: PUMP OFF")
        esp32_command("/pumpOff")
        pump_running_until = 0
        pump_timer = None


def start_automatic_irrigation():
    global last_pump_run, pump_running_until, pump_timer
    with pump_lock:
        now = time.time()

        if now < pump_running_until:
            return  # already running

        if now - last_pump_run < PUMP_COOLDOWN_SECONDS:
            remaining = PUMP_COOLDOWN_SECONDS - (now - last_pump_run)
            print("AUTOMATIC IRRIGATION: COOLDOWN", round(remaining), "seconds remaining")
            return

        print("AUTOMATIC IRRIGATION: PUMP ON")
        if not esp32_command("/pumpOn"):
            print("AUTOMATIC IRRIGATION: FAILED TO START PUMP")
            return

        last_pump_run = now
        pump_running_until = now + PUMP_RUN_SECONDS
        pump_timer = threading.Timer(PUMP_RUN_SECONDS, automatic_pump_off)
        pump_timer.daemon = True
        pump_timer.start()


def control_automatic_irrigation(decision, weather):
    if not AUTO_IRRIGATION:
        return
    if not esp32_online:
        print("AUTOMATIC IRRIGATION: ESP32 OFFLINE")
        return
    if not weather or not weather.get("available", False):
        print("AUTOMATIC IRRIGATION: WEATHER UNAVAILABLE")
        return

    irrigation = decision.get("irrigation")
    if irrigation == "RECOMMENDED":
        print("AUTOMATIC IRRIGATION: RECOMMENDED")
        start_automatic_irrigation()
    else:
        print("AUTOMATIC IRRIGATION:", irrigation)


# ============================================================
# INTER-CROP RECOMMENDATION (offline engine, no external AI service)
# ============================================================
def calculate_gap_days(harvest_date, next_planting_date):
    try:
        harvest = datetime.strptime(harvest_date, "%Y-%m-%d")
        planting = datetime.strptime(next_planting_date, "%Y-%m-%d")
        return (planting - harvest).days
    except Exception as e:
        print("Gap calculation error:", e)
        return None


def get_intercrop_ai_recommendation(previous_crop, next_crop, harvest_date,
                                     next_planting_date, sensor, weather,
                                     decision, soil_image=None):
    """Offline-first inter-crop recommendation. Runs entirely locally — no
    Gemini or other external generative-AI service required."""
    gap_days = calculate_gap_days(harvest_date, next_planting_date)
    if gap_days is None or gap_days <= 0:
        raise ValueError("Next planting date must be after harvest date.")

    result = recommend_intercrops(
        previous_crop=previous_crop,
        next_crop=next_crop,
        gap_days=gap_days,
        sensor=sensor,
        weather=weather,
        decision=decision,
        soil_image=soil_image
    )

    print("\n" + "=" * 60)
    print("OFFLINE INTER-CROP DECISION ENGINE")
    print("=" * 60)
    print("Previous crop:", previous_crop)
    print("Next crop:", next_crop)
    print("Gap:", gap_days, "days")
    print("Soil state:", result.get("soil_state"))
    print("Soil photo:", "YES" if soil_image and soil_image.get("base64") else "NO")
    print("Recommendations:", len(result.get("recommendations", [])))
    print("=" * 60)

    return result


# ============================================================
# DATABASE HISTORY API (disabled — future: sensor history graphs)
# ============================================================
@app.route("/api/sensors/history")
def sensor_history():
    try:
        limit = request.args.get("limit", default=100, type=int)
        limit = max(1, min(limit, 1000))
        history = get_sensor_history(limit)

        response = jsonify({"success": True, "count": len(history), "data": history})
        response.headers["Cache-Control"] = "no-store"
        return response

    except Exception as e:
        print("History API error:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# DASHBOARD / HOME
# ============================================================
@app.route("/dashboard_data")
def dashboard_data():
    sensor = get_sensor_data()
    weather = get_weather()
    decision = agricultural_decision(sensor, weather)

    response = jsonify({
        "sensor": sensor,
        "weather": weather,
        "decision": decision,
        "esp32_online": esp32_online,
        "detection": last_detection,
        "health": health_status,
        "health_details": health_details
    })
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.route("/manifest.json")
def serve_manifest():
    return send_from_directory("static", "manifest.json", mimetype="application/manifest+json")


@app.route("/sw.js")
def serve_service_worker():
    response = send_from_directory("static", "sw.js", mimetype="application/javascript")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response


@app.route("/download/AgriRover.apk")
def download_apk():
    apk_dir = os.path.join(os.path.dirname(__file__), "android_build", "dist")
    if os.path.exists(os.path.join(apk_dir, "AgriRover.apk")):
        return send_from_directory(apk_dir, "AgriRover.apk", as_attachment=True)
    return jsonify({"error": "APK not built yet"}), 404


@app.route("/")
def home():
    sensor = get_sensor_data()
    weather = get_weather()
    decision = agricultural_decision(sensor, weather)

    return render_template(
        "index.html",
        health=health_status,
        health_details=health_details,
        detection=last_detection,
        sensor=sensor,
        weather=weather,
        decision=decision,
        weather_location=weather_location,
        esp32_online=esp32_online
    )


# ============================================================
# PUMP CONTROLS (Mapped to physical relay action)
# ============================================================
@app.route("/pump/on")
def pump_on():
    # User requested PUMP ON -> send signal that activates the relay
    return jsonify({"success": esp32_command("/pumpOff")})


@app.route("/pump/off")
def pump_off():
    # User requested PUMP OFF -> send signal that deactivates the relay
    return jsonify({"success": esp32_command("/pumpOn")})


@app.route("/pump/invert")
def pump_invert():
    return jsonify({"success": esp32_command("/pumpInvert")})


@app.route("/pump/test")
def pump_test():
    return jsonify({"success": esp32_command("/pumpTest")})


# ============================================================
# PLANT HEALTH
# ============================================================
@app.route("/scan")
def scan():
    global health_status, health_details
    try:
        telemetry = get_sensor_data()
        diag = scan_plant(telemetry=telemetry)
        health_status = diag.get("summary", "Scan Complete")
        health_details = diag
    except Exception as e:
        print("Plant scan error:", e)
        health_status = f"Scan Failed: {type(e).__name__}"
        health_details = {"treatment": "Check camera connection."}
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.args.get("ajax"):
        return jsonify({"health": health_status, "details": health_details})
    return redirect("/")


# ============================================================
# ROVER CONTROLS
# ============================================================
@app.route("/auto")
def auto_mode():
    esp32_command("/auto")
    return redirect("/")


@app.route("/manual")
def manual_mode():
    esp32_command("/manual")
    return redirect("/")


@app.route("/forward")
def forward_cmd():
    esp32_command("/forward")
    return jsonify({"success": True, "command": "forward"})


@app.route("/backward")
def backward_cmd():
    esp32_command("/backward")
    return jsonify({"success": True, "command": "backward"})


@app.route("/left")
def left_cmd():
    esp32_command("/left")
    return jsonify({"success": True, "command": "left"})


@app.route("/right")
def right_cmd():
    esp32_command("/right")
    return jsonify({"success": True, "command": "right"})


@app.route("/stop")
def stop_cmd():
    esp32_command("/stop")
    return jsonify({"success": True, "command": "stop"})


@app.route("/speed/<int:val>")
def speed_cmd(val):
    val = max(50, min(255, val))
    esp32_command(f"/speed?val={val}")
    return jsonify({"success": True, "speed": val})


# ============================================================
# CAMERA CONTROLS
# ============================================================
@app.route("/camera/pan/left")
def cam_pan_left():
    esp32_command("/panLeft")
    return redirect("/")


@app.route("/camera/pan/right")
def cam_pan_right():
    esp32_command("/panRight")
    return redirect("/")


@app.route("/camera/tilt/up")
def cam_tilt_up():
    esp32_command("/tiltUp")
    return redirect("/")


@app.route("/camera/tilt/down")
def cam_tilt_down():
    esp32_command("/tiltDown")
    return redirect("/")


@app.route("/camera/center")
def cam_center():
    esp32_command("/center")
    return redirect("/")


@app.route("/camera/scan")
def cam_scan():
    esp32_command("/scan")
    return redirect("/")


# ============================================================
# SOIL PROBE SERVO CONTROLS (GPIO 25)
# ============================================================
def _send_serial_probe(cmd_str):
    try:
        import serial
        s = serial.Serial()
        s.port = 'COM8'
        s.baudrate = 115200
        s.dtr = False
        s.rts = False
        s.timeout = 0.2
        s.open()
        s.write(cmd_str.encode('utf-8'))
        s.close()
    except Exception:
        pass


@app.route("/probe/retract")
def probe_retract():
    _send_serial_probe("RETRACT\n")
    esp32_command("/probe/retract")
    return jsonify({"success": True, "action": "retract", "angle": 55})


@app.route("/probe/deploy")
def probe_deploy():
    _send_serial_probe("DEPLOY\n")
    esp32_command("/probe/deploy")
    return jsonify({"success": True, "action": "deploy", "angle": 135})


@app.route("/probe/up")
def probe_up():
    esp32_command("/probe/up")
    return jsonify({"success": True, "action": "up"})


@app.route("/probe/down")
def probe_down():
    esp32_command("/probe/down")
    return jsonify({"success": True, "action": "down"})


@app.route("/probe/angle")
def probe_angle():
    val = request.args.get("val", type=int)
    if val is not None:
        val = max(20, min(160, val))
        _send_serial_probe(f"SERVO25:{val}\n")
        esp32_command(f"/probe/angle?val={val}")
        return jsonify({"success": True, "angle": val})
    return jsonify({"success": False, "error": "Missing val parameter"}), 400



# ============================================================
# SENSOR / WEATHER / STATUS ENDPOINTS
# ============================================================
@app.route("/sensor_data")
def sensor_data():
    data = get_sensor_data()
    data["detection"] = last_detection
    data["health"] = health_status
    response = jsonify(data)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/weather_data")
def weather_endpoint():
    response = jsonify(get_weather())
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/agri_intelligence")
def agri_intelligence():
    sensor = get_sensor_data()
    weather = get_weather()
    decision = agricultural_decision(sensor, weather)

    response = jsonify({"sensor": sensor, "weather": weather, "decision": decision})
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/esp32_status")
def esp32_status():
    return jsonify({"online": esp32_online, "data": get_sensor_data()})


# ============================================================
# INTER-CROP RECOMMENDATION API
# ============================================================
@app.route("/api/intercrop-recommendation", methods=["POST"])
def intercrop_recommendation():
    try:
        previous_crop = request.form.get("previous_crop", "").strip()
        next_crop = request.form.get("next_crop", "").strip()
        harvest_date = request.form.get("harvest_date", "").strip()
        next_planting_date = request.form.get("next_planting_date", "").strip()
        soil_image = request.files.get("soil_image")

        # --- Soil image (optional) ---
        soil_image_base64 = None
        soil_image_mime = None
        if soil_image and soil_image.filename:
            allowed_types = {"image/jpeg", "image/png", "image/webp"}
            soil_image_mime = soil_image.mimetype
            if soil_image_mime not in allowed_types:
                return jsonify({"success": False, "error": "Soil image must be JPG, PNG, or WebP."}), 400

            image_bytes = soil_image.read()
            if len(image_bytes) > 5 * 1024 * 1024:
                return jsonify({"success": False, "error": "Soil image must be smaller than 5 MB."}), 400

            soil_image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # --- Validation ---
        if not previous_crop:
            return jsonify({"success": False, "error": "Previous crop is required."}), 400
        if not next_crop:
            return jsonify({"success": False, "error": "Next planned crop is required."}), 400
        if not harvest_date:
            return jsonify({"success": False, "error": "Harvest date is required."}), 400
        if not next_planting_date:
            return jsonify({"success": False, "error": "Next planting date is required."}), 400

        gap_days = calculate_gap_days(harvest_date, next_planting_date)
        if gap_days is None:
            return jsonify({"success": False, "error": "Invalid dates."}), 400
        if gap_days <= 0:
            return jsonify({"success": False, "error": "Next planting date must be after harvest date."}), 400

        sensor = get_sensor_data()
        weather = get_weather()
        decision = agricultural_decision(sensor, weather)

        print("\n" + "=" * 60)
        print("OFFLINE INTER-CROP ANALYSIS")
        print("=" * 60)
        print("Previous crop:", previous_crop)
        print("Next crop:", next_crop)
        print("Gap:", gap_days, "days")
        print("Temperature:", sensor.get("temperature"))
        print("Humidity:", sensor.get("humidity"))
        print("Soil:", sensor.get("soil"))
        print("Rain probability:", weather.get("rain_probability"))
        print("Forecast rain:", weather.get("rain_forecast"))
        print("Irrigation:", decision.get("irrigation"))
        print("Overall risk:", decision.get("risk"))
        print("Soil image:", "YES" if soil_image_base64 else "NO")
        print("=" * 60)

        ai_result = get_intercrop_ai_recommendation(
            previous_crop=previous_crop,
            next_crop=next_crop,
            harvest_date=harvest_date,
            next_planting_date=next_planting_date,
            sensor=sensor,
            weather=weather,
            decision=decision,
            soil_image={"base64": soil_image_base64, "mime_type": soil_image_mime}
        )

        return jsonify({
            "success": True,
            "gap_days": gap_days,
            "recommendations": ai_result.get("recommendations", []),
            "message": ai_result.get("message", ""),
            "sensor": sensor,
            "weather": weather,
            "decision": decision,
            "engine": ai_result.get("engine", "AGRI-VISE Offline Inter-Crop Decision Engine"),
            "soil_visual": ai_result.get("soil_visual", "No soil photo used"),
            "inputs_used": ai_result.get("inputs_used", {})
        })

    except Exception as e:
        print("Inter-crop AI error:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# CAMERA STREAM
# ============================================================
def make_offline_frame():
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (30, 30, 35)
    cv2.putText(img, "AGRO-VATORS CAMERA", (150, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 220, 120), 2)
    cv2.putText(img, f"ESP32-CAM Offline ({ESP32_CAM_IP})", (110, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(img, "Turn on hotspot 'phone1' (pass: 12345678)", (90, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(img, "Or update ESP32_CAM_IP in .env", (150, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
    ret, buf = cv2.imencode(".jpg", img)
    return buf.tobytes() if ret else b""


# ============================================================
# CENTRAL CAMERA CAPTURE & AUTO-EXPOSURE WORKER THREAD
# ============================================================
latest_annotated_jpeg = None
camera_lock = threading.Lock()
clahe_filter = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))


def camera_worker():
    global latest_annotated_jpeg, last_detection
    print("Central Camera Worker Thread Started.")
    while True:
        try:
            req = urllib.request.Request(ESP32_URL, headers={"User-Agent": "AgriRover/1.0"})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                raw_bytes = resp.read()

            if not raw_bytes or len(raw_bytes) < 500:
                time.sleep(0.1)
                continue

            img_np = np.frombuffer(raw_bytes, dtype=np.uint8)
            frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            if frame is None:
                time.sleep(0.1)
                continue

            # Auto-exposure compensation on luminance channel
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            cl = clahe_filter.apply(l)
            frame = cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)

            frame = cv2.resize(frame, (640, 480))
            results = model(frame, imgsz=320, verbose=False)
            annotated = results[0].plot()

            best_name, best_conf = "None", 0.0
            for box in results[0].boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if conf > best_conf and conf > 0.40:
                    best_conf = conf
                    best_name = model.names[cls]

            # --------------------------------------------------------
            # REAL-TIME COMPUTER VISION LEAF & PLANT PATHOLOGY DETECTOR
            # --------------------------------------------------------
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask_green = cv2.inRange(hsv, np.array([25, 35, 35]), np.array([88, 255, 255]))
            mask_yellow = cv2.inRange(hsv, np.array([18, 40, 50]), np.array([28, 255, 255]))
            mask_brown = cv2.inRange(hsv, np.array([8, 45, 25]), np.array([18, 255, 180]))

            plant_mask = cv2.bitwise_or(mask_green, cv2.bitwise_or(mask_yellow, mask_brown))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            plant_mask = cv2.morphologyEx(plant_mask, cv2.MORPH_OPEN, kernel)
            plant_mask = cv2.morphologyEx(plant_mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(plant_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            leaf_found = False

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 1200:
                    x, y, w, h = cv2.boundingRect(cnt)

                    roi_g = cv2.countNonZero(mask_green[y:y+h, x:x+w])
                    roi_y = cv2.countNonZero(mask_yellow[y:y+h, x:x+w])
                    roi_b = cv2.countNonZero(mask_brown[y:y+h, x:x+w])
                    total_roi = max(1, roi_g + roi_y + roi_b)

                    lesion_pct = (roi_b / total_roi) * 100
                    yellow_pct = (roi_y / total_roi) * 100
                    green_pct = (roi_g / total_roi) * 100

                    if lesion_pct > 14:
                        label = f"Leaf Blight/Spot ({lesion_pct:.0f}%)"
                        color = (30, 30, 220) # Red
                    elif yellow_pct > 22:
                        label = f"Leaf Chlorosis ({yellow_pct:.0f}%)"
                        color = (0, 215, 255) # Yellow/Gold
                    else:
                        label = f"Healthy Leaf ({green_pct:.0f}%)"
                        color = (40, 220, 80) # Vibrant Green

                    cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
                    (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                    banner_top = max(0, y - 22)
                    cv2.rectangle(annotated, (x, banner_top), (x + text_w + 10, banner_top + 22), color, -1)
                    cv2.putText(annotated, label, (x + 5, banner_top + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

                    if not leaf_found or area > 3000:
                        best_name = label
                        leaf_found = True

            last_detection = best_name
            ret, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ret:
                with camera_lock:
                    latest_annotated_jpeg = buffer.tobytes()

            time.sleep(0.06)

        except Exception as e:
            with camera_lock:
                latest_annotated_jpeg = make_offline_frame()
            time.sleep(0.5)


# Start persistent single-instance camera thread
cam_worker_thread = threading.Thread(target=camera_worker, daemon=True)
cam_worker_thread.start()


def generate_frames():
    while True:
        with camera_lock:
            jpeg = latest_annotated_jpeg
        if jpeg:
            length = len(jpeg)
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n"
                   b"Content-Length: " + str(length).encode() + b"\r\n\r\n" +
                   jpeg + b"\r\n")
        time.sleep(0.08)


@app.route("/current_frame.jpg")
def current_frame():
    with camera_lock:
        jpeg = latest_annotated_jpeg
    if not jpeg:
        jpeg = make_offline_frame()
    response = Response(jpeg, mimetype="image/jpeg")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


# ============================================================
# START
# ============================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Starting AGRO-VATORS Dashboard on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
