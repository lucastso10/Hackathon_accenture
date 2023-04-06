import torch
import numpy as np
import cv2
from torchvision.io import decode_image, ImageReadMode
from torchvision.transforms import Resize
from typing import List
from detectionfactory.inference import (Point,
                                        Polygon,
                                        Prediction,
                                        InferenceFrameData,
                                        InferencePredictionData)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class YOLOv5():
    def __init__(self,
                 model_size="yolov5m",
                 img_size=640,
                 conf=0.25,
                 classes=None) -> None:
        """
        Wrapper to the YOLOv5 Model.

        Parameters:
            model_size: model size "yolov5s" or path "path/to/model.pt"
            img_size: inference size h,w
            conf: confidence threshold
            classes (list or None): interest classes
        """
        self.model = torch.hub.load("ultralytics/yolov5",
                                    model=model_size,
                                    pretrained=True)
        if classes:
            self.model.classes = [int(c) for c in classes.keys()]

        self.model.conf = conf
        self.model.amp = True
        self.model.to(DEVICE)

        self.img_size = int(img_size)

    def _yolo_output_to_predictions(self, results) -> List[Prediction]:
        """ Converts YOLOv5 Detections to AIV Prediction """
        frames_predictions = []

        for preds in results.xyxy:
            frame_predictions = []
            for pred in preds:
                bbox_coords = pred[:4]
                confidence_score = pred[4].item()
                class_id = int(pred[5].item())
                class_name = self.model.names[class_id]

                x1, y1, x2, y2 = bbox_coords
                x1 = x1.item()
                y1 = y1.item()
                x2 = x2.item()
                y2 = y2.item()

                bbox = Polygon(type="quadrilateral",
                               coordinates=[Point(x=x1, y=y1),
                                            Point(x=x2, y=y1),
                                            Point(x=x2, y=y2),
                                            Point(x=x1, y=y2)])
                pred = Prediction(classId=class_name,
                                  confidence=confidence_score,
                                  boundingBox=bbox,
                                  related=[])

                frame_predictions.append(pred)

            frames_predictions.append(frame_predictions)

        return frames_predictions

    def _batch_to_cv2(self,
                      batch: List[InferenceFrameData]) -> List[np.ndarray]:
        imgs = []

        for batch_dict in batch:
            img_raw = batch_dict["frame"]
            img_arr = np.frombuffer(img_raw, dtype=np.uint8)
            img = cv2.imdecode(img_arr, flags=cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.astype(float)
            imgs.append(img)

        return imgs

    def __call__(self,
                 batch: List[InferenceFrameData]) -> List[InferencePredictionData]:
        imgs = self._batch_to_cv2(batch)

        results = self.model(imgs, size=self.img_size)
        frames_predictions = self._yolo_output_to_predictions(results)

        predictions_data = []

        for batch_dict, frame_predictions in zip(batch, frames_predictions):
            frame_data = batch_dict["newFrameData"]

            prediction_data = InferencePredictionData(
                    predictions=frame_predictions,
                    newFrameData=frame_data,
                    misc={}
                    )
            predictions_data.append(prediction_data)

        return predictions_data
