from flask import Flask, render_template, request
import tensorflow as tf
import numpy as np
from PIL import Image
import sqlite3
from datetime import datetime
import os


app = Flask(__name__)


# ==========================================================
# Configuration
# ==========================================================

MODEL_PATH = "model/best_model_CNN.keras"

DATABASE = "database/app.db"

UPLOAD_FOLDER = "static/uploads"


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Create required folders

os.makedirs("database", exist_ok=True)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================================================
# Load Trained CNN Model
# ==========================================================

model = tf.keras.models.load_model(
    MODEL_PATH
)


# ==========================================================
# Class Names
# ==========================================================

CLASS_NAMES = [

    "early_brahmi",

    "later_brahmi",

    "medieval_sinhala",

    "modern_sinhala",

    "transitional_brahmi"

]


# ==========================================================
# Initialize Database
# ==========================================================

def init_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            image_name TEXT NOT NULL,

            predicted_class TEXT NOT NULL,

            confidence REAL NOT NULL,

            created_at TEXT NOT NULL

        )
    """)


    connection.commit()

    connection.close()


# ==========================================================
# Image Preprocessing
# ==========================================================

def preprocess_image(image):

    # Convert to grayscale
    image = image.convert("L")

    # Resize
    image = image.resize((64, 64))

    # Convert to NumPy
    image = np.array(image)

    # Normalize
    image = image / 255.0

    # Reshape
    image = image.reshape(
        1,
        64,
        64,
        1
    )

    return image


# ==========================================================
# Home Page
# ==========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================================
# Recognition Page
# ==========================================================

@app.route("/recognize")
def recognize():

    return render_template(
        "recognize.html"
    )


# ==========================================================
# Prediction
# ==========================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    # Check file
    if "image" not in request.files:

        return "No image uploaded."


    file = request.files["image"]


    if file.filename == "":

        return "No image selected."


    # Save uploaded image
    image_name = file.filename

    image_path = os.path.join(
        UPLOAD_FOLDER,
        image_name
    )

    file.save(image_path)


    # Open image
    image = Image.open(
        image_path
    )


    # Preprocess
    processed_image = preprocess_image(
        image
    )


    # Model prediction
    predictions = model.predict(
        processed_image,
        verbose=0
    )


    probabilities = predictions[0]


    # Predicted class
    predicted_index = np.argmax(
        probabilities
    )


    predicted_class = CLASS_NAMES[
        predicted_index
    ]


    # Confidence
    confidence = float(
        probabilities[predicted_index] * 100
    )


    # ======================================================
    # Probability Data
    # ======================================================

    probability_data = []


    for i in range(
        len(CLASS_NAMES)
    ):

        probability_data.append({

            "class_name":
                CLASS_NAMES[i],

            "probability":
                float(
                    probabilities[i] * 100
                )

        })


    # ======================================================
    # Save Prediction
    # ======================================================

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()


    cursor.execute("""
        INSERT INTO predictions
        (
            image_name,
            predicted_class,
            confidence,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (

        image_name,

        predicted_class,

        confidence,

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    ))


    connection.commit()

    connection.close()


    # ======================================================
    # Result Page
    # ======================================================

    return render_template(

        "result.html",

        predicted_class=predicted_class,

        confidence=confidence,

        probability_data=probability_data,

        image_name=image_name

    )


# ==========================================================
# Prediction History
# ==========================================================

@app.route("/history")
def history():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM predictions
        ORDER BY id DESC
    """)


    predictions = cursor.fetchall()


    connection.close()


    return render_template(
        "history.html",
        predictions=predictions
    )


# ==========================================================
# About Page
# ==========================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# ==========================================================
# Run Application
# ==========================================================

if __name__ == "__main__":

    init_database()

    app.run(
        debug=True
    )