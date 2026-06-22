import threading
import time

import cv2

from hand_helper import HandTracker


class HandTrackingController:
	def __init__(self, camera_stream):
		self.camera_stream = camera_stream
		self._x = 0.5
		self._seen = False
		self._running = False
		self._lock = threading.Lock()
		self._thread = threading.Thread(target=self._run, daemon=True)

	def start(self):
		self._running = True
		self._thread.start()

	def _run(self):
		tracker = HandTracker()

		try:
			while self._running:
				frame = self.camera_stream.read()

				if frame is None:
					time.sleep(0.005)
					continue

				rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				result = tracker.process(rgb)

				with self._lock:
					if result["seen"]:
						new_x = 1.0 - result["x"]
						self._x = 0.6 * self._x + 0.4 * new_x
						self._seen = True
					else:
						self._seen = False
		finally:
			tracker.close()

	def stop(self):
		self._running = False
		if self._thread.is_alive():
			self._thread.join()

	@property
	def x(self):
		with self._lock:
			return self._x

	@property
	def seen(self):
		with self._lock:
			return self._seen
