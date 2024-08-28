from flask import Flask, request, jsonify, render_template, Blueprint
import os
import json
import shutil

home_Classification_blueprint = Blueprint('home_Classification', __name__)

@home_Classification_blueprint.route('/classification_home')
def handclassification_home():
    # Move the images that have no detection to the error_label folder
    display_image_folder = os.path.join(os.getcwd(),'HandClassification', 'change_label', "display")
    raw_image_folder = os.path.join(os.getcwd(), 'HandClassification', 'change_label', 'raw')
    error_bbox_folder = os.path.join(os.getcwd(), 'HandClassification', 'Adapt_bbox')
    path_to_error_label_file = os.path.join(os.getcwd(),'HandClassification', 'change_label', 'error_label.json')
    if os.path.exists(path_to_error_label_file):
        with open(path_to_error_label_file, 'r') as f:
            json_list = f.readlines()

        json_list = json.loads(json_list[0])
        updated_error_label_list = []
        updated_error_bbox_list = []
        for dic in json_list:
            try:
                if 'box' not in dic:
                    shutil.move(os.path.join(raw_image_folder, dic['picture']), os.path.join(error_bbox_folder, dic['picture']))
                    os.remove(os.path.join(display_image_folder, dic['picture']))
                    updated_error_bbox_list.append(dic)
                else:
                    updated_error_label_list.append(dic)
            except KeyError:
                updated_error_label_list.append(dic)
                print(dic)

            with open(path_to_error_label_file, 'w') as f:
                json.dump(updated_error_label_list, f)

        path_to_error_bbox_file = os.path.join(os.getcwd(),'HandClassification', 'error_bbox.json')
        if os.path.exists(path_to_error_bbox_file):
            with open(path_to_error_bbox_file, 'r') as f:
                json_list = f.readlines()

            json_list = json.loads(json_list[0])
            json_list.extend(updated_error_bbox_list)
            with open(path_to_error_bbox_file, 'w') as f:
                json.dump(json_list, f)
        else:
            with open(path_to_error_bbox_file, 'w') as f:
                json.dump(updated_error_bbox_list, f)

    return render_template('classificator_home.html')

@home_Classification_blueprint.route('/get_numbers', methods=['GET'])
def get_numbers():
    count_label = len(os.listdir("HandClassification/change_label/raw"))
    count_bounding_box = len(os.listdir("HandClassification/Adapt_bbox"))
    return jsonify({'labelNumber': count_label, 'boundingBoxNumber': count_bounding_box})