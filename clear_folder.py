import os
import shutil

def delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def delete_file(file_path):
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        else:
            print(f'Error: {file_path} is not a file or a symbolic link')
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

delete_files_in_folder(os.path.join(os.getcwd(),"HandClassification", "Adapt_bbox"))
delete_files_in_folder(os.path.join(os.getcwd(),"HandClassification", "change_label","raw"))
delete_files_in_folder(os.path.join(os.getcwd(),"HandClassification", "change_label","display"))
delete_files_in_folder(os.path.join(os.getcwd(),"Trainingsdaten","images"))
delete_file(os.path.join(os.getcwd(),"Trainingsdaten","ready_to_train.json"))
delete_file(os.path.join(os.getcwd(),"HandClassification","error_bbox.json"))
delete_file(os.path.join(os.getcwd(),"HandClassification", "change_label","error_label.json"))
