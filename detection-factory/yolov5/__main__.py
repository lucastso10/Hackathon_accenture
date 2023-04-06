import json
import logging
from .yolo import YOLOv5

from detectionfactory.configuration import cfg
from detectionfactory.detection_factory import DetectionFactory

logging.basicConfig()
logging.info("Bootstraping YOLO inference worker")

ai_cfg = json.loads(json.loads(cfg.ai))

model = YOLOv5(model_size=ai_cfg["model_size"],
               img_size=ai_cfg["img_size"],
               classes=ai_cfg["classes"],
               conf=ai_cfg["conf_thres"])

df = DetectionFactory(cfg.library, model)

logging.info("Bootstraping done.")

df.start()
