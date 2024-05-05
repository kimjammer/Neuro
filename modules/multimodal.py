import mss, cv2, base64
import numpy as np
from modules.module import Module
from modules.injection import Injection
from constants import *

class MultiModal(Module):

    def __init__(self, signals, enabled=True):
        super().__init__(signals, enabled)

        self.API = self.API(self)
        self.MSS = mss.mss()

    def get_prompt_injection(self):
        return self.prompt_injection

    async def run(self):
        pass

    class API:
        def __init__(self, outer):
            self.outer = outer

        # Determines when a prompt should go to the multimodal model
        def multimodal_now(self):
            return True

        def screen_shot(self):
            # Take a screenshot of the main screen
            frame_bytes = self.outer.MSS.grab(self.outer.MSS.monitors[PRIMARY_MONITOR])

            frame_array = np.array(frame_bytes)
            # resize
            frame_resized = cv2.resize(frame_array, (1920, 1080), interpolation=cv2.INTER_CUBIC)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            result, frame_encoded = cv2.imencode('.jpg', frame_resized, encode_param)
            # base64
            frame_base64 = base64.b64encode(frame_encoded)

            return frame_base64