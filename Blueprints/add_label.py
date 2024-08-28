from flask import request, jsonify, render_template, Blueprint, send_from_directory
import os
import json
import shutil
import traceback

add_label_blueprint = Blueprint('add_label', __name__)

@add_label_blueprint.route('/add_labels')
def add_labels():
    display_image_folder = os.path.join(os.getcwd(),'HandClassification', 'change_label', "display")
    raw_image_folder = os.path.join(os.getcwd(), 'HandClassification', 'change_label', 'raw')
    error_bbox_folder = os.path.join(os.getcwd(), 'HandClassification', 'Adapt_bbox')
    path_to_error_label_file = os.path.join(os.getcwd(),'HandClassification', 'change_label', 'error_label.json')
    with open(path_to_error_label_file, 'r') as f:
        json_list = f.readlines()

    json_list = json.loads(json_list[0])
    updated_error_label_list = []
    for dic in json_list:
        if dic['class'] == "no detection":
            shutil.move(os.path.join(raw_image_folder, dic['picture']), os.path.join(error_bbox_folder, dic['picture']))
            os.remove(os.path.join(display_image_folder, dic['picture']))
        else:
            updated_error_label_list.append(dic)

    with open(path_to_error_label_file, 'w') as f:
        json.dump(updated_error_label_list, f)

    #Get the images for the website
    images = os.listdir(display_image_folder)
    return render_template('label.html', images=images)

@add_label_blueprint.route('/serve_image/<filename>')
def serve_image(filename):
    image_folder = os.path.join(os.getcwd(),'HandClassification', 'change_label', "display")
    return send_from_directory(image_folder, filename)

@add_label_blueprint.route('/save_labels', methods=['POST'])
def save_labels():
    # Get the data from the request
    classification_json = request.get_json()

    #Filter out the pictures that were labeled
    classification_json_for_changes = [d for d in classification_json if 'group' in d]

    #categories
    file_path_categories = os.path.join(os.getcwd(), 'categories.json')
    with open(file_path_categories, 'r') as f:
        categories_list = json.load(f)

    #imgs
    source_folder = os.path.join(os.getcwd(), 'Handclassification', 'change_label')
    source_folder_raw_imgs = os.path.join(source_folder,'raw')
    source_folder_display_imgs = os.path.join(source_folder,'display')
    destination_folder_train_imgs = os.path.join("Trainingsdaten", "images")

    #load json that needs to be adapted for the images that were labeled
    path_to_error_label_file = os.path.join(os.getcwd(),'HandClassification', 'change_label', 'error_label.json')
    with open(path_to_error_label_file, 'r') as f:
        error_label_dict_list = f.readlines()

    ready_to_train_list = []
    updated_error_label_list = []
    print("Error_Label LIST: ", error_label_dict_list)
    for element in classification_json_for_changes:
        filename = element['image'].split('/')[-1]
        json_list = json.loads(error_label_dict_list[0])
        for dic in json_list:
            try:
                if dic['picture'] == filename:
                    ready_to_train_dic = {}
                    if element['krank'] == False:
                        for category in categories_list[4:7]:
                            if category["name"] == element['group']:
                                ready_to_train_dic["class"] = category["id"]
                                ready_to_train_dic['name'] = category["name"]
                                break
                    else:
                        for category in categories_list:
                            if category["name"].split("_")[0] == element['group']:
                                ready_to_train_dic['name'] = category["name"]
                                ready_to_train_dic["class"] = category["id"]
                                break
                    ready_to_train_dic['box'] = dic['box']
                    ready_to_train_dic['picture'] = dic['picture']
                    ready_to_train_dic['width'] = dic['width']
                    ready_to_train_dic['height'] = dic['height']
                    shutil.move(os.path.join(source_folder_raw_imgs, filename), os.path.join(destination_folder_train_imgs, filename))
                    os.remove(os.path.join(source_folder_display_imgs, filename))
                    ready_to_train_list.append(ready_to_train_dic)
                    break
            except KeyError:
                traceback.print_exc()
                print(f"Error while processing {dic}")
                continue

        json_list = json.loads(error_label_dict_list[0])
        for dic in json_list:
            if dic['picture'] not in [d['image'].split('/')[-1] for d in classification_json_for_changes]:
                updated_error_label_list.append(dic)

    # Speichern Sie die aktualisierte result_json_list zurück in die Datei
    with open(path_to_error_label_file, 'w') as f:
        json.dump(updated_error_label_list, f)

    ready_to_train_filename = os.path.join(os.getcwd(),"Trainingsdaten", "ready_to_train.json")
    if ready_to_train_list:
        if os.path.exists(ready_to_train_filename):
            with open(ready_to_train_filename, 'r') as f:
                existing_ready_to_train_list = json.load(f)
        else:
            existing_ready_to_train_list = []
        
        # Append the new list to the existing list
        updated_ready_to_train_list = existing_ready_to_train_list + ready_to_train_list

        # Write the updated list to the file
        with open(ready_to_train_filename, 'w') as f:
            json.dump(updated_ready_to_train_list, f)

    return "Labels saved successfully"