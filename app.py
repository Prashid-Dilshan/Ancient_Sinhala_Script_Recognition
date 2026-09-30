from flask import Flask, render_template, request, redirect, url_for
import tensorflow as tf
import numpy as np
from PIL import Image
import sqlite3
from datetime import datetime
import os
import uuid


# ==========================================================
# Flask Application
# ==========================================================

app = Flask(__name__)


# ==========================================================
# Configuration
# ==========================================================

MODEL_PATH = "model/best_model_CNN.keras"

DATABASE = "database/app.db"

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ==========================================================
# Upload Validation Settings
# ==========================================================

# Allowed image extensions
ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


# Maximum upload size = 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


# ==========================================================
# Create Required Folders
# ==========================================================

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

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            original_filename TEXT NOT NULL,

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

    # Convert image to grayscale
    image = image.convert("L")


    # Resize image to 64 x 64
    image = image.resize(
        (64, 64)
    )


    # Convert image to NumPy array
    image = np.array(
        image
    )


    # Normalize pixel values
    image = image / 255.0


    # Reshape for CNN
    image = image.reshape(
        1,
        64,
        64,
        1
    )


    return image


# ==========================================================
# Check Allowed Image Extension
# ==========================================================

def allowed_file(filename):

    if "." not in filename:

        return False


    extension = filename.rsplit(
        ".",
        1
    )[1].lower()


    return extension in ALLOWED_EXTENSIONS


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


    # ======================================================
    # Check Whether Image Was Uploaded
    # ======================================================

    if "image" not in request.files:

        return render_template(
            "recognize.html",
            error="No image was uploaded."
        )


    file = request.files["image"]


    # ======================================================
    # Check Filename
    # ======================================================

    if file.filename == "":

        return render_template(
            "recognize.html",
            error="Please select an image."
        )


    # ======================================================
    # Original Filename
    # ======================================================

    original_filename = file.filename


    # ======================================================
    # Check File Extension
    # ======================================================

    if not allowed_file(original_filename):

        return render_template(
            "recognize.html",
            error=(
                "Invalid image format. "
                "Please upload JPG, JPEG, PNG or WEBP."
            )
        )


    # ======================================================
    # Check File Size
    # ======================================================

    file.seek(
        0,
        os.SEEK_END
    )

    file_size = file.tell()

    file.seek(0)


    if file_size > MAX_FILE_SIZE:

        return render_template(
            "recognize.html",
            error=(
                "Image is too large. "
                "Maximum file size is 5 MB."
            )
        )


    # ======================================================
    # Validate Actual Image Content
    # ======================================================

    try:

        image = Image.open(file)

        # Verify image integrity
        image.verify()


    except Exception:

        return render_template(
            "recognize.html",
            error=(
                "Invalid or corrupted image file."
            )
        )


    # ======================================================
    # Re-open Image After verify()
    # ======================================================

    file.seek(0)


    try:

        image = Image.open(file)

        image.load()


    except Exception:

        return render_template(
            "recognize.html",
            error=(
                "Unable to read the uploaded image."
            )
        )


    # ======================================================
    # Get File Extension
    # ======================================================

    file_extension = os.path.splitext(
        original_filename
    )[1].lower()


    # ======================================================
    # Generate Unique Filename
    # ======================================================

    image_name = (
        str(uuid.uuid4())
        + file_extension
    )


    # ======================================================
    # Create Image Path
    # ======================================================

    image_path = os.path.join(
        UPLOAD_FOLDER,
        image_name
    )


    # ======================================================
    # Save Valid Image
    # ======================================================

    try:

        file.seek(0)

        file.save(
            image_path
        )


    except Exception:

        return render_template(
            "recognize.html",
            error=(
                "Unable to save the uploaded image."
            )
        )


    # ======================================================
    # Preprocess Image
    # ======================================================

    try:

        processed_image = preprocess_image(
            image
        )


    except Exception:

        # Delete uploaded image
        if os.path.exists(image_path):

            os.remove(image_path)


        return render_template(
            "recognize.html",
            error=(
                "Unable to process the uploaded image."
            )
        )


    # ======================================================
    # Model Prediction
    # ======================================================

    try:

        predictions = model.predict(
            processed_image,
            verbose=0
        )


    except Exception:

        # Delete uploaded image
        if os.path.exists(image_path):

            os.remove(image_path)


        return render_template(
            "recognize.html",
            error=(
                "An error occurred while "
                "running the AI model."
            )
        )


    # ======================================================
    # Get Probability Array
    # ======================================================

    probabilities = predictions[0]


    # ======================================================
    # Get Predicted Class Index
    # ======================================================

    predicted_index = np.argmax(
        probabilities
    )


    # ======================================================
    # Get Predicted Class
    # ======================================================

    predicted_class = CLASS_NAMES[
        predicted_index
    ]


    # ======================================================
    # Get Confidence
    # ======================================================

    confidence = float(
        probabilities[
            predicted_index
        ] * 100
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
    # Save Prediction to Database
    # ======================================================

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()


    cursor.execute("""
        INSERT INTO predictions
        (
            original_filename,
            image_name,
            predicted_class,
            confidence,
            created_at
        )

        VALUES (?, ?, ?, ?, ?)

    """, (

        original_filename,

        image_name,

        predicted_class,

        confidence,

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    ))


    # ======================================================
    # Get Newly Created Prediction ID
    # ======================================================

    prediction_id = cursor.lastrowid


    connection.commit()

    connection.close()


    # ======================================================
    # Show Result Page
    # ======================================================

    return render_template(

        "result.html",

        predicted_class=predicted_class,

        confidence=confidence,

        probability_data=probability_data,

        image_name=image_name,

        original_filename=original_filename,

        prediction_id=prediction_id

    )


# ==========================================================
# Prediction History
# ==========================================================

@app.route("/history")
def history():


    # ======================================================
    # Get Search Value
    # ======================================================

    search = request.args.get(
        "search",
        ""
    ).strip()


    # ======================================================
    # Get Selected Era
    # ======================================================

    selected_era = request.args.get(
        "era",
        ""
    ).strip()


    # ======================================================
    # Database Connection
    # ======================================================

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()


    # ======================================================
    # Base Query
    # ======================================================

    query = """
        SELECT *
        FROM predictions
        WHERE 1=1
    """


    parameters = []


    # ======================================================
    # Search Filter
    # ======================================================

    if search:

        query += """
            AND (
                original_filename LIKE ?
                OR predicted_class LIKE ?
            )
        """


        search_value = f"%{search}%"


        parameters.extend([

            search_value,

            search_value

        ])


    # ======================================================
    # Era Filter
    # ======================================================

    if selected_era:

        query += """
            AND predicted_class = ?
        """


        parameters.append(
            selected_era
        )


    # ======================================================
    # Order
    # ======================================================

    query += """
        ORDER BY id DESC
    """


    # ======================================================
    # Execute Query
    # ======================================================

    cursor.execute(
        query,
        parameters
    )


    predictions = cursor.fetchall()


    connection.close()


    # ======================================================
    # History Page
    # ======================================================

    return render_template(

        "history.html",

        predictions=predictions,

        search=search,

        selected_era=selected_era,

        class_names=CLASS_NAMES

    )


# ==========================================================
# Delete Prediction
# ==========================================================

@app.route(
    "/delete/<int:prediction_id>",
    methods=["POST"]
)
def delete_prediction(
    prediction_id
):


    # ======================================================
    # Database Connection
    # ======================================================

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()


    # ======================================================
    # Find Prediction
    # ======================================================

    cursor.execute("""
        SELECT image_name
        FROM predictions
        WHERE id = ?
    """, (

        prediction_id,

    ))


    prediction = cursor.fetchone()


    # ======================================================
    # If Prediction Exists
    # ======================================================

    if prediction:

        image_name = prediction[
            "image_name"
        ]


        # ==================================================
        # Delete Database Record
        # ==================================================

        cursor.execute("""
            DELETE FROM predictions
            WHERE id = ?
        """, (

            prediction_id,

        ))


        connection.commit()


        # ==================================================
        # Delete Uploaded Image
        # ==================================================

        image_path = os.path.join(
            UPLOAD_FOLDER,
            image_name
        )


        if os.path.exists(
            image_path
        ):

            os.remove(
                image_path
            )


    # ======================================================
    # Close Database
    # ======================================================

    connection.close()


    # ======================================================
    # Redirect to History
    # ======================================================

    return redirect(
        url_for("history")
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


    # Initialize database
    init_database()


    # Run Flask application
    app.run(
        debug=True
    )