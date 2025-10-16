import os
from flask import Flask, render_template

# --- Flask setup ---
app = Flask(__name__)

# --- Main route ---
@app.route("/", methods=["GET", "POST"])
def random_function():
    
    variable_here = True

    return render_template(
        "index.html",
        variable_here= variable_here,
    )

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)