_base_ = [
    '../_base_/models/retinanet_r50_fpn_car.py',
    # '../_base_/datasets/custom_tss.py',
    '../_base_/default_runtime.py',
    '../_base_/schedules/schedule_1x.py',
    '../_base_/datasets/dataset_002_coco_8000.py'
]
# optimizer
optimizer = dict(type='SGD', lr=0.001, momentum=0.9, weight_decay=0.0001)

