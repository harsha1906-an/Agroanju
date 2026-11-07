import requests
import urllib.request
import os
import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ROBOFLOW_API_KEY", "")
MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID", "")
ESP32_CAM_IP = os.getenv("ESP32_CAM_IP", "192.168.93.28")
ESP32_URL = f"http://{ESP32_CAM_IP}/capture"

# Comprehensive Agricultural Treatment Protocols
DISEASE_PRESCRIPTIONS = {
    "EARLY_BLIGHT": {
        "name": "Early Blight (Alternaria solani)",
        "symptoms": "Concentric brown/black target-pattern necrotic lesions.",
        "treatment": "Spray Copper Oxychloride (2.5g/L) or Mancozeb 75 WP. Prune lower infected leaves; sanitize shears.",
        "prevention": "Avoid overhead watering; mulch soil to stop fungal spore splashback."
    },
    "LATE_BLIGHT": {
        "name": "Late Blight (Phytophthora infestans)",
        "symptoms": "Rapidly spreading water-soaked dark lesions with pale margins.",
        "treatment": "High Urgency: Apply systemic Metalaxyl + Mancozeb (Ridomil MZ @ 2g/L) immediately.",
        "prevention": "Improve field drainage, increase plant spacing for airflow, destroy cull piles."
    },
    "LEAF_RUST": {
        "name": "Crop Leaf Rust (Puccinia spp.)",
        "symptoms": "Raised reddish-brown or copper fungal spore pustules on leaf blade.",
        "treatment": "Spray Triazole fungicide (Propiconazole or Tebuconazole @ 1ml/L water).",
        "prevention": "Plant resistant cultivars; eliminate alternative host weeds around field perimeter."
    },
    "SEPTORIA_SPOT": {
        "name": "Septoria Leaf Spot (Septoria spp.)",
        "symptoms": "Numerous small circular brown spots with dark margins and gray centers.",
        "treatment": "Apply Chlorothalonil or Bio-fungicide (Bacillus subtilis). Avoid working in wet fields.",
        "prevention": "Rotate crops on a 3-year cycle; remove all solanaceous crop debris after harvest."
    },
    "POWDERY_MILDEW": {
        "name": "Powdery Mildew (Erysiphales)",
        "symptoms": "White talcum-powder-like fungal patches on the upper leaf surface.",
        "treatment": "Spray Wettable Sulfur (2g/L) or Potassium Bicarbonate / Cold-pressed Neem oil (5ml/L).",
        "prevention": "Ensure direct sunlight penetration; avoid excessive high-nitrogen feeding."
    },
    "NITROGEN_DEFICIENCY": {
        "name": "Nitrogen Chlorosis Deficiency",
        "symptoms": "Uniform pale yellowing starting from leaf tip and older lower foliage.",
        "treatment": "Top-dress with Urea (46% N) or Calcium Ammonium Nitrate (CAN); apply compost tea.",
        "prevention": "Maintain soil pH between 6.0–6.8 to ensure optimal nitrogen root bioavailability."
    },
    "IRON_DEFICIENCY": {
        "name": "Interveinal Iron Chlorosis",
        "symptoms": "Yellowing of leaf blade while the main veins remain distinctly dark green.",
        "treatment": "Foliar spray of Chelated Iron (Fe-EDDHA or Fe-EDTA @ 1g/L) during early morning.",
        "prevention": "Correct alkaline/calcareous soil; avoid waterlogged conditions that lock up iron."
    },
    "HEALTHY": {
        "name": "Healthy Plant Foliage",
        "symptoms": "Vibrant green chlorophyll pigment with strong cellular turgidity.",
        "treatment": "No disease treatment required. Continue standard balanced NPK fertilization.",
        "prevention": "Maintain scheduled soil probe monitoring and drip irrigation."
    }
}


def analyze_leaf_image(img_bytes, telemetry=None):
    """
    Agricultural Plant Pathology & Disease Classification Engine
    """
    frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return {
            "summary": "❌ Error: Could not decode camera image",
            "disease_name": "Image Error",
            "severity": 0,
            "treatment": "Check camera lens and Wi-Fi connection."
        }

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, w, _ = frame.shape
    total_pixels = h * w

    # Color Space Filters (Pathology Wavelengths)
    # 1. Healthy Chlorophyll Green (Hue 25-88)
    mask_green = cv2.inRange(hsv, np.array([25, 35, 35]), np.array([88, 255, 255]))

    # 2. Chlorosis Yellow (Hue 18-28)
    mask_yellow = cv2.inRange(hsv, np.array([18, 40, 50]), np.array([28, 255, 255]))

    # 3. Necrotic Blight / Dark Brown Spots (Hue 8-18)
    mask_brown = cv2.inRange(hsv, np.array([8, 45, 25]), np.array([18, 255, 180]))

    # 4. White / Gray Powdery Mildew
    mask_powdery = cv2.inRange(hsv, np.array([0, 0, 185]), np.array([180, 45, 255]))

    # Combine foliage masks
    plant_mask = cv2.bitwise_or(mask_green, cv2.bitwise_or(mask_yellow, mask_brown))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    plant_mask = cv2.morphologyEx(plant_mask, cv2.MORPH_OPEN, kernel)
    plant_mask = cv2.morphologyEx(plant_mask, cv2.MORPH_CLOSE, kernel)

    # Restrict powdery mildew mask strictly to plant foliage
    mask_powdery = cv2.bitwise_and(mask_powdery, plant_mask)

    plant_pixel_count = cv2.countNonZero(plant_mask)
    coverage_pct = (plant_pixel_count / total_pixels) * 100

    if plant_pixel_count < 1200 or coverage_pct < 2.0:
        return {
            "summary": "❓ No Leaf Detected (Hold leaf closer to camera)",
            "disease_name": "No Leaf in View",
            "severity": 0,
            "treatment": "Point rover camera directly at the crop foliage or leaf blade."
        }

    green_count = cv2.countNonZero(mask_green)
    yellow_count = cv2.countNonZero(mask_yellow)
    brown_count = cv2.countNonZero(mask_brown)
    powdery_count = cv2.countNonZero(mask_powdery)
    total_valid = max(1, green_count + yellow_count + brown_count)

    green_pct = (green_count / total_valid) * 100
    yellow_pct = (yellow_count / total_valid) * 100
    lesion_pct = (brown_count / total_valid) * 100
    powdery_pct = (powdery_count / max(1, plant_pixel_count)) * 100

    # Spot morphology analysis (contour size)
    brown_contours, _ = cv2.findContours(mask_brown, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_spot_area = max([cv2.contourArea(c) for c in brown_contours], default=0)
    spot_count = len([c for c in brown_contours if cv2.contourArea(c) > 25])

    # Diagnostic Classifier
    disease_key = "HEALTHY"
    severity = lesion_pct

    if powdery_pct > 15:
        disease_key = "POWDERY_MILDEW"
        severity = powdery_pct
    elif lesion_pct > 12:
        if max_spot_area > 400:
            disease_key = "LATE_BLIGHT"
        elif max_spot_area > 120:
            disease_key = "EARLY_BLIGHT"
        elif spot_count > 8:
            disease_key = "SEPTORIA_SPOT"
        else:
            disease_key = "LEAF_RUST"
    elif yellow_pct > 22:
        if green_pct > 40:
            disease_key = "IRON_DEFICIENCY"
        else:
            disease_key = "NITROGEN_DEFICIENCY"
        severity = yellow_pct
    elif green_pct >= 75:
        disease_key = "HEALTHY"
        severity = 0
    else:
        disease_key = "EARLY_BLIGHT"
        severity = max(lesion_pct, 10.0)

    severity = min(100.0, max(0.0, severity))

    disease_info = DISEASE_PRESCRIPTIONS[disease_key]

    # Telemetry Cross-Referencing
    telemetry_warnings = []
    if telemetry:
        humidity = telemetry.get("humidity")
        soil = telemetry.get("soil")
        temp = telemetry.get("temperature")

        try:
            if humidity and float(humidity) > 75 and disease_key in ["EARLY_BLIGHT", "LATE_BLIGHT", "SEPTORIA_SPOT", "LEAF_RUST"]:
                telemetry_warnings.append(f"High microclimate humidity ({humidity}%) accelerates fungal spore transmission.")
            if soil and int(soil) < 2200 and disease_key in ["LATE_BLIGHT", "EARLY_BLIGHT"]:
                telemetry_warnings.append("Oversaturated soil detected by probe. Reduce watering to stop root-zone fungal multiplication.")
            if soil and int(soil) > 3800 and disease_key in ["NITROGEN_DEFICIENCY", "IRON_DEFICIENCY"]:
                telemetry_warnings.append("Drought stress detected. Water the plant thoroughly before applying fertilizers to avoid root burn.")
            if temp and float(temp) > 32 and disease_key == "POWDERY_MILDEW":
                telemetry_warnings.append("High ambient temperature detected. Apply neem oil only during cool evening hours to prevent leaf scorch.")
        except (ValueError, TypeError):
            pass

    warning_text = " " + " ".join(telemetry_warnings) if telemetry_warnings else ""

    if disease_key == "HEALTHY":
        summary = f"HEALTHY LEAF ✅ ({green_pct:.0f}% Vigor)"
    elif "BLIGHT" in disease_key or "RUST" in disease_key or "SPOT" in disease_key:
        summary = f"{disease_info['name']} ❌ ({severity:.0f}% Severity)"
    else:
        summary = f"{disease_info['name']} ⚠️ ({severity:.0f}% Severity)"

    return {
        "summary": summary,
        "disease_key": disease_key,
        "disease_name": disease_info["name"],
        "severity": round(severity, 1),
        "chlorophyll_pct": round(green_pct, 1),
        "symptoms": disease_info["symptoms"],
        "treatment": disease_info["treatment"] + warning_text,
        "prevention": disease_info["prevention"],
        "metrics": {
            "green_pct": round(green_pct, 1),
            "yellow_pct": round(yellow_pct, 1),
            "lesion_pct": round(lesion_pct, 1),
            "coverage_pct": round(coverage_pct, 1)
        }
    }


def scan_plant(telemetry=None):
    try:
        print(f"📷 Capturing leaf from ESP32-CAM ({ESP32_URL})...")
        img = urllib.request.urlopen(ESP32_URL, timeout=5).read()
        print(f"✅ Image received: {len(img)} bytes")

        # 1. Check Roboflow if valid API key is present
        if API_KEY and API_KEY != "your_api_key_here" and MODEL_ID and MODEL_ID != "your_model_id_here":
            try:
                res = requests.post(
                    f"https://classify.roboflow.com/{MODEL_ID}",
                    params={"api_key": API_KEY},
                    files={"file": ("plant.jpg", img, "image/jpeg")},
                    timeout=8
                )
                if res.status_code == 200:
                    data = res.json()
                    preds = data.get("predictions", {})
                    if preds:
                        best = max(preds, key=lambda x: preds[x]["confidence"])
                        conf = preds[best]["confidence"] * 100
                        if conf >= 50:
                            return {
                                "summary": f"{best} ({conf:.0f}%)",
                                "disease_name": best,
                                "severity": round(100 - conf, 1),
                                "treatment": "Consult agricultural extension officer for regional treatment protocol.",
                                "symptoms": f"Identified by cloud agricultural model: {best}."
                            }
            except Exception as e:
                print("Roboflow skipped:", e)

        # 2. Complete Local Plant Pathology & Treatment Engine
        return analyze_leaf_image(img, telemetry=telemetry)

    except Exception as e:
        print("\n❌ PLANT SCAN ERROR:", e)
        return {
            "summary": f"Scan Failed: {type(e).__name__}",
            "disease_name": "Connection Error",
            "severity": 0,
            "treatment": "Ensure rover camera is powered on and streaming."
        }


if __name__ == "__main__":
    result = scan_plant()
    print("\n====================")
    print("FINAL DIAGNOSIS:")
    print(result)
    print("====================")
