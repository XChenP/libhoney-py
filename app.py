from flask import Flask, request, jsonify
from libhoney.client import Client
import logging

app = Flask(__name__)
app.config["DEBUG"] = True

# Initialize Honeycomb client
honey_client = Client(
    writekey="YOUR_API_KEY", dataset="YOUR_DATASET", api_host="https://api.honeycomb.io"
)


def julian_to_unix(julian_date):
    return (julian_date - 2440587.5) * 86400.0


def unix_to_julian(unix_time):
    return (unix_time / 86400.0) + 2440587.5


@app.route("/createMarker", methods=["POST"])
def create_marker():
    data = request.get_json()

    # Validate required fields
    required = ["start_time", "message"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required field(s)"}), 400

    # Validate data types
    try:
        start_time = float(data["start_time"])
        end_time = float(data["end_time"]) if "end_time" in data else None
    except ValueError:
        return jsonify({"error": "Invalid Julian date format"}), 400

    # Convert Julian to Unix
    try:
        start_unix = julian_to_unix(start_time)
        end_unix = julian_to_unix(end_time) if end_time else None
    except:
        return jsonify({"error": "Invalid time conversion"}), 400

    # Create marker
    try:
        marker = honey_client.create_marker(
            start_time=start_unix,
            message=data["message"],
            end_time=end_unix,
            type=data.get("type"),
            url=data.get("url"),
        )
    except Exception as e:
        logging.error(f"Marker creation failed: {e}")
        return jsonify({"error": "Marker creation failed"}), 500

    # Prepare response
    response_data = {
        "id": marker.get("id"),
        "created_at": marker.get("created_at"),
        "updated_at": marker.get("updated_at"),
        "start_time": start_time,  # Original Julian input
        "message": marker.get("message"),
        "type": marker.get("type"),
    }
    if end_time is not None:
        response_data["endtime"] = end_time

    return jsonify(response_data), 201


if __name__ == "__main__":
    app.run()
