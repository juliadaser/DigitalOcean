from flask import Flask
from flask import render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from werkzeug.utils import secure_filename
import base64
import os
import pickle 
from deepface import DeepFace
import numpy as np

# --- Utility functions ---
def get_embedding(img_path, model_name="Facenet"):
    result = DeepFace.represent(img_path=img_path, model_name=model_name, enforce_detection=False)
    if isinstance(result, list):
        return result[0]["embedding"]
    return result["embedding"]

def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    cos_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return (cos_sim + 1) / 2


# # --- Memory Usage ---
# def print_memory_usage(note=""):
#     process = psutil.Process()
#     mem = process.memory_info().rss / (1024 * 1024)  # MB
#     print(f"[MEMORY] {note} - {mem:.2f} MB")

app = Flask(__name__)
app.config["SECRET_KEY"] = "randomstring"

# Reference folder with money bills
REFERENCE_DIR = "./static/bills_db"
os.makedirs(REFERENCE_DIR, exist_ok=True)

# Precompute embeddings once
EMBEDDINGS_FILE = "./embeddings/embeddings.pkl"

with open(EMBEDDINGS_FILE, "rb") as f:
    REFERENCE_EMBEDDINGS = pickle.load(f)
# print_memory_usage("After loading reference embeddings")

# --- Form definition ---
class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(["jpg", "jpeg", "png"], "Only images are allowed"),
            FileRequired("File field should not be empty"),
        ]
    )
    submit = SubmitField("Upload")


@app.route("/", methods=["GET", "POST"])
def hello_world():
    form = UploadForm()
    file_url = None
    similarity_results = []

    if form.validate_on_submit():
        # Read user's selfie into memory
        file = form.photo.data
        img_bytes = file.read()

        # Convert selfie base64 to display on webpage
        file_url = "data:image/png;base64," + base64.b64encode(img_bytes).decode("utf-8")

        # Save selfie temporarily to disk just for DeepFace
        temp_filename = f"temp_{secure_filename(file.filename)}"
        with open(temp_filename, "wb") as f:
            f.write(img_bytes)

        # Compute embedding for user's file
        user_embedding = get_embedding(temp_filename, model_name="Facenet")
        # print_memory_usage("After computing user embedding")

        
        # Delete user's selfie
        os.remove(temp_filename)

        # Compare selfie embedding against precomputed embeddings
        results = []
        if user_embedding is not None:
            for ref_path, ref_embedding in REFERENCE_EMBEDDINGS:
                similarity = cosine_similarity(user_embedding, ref_embedding)
                results.append((os.path.basename(ref_path), similarity))

            # Sort results by similarity
            similarity_results = sorted(results, key=lambda x: x[1], reverse=True)


    return render_template("index.html", form=form,
        file_url=file_url,
        similarity_results=similarity_results,)


if __name__ == "__main__":  # ← this part must exist
    app.run(host="0.0.0.0", port=8080, debug=True)
