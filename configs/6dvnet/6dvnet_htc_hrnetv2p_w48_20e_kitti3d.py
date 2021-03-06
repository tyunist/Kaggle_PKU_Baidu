# model settings
model = dict(
    type='SIXDVNET',
    num_stages=3,
    interleaved=True,
    mask_info_flow=True,
    car_cls_info_flow=False,
    backbone=dict(
        type='HRNet',
        extra=dict(
            stage1=dict(
                num_modules=1,
                num_branches=1,
                block='BOTTLENECK',
                num_blocks=(4,),
                num_channels=(64,)),
            stage2=dict(
                num_modules=1,
                num_branches=2,
                block='BASIC',
                num_blocks=(4, 4),
                num_channels=(48, 96)),
            stage3=dict(
                num_modules=4,
                num_branches=3,
                block='BASIC',
                num_blocks=(4, 4, 4),
                num_channels=(48, 96, 192)),
            stage4=dict(
                num_modules=3,
                num_branches=4,
                block='BASIC',
                num_blocks=(4, 4, 4, 4),
                num_channels=(48, 96, 192, 384)))),
    neck=dict(
        type='HRFPN',
        in_channels=[48, 96, 192, 384],
        out_channels=256),
    rpn_head=dict(
        type='RPNHead',
        in_channels=256,
        feat_channels=256,
        anchor_scales=[8],
        anchor_ratios=[0.5, 1.0, 2.0],
        anchor_strides=[4, 8, 16, 32, 64],
        target_means=[.0, .0, .0, .0],
        target_stds=[1.0, 1.0, 1.0, 1.0],
        loss_cls=dict(
            type='CrossEntropyLoss', use_sigmoid=True, loss_weight=1.0),
        loss_bbox=dict(type='SmoothL1Loss', beta=1.0 / 9.0, loss_weight=1.0)),
    bbox_roi_extractor=dict(
        type='SingleRoIExtractor',
        roi_layer=dict(type='RoIAlign', out_size=7, sample_num=2),
        out_channels=256,
        featmap_strides=[4, 8, 16, 32]),
    bbox_head=[
        dict(
            type='SharedFCBBoxHead',
            num_fcs=2,
            in_channels=256,
            fc_out_channels=1024,
            roi_feat_size=7,
            num_classes=81,
            target_means=[0., 0., 0., 0.],
            target_stds=[0.1, 0.1, 0.2, 0.2],
            reg_class_agnostic=True,
            loss_cls=dict(
                type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
            loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),
        dict(
            type='SharedFCBBoxHead',
            num_fcs=2,
            in_channels=256,
            fc_out_channels=1024,
            roi_feat_size=7,
            num_classes=81,
            target_means=[0., 0., 0., 0.],
            target_stds=[0.05, 0.05, 0.1, 0.1],
            reg_class_agnostic=True,
            loss_cls=dict(
                type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
            loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),
        dict(
            type='SharedFCBBoxHead',
            num_fcs=2,
            in_channels=256,
            fc_out_channels=1024,
            roi_feat_size=7,
            num_classes=81,
            target_means=[0., 0., 0., 0.],
            target_stds=[0.033, 0.033, 0.067, 0.067],
            reg_class_agnostic=True,
            loss_cls=dict(
                type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
            loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0))
    ],
    mask_roi_extractor=dict(
        type='SingleRoIExtractor',
        roi_layer=dict(type='RoIAlign', out_size=14, sample_num=2),
        out_channels=256,
        featmap_strides=[4, 8, 16, 32]),
    mask_head=dict(
        type='HTCMaskHead',
        num_convs=4,
        in_channels=256,
        conv_out_channels=256,
        num_classes=81,
        loss_mask=dict(
            type='CrossEntropyLoss', use_mask=True, loss_weight=1.0)),

    with_semantic_loss=False,
    with_car_cls_rot=True,
    with_translation=True,
    # This is DI WU's customised model
    semantic_fusion=('bbox', 'mask', 'car_cls_rot'),
    car_cls_rot_roi_extractor=dict(
        type='SingleRoIExtractor',
        roi_layer=dict(type='RoIAlign', out_size=14, sample_num=2),
        out_channels=256,
        featmap_strides=[4, 8, 16, 32]),

    car_cls_rot_head=dict(
        type='SharedCarClsRotHead',
        in_channels=256,
        fc_out_channels=1024,
        roi_feat_size=14,
        num_classes=34,  # There are total 34 car classes
        reg_class_agnostic=True,
        loss_car_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
        loss_quaternion=dict(type='L1', beta=1.0, loss_weight=1.0)),

    translation_head=dict(
        type='SharedTranslationHead',
        in_channels_bboxes=4,
        in_channels_carclsrot=1024,
        fc_out_channels=100,
        num_translation_reg=3,
        bbox_relative=True,  # if bbox_relative=False, then it requires training/test input the same
        translation_bboxes_regression=False,  # If set to True, we will have a SSD like offset regression
        bboxes_regression=dict(type='maxIoU', iou_thresh=0.1),
        loss_translation=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),

    bayesian_weight_learning=True,  # If set to true, the loss weight coefficient will be updated.

)

# model training and testing settings
train_cfg = dict(
    rpn=dict(
        assigner=dict(
            type='MaxIoUAssigner',
            pos_iou_thr=0.7,
            neg_iou_thr=0.3,
            min_pos_iou=0.3,
            ignore_iof_thr=-1),
        sampler=dict(
            type='RandomSampler',
            num=256,
            pos_fraction=0.5,
            neg_pos_ub=-1,
            add_gt_as_proposals=False),
        allowed_border=0,
        pos_weight=-1,
        debug=False),
    rpn_proposal=dict(
        nms_across_levels=False,
        nms_pre=2000,
        nms_post=2000,
        max_num=2000,
        nms_thr=0.7,
        min_bbox_size=0),
    rcnn=[
        dict(
            assigner=dict(
                type='MaxIoUAssigner',
                pos_iou_thr=0.5,
                neg_iou_thr=0.5,
                min_pos_iou=0.5,
                ignore_iof_thr=-1),
            sampler=dict(
                type='RandomSampler',
                num=512,
                pos_fraction=0.25,
                neg_pos_ub=-1,
                add_gt_as_proposals=True),
            mask_size=28,
            pos_weight=-1,
            debug=False),
        dict(
            assigner=dict(
                type='MaxIoUAssigner',
                pos_iou_thr=0.6,
                neg_iou_thr=0.6,
                min_pos_iou=0.6,
                ignore_iof_thr=-1),
            sampler=dict(
                type='RandomSampler',
                num=512,
                pos_fraction=0.25,
                neg_pos_ub=-1,
                add_gt_as_proposals=True),
            mask_size=28,
            pos_weight=-1,
            debug=False),
        dict(
            assigner=dict(
                type='MaxIoUAssigner',
                pos_iou_thr=0.7,
                neg_iou_thr=0.7,
                min_pos_iou=0.7,
                ignore_iof_thr=-1),
            sampler=dict(
                type='RandomSampler',
                num=512,
                pos_fraction=0.25,
                neg_pos_ub=-1,
                add_gt_as_proposals=True),
            mask_size=28,
            pos_weight=-1,
            debug=False)
    ],
    stage_loss_weights=[1, 0.5, 0.25],

    car_cls_weight=1.0,
    rot_weight=10.,
    translation_weight=10.,
)
test_cfg = dict(
    rpn=dict(
        nms_across_levels=False,
        nms_pre=1000,
        nms_post=1000,
        max_num=1000,
        nms_thr=0.7,
        min_bbox_size=0),
    rcnn=dict(
        score_thr=0.001,
        nms=dict(type='nms', iou_thr=0.5),
        max_per_img=100,
        mask_thr_binary=0.5),
    keep_all_stages=False,
)
# dataset settings
dataset_type = 'KittiObjectDataset'

img_norm_cfg = dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)

train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True, with_mask=True,
         with_carcls_rot=True, with_translation=True, with_camera_rot=True),
    dict(type='Resize', img_scale=(2000, 600), keep_ratio=True),
    dict(type='RandomFlip', flip_ratio=0.),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size_divisor=32),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect',
         keys=['img', 'gt_bboxes', 'gt_labels', 'gt_masks',
               'carlabels', 'quaternion_semispheres', 'translations',
               'scale_factor']),
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(2000, 600),
        flip=False,  # test pipelines doest not need this
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip', flip_ratio=0.),   # We always want to have this flip_ratio=1.0 for test
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]

data_root = '/data/KITTI/'
data = dict(
    imgs_per_gpu=1,
    workers_per_gpu=2,
    train=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root+'training/label_2',
        img_prefix=data_root + 'training/image_2/',
        pipeline=train_pipeline,
        rotation_augmenation=True),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root+'training/label_2',
        img_prefix=data_root + 'training/image_2/',
        pipeline=test_pipeline),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file="",
        img_prefix=data_root + 'testing/image_2/',
        pipeline=test_pipeline))


evaluation = dict(
    conf_thresh=0.1,
    interval=1,
)
# optimizer
optimizer = dict(type='Adam', lr=0.003)  # We increase the learning rate to 3e-4 (It is supposed to be the best practice)

optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=1.0 / 3,
    step=[80, 180])
checkpoint_config = dict(interval=1)
# yapf:disable
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        dict(type='TensorboardLoggerHook')
    ])
# yapf:enable
# runtime settings
total_epochs = 200
#dist_params = dict(backend='nccl')
dist_params = dict(backend='nccl', init_method="tcp://127.0.0.1:8001")

log_level = 'INFO'
work_dir = '/data/KITTI/wudi_data/'
load_from = None
resume_from = None
workflow = [('train', 1)]

