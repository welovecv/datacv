# This script mainly add bus and truck annotation from coco train2017
import json
import shutil
import os

coco_json_file = '/data/vdu2024/source_pool/coco_annotation.json'

with open(coco_json_file, 'r') as f:
    coco_data = json.load(f)

image_names = [image['file_name'] for image in coco_data['images']]

coco_json_file = '/data/vdu2024/source_pool/annotations/instances_train2017.json'
# coco_json_file = 'source_pool/instances_val2017.json'

with open(coco_json_file, 'r') as f:
    coco_data = json.load(f)


selected_image_ids = [image['id'] for image in coco_data['images'] if image['file_name'] in image_names]
selected_category_ids = [category['id'] for category in coco_data['categories'] if category['name'] in ['car', 'bus', 'truck']]
selected_annotations = [annotation for annotation in coco_data['annotations'] if annotation['image_id'] in selected_image_ids and annotation['category_id'] in selected_category_ids]

selected_coco = {
    "images": [image for image in coco_data['images'] if image['id'] in selected_image_ids],
    "annotations": selected_annotations,
    "categories": [category for category in coco_data['categories'] if category['id'] in selected_category_ids]
}

output_json_file = '/data/vdu2024/source_pool/coco_add_bus_truck.json'
# output_json_file = 'selected_from_coco_val2017.json'
with open(output_json_file, 'w') as f:
    json.dump(selected_coco, f)

coco_json_file = '/data/vdu2024/source_pool/coco_add_bus_truck.json'

output_json_file = '/data/vdu2024/source_pool/coco_updated.json'

with open(coco_json_file, 'r') as f:
    coco_data = json.load(f)

coco_data['categories'] = [{"id": 1, "name": "car", "supercategory": "vehicle"}]

for annotation in coco_data['annotations']:
    annotation['category_id'] = 1

with open(output_json_file, 'w') as f:
    json.dump(coco_data, f)

print(f"change all categories into car，save to {output_json_file}")
