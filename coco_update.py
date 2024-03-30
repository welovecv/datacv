import json
import shutil
import os

# COCO JSON文件的路径
coco_json_file = '/data/vdu2024/source_pool/coco_annotation.json'

# 读取COCO JSON文件
with open(coco_json_file, 'r') as f:
    coco_data = json.load(f)

# 提取所有图片名的列表
image_names = [image['file_name'] for image in coco_data['images']]


# -------------------------------------------------------------------------
# # 打印图片名列表
# print(len(image_names))
# #print(image_names[0])

# # 图片所在的文件夹路径
# image_directory = 'source_pool/coco_train/'

# # 要移动剩余图片的目标文件夹路径
# destination_directory = 'source_pool/coco_no_label/'

# for filename in os.listdir(image_directory):
#     # 如果文件名在COCO JSON文件中的图片名列表中，则保留在原位
#     if filename in image_names:
#         continue
#     # 否则，移动文件到目标文件夹
#     shutil.move(os.path.join(image_directory, filename), os.path.join(destination_directory, filename))

# print("操作完成。保留的图片在原位，其余图片已移动到目标文件夹。")

# --------------------------------------------------------------------------

# COCO JSON文件的路径
coco_json_file = '/data/vdu2024/source_pool/instances_train2017.json'
# coco_json_file = 'source_pool/instances_val2017.json'

# 包含图片名称的列表
# image_names = ['image1.jpg', 'image2.jpg', 'image3.jpg']  # 替换为你的图片名称列表

# 读取COCO JSON文件
with open(coco_json_file, 'r') as f:
    coco_data = json.load(f)

# 过滤出符合条件的图片ID
selected_image_ids = [image['id'] for image in coco_data['images'] if image['file_name'] in image_names]

# 过滤出符合条件的类别ID（car, bus, truck）
selected_category_ids = [category['id'] for category in coco_data['categories'] if category['name'] in ['car', 'bus', 'truck']]

# 过滤出符合条件的标注
selected_annotations = [annotation for annotation in coco_data['annotations'] if annotation['image_id'] in selected_image_ids and annotation['category_id'] in selected_category_ids]

# 创建一个新的COCO字典，只包含选中的图片和标注
selected_coco = {
    "images": [image for image in coco_data['images'] if image['id'] in selected_image_ids],
    "annotations": selected_annotations,
    "categories": [category for category in coco_data['categories'] if category['id'] in selected_category_ids]
}

# 将新的COCO字典写入JSON文件
output_json_file = '/data/vdu2024/source_pool/coco_add_bus_truck.json'
# output_json_file = 'selected_from_coco_val2017.json'
with open(output_json_file, 'w') as f:
    json.dump(selected_coco, f)

# COCO JSON文件的路径
coco_json_file = '/data/vdu2024/source_pool/coco_add_bus_truck.json'

# 输出修改后的COCO JSON文件的路径
output_json_file = '/data/vdu2024/source_pool/coco_updated.json'

# 读取COCO JSON文件
with open(coco_json_file, 'r') as f:
    coco_data = json.load(f)

# 修改categories字段，将所有类别都改为car（id为1）
coco_data['categories'] = [{"id": 1, "name": "car", "supercategory": "vehicle"}]

# 遍历所有annotations，将category_id都改为1
for annotation in coco_data['annotations']:
    annotation['category_id'] = 1

# 将修改后的COCO字典写入JSON文件
with open(output_json_file, 'w') as f:
    json.dump(coco_data, f)

print(f"change all categories into car，save to {output_json_file}")