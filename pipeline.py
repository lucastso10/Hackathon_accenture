import json
import base64
from typing import Union

from eventfactory.pipeline import (Detection,
                                   EventPipeline,
                                   EventEndedSignal,
                                   EventStartedSignal)
from .roi import RegionOfInterest
from .business_logic import RoIBusinessLogic
from .class_filter import ClassFilter

class Pipeline(EventPipeline):

    def __init__(self, cfg):
        area_of_interest_b64 = cfg.use_case.area_of_interest
        area_of_interest = json.loads(base64.b64decode(area_of_interest_b64))
        region_coords = area_of_interest["polygon"]["coordinates"]

        self._region_of_interest = RegionOfInterest(region_coords)

        params_b64 = cfg.use_case.params
        params = json.loads(base64.b64decode(params_b64).decode("utf8"))
        self.filter_object = ClassFilter({"56":"chair"})

        self._business_logic = RoIBusinessLogic()

    def process_detection(self, detection: Detection) -> Union[
                                                        None,
                                                        EventEndedSignal,
                                                        EventStartedSignal]:

        detection = self._region_of_interest.process(detection)
        # print()
        # print(detection)
        detection = self.filter_object.process(detection)
        # print("============filtro=======",)
        # print( detection)
        # print("============================")
        event = self._business_logic.process(detection)
        # print("--------------------------------")
        # print(f"\nEVENT====={event}\n")
        # print("--------------------------------")
        

        return event
