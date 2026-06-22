import pygame
import random
import sys
import time
from gpiozero import RGBLED

from hand_tracking import HandTrackingController
from ip_camera import CameraStream, get_valid_stream_url

# =====================================================
# RGB LED SETUP
# =====================================================

led1 = RGBLED(red=17, green=27, blue=22)
led2 = RGBLED(red=5, green=6, blue=13)
led3 = RGBLED(red=19, green=26, blue=20)
led4 = RGBLED(red=16, green=12, blue=21)

leds = [led1, led2, led3, led4]

# Your LEDs are wired as (B, G, R)
RED = (0, 0, 1)
GREEN = (0, 1, 0)
BLUE = (1, 0, 0)
YELLOW = (0, 1, 1)
MAGENTA = (1, 0, 1)
CYAN = (1, 1, 0)
WHITE = (1, 1, 1)
OFF = (0, 0, 0)

# 8 possible states for each score LED
COLORS = [
    OFF,      # 0
    RED,      # 1
    GREEN,    # 2
    BLUE,     # 3
    YELLOW,   # 4
    MAGENTA,  # 5
    CYAN,     # 6
    WHITE     # 7
]


def all_leds_off():
    for led in leds:
        led.color = OFF


def flash_red():

    old1 = led1.color
    old2 = led2.color
    old3 = led3.color
    old4 = led4.color

    for led in leds:
        led.color = RED

    time.sleep(0.20)

    led1.color = old1
    led2.color = old2
    led3.color = old3
    led4.color = old4


def update_leds(score, lives):

    # ==========================================
    # LED1 = LIFE INDICATOR
    # 1 life -> Red
    # 2 lives -> Blue
    # 3 lives -> Green
    # ==========================================

    lives = max(1, min(lives, 3))

    if lives == 1:
        led1.color = RED
    elif lives == 2:
        led1.color = BLUE
    else:
        led1.color = GREEN

    # ==========================================
    # SCORE INDICATOR
    #
    # LED2 : score 0-7
    # LED3 : score 8-15
    # LED4 : score 16-23
    # ==========================================

    score = max(0, min(score, 23))

    led2_value = min(score, 7)

    if score < 8:
        led3_value = 0
    else:
        led3_value = min(score - 8, 7)

    if score < 16:
        led4_value = 0
    else:
        led4_value = min(score - 16, 7)

    led2.color = COLORS[led2_value]
    led3.color = COLORS[led3_value]
    led4.color = COLORS[led4_value]

# =====================================================
# SHARED STATE
# =====================================================

state = {
    "running": True
}

camera_stream = None
hand_tracker = None

# =====================================================
# CAMERA SETUP
# =====================================================

def start_camera_stream():
    global camera_stream

    stream_url = get_valid_stream_url()
    camera_stream = CameraStream(stream_url, width=640, height=480)
    camera_stream.start()


# =====================================================
# START THREADS
# =====================================================

start_camera_stream()
hand_tracker = HandTrackingController(camera_stream)
hand_tracker.start()

# =====================================================
# PYGAME
# =====================================================

pygame.init()

W, H = 800, 600

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Apple Catcher")

clock = pygame.time.Clock()

font = pygame.font.SysFont(
    "Arial",
    36,
    bold=True
)

big_font = pygame.font.SysFont(
    "Arial",
    72,
    bold=True
)

# =====================================================
# LOAD SPRITES
# =====================================================

apple_img = pygame.image.load(
    "apple.png"
).convert_alpha()

golden_img = pygame.image.load(
    "golden_apple.png"
).convert_alpha()

bomb_img = pygame.image.load(
    "bomb.png"
).convert_alpha()

basket_img = pygame.image.load(
    "basket.png"
).convert_alpha()

apple_img = pygame.transform.smoothscale(
    apple_img,
    (40, 40)
)

golden_img = pygame.transform.smoothscale(
    golden_img,
    (40, 40)
)

bomb_img = pygame.transform.smoothscale(
    bomb_img,
    (40, 40)
)

basket_img = pygame.transform.smoothscale(
    basket_img,
    (180, 50)
)

basket_width = 180

# =====================================================
# START SCREEN
# =====================================================

waiting = True

while waiting:

    screen.fill((100, 200, 255))

    t1 = font.render(
        "Show your hand",
        True,
        (0, 0, 0)
    )

    t2 = font.render(
        "Press SPACE to Start",
        True,
        (0, 0, 0)
    )

    screen.blit(t1, (250, 220))
    screen.blit(t2, (200, 300))

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:
        waiting = False


# =====================================================
# COUNTDOWN
# =====================================================

