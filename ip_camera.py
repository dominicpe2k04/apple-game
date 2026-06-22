import os
import threading
import time

import cv2


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "camera_config.txt")


class CameraStream(threading.Thread):
    def __init__(self, src, width=None, height=None):
        super().__init__(daemon=True)
        self.src = src
        self.width = width
        self.height = height
        self.cap = cv2.VideoCapture(self.src)
        if self.width is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.stopped = False
        self.frame = None
        self.lock = threading.Lock()

    def run(self):
        while not self.stopped:
            if not self.cap.isOpened():
                time.sleep(0.5)
                continue

            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            with self.lock:
                self.frame = frame

    def read(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def stop(self):
        self.stopped = True
        if self.cap.isOpened():
            self.cap.release()


def load_config_value(config_path=CONFIG_FILE):
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            return config_file.read().strip()
    except OSError:
        return ""


def save_config_value(config_path, value):
    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.write(value.strip())


def resolve_stream_url(stream_value):
    if stream_value.startswith(("http://", "https://")):
        return stream_value
    if "/" in stream_value:
        host_port, path = stream_value.split("/", 1)
        return f"http://{host_port}/{path.lstrip('/')}"
    return f"http://{stream_value}/video"


def prompt_for_stream_value(config_path=CONFIG_FILE, input_func=input, print_func=print):
    while True:
        stream_value = input_func("Enter camera IP address or stream URL: ").strip()
        if stream_value:
            save_config_value(config_path, stream_value)
            return stream_value
        print_func("Input cannot be empty.")

def load_or_prompt_stream_value(config_path=CONFIG_FILE, input_func=input, print_func=print):
    stream_value = load_config_value(config_path)
    if stream_value:
        return stream_value

    print_func(f"No readable IP configuration found at {config_path}.")
    return prompt_for_stream_value(config_path=config_path, input_func=input_func, print_func=print_func)


def can_open_stream(stream_url, timeout_seconds=5):
    cap = cv2.VideoCapture(stream_url)
    start_time = time.time()

    try:
        while time.time() - start_time < timeout_seconds:
            if not cap.isOpened():
                time.sleep(0.2)
                continue

            ret, frame = cap.read()
            if ret and frame is not None:
                return True

            time.sleep(0.1)
        return False
    finally:
        cap.release()


def get_valid_stream_url(config_path=CONFIG_FILE, input_func=input, print_func=print):
    stream_value = load_or_prompt_stream_value(
        config_path=config_path,
        input_func=input_func,
        print_func=print_func,
    )
    stream_url = resolve_stream_url(stream_value)

    while not can_open_stream(stream_url):
        print_func(f"Connection failed or stream unreachable: {stream_url}")
        stream_value = prompt_for_stream_value(
            config_path=config_path,
            input_func=input_func,
            print_func=print_func,
        )
        stream_url = resolve_stream_url(stream_value)

    return stream_url


def run_viewer(config_path=CONFIG_FILE, width=640, height=480, input_func=input, print_func=print):
    stream_url = get_valid_stream_url(
        config_path=config_path,
        input_func=input_func,
        print_func=print_func,
    )

    print_func(f"Starting camera stream from: {stream_url}")
    stream = CameraStream(stream_url, width=width, height=height)
    stream.start()

    try:
        while True:
            frame = stream.read()
            if frame is None:
                time.sleep(0.05)
                continue

            cv2.imshow("Pi5 Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break
    finally:
        stream.stop()
        cv2.destroyAllWindows()


def main():
    run_viewer()


if __name__ == "__main__":
    main()


#from ip_camera import CameraStream, get_valid_stream_url
#stream_url = get_valid_stream_url()
#stream = CameraStream(stream_url, width=640, height=480)
#stream.start()