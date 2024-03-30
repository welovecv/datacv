#-----------------------------------------------------------------
# step1 split the labels json for each image(by image id)
# for ground truth
import os
import sys
import json
import shutil
from tqdm import tqdm
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval


coco_annotation_file = '/data/vdu2024/source_pool/coco_updated.json'
gt_folder = './ap_sort/gt_each'
infer_folder = './ap_sort/infer_each'
new_label_dir = './ap_sort/gt_8000/'

if not os.path.exists(gt_folder):
    os.makedirs(gt_folder)
if not os.path.exists(infer_folder):
    os.makedirs(infer_folder)
if not os.path.exists(new_label_dir):
    os.makedirs(new_label_dir)
    
with open(coco_annotation_file, 'r') as f:
    coco_data = json.load(f)

coco = COCO(coco_annotation_file)

img_ids = coco.getImgIds()

for img_id in img_ids:
    single_img_coco = {
        "images": [coco.imgs[img_id]],
        "annotations": [],
        "categories": coco_data['categories']
    }

    ann_ids = coco.getAnnIds(imgIds=img_id)
    annotations = coco.loadAnns(ann_ids)

    single_img_coco["annotations"] = annotations

    output_file = f'./ap_sort/gt_each/{img_id}.json'
    with open(output_file, 'w') as f:
        json.dump(single_img_coco, f)

print("ground truth splited")

# for predict results

coco_result_file = './ap_sort/infer_coco.json'

with open(coco_result_file, 'r') as f:
    coco_results = json.load(f)

img_results = {}
for result in coco_results:
    img_id = result['image_id']
    if img_id not in img_results:
        img_results[img_id] = []
    img_results[img_id].append(result)

for img_id, results in img_results.items():
    output_file = f'./ap_sort/infer_each/{img_id}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f)

print("predict results splited")

#-----------------------------------------------------------------
# step2 sort the ap for each image

gt_files = [f for f in os.listdir(gt_folder) if f.endswith('.json')]
infer_files = [f for f in os.listdir(infer_folder) if f.endswith('.json')]

ap_results = {}

for gt_file in tqdm(gt_files):
    image_id = os.path.splitext(gt_file)[0]

    infer_file = f"{image_id}.json"
    if infer_file in infer_files:
        with open(os.path.join(gt_folder, gt_file), 'r') as f:
            gt_data = json.load(f)

        image_name = next(img['file_name'] for img in gt_data['images'] if img['id'] == int(image_id))

        with open(os.devnull, 'w') as devnull: # set no output in command shell
            old_stdout = sys.stdout
            sys.stdout = devnull
            cocoGt = COCO(os.path.join(gt_folder, gt_file))
            cocoDt = cocoGt.loadRes(os.path.join(infer_folder, infer_file))
            cocoEval = COCOeval(cocoGt, cocoDt, 'bbox')
            cocoEval.evaluate()
            cocoEval.accumulate()
            cocoEval.summarize()
            sys.stdout = old_stdout

        ap = cocoEval.stats[0]  # AP @[ IoU=0.50:0.95 | area=   all | maxDets=100 ]
        ap_results[(image_name, image_id)] = ap

sorted_ap_results = sorted(ap_results.items(), key=lambda x: x[1], reverse=True)

with open('./ap_sort/ap_results.txt', 'w') as f:
    for (image_name, image_id), ap in sorted_ap_results:
        f.write(f"Image Name: {image_name}, Image ID: {image_id}, AP: {ap}\n")

print("Results have been saved to ap_results.txt")

#-----------------------------------------------------------------
# step3 select the first 8000 as the final train set

sort_txt_file = './ap_sort/ap_results.txt'

original_label_dir = './ap_sort/gt_each/'

image_names = []
with open(sort_txt_file, 'r') as f:
    for i, line in enumerate(f):
        if i >= 8000:
            break
        parts = line.strip().split(', ')
        image_name = parts[0].split(': ')[1]
        image_names.append(image_name)

for image_name in image_names:
    label_file_name = os.path.splitext(image_name)[0].lstrip('0') + '.json'
    original_label_path = os.path.join(original_label_dir, label_file_name)

    new_label_path = os.path.join(new_label_dir, label_file_name)

    shutil.copy(original_label_path, new_label_path)

print(f"select 8000 images' json to {new_label_dir}")

gt_each_folder = './ap_sort/gt_8000'
output_json_file = '/data/vdu2024/source_pool/coco_8000.json'

merged_annotations = {
    "images": [],
    "annotations": [],
    "categories": []
}

for filename in os.listdir(gt_each_folder):
    if filename.endswith('.json'): 
        file_path = os.path.join(gt_each_folder, filename)
        with open(file_path, 'r') as f:
            annotations = json.load(f)

            merged_annotations["images"].extend(annotations["images"])

            if "annotations" in annotations:
                merged_annotations["annotations"].extend(annotations["annotations"])

            if "categories" in annotations:
                merged_annotations["categories"].extend(annotations["categories"])

unique_categories = {cat['id']: cat for cat in merged_annotations['categories']}.values()
merged_annotations['categories'] = list(unique_categories)

# 将合并后的数据写入到JSON文件
with open(output_json_file, 'w') as f:
    json.dump(merged_annotations, f)

print(f"merged and saved to {output_json_file}")
