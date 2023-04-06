import time
from uuid import uuid4
from typing import Union, List
from eventfactory import Detection
from eventfactory import EventEndedSignal, EventStartedSignal
from eventfactory.pipeline.steps import BusinessLogic


class Event():
    """
    A class representing an event detected in a video frame.

    Attributes:
    -----------
    detection : Detection
        The detection asociated with the event
    num_detected_frames : int
        The number of frames in which the event has been detected
    creation_time : float
        The time at which the vent was first created
    ttl : int
        The time-to-live for the event in seconds

    Methods:
    --------
    _reset_ttl() -> None:
        Resets the time-to-live value for the event
    no_detection() -> None:
        Decreases current time-to-live value when the object is not detected in
        the current frame
    new_detection(detection: Detection) -> None:
        Updates the detection for the event and resets its time-to-live value
    is_expired() -> bool:
        Returns True is the event has expired, i.e., if its time-to-live has
        elapsed
    """

    def __init__(self, detection: Detection, ttl: int) -> None:
        self.detection = detection
        self.num_detected_frames = 1
        self.creation_time = time.time()
        self.ttl = ttl
        self.current_ttl = self.ttl

    def _reset_ttl(self) -> None:
        self.current_ttl = self.ttl

    def no_detection(self) -> None:
        self.current_ttl -= 1

    def new_detection(self, detection: Detection) -> None:
        """
        Updates the detection for the event and resets its time-to-live value.

        Parameters:
        -----------
        detection : Detection
            The new detection associated with the event
        """
        self.detection = detection
        self.num_detected_frames += 1
        self._reset_ttl()

    def is_expired(self) -> bool:
        return self.current_ttl <= 0


class RoIBusinessLogic(BusinessLogic):
    """
    Class representing the business logic for detecting events in a video frame

    Methods:
    --------
    _add_count(self) -> dict:
        Returns a dict simulating an object for predictions that contains
        information the count of the chairs, so that we can draw it on screen.
        
    def _create_point(self, point : dict, name : str) -> dict:
        Returns a dict simulating an object for predictions, the name and the
        point of the object can be inputed into the fucntion.
        
    _insert_info(self, detection : Detection) -> Detection:
        Inserts the info we want to draw on the screen on the Detection class.
    
    _calculate_medium_point(self, chair) -> dict:
        Returns the medium point of an object detected by the AI.
        
    _create_chair_map(self, detection : Detection) -> List[List[dict]]:
        Returns a matrix with the medium points of the chairs mapping all 
        the chairs in their respective lines.
        
    _check_chair_map(self, detection) -> bool:
        Check if any of the chairs in the _chair_map matrix need to change
        state and returns if any chair has changed estate.
        
    _check_chair_occupied(self, line : int, column : int, detection : Detection) -> bool:
        Checks if an especific chair needs to change state or not, and returns a bool
        telling if the chair changed states.
        
    _create_event(self, detection: Detection) -> List[Union[EventStartedSignal, EventEndedSignal]]:
        Returns a list with the starter and the ender of the same event
        so that the event starts and ends in the same frame.
    """

    def __init__(self):
        self._chair_count = 0
        self._chair_map = []
    
    def _add_count(self) -> dict:
        """
        adds the count of chairs to the left top corner of the stream by
        acting as an object to the image drawer.

        Returns:
            dict : A dict that acts like an object to the drawer with the
            same attributes as one.
            
        """
        occupied_chairs = 0
        for line in self._chair_map:
            for chair in line:
                if chair['occupied']:
                    occupied_chairs += 1
                    
        return {'classId': f'Total de caideras: {self._chair_count} | Cadeiras ocupadas: {occupied_chairs} | Cadeiras livres: {self._chair_count - occupied_chairs}', 
                 'trackId': '', 
                 'confidence': 0.9, 
                 'boundingBox': {'type': 'quadrilateral', 
                                 'coordinates': [{'x': 0.0, 'y': 0.0}, 
                                                 {'x': 1.0, 'y': 0.0}, 
                                                 {'x': 1.0, 'y': 1.0}, 
                                                 {'x': 0.0, 'y': 1.0}]},
                 'related': []}
        
    def _create_point(self, point : dict, name : str) -> dict:
        """
        creates a point in a Detection class by simulating an object, with the coordinates
        and name passed to it. This is usefull to draw things on the screen.
        
        Parameters:
        -----------
            point (dict): a dict with the coordinates of the point.
            name (string): a string with the name of the point.

        Returns:
            dict: containing the coordinates of the point.
        """
        return {'classId': f'{name}', 
                 'trackId': '', 
                 'confidence': 0.9, 
                 'boundingBox': {'type': 'quadrilateral', 
                                 'coordinates': [{'x': (point['x']), 'y': (point['y'])}, 
                                                 {'x': (point['x']+2), 'y': (point['y'])}, 
                                                 {'x': (point['x']+2), 'y': (point['y']+2)}, 
                                                 {'x': (point['x']), 'y': (point['y']+2)}]},
                 'related': []}
        
    def _insert_info(self, detection : Detection) -> Detection:
        """
        Inserts the info we want to draw on the image to the dection class,
        so that they are drawn the image.
        
        Parameters:
        -----------
            detection (Detection): A Detection object containing information
            about the objects detected in a video frame.

        Returns:
            Detection : with all the extra information we wanted to add.
        """
        
        detection['predictions'].append(self._add_count())
        
        for i in range(0,len(self._chair_map)):
            for point in self._chair_map[i]:
                if point['occupied']:
                    detection['predictions'].append(self._create_point(point,f"M{i}(ocupado)"))
                else:
                    detection['predictions'].append(self._create_point(point,f"M{i}(livre)"))
                    
        return detection
    
    def _calculate_medium_point(self, chair) -> dict:
        """
        Calculates the medium point of the of an object.
        
        Parameters:
        -----------
            chair: an object detected by the ai, in this case only the object
            chair can pass, that is why it has that name.

        Returns:
            dict: containing the coordinates of the point.
        """
        return {'x' : (((chair['boundingBox']['coordinates'][1]['x'] - chair['boundingBox']['coordinates'][0]['x'])/2) +  chair['boundingBox']['coordinates'][0]['x']),
                'y' : (((chair['boundingBox']['coordinates'][2]['y'] - chair['boundingBox']['coordinates'][1]['y'])/2) +  chair['boundingBox']['coordinates'][1]['y'])}
        
                
    def _create_chair_map(self, detection : Detection) -> List[List[dict]]:
        """
        Creates a matrix of all the chairs in the detection.
        This method is only supposed to be run once on the first frame.
        It filter lines of chairs that has only 4 assuming that
        they are probably an erorr commited by the ai.
        The matrix it returns will be used as the reference map
        for all the other frames.
        
        Parameters:
        -----------
            detection (Detection): A Detection object containing information
            about the objects detected in a video frame.

        Returns:
            List[Union[List[Union[Detection]]]]: with the matrix.
        """
        matrix_chairs = []
        main_chairs = []
        for chair in detection['predictions']:
            chair = self._calculate_medium_point(chair)
            chair.update({'occupied' : False})

            added = False
            
            if not main_chairs:
                main_chairs.append(chair)
                matrix_chairs.append([chair])
                continue

            for i in range(0,len(main_chairs)):
                if chair['y'] < (main_chairs[i]['y'] + 55) and chair['y'] > (main_chairs[i]['y'] - 55):
                    matrix_chairs[i].append(chair)
                    added = True
                
            if not added:
                matrix_chairs.append([chair])
                main_chairs.append(chair)

        remove = []
        for i in range(0,len(matrix_chairs)):
            if len(matrix_chairs[i]) <= 4:
                remove.insert(0, i)
        
        for i in remove:
            matrix_chairs.pop(i)
            
        return matrix_chairs

    def _check_chair_map(self, detection) -> bool:
        """
        Check the whole matrix map to see if a chair changed states.

        Parameters:
        -----------
            detection (Detection): A Detection object containing information
            about the objects detected in a video frame.

        Returns:
            bool : it returns a bool telling if the state of any of the chairs
            changed.
        """
        changed = False
        for i in range(0, len(self._chair_map)):
            for j in range (0, len(self._chair_map[i])):
                if self._check_chair_occupied(i, j, detection):
                    changed = True
            
        return changed
    
    def _check_chair_occupied(self, line : int, column : int, detection : Detection) -> bool:
        """
        Check if the specific is occupied or not by checking every prediction made
        by the ai and seeing if the medium point of the chair is inside any of the
        squares.

        Parameters:
        -----------
            detection (Detection): A Detection object containing information
            about the objects detected in a video frame.
            line (int): the line the chair is in the matrix.
            chair (int): the column the chair is in the matrix.

        Returns:
            bool : it returns a bool telling if the state of the chair was changed
            or not.
        """
        changed = False
        for pred in detection['predictions']:
            
            if self._chair_map[line][column]['x'] >= pred['boundingBox']['coordinates'][0]['x'] and self._chair_map[line][column]['x'] <= pred['boundingBox']['coordinates'][1]['x']:
                
                if self._chair_map[line][column]['y'] >= pred['boundingBox']['coordinates'][1]['y'] and self._chair_map[line][column]['y'] <= pred['boundingBox']['coordinates'][2]['y']:
                    
                    if not self._chair_map[line][column]['occupied']:
                        return False
                    else:
                        self._chair_map[line][column]['occupied'] = False
                        return True
    
    
        if self._chair_map[line][column]['occupied']:
            return False
        else:
            self._chair_map[line][column]['occupied'] = True
            return True
            
    
    def _create_event(self, detection: Detection) -> List[Union[EventStartedSignal, EventEndedSignal]]:
        """
        Creates a list with the event starter and the event ender in the same
        list so that the event starts and ends in the same frame.

        Parameters:
        -----------
            detection (Detection): A Detection object containing information
            about the objects detected in a video frame.

        Returns:
            List[EventEndedSignal, EventStartedSignal]: A list with the event
            starter and the event ender.
        """
        
        event_id = str(uuid4())
        return [EventStartedSignal(event_id, detection), EventEndedSignal(event_id, detection)]
        

    def process(self, detection: Detection) -> List[Union[EventEndedSignal, EventStartedSignal]]:
        """
        Process a detection and generate a list of event signals based on its
        properties and behavior.

        Parameters:
        -----------
            detection (Detection): A Detection object containing information
            about the objects detected in a video frame.

        Returns:
            List[Union[EventEndedSignal, EventStartedSignal]]: A list of event
            signals generated based on the properties and behavior of the
            objects detected in the video frame. Each signal is an instance of
            either the EventStartedSignal or EventEndedSignal class.
        """
        events = []
        if not self._chair_map:
            self._chair_map = self._create_chair_map(detection)
            
            for lines in self._chair_map:
                self._chair_count += len(lines)
            
            detection = self._insert_info(detection)
            
            events = self._create_event(detection)
        else:
            if self._check_chair_map(detection):
                detection = self._insert_info(detection)
                events = self._create_event(detection)
        
        return events if events else None
