
from pathlib import Path
import hashlib

from PIL import Image
import piexif


# ==========================================
# Supported image formats
# ==========================================

SUPPORTED_FORMATS = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
}


# ==========================================
# SHA-256
# ==========================================

def calculate_sha256(file_path):
    """
    Calculate SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


# ==========================================
# GPS conversion
# ==========================================

def convert_gps_coordinate(value, reference):
    """
    Convert EXIF GPS coordinates from
    degrees/minutes/seconds to decimal.
    """

    try:

        degrees = float(value[0][0]) / float(value[0][1])
        minutes = float(value[1][0]) / float(value[1][1])
        seconds = float(value[2][0]) / float(value[2][1])

        decimal = degrees + (minutes / 60) + (seconds / 3600)

        if reference in ["S", "W"]:
            decimal = -decimal

        return round(decimal, 6)

    except Exception:
        return None


# ==========================================
# Extract GPS
# ==========================================

def extract_gps(exif_data):
    """
    Extract GPS latitude and longitude.
    """

    result = {}

    gps = exif_data.get("GPS", {})

    if not gps:
        return result

    latitude = gps.get(piexif.GPSIFD.GPSLatitude)
    latitude_ref = gps.get(piexif.GPSIFD.GPSLatitudeRef)

    longitude = gps.get(piexif.GPSIFD.GPSLongitude)
    longitude_ref = gps.get(piexif.GPSIFD.GPSLongitudeRef)

    if latitude and latitude_ref:

        if isinstance(latitude_ref, bytes):
            latitude_ref = latitude_ref.decode(
                errors="ignore"
            )

        result["GPS Latitude"] = convert_gps_coordinate(
            latitude,
            latitude_ref
        )

    if longitude and longitude_ref:

        if isinstance(longitude_ref, bytes):
            longitude_ref = longitude_ref.decode(
                errors="ignore"
            )

        result["GPS Longitude"] = convert_gps_coordinate(
            longitude,
            longitude_ref
        )

    return result


# ==========================================
# EXIF value conversion
# ==========================================

def clean_exif_value(value):
    """
    Convert EXIF values into readable text.
    """

    if isinstance(value, bytes):

        try:
            return value.decode(
                "utf-8",
                errors="ignore"
            )
        except Exception:
            return str(value)

    return str(value)


# ==========================================
# Image Analyzer
# ==========================================

def analyze_image(file_path):
    """
    Analyze a JPEG or PNG image.

    Returns a dictionary containing:
    - file information
    - metadata
    - privacy findings
    - risk score
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_FORMATS:
        raise ValueError(
            "Unsupported image format. "
            "Use JPG, JPEG or PNG."
        )

    # --------------------------------------
    # Basic file information
    # --------------------------------------

    file_size = path.stat().st_size

    file_hash = calculate_sha256(path)

    metadata = {}

    findings = []

    # --------------------------------------
    # Open image
    # --------------------------------------

    with Image.open(path) as image:

        image_format = image.format

        width, height = image.size

        color_mode = image.mode

        metadata["File Name"] = path.name
        metadata["File Type"] = image_format
        metadata["File Size"] = f"{file_size:,} bytes"
        metadata["Width"] = width
        metadata["Height"] = height
        metadata["Color Mode"] = color_mode

        # ----------------------------------
        # JPEG EXIF
        # ----------------------------------

        if image_format == "JPEG":

            try:

                exif_bytes = image.info.get("exif")

                if exif_bytes:

                    exif_data = piexif.load(exif_bytes)

                    # --------------------------
                    # EXIF
                    # --------------------------

                    for ifd_name in [
                        "0th",
                        "Exif",
                        "GPS",
                        "1st"
                    ]:

                        ifd_data = exif_data.get(
                            ifd_name,
                            {}
                        )

                        for tag_id, value in ifd_data.items():

                            try:

                                tag_name = piexif.TAGS[
                                    ifd_name
                                ][tag_id]["name"]

                            except Exception:

                                tag_name = str(tag_id)

                            if tag_name == "GPSLatitude":
                                continue

                            if tag_name == "GPSLongitude":
                                continue

                            if tag_name == "GPSLatitudeRef":
                                continue

                            if tag_name == "GPSLongitudeRef":
                                continue

                            metadata[tag_name] = (
                                clean_exif_value(value)
                            )

                    # --------------------------
                    # GPS
                    # --------------------------

                    gps_data = extract_gps(exif_data)

                    metadata.update(gps_data)

            except Exception as error:

                metadata["EXIF Error"] = str(error)

        # ----------------------------------
        # PNG metadata
        # ----------------------------------

        elif image_format == "PNG":

            for key, value in image.info.items():

                if key == "exif":
                    continue

                metadata[f"PNG: {key}"] = str(value)

    # ======================================
    # Risk analysis
    # ======================================

    score = 0

    # GPS = very high privacy significance
    if (
        "GPS Latitude" in metadata
        or "GPS Longitude" in metadata
    ):

        findings.append({
            "category": "Location",
            "field": "GPS Coordinates",
            "value": (
                f"{metadata.get('GPS Latitude', 'N/A')}, "
                f"{metadata.get('GPS Longitude', 'N/A')}"
            ),
            "risk": "HIGH",
            "points": 40
        })

        score += 40

    # Camera/device information
    device_fields = [
        "Make",
        "Model",
        "BodySerialNumber",
        "LensSerialNumber"
    ]

    found_device_fields = [
        field
        for field in device_fields
        if field in metadata
    ]

    if found_device_fields:

        findings.append({
            "category": "Device Information",
            "field": ", ".join(found_device_fields),
            "value": "; ".join(
                f"{field}: {metadata.get(field, '')}"
                for field in found_device_fields
            ),
            "risk": "MEDIUM",
            "points": 20
        })

        score += 20

    # Date/time information
    date_fields = [
        "DateTime",
        "DateTimeOriginal",
        "DateTimeDigitized"
    ]

    found_date_fields = [
        field
        for field in date_fields
        if field in metadata
    ]

    if found_date_fields:

        findings.append({
            "category": "Date & Time",
            "field": ", ".join(found_date_fields),
            "value": "; ".join(
                f"{field}: {metadata.get(field, '')}"
                for field in found_date_fields
            ),
            "risk": "LOW",
            "points": 10
        })

        score += 10

    # Software information
    if "Software" in metadata:

        findings.append({
            "category": "Software",
            "field": "Software",
            "value": metadata["Software"],
            "risk": "LOW",
            "points": 5
        })

        score += 5

    # Copyright / author information
    identity_fields = [
        "Artist",
        "Copyright",
        "XPAuthor",
        "XPComment"
    ]

    found_identity = [
        field
        for field in identity_fields
        if field in metadata
    ]

    if found_identity:

        findings.append({
            "category": "Identity",
            "field": ", ".join(found_identity),
            "value": "; ".join(
                f"{field}: {metadata.get(field, '')}"
                for field in found_identity
            ),
            "risk": "MEDIUM",
            "points": 15
        })

        score += 15

    # --------------------------------------
    # Cap score
    # --------------------------------------

    score = min(score, 100)

    # --------------------------------------
    # Risk level
    # --------------------------------------

    if score >= 70:
        risk_level = "HIGH"

    elif score >= 40:
        risk_level = "MEDIUM"

    elif score > 0:
        risk_level = "LOW"

    else:
        risk_level = "MINIMAL"

    return {
        "file": {
            "name": path.name,
            "type": image_format,
            "size": file_size,
            "width": width,
            "height": height,
            "sha256": file_hash
        },

        "metadata": metadata,

        "findings": findings,

        "risk": {
            "score": score,
            "level": risk_level
        }
    }


# ==========================================
# Command-line test
# ==========================================

if __name__ == "__main__":

    file_path = input(
        "Enter image path: "
    ).strip().strip('"')

    try:

        result = analyze_image(file_path)

        print("\n================================")
        print("CAUGHTIN4K IMAGE ANALYSIS")
        print("================================")

        print("\nFile:")
        print("Name:", result["file"]["name"])
        print("Type:", result["file"]["type"])
        print("Size:", result["file"]["size"], "bytes")
        print("Resolution:",
              result["file"]["width"],
              "x",
              result["file"]["height"])

        print("\nSHA-256:")
        print(result["file"]["sha256"])

        print("\nMetadata:")

        for key, value in result["metadata"].items():
            print(f"{key}: {value}")

        print("\nPrivacy Findings:")

        if result["findings"]:

            for finding in result["findings"]:

                print(
                    f"[{finding['risk']}] "
                    f"{finding['category']} - "
                    f"{finding['field']}"
                )

        else:

            print("No privacy-sensitive metadata detected.")

        print("\nPrivacy Risk:")
        print(
            f"{result['risk']['score']}/100 "
            f"({result['risk']['level']})"
        )

    except Exception as error:

        print("\nAnalysis failed:")
        print(error)
