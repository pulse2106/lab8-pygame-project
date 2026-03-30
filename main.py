import pygame
import random

WINDOW_WIDTH = 1680
WINDOW_HEIGHT = 920
BACKGROUND_COLOR = (20, 20, 20)
SQUARE_COLOR = (40, 180, 255)
SQUARE_COUNT = 100
FPS = 60


def random_velocity(speed: float) -> int:
    return speed if random.choice([True, False]) else -speed


def create_square(size: float, speed: float) -> dict[str, int]:
    return {
        "x": random.uniform(0, WINDOW_WIDTH - size),
        "y": random.uniform(0, WINDOW_HEIGHT - size),
        "vx": random_velocity(speed),
        "vy": random_velocity(speed),
    }


def update_square(square: dict[str, int], size: float) -> None:
    square["x"] += square["vx"]
    square["y"] += square["vy"]

    if square["x"] <= 0 or square["x"] >= WINDOW_WIDTH - size:
        square["vx"] *= -1
        square["x"] = max(0, min(square["x"], WINDOW_WIDTH - size))

    if square["y"] <= 0 or square["y"] >= WINDOW_HEIGHT - size:
        square["vy"] *= -1
        square["y"] = max(0, min(square["y"], WINDOW_HEIGHT - size))


def draw_scene(win: pygame.Surface, squares: list[dict[str, int]], size: float) -> None:
    """Render the current frame."""
    win.fill(BACKGROUND_COLOR)

    for square in squares:
        square_rect = pygame.Rect(square["x"], square["y"], size, size)
        pygame.draw.rect(win, SQUARE_COLOR, square_rect)

    pygame.display.flip()

def speed(size: float) -> float:
    max_spped = (1/(size) * 20)
    return max_spped

# infinite loop
def main() -> None:
    pygame.init()

    
    square_size = random.uniform(5, 60)
    square_speed_max = speed(square_size)
    square_speed = random.uniform(2, square_speed_max)

    clock = pygame.time.Clock()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # setting title to the window
    pygame.display.set_caption("Moving Squares")

    squares = [create_square(square_size, square_speed) for _ in range(SQUARE_COUNT)]

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for square in squares:
            update_square(square, square_size)

        draw_scene(win, squares, square_size)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
