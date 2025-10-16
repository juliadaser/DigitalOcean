from flask import Flask
from flask import render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from werkzeug.utils import secure_filename
import base64
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "randomstring"

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
        
        # Delete user's selfie
        os.remove(temp_filename)


        

    return render_template("index.html", form=form,
        file_url=file_url,
        similarity_results=similarity_results,)


if __name__ == "__main__":  # ← this part must exist
    app.run(host="0.0.0.0", port=8080, debug=True)
