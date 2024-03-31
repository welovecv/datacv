import json
import random
import os
from PIL import Image

# Load the original COCO dataset
with open('/data/vdu2024/source_pool/coco_8000.json', 'r') as f:
    coco_data = json.load(f)

if not os.path.exists("/data/vdu2024/source_pool/coco_8000_mosaic/"):
    os.mkdir("/data/vdu2024/source_pool/coco_8000_mosaic/")

# Create a list where each image appears four times
image_ids = [img['id'] for img in coco_data['images']]
image_ids_repeated = image_ids * 4  # Repeat each image ID four times

# Shuffle the list to ensure random distribution
random.shuffle(image_ids_repeated)

# Function to resize image maintaining aspect ratio
def resize_image(image, max_width, max_height):
    original_width, original_height = image.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_size = (int(original_width * ratio), int(original_height * ratio))
    resized_image = image.resize(new_size, Image.ANTIALIAS)
    return resized_image, ratio

# Function to create mosaic images and update annotations
def create_mosaic(group_ids, new_image_id, new_annotation_id):
    new_image = Image.new('RGB', (1024, 1024))
    new_annotations = []
    quadrant_width, quadrant_height = 512, 512

    for i, img_id in enumerate(group_ids):
        # Find the image by ID
        item = next(item for item in coco_data["images"] if item["id"] == img_id)
        original_image = Image.open("/data/vdu2024/source_pool/coco_train/" + item["file_name"])
        resized_image, scale = resize_image(original_image, quadrant_width, quadrant_height)

        x_offset = (i % 2) * quadrant_width
        y_offset = (i // 2) * quadrant_height
        new_image.paste(resized_image, (x_offset, y_offset))

        # Update annotations
        for ann in coco_data["annotations"]:
            if ann["image_id"] == img_id:
                new_ann = ann.copy()
                new_ann['id'] = new_annotation_id
                new_ann["image_id"] = new_image_id
                new_ann["bbox"] = [
                    ann["bbox"][0] * scale + x_offset,
                    ann["bbox"][1] * scale + y_offset,
                    ann["bbox"][2] * scale,
                    ann["bbox"][3] * scale
                ]
                new_annotations.append(new_ann)
                new_annotation_id += 1

    return new_image, new_annotations, new_annotation_id

# Prepare new dataset structure
new_coco_data = {
    "images": [],
    "annotations": [],
    "categories": coco_data["categories"]
}

# Generate mosaic images
new_image_id = 1
new_annotation_id = max(ann['id'] for ann in coco_data['annotations']) + 1 if coco_data['annotations'] else 1

# Split the image IDs into groups of four for the mosaics
for i in range(0, len(image_ids_repeated), 4):
    group_ids = image_ids_repeated[i:i + 4]
    new_image, new_annotations, new_annotation_id = create_mosaic(group_ids, new_image_id, new_annotation_id)
    new_image_file_name = f'mosaic_{new_image_id}.jpg'
    new_image.save(f'/data/vdu2024/source_pool/coco_8000_mosaic/{new_image_file_name}')

    # Update the new dataset
    new_coco_data["images"].append({
        "id": new_image_id,
        "file_name": new_image_file_name,
        "width": 1024,
        "height": 1024
    })
    new_coco_data["annotations"].extend(new_annotations)

    new_image_id += 1

# Save the new COCO-formatted JSON
with open('/data/vdu2024/source_pool/coco_8000_mosaic.json', 'w') as f:
    json.dump(new_coco_data, f)