for text in ["3", "2", "1", "GO!"]:

    screen.fill((100, 200, 255))

    t = big_font.render(
        text,
        True,
        (0, 0, 0)
    )

    screen.blit(
        t,
        (
            W // 2 - t.get_width() // 2,
            H // 2 - 50
        )
    )

    pygame.display.flip()

    pygame.time.wait(1000)


# =====================================================
# RESET FUNCTION
# =====================================================

def reset_game():

    return {
        "basket_x": W // 2,
        "score": 0,
        "lives": 3,
        "objects": [],
        "spawn_timer": 0,
        "game_start_time": time.time(),
        "game_over": False
    }


game = reset_game()

# =====================================================
# MAIN LOOP
# =====================================================

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False
            state["running"] = False

    if game["game_over"]:

        keys = pygame.key.get_pressed()

        if keys[pygame.K_r]:
            game = reset_game()
            all_leds_off()

    game["basket_x"] = int(hand_tracker.x * W)

    game["basket_x"] = max(
        basket_width // 2,
        min(
            W - basket_width // 2,
            game["basket_x"]
        )
    )

    paused = game["game_over"]

    if not paused:

        elapsed = (
            time.time()
            - game["game_start_time"]
        )

        difficulty = min(
            elapsed / 120,
            3
        )

        fall_speed = 2.0 + difficulty

        game["spawn_timer"] -= 1

        if game["spawn_timer"] <= 0:

            r = random.random()

            if r < 0.10:
                obj_type = "golden"
            elif r < 0.20:
                obj_type = "bomb"
            else:
                obj_type = "apple"

            game["objects"].append({
                "type": obj_type,
                "x": random.randint(
                    50,
                    W - 50
                ),
                "y": 0
            })

            game["spawn_timer"] = random.randint(
                35,
                80
            )

        for obj in game["objects"][:]:

            obj["y"] += fall_speed

            if (
                obj["y"] >= 540
                and abs(
                    obj["x"]
                    - game["basket_x"]
                ) < (basket_width // 2)
            ):

                if obj["type"] == "apple":
                    game["score"] += 1

                elif obj["type"] == "golden":
                    game["lives"] = min(game["lives"] + 1, 3)

                elif obj["type"] == "bomb":
                    game["lives"] -= 1
                    flash_red()

                game["objects"].remove(obj)

            elif obj["y"] > H:

                if obj["type"] == "apple":
                    game["lives"] -= 1
                    flash_red()

                game["objects"].remove(obj)

        game["lives"] = max(0, min(game["lives"], 3))

        if game["score"] >= 23:
            game["score"] = 23
            game["game_over"] = True

    update_leds(
    game["score"],
    game["lives"])

    # =================================================
    # DRAW
    # =================================================

    screen.fill((100, 200, 255))

    for obj in game["objects"]:

        rect = pygame.Rect(
            obj["x"] - 20,
            obj["y"] - 20,
            40,
            40
        )

        if obj["type"] == "apple":
            screen.blit(
                apple_img,
                rect
            )

        elif obj["type"] == "golden":
            screen.blit(
                golden_img,
                rect
            )

        else:
            screen.blit(
                bomb_img,
                rect
            )

    basket_rect = basket_img.get_rect(
        center=(
            game["basket_x"],
            550
        )
    )

    screen.blit(
        basket_img,
        basket_rect
    )

    score_text = font.render(
        f"Score {game['score']}  Lives {game['lives']}",
        True,
        (0, 0, 0)
    )

    screen.blit(
        score_text,
        (20, 20)
    )

    if game["lives"] <= 0:

        game["game_over"] = True

        t1 = font.render(
            "GAME OVER",
            True,
            (255, 0, 0)
        )

        t2 = font.render(
            "Press R to Restart",
            True,
            (0, 0, 0)
        )

        screen.blit(
            t1,
            (250, 230)
        )

        screen.blit(
            t2,
            (180, 300)
        )

    if game["score"] >= 23:

        game["game_over"] = True

        win = font.render(
            "YOU WIN!",
            True,
            (0, 120, 0)
        )

        t2 = font.render(
            "Press R to Restart",
            True,
            (0, 0, 0)
        )

        screen.blit(
            win,
            (280, 230)
        )

        screen.blit(
            t2,
            (180, 300)
        )

    pygame.display.flip()

    clock.tick(60)

# =====================================================
# SHUTDOWN
# =====================================================

state["running"] = False

if hand_tracker is not None:
    hand_tracker.stop()

if camera_stream is not None:
    camera_stream.stop()

all_leds_off()

pygame.quit()
sys.exit()