# This is the code for transforming yolo predict results into coco format
import os
import json
from PIL import Image

#-----------------------------------------------------------------
# step1: adjust the label id to 0
# the dir of yolov8 inference results
directory = './ap_sort/predict/labels'

for filename in os.listdir(directory):
    if filename.endswith('.txt'):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            lines = file.readlines()
        # change the label id of bus and truck
        modified_lines = []
        for line in lines:
            if line.strip():  
                modified_line = '0'+' '+ line.split(None, 1)[1]
                modified_lines.append(modified_line)
            else:
                modified_lines.append(line)
        # 将修改后的内容写回文件
        with open(file_path, 'w') as file:
            file.writelines(modified_lines)

# print("all txt labels' first col turned to 0")

#-----------------------------------------------------------------
# step2: turn yolo format into coco

def yolo_to_coco(box, img_size):
    # YOLO：[x_center, y_center, width, height]
    # COCO：[x_min, y_min, width, height]
    x_center, y_center, width, height = box
    x_min = int((x_center - width / 2) * img_size[0])
    y_min = int((y_center - height / 2) * img_size[1])
    return [x_min, y_min, int(width * img_size[0]), int(height * img_size[1])]

coco_dict = {
    "images": [],
    "annotations": [],
    "categories": [{"id": 1, "name": "car", "supercategory": "vehicle"}]
}

yolo_label_dir = './ap_sort/predict/labels/'
image_dir = '/data/vdu2024/region_100/train/'
output_json_file = '/data/vdu2024/region_100/train_yolov8.json'
image_id = 1
annotation_id = 1


for filename in os.listdir(yolo_label_dir):
    if filename.endswith('.txt'):
        with open(os.path.join(yolo_label_dir, filename), 'r') as f:
            lines = f.readlines()
        
        image_name = filename[:-4] + '.jpg'
        image_path = os.path.join(image_dir, image_name)
        img = Image.open(image_path)
        img_size = img.size
        coco_dict["images"].append({
            "id": image_id,
            "file_name": image_name,
            "width": img_size[0],
            "height": img_size[1]
        })
        
        for line in lines:
            parts = line.strip().split()
            class_id, x_center, y_center, width, height = map(float, parts)
            if class_id == 0: 
                coco_dict["annotations"].append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": 1,
                    "bbox": yolo_to_coco([x_center, y_center, width, height], img_size),
                    "area": width * height * img_size[0] * img_size[1],
                    "iscrowd": 0
                })
                annotation_id += 1
        
        image_id += 1

with open(output_json_file, 'w') as f:
    json.dump(coco_dict, f)

print(f"Pseudo saved to {output_json_file}")

