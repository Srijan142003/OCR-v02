from PIL import Image
import google.generativeai as genai
from flask import Flask, request, jsonify
import re
import os

# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API using environment variable
API_KEY = "AIzaSyAIFTRTgBbeg7vThtYzn-R_-T0JhXMNWtY"
genai.configure(api_key=API_KEY)

# Function to extract Prescription ID
def extract_prescription_id(text):
    prescription_id_match = re.search(r"(?:Prescription ID|ID):\s*([\w\-]+)", text, re.IGNORECASE)
    return prescription_id_match.group(1) if prescription_id_match else "Not Found"

# Function to extract Medicine Names
def extract_medicine_names(text):

    medicine_names = re.findall(r"\*\s*([A-Za-z0-9\s\.\-]+)", text)
    # Filter out irrelevant matches
    medicine_names = [
        medicine.strip()
        for medicine in medicine_names
        if medicine.strip() and not re.search(r"(Patient ID|Prescription ID|^\d+\.?$)", medicine, re.IGNORECASE)
    ]
    return medicine_names

# Function to process the image and extract Prescription ID
def extract_prescriptionid(image_path):
    try:
        # Load image
        image = Image.open(image_path)

        # Define prompt for Gemini OCR
        prompt = """
        Extract the following details from this prescription image:
        1. Prescription ID (e.g., "ID: <value>").
        """

        # Process image with Gemini API
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content([prompt, image])

        # Parse response text for required details
        text = response.text

        # Extract Prescription ID
        prescription_id = extract_prescription_id(text)

        return {"Prescription ID": prescription_id}
    except Exception as e:
        return {"error": f"Error extracting Prescription ID: {str(e)}"}

# Function to process the image and extract Medicine Details
def extract_medicine_details(image_path):
    try:
        # Load image
        image = Image.open(image_path)

        # Define prompt for Gemini OCR
        prompt = """
        Extract the following details from this prescription image:
        Medicine names listed under the 'Medicine Name' column
        """

        # Process image with Gemini API
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content([prompt, image])

        # Parse response text for required details
        text = response.text

        # Extract Prescription ID and Medicine Names
        # prescription_id = extract_prescription_id(text)
        medicine_names = extract_medicine_names(text)

        return {
            "Medicines": medicine_names,
        }
    except Exception as e:
        return {"error": f"Error extracting Medicine Details: {str(e)}"}

# Route to handle Prescription ID extraction
@app.route('/id', methods=['POST'])
def extract_prescription_id_route():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_path = f"/tmp/{image_file.filename}"
    try:
        image_file.save(image_path)
        
        # Perform extraction
        result = extract_prescriptionid(image_path)
        
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)  # Cleanup temporary file

    return jsonify(result)

# Route to handle Medicine Details extraction
@app.route('/medi', methods=['POST'])
def extract_medicine_details_route():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_path = f"/tmp/{image_file.filename}"
    try:
        image_file.save(image_path)
        
        # Perform extraction
        result = extract_medicine_details(image_path)
        
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)  # Cleanup temporary file

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)