import os
import sys
sys.path.append(os.path.join(os.getcwd(), "Blueprints"))
print(sys.path)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ai_predictor import ai_classification_blueprint
from main import home_Classification_blueprint
from add_label import add_label_blueprint
from add_bbox import add_bbox_blueprint

app = Flask(__name__)
CORS(app)  # Erlaubt Anfragen von allen Domänen


app.register_blueprint(home_Classification_blueprint)
if __name__ == '__main__':
    app.run(debug=True)

app.register_blueprint(add_label_blueprint)
app.register_blueprint(add_bbox_blueprint)
app.register_blueprint(ai_classification_blueprint)


@app.route('/')
def home():
    return render_template('classificator_home.html')