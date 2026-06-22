import pygame
import random
import sys
import time

pygame.init()

W, H = 800, 600

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Apple Catcher - Keyboard Version")

clock = pygame.time.Clock()

font = pygame.font.SysFont(
    "Arial",
    36,
    bold=True
)

basket_x = W // 2

score = 0
lives = 3

apples = []

spawn_timer = 0

game_start_time = time.time()

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        basket_x = max(
            60,
            basket_x - 8
        )

    if keys[pygame.K_RIGHT]:
        basket_x = min(
            W - 60,
            basket_x + 8
        )

    # Difficulty increases with time

    elapsed = time.time() - game_start_time

    difficulty = min(
        elapsed / 60,
        4
    )

    # Spawn apples

    spawn_timer -= 1

    if spawn_timer <= 0:

        apple_speed = random.uniform(
            2.5 + difficulty,
            4.0 + difficulty
        )

        apples.append([
            random.randint(50, W - 50),
            0,
            apple_speed
        ])

        spawn_min = max(
            10,
            int(30 - difficulty * 4)
        )

        spawn_max = max(
            20,
            int(60 - difficulty * 8)
        )

        spawn_timer = random.randint(
            spawn_min,
            spawn_max
        )

    # Update apples

    for apple in apples[:]:

        apple[1] += apple[2]

        # Catch

        if (
            apple[1] >= 540
            and abs(apple[0] - basket_x) < 60
        ):

            score += 1
            apples.remove(apple)

        # Miss

        elif apple[1] > H:

            lives -= 1
            apples.remove(apple)

    # Draw

    screen.fill((100, 200, 255))

    for apple in apples:

        pygame.draw.circle(
            screen,
            (220, 30, 30),
            (
                int(apple[0]),
                int(apple[1])
            ),
            20
        )

    pygame.draw.rect(
        screen,
        (139, 69, 19),
        (
            basket_x - 60,
            540,
            120,
            25
        )
    )

    score_text = font.render(
        f"Score {score}   Lives {lives}",
        True,
        (0, 0, 0)
    )

    screen.blit(
        score_text,
        (20, 20)
    )

    if lives <= 0:

        game_over = font.render(
            f"GAME OVER  Final Score: {score}",
            True,
            (255, 0, 0)
        )

        screen.blit(
            game_over,
            (120, 280)
        )

        pygame.display.flip()

        pygame.time.wait(3000)

        running = False

    pygame.display.flip()

    clock.tick(60)

pygame.quit()