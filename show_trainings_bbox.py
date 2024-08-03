import json
import os
import cv2


path = os.path.join("Trainingsdaten","ready_to_train.json")
image_path = os.path.join("Trainingsdaten", "images")
#categories
with open(path, 'r') as f:
    training = json.load(f)

for picture in training:
    if 'box' in picture:
        filename = picture['picture']
        
        img = cv2.imread(os.path.join(image_path, filename))
        print(os.path.join(image_path, filename))
        # Draw the bounding box
        # Calculate the actual x, y, width, and height of the box
        box_x1 = picture['box']['x1'] * picture['width']
        box_y1 = picture['box']['y1'] * picture['height']
        box_x2 = picture['box']['x2'] * picture['width']
        box_y2 = picture['box']['y2'] * picture['height']

        # The start and end points of the box are directly the x1, y1 and x2, y2 values
        start_point = (int(box_x1), int(box_y1))
        end_point = (int(box_x2), int(box_y2))
        color = (0, 0, 255)  # Green color in BGR
        thickness = 2  # Line thickness of 2 px

        img = cv2.rectangle(img, start_point, end_point, color, thickness)
        cv2.imshow("Image",img)
        cv2.waitKey(600)
    else:
        print("No box in picture: ", picture['picture'])

print(training)
