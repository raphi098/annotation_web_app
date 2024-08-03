from flask import Blueprint, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
import subprocess
from ultralytics import YOLO
import json
from PIL import Image
import shutil
import glob
import re
import hashlib
import random
import json

ai_classification_blueprint = Blueprint('Ki Klassifizierung', __name__)
@ai_classification_blueprint.route('/ai_classification')
def ai_classification():
    return render_template('ai_classification.html')
def extract_frames(video_path, output_dir, every_n_frames):
    print('Extracting frames...')

    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"fps={every_n_frames}",  # Select every every_n_frames frame
        os.path.join(output_dir, 'frame_%04d.png')  # use the output file path here
    ]
    subprocess.run(command)

# Generate hash values for the extracted frames = max_number + random_number + picture_name
    # List all the files in the directories
    path_error_labels_img = os.path.join(os.getcwd(), 'HandClassification', 'change_label', 'raw')
    path_error_bboxes_img = os.path.join(os.getcwd(), 'HandClassification', 'Adapt_bbox')
    path_trainingsdaten_img = os.path.join(os.getcwd(), 'Trainingsdaten', 'images')

    hand_classification_files = os.listdir(path_error_labels_img) + os.listdir(path_error_bboxes_img)
    trainingsdaten_images_files = os.listdir(path_trainingsdaten_img)

    # Combine the two lists of files
    all_files = hand_classification_files + trainingsdaten_images_files

    # Extract the numbers from the filenames
    numbers = [int(re.search(r'\d+', filename).group()) for filename in all_files if re.search(r'\d+', filename)]

    # Find the maximum number, or use 0 if the list is empty
    max_number = max(numbers) if numbers else 0

    # Get the current picture names of the extracted frames
    file_names = os.listdir(output_dir)
    
    # Filter out files that are not .png
    png_files = [file for file in file_names if file.endswith('.png')]

    # Rename the files with hash values
    for png in png_files:
        # Generate a random number between 1 and 1000000
        random_number = random.randint(1, 1000000)

        # Create a string from the picture name, max_number, and random_number
        input_string = png + str(max_number) + str(random_number)

        # Create a hash value
        hash_object = hashlib.sha1(input_string.encode())
        hex_dig = hash_object.hexdigest()

        # Convert the hexadecimal hash to a decimal number
        id = int(hex_dig, 16) % 10000000000

        # Rename the file with the hash value
        os.rename(os.path.join(output_dir, png), os.path.join(output_dir, f'{id}.png'))

def append_list(filename, list):
    if list:
        # Load the existing list if the file exists
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing_list = json.load(f)
        else:
            existing_list = []

        # Append the new list to the existing list
        list = existing_list + list

        # Save the updated list to the file
        with open(filename, 'w') as f:
            json.dump(list, f)


@ai_classification_blueprint.route('/upload', methods=['POST'])
def upload_file():
    print('Uploading file...')
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
    try:
        video_path = os.path.join('Videos', filename)
        file.save(video_path)

        # Specify the directory
        dir_path = os.path.join(os.getcwd(), 'extracted_frames')

        # Delete all image files in the directory
        image_files = os.listdir(dir_path)
        for file in image_files:
            os.remove(os.path.join(dir_path, file))
        extract_frames(video_path, 'extracted_frames', int(request.form['frames']) )  # Change 'Frames' to 'extracted_frames'
    except Exception as e:
        print("Error saving file:", e)
        return 'Error saving file'
    video_title, extension = filename.split('.')[0], filename.split('.')[1]
    return f'Video: {video_title}, Upload erfolgreich'


@ai_classification_blueprint.route('/predict', methods=['GET'])
def predict():
    # Clear the directory of old prediciton images
    directory = 'static/detected_nerves/*'
    files = glob.glob(directory)
    for f in files:
        os.remove(f)
    # Extract file_paths in the extracted_frames directory + make sure that they are .png files
    files = os.listdir("extracted_frames")
    pictures = list(filter(lambda x: x.endswith('.png'), files))
    picture_paths = [os.path.join("extracted_frames", picture) for picture in pictures]

    # Path to trained model and prediction for pictures in extracted_frames saved in results
    model_path = os.path.join("prediction_model", "yolo_n_v8.pt")
    model = YOLO(model_path)
    results = model.predict(picture_paths, max_det = 1)

    # Create a JSON file with the results + Picture size and width + save it in the runs folder
    with Image.open(picture_paths[0]) as img:
        width, height = img.size

    result_json_list = []
    filenames = []
    for index, result in enumerate(results):
        try:
            result_dict = json.loads(result.tojson(normalize=True))[0]
        except IndexError:
            result_dict = {"class": "no detection"}
        result_dict["picture"] = pictures[index]
        result_dict["width"] = width
        result_dict["height"] = height
        result_json_list.append(result_dict)
        filenames.append(pictures[index])
        result.save(f"static/detected_nerves/{pictures[index]}")

    with open('runs/result_json_list.json', 'w') as f:
        json.dump(result_json_list, f)

    return jsonify(filenames)

@ai_classification_blueprint.route('/save_data', methods=['POST'])
def save_data():
    # Get the data from the request
    prediction_categorie_list = request.get_json()

    # Determine the nerve name and class
    nerv_is_krank = False
    nerv_class = None
    nerv_name = None
    with open(os.path.join(os.getcwd(), 'categories.json' ), 'r') as f:
        catergory_list = json.load(f)

    if prediction_categorie_list[0]["selectedRadioValue"] is not None:
        nerv_is_krank = prediction_categorie_list[0]["krankBoxChecked"]
        if nerv_is_krank is False:
            nerv_name = prediction_categorie_list[0]["selectedRadioValue"]
        else:
            nerv_name = prediction_categorie_list[0]["selectedRadioValue"] + "_krank"
        for category in catergory_list:
            if category["name"] == nerv_name:
                nerv_class = category["id"]
                break

    #Paths to the source and destination folders of images and json files
    source_folder_raw_imgs = 'extracted_frames' 
    source_folder_display_imgs = os.path.join("static", "detected_nerves")
    destination_folder_train_imgs = os.path.join("Trainingsdaten", "images")
    destination_folder_error_bbox_imgs = os.path.join("HandClassification", "Adapt_bbox")
    destination_folder_error_bbox_json = os.path.join("HandClassification")
    destination_folder_error_label_raw_imgs = os.path.join("HandClassification", "change_label", "raw")
    destination_folder_error_label_display_imgs = os.path.join("HandClassification", "change_label", "display")

    #get data from the result json from the prediction
    path_to_file = os.path.join(os.getcwd(), "runs", 'result_json_list.json')
    with open(path_to_file, 'r') as f:
        result_json_list = f.readlines()
    result_json_list = json.loads(result_json_list[0])

    # Add the borderStyle to the result_json_list 
    #(borderStyle categories: green = ready to train, red = bbox wrong, orange = label wrong)
    combined_dic_list = []
    for element in result_json_list:
        for element2 in prediction_categorie_list:
            if element["picture"] == element2["filename"]:
                element["borderStyle"] = element2["borderStyle"]
                combined_dic_list.append(element)
                break

    ready_to_train_list = []
    error_label_list = []
    error_bbox_list = []

    for element in combined_dic_list:
        filename = element['picture']
        source = os.path.join(source_folder_raw_imgs, filename)
        # Check if the nerve is labeled in the Predictor screen
        if nerv_class is not None:
            element['class'] = nerv_class
            element['name'] = nerv_name
        elif nerv_class is None and element['borderStyle'] == '4px solid orange' or nerv_class is None and element['borderStyle'] == '4px solid red':
            element['class'] = "not labeled"
            element['name'] = "not labeled"

        if element['borderStyle'] == '4px solid green' or element['borderStyle'] == '4px solid orange' and nerv_class is not None:
            destination_imgs = os.path.join(destination_folder_train_imgs, filename)
            ready_to_train_list.append(element)
        elif element['borderStyle'] == '4px solid red':
            destination_imgs = os.path.join(destination_folder_error_bbox_imgs, filename)
            error_bbox_list.append(element)
        else:
            destination_imgs = os.path.join(destination_folder_error_label_raw_imgs, filename)
            error_label_list.append(element)
            shutil.move(os.path.join(source_folder_display_imgs, filename), os.path.join(destination_folder_error_label_display_imgs, filename))
            
        # Check if file exists in the source folder
        if os.path.exists(source):
            # Move the file
            shutil.move(source, destination_imgs)
        else:
            print(f'File {source} not found in source folder')
    # Define the filenames for the error_bbox, error_label and okay lists
    error_label_filename = os.path.join(os.getcwd(),"HandClassification", 'change_label', "error_label.json")
    error_bbox_filename = os.path.join(destination_folder_error_bbox_json, "error_bbox.json")
    ready_to_train_filename = os.path.join(os.getcwd(),"Trainingsdaten", "ready_to_train.json")

    append_list(error_label_filename, error_label_list)
    append_list(ready_to_train_filename, ready_to_train_list)
    append_list(error_bbox_filename, error_bbox_list)
    return jsonify({'result': True})
