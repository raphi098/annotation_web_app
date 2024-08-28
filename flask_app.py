import os
import sys
sys.path.append(os.path.join(os.getcwd(), "Blueprints"))
print(sys.path)
from flask import Flask, render_template
from flask_cors import CORS
from Blueprints.ai_predictor import ai_classification_blueprint
from Blueprints.main import home_Classification_blueprint
from Blueprints.add_label import add_label_blueprint
from Blueprints.add_bbox import add_bbox_blueprint

app = Flask(__name__)
CORS(app)  # Allows requests from all domains

app.register_blueprint(home_Classification_blueprint) 

app.register_blueprint(add_label_blueprint)
app.register_blueprint(add_bbox_blueprint)
app.register_blueprint(ai_classification_blueprint)

@app.route('/')
def home():
    return render_template('classificator_home.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
