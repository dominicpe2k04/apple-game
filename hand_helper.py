import mediapipe as mp
import math


class HandTracker:

    def __init__(self, confidence=0.7):
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=confidence,
            min_tracking_confidence=0.5,
        )

        self.landmarks = None

    def process(self, rgb_frame):

        results = self._hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            self.landmarks = None
            return {"seen": False}

        self.landmarks = results.multi_hand_landmarks[0]

        lm = self.landmarks.landmark

        tip = lm[8]
        wrist = lm[0]

        d = math.hypot(
            tip.x - wrist.x,
            tip.y - wrist.y
        )

        return {
            "seen": True,
            "x": tip.x,
            "y": tip.y,
            "fist": d < 0.15
        }

    def close(self):
        self._hands.close()