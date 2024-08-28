from flask import request, jsonify, render_template, Blueprint, send_from_directory
import os
import json
import shutil
from PIL import Image, ImageDraw
add_bbox_blueprint= Blueprint('BboxClassification', __name__)

def create_img_with_bbox(label_data_list):
    for data in label_data_list:
        print("Start of loop")
        x1 = data['box']['x1'] * data['width']
        y1 = data['box']['y1'] * data['height']
        x2 = data['box']['x2'] * data['width']
        y2 = data['box']['y2'] * data['height']

        print("Before opening image")
        img = Image.open(os.path.join(os.getcwd(), 'HandClassification', 'Adapt_bbox', data['picture']))
        print("After opening image")

        draw = ImageDraw.Draw(img)

        print("Before drawing rectangle")
        start_point = (int(x1), int(y1))
        end_point = (int(x2), int(y2))
        draw.rectangle([start_point, end_point], outline ="red")
        print("After drawing rectangle")

        print("Before saving image")
        img_path = os.path.join(os.getcwd(), 'HandClassification', 'change_label', 'display', data['picture'])
        # Save the image
        print("Before saving image")
        img.save(img_path)
        print("After saving image: ", img_path)
        # Close the image file
        img.close()

        print("Before moving image")
        src_path = os.path.join(os.getcwd(), 'HandClassification', 'Adapt_bbox', data['picture'])
        dst_path = os.path.join(os.getcwd(), 'HandClassification', 'change_label', 'raw', data['picture'])
        shutil.move(src_path, dst_path)


@add_bbox_blueprint.route('/BboxClassification')
def home():
    image_folder = os.path.join(os.getcwd(),'HandClassification', 'Adapt_bbox')
    images = os.listdir(image_folder)
    print(images)
    return render_template('Expand_knowledge.html', images=images)

@add_bbox_blueprint.route('/serve_image2/<filename>')
def serve_image2(filename):
    image_folder = os.path.join(os.getcwd(),'HandClassification', 'Adapt_bbox')
    print(image_folder)
    return send_from_directory(image_folder, filename)

@add_bbox_blueprint.route('/image_list')
def image_list():
    image_folder = os.path.join(os.getcwd(), 'HandClassification', 'Adapt_bbox')
    image_files = os.listdir(image_folder)
    return jsonify(image_files)

@add_bbox_blueprint.route('/get_error_bbox_json')
def get_error_bbox_json():
    with open(os.path.join(os.getcwd(), 'HandClassification', 'error_bbox.json'), 'r') as f:
        error_bbox_list = json.load(f)
    return error_bbox_list

@add_bbox_blueprint.route('/save_bbox', methods=['POST'])
def save_bbox():
    label_value_list = request.get_json()
    print("Label value list: ", label_value_list)

    train_data_list = []
    label_data_list = []
    bbox_data_list = []
    # Scale the bounding boxes because when they were drown pictures bigger that 640*480 were downscaled
    for label_value in label_value_list:
        if label_value['rect'] is not None:
            # Calculate the scale factor
            maxWidth = 640
            maxHeight = 480
            width = label_value['width']
            height = label_value['height']
            scale = 1
            if width > maxWidth or height > maxHeight:
                scale = min(maxWidth / width, maxHeight / height)

            # Scale the rectangle dimensions
            label_value['rect']['startX'] *= scale
            label_value['rect']['startY'] *= scale
            label_value['rect']['width'] *= scale
            label_value['rect']['height'] *= scale
            if label_value['group'] == None and label_value['krank'] == None:
                label_data_list.append(label_value)
            else:
                train_data_list.append(label_value)
        else:
            bbox_data_list.append(label_value)
    print("Label_data_list:", label_data_list)
    final_label_data_list = []
    for data in label_data_list:
        label_list = {}
        label_list['class'] = "not labeled"
        label_list['picture'] = data['img_name']
        label_list['width'] = data['width']
        label_list['height'] = data['height']
        label_list['borderStyle'] = '4px solid orange'
         # Assign initial values to x1, y1, x2, and y2
        x1 = data['rect']['startX']
        y1 = data['rect']['startY']
        x2 = x1 + data['rect']['width']
        y2 = y1 + data['rect']['height']
        #Normalize the box values
        x1 /= data['width']
        y1 /= data['height']
        x2 /= data['width']
        y2 /= data['height']
        label_list['box'] = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
        label_list['name'] = "not labeled"
        final_label_data_list.append(label_list)
    print("Final label data list: ", final_label_data_list)

    # Move the images that have no detection to the error_label folder
    if final_label_data_list:
        create_img_with_bbox(final_label_data_list)
        # Define the path to the JSON file
        json_file_path = os.path.join(os.getcwd(), 'HandClassification', 'change_label', 'error_label.json')

        # Check if the JSON file exists
        if os.path.exists(json_file_path):
            # Load the data from the JSON file
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)

            # Add the data to final_label_data_list
            data.extend(final_label_data_list)
            # Save label_data_list to the same file, replacing the old list
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file)
        else:
            # If the file does not exist, save label_data_list to a new file named error_label.json
            with open(json_file_path, 'w') as json_file:
                json.dump(final_label_data_list, json_file)

    # Load the categories
    with open('categories.json', 'r') as f:
        categories_list = json.load(f)
    final_train_data_list = []
    for data in train_data_list:
        data_dict = {}
        data_dict['picture'] = data['img_name']
        x1 = data['rect']['startX']
        y1 = data['rect']['startY']
        x2 = x1 + data['rect']['width']
        y2 = y1 + data['rect']['height']
        data_dict['width'] = data['width']
        data_dict['height'] = data['height']
        #Normalize the box values
        x1 /= data['width']
        y1 /= data['height']
        x2 /= data['width']
        y2 /= data['height']
        data_dict['box'] = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
        for category in categories_list:
            if data['krank'] == 'krank':
                cat = category['name'].split('_')[0]
                if cat == data['group']:
                    data_dict['class'] = category['id']
                    data_dict['name'] = category['name']
                    break
            else:
                if category['name'] == data['group']:
                    data_dict['class'] = category['id']
                    data_dict['name'] = category['name']
                    break
        final_train_data_list.append(data_dict)
        print("Final train data list: ", final_train_data_list)
        shutil.move(os.path.join(os.getcwd(), 'HandClassification', 'Adapt_bbox', data_dict['picture']),
                    os.path.join(os.getcwd(), 'Trainingsdaten','images', data_dict['picture']))

    # Define the path to the JSON file
    json_file_path = os.path.join(os.getcwd(), 'Trainingsdaten','ready_to_train.json')

    # Check if the JSON file exists
    if os.path.exists(json_file_path):
        # Load the data from the JSON file
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        # Add the data to final_label_data_list
        data.extend(final_train_data_list)
        # Save final_train_data_list to the same file, replacing the old list
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file)
    else:
        # If the file does not exist, save final_train_data_list to a new file named ready_to_train.json
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file)

    combined_data_list = final_train_data_list + final_label_data_list       
    file_path = os.path.join(os.getcwd(), 'HandClassification', 'error_bbox.json')
    with open(file_path, 'r') as f:
        current_data = json.load(f)
    print("Combined data list", combined_data_list)
        
    new_error_data = []
    for data in current_data:
        for i, combined_data in enumerate(combined_data_list):
            if data['picture'] == combined_data['picture']:
                break
            if i == len(combined_data_list) - 1:
                new_error_data.append(data)
                
    with open(file_path, 'w') as f:
        json.dump(new_error_data, f)

    return jsonify(success=True)