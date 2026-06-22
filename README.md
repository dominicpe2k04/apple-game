# Apple Catcher

Apple Catcher is a Raspberry Pi arcade game that uses an IP camera and hand tracking to move a basket left and right. Catch apples to score points, catch golden apples to regain lives, and avoid bombs. The game also drives four RGB LEDs to show lives and score.

## Demo Video
Click the below image to play the video
[![Watch the video](https://img.youtube.com/vi/aswg6B4YwsU/maxresdefault.jpg)](https://www.youtube.com/watch?v=aswg6B4YwsU)

led Core bar
[![Gameplay Screenshot](images/led_score_bar.png)](images/led_score_bar.png)
## Features

- Hand-controlled basket movement using MediaPipe hand tracking
- IP camera input through OpenCV
- Pygame-based game display
- RGB LED status indicators for lives and score
- Game over and restart flow with `R`

## Requirements

- Python 3.11
- Raspberry Pi or compatible Linux device with GPIO support
- IP camera or webcam stream reachable from the device
- A connected RGB LED setup on the GPIO pins defined in `main.py`

Python dependencies are listed in `requirements.txt`.

## LED to GPIO Wiring

The game uses four `RGBLED` objects from `gpiozero`, and the LED pins are defined in `main.py`.

- LED 1: red `GPIO17`, green `GPIO27`, blue `GPIO22`
- LED 2: red `GPIO5`, green `GPIO6`, blue `GPIO13`
- LED 3: red `GPIO19`, green `GPIO26`, blue `GPIO20`
- LED 4: red `GPIO16`, green `GPIO12`, blue `GPIO21`

Wire each RGB LED to those GPIO pins so the game can show lives and score on the hardware.

## Project Files

- `main.py` - game entry point
- `hand_tracking.py` - background hand tracking controller
- `hand_helper.py` - MediaPipe hand landmark processing
- `ip_camera.py` - camera stream configuration and viewer helper
- `camera_config.txt` - saved camera IP address or stream URL
- `requirements.txt` - Python package dependencies
- `system pacakage requirements.txt` - system package notes for the Raspberry Pi setup

## Setup

1. Create and activate a virtual environment.
2. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install any needed system packages for GPIO support. The repo includes a `system pacakage requirements.txt` note that mentions `python3-lgpio`.
4. Make sure the game image assets are present in the project folder:
   - `apple.png`
   - `golden_apple.png`
   - `bomb.png`
   - `basket.png`

## Camera Configuration

The game reads the camera source from `camera_config.txt`.

- You can store a raw IP address like `192.168.1.38:8080`
- You can also store a full stream URL like `http://192.168.1.38:8080/video`
- If the file is empty or missing, the app will prompt you for the camera address and save it

## Run

Start the game from the project folder:

```bash
python main.py
```

## Controls

- Move your hand in front of the camera to move the basket
- Press `Space` to start
- Press `R` to restart after game over or a win
- Close the window to quit

## Gameplay

- Catch apples to gain points
- Catch golden apples to gain an extra life, up to 3
- Avoid bombs
- Missing apples reduces lives
- Reaching a score of 23 wins the game

## Notes

- The LED pin assignments are defined in `main.py`
- The game expects the camera stream to be reachable before it starts
- If you are using a Raspberry Pi, make sure GPIO permissions and camera access are configured correctly
