import pygame
import math
import random
import time

WINDOW_WIDTH: int = 1680
WINDOW_HEIGHT: int = 920
BACKGROUND_COLOR: tuple[int, int, int] = (20, 20, 20)
SQUARE_COLOR: tuple[int, int, int] = (40, 180, 255)
SQUARE_COUNT: int = 45
FPS: int = 60
TEST_MODE_ON: bool = True
GROWTH_SPEED: int = 500

# Named constants make tuning easier than editing repeated magic numbers.
# MIN_SIZE: float = 5.0
# MAX_SIZE: float = 60.0
MIN_SPEED: float = 100.0
MAX_BASE_SPEED: float = 450.0
SIZE_SPEED_FACTOR: float = 300.0
WALL_MARGIN: int = 75
JITTER_STRENGTH: float = 20.0
MIN_LIFE_SPAN: int = 30
MAX_LIFE_SPAN: int = 60
TRAILS_LENGTH: int = 30

MAX_SIZE: float = 25.0
MEDIUM_SIZE: float = 10.0
MIN_SIZE: float = 4.0
SIZE_LIST: list = []

def sizes() -> list[float]:
    for i in range(30):
        SIZE_LIST.append(MIN_SIZE)
    for i in range(10):
        SIZE_LIST.append(MEDIUM_SIZE)
    for i in range(5):
        SIZE_LIST.append(MAX_SIZE)
    
    return SIZE_LIST

sizes()

def safe_normalize(vector: pygame.Vector2) -> pygame.Vector2:
    # Zero-length vectors cannot be normalized safely, so keep them unchanged.
    return vector.normalize() if vector.length_squared() > 0 else vector


def blend_color(
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    ratio: float,
) -> tuple[int, int, int]:
    # Linear interpolation: mix between two colors using a ratio in [0, 1].
    return (
        int((start[0] * (1.0 - ratio)) + (end[0] * ratio)),
        int((start[1] * (1.0 - ratio)) + (end[1] * ratio)),
        int((start[2] * (1.0 - ratio)) + (end[2] * ratio)),
    )


class Square:
    def __init__(self) -> None:
        self.size = random.choice(SIZE_LIST)
        size_ratio = (self.size - MIN_SIZE) / (MAX_SIZE - MIN_SIZE)
        self.max_speed = MAX_BASE_SPEED - (size_ratio * SIZE_SPEED_FACTOR)
        self.square_speed = random.uniform(MIN_SPEED, self.max_speed)
        self.vector = pygame.Vector2(
            random.uniform(0, WINDOW_WIDTH - self.size),
            random.uniform(0, WINDOW_HEIGHT - self.size),
        )
        self.movement_vect = pygame.Vector2(
            self.random_velocity(), self.random_velocity()
        )
        self.jitter_strength = JITTER_STRENGTH
        self.birth_time = time.time()
        self.life_span = random.randint(MIN_LIFE_SPAN, MAX_LIFE_SPAN)
        self.base_max_speed = self.max_speed
        self.current_color = SQUARE_COLOR

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.vector.x, self.vector.y, self.size, self.size)
    
    def collision(self, other: Square) -> bool:
        return self.rect().colliderect(other)

    def center(self) -> pygame.Vector2:
        # One center helper replaces separate x/y methods and keeps distance math simpler.
        rect_center = self.rect().center
        return pygame.Vector2(rect_center[0], rect_center[1])

    def aging_effects(self) -> None:
        age = time.time() - self.birth_time

        # Guard against invalid lifespan to avoid division errors from bad input/state.
        life_span = max(1, self.life_span)
        lived_ratio = max(0.0, min(1.0, age / life_span))

        death_color = (255, 30, 30)
        self.current_color = blend_color(SQUARE_COLOR, death_color, lived_ratio)

    def random_velocity(self) -> float:
        return self.square_speed if random.choice([True, False]) else -self.square_speed

    def clamp_speed(self) -> None:
        self.movement_vect.x = max(
            -self.max_speed, min(self.movement_vect.x, self.max_speed)
        )
        self.movement_vect.y = max(
            -self.max_speed, min(self.movement_vect.y, self.max_speed)
        )

    def jitter(self, dt: float) -> None:
        jitter_vect = pygame.Vector2(
            random.choice([-self.jitter_strength, self.jitter_strength]),
            random.choice([-self.jitter_strength, self.jitter_strength]),
        )
        self.movement_vect += jitter_vect * dt
        self.clamp_speed()

    def clamp_size(self) -> None:
        self.size = max(MIN_SIZE, (MAX_SIZE + MEDIUM_SIZE))

    def wall_mech(self) -> None:
        if self.vector.x <= 0:
            self.movement_vect.x = abs(self.movement_vect.x)
            self.vector.x = 0
        elif self.vector.x >= WINDOW_WIDTH - self.size:
            self.movement_vect.x = -abs(self.movement_vect.x)
            self.vector.x = WINDOW_WIDTH - self.size

        if self.vector.y <= 0:
            self.movement_vect.y = abs(self.movement_vect.y)
            self.vector.y = 0
        elif self.vector.y >= WINDOW_HEIGHT - self.size:
            self.movement_vect.y = -abs(self.movement_vect.y)
            self.vector.y = WINDOW_HEIGHT - self.size

    def find_threat_prey(
        self, squares: list[Square]
    ) -> tuple[Square | None, Square | None]:
        self_center = self.center()

        def distance(other: Square) -> float:
            return (other.center() - self_center).length_squared()

        threat: Square | None = None
        min_threat_distance = math.inf
        prey: Square | None = None
        min_prey_distance = math.inf

        for other in squares:
            if other is self:
                continue

            dist = distance(other)

            vision_radius_squared = (other.size * 10) ** 2

            if dist < vision_radius_squared:
                if other.size > self.size and dist < min_threat_distance:
                    threat, min_threat_distance = other, dist
                elif other.size < self.size and dist < min_prey_distance:
                    prey, min_prey_distance = other, dist

        return threat, prey

    def move_vect(self, threat: Square | None, prey: Square | None) -> pygame.Vector2:
        run_vect = pygame.Vector2()
        chase_vect = pygame.Vector2()

        if threat:
            run_vect = safe_normalize(self.vector - threat.vector)

        if prey:
            chase_vect = safe_normalize(prey.vector - self.vector)

        movement_vect = chase_vect + run_vect

        wall_push = pygame.Vector2()

        if self.vector.x < WALL_MARGIN:
            wall_push.x = 1
        elif self.vector.x > WINDOW_WIDTH - self.size - WALL_MARGIN:
            wall_push.x = -1

        if self.vector.y < WALL_MARGIN:
            wall_push.y = 1
        elif self.vector.y > WINDOW_HEIGHT - self.size - WALL_MARGIN:
            wall_push.y = -1

        if wall_push.length_squared() > 0:
            movement_vect += wall_push * 5

        movement_vect = safe_normalize(movement_vect)

        steering_multiplier = 4.0

        if threat:
            size_difference = threat.size - self.size
            fear_factor = 1 + (size_difference / 10)
            steering_multiplier *= fear_factor

        return movement_vect * (self.max_speed * steering_multiplier)

    def square_run_chase(self, squares: list[Square], dt: float) -> None:
        threat, prey = self.find_threat_prey(squares)
        dodging_vect = self.move_vect(threat, prey)
        self.movement_vect += dodging_vect * dt

        self.clamp_speed()

    def eating_check(self, other: Square) -> bool:
        if self.size > other.size:
            other.birth_time = 0
            self.rect().union(other)
            self.size += other.size
            self.clamp_size()
            return True
        else:
            return False

    # def collision_action(self, squares: list[Square], dt: float) -> None:
    #     for other in squares:
    #         if other is self:
    #             continue
    #         elif self.collision(other) == True:
    #             self.movement_vect *= -1

    def eating(self, squares: list[Square]) -> None:
        for other in squares:
            if other is self:
                continue
            
            if self.collision(other) == True:
                self.eating_check(other)

    def square_movement(self, dt: float) -> None:
        self.jitter(dt)
        self.vector += self.movement_vect * dt

    def update(self, squares: list[Square], dt: float) -> None:
        self.aging_effects()
        self.eating(squares)

        # self.collision_action(squares, dt)
        self.square_run_chase(squares, dt)
        self.square_movement(dt)
        self.wall_mech()

    def draw(self, win: pygame.Surface) -> None:
        pygame.draw.rect(win, self.current_color, self.rect())
        start_pos: tuple = (self.vector.x, self.vector.y)
        end_pos: tuple = (self.vector.x + TRAILS_LENGTH, self.vector.y + TRAILS_LENGTH)
        width: int = 2
        pygame.draw.line(win, self.current_color, start_pos, end_pos, width)


def filter_alive_squares(squares: list[Square], die: pygame.Sound) -> list[Square]:
    survivors = []
    for square in squares:
        if time.time() - square.birth_time < square.life_span:
            survivors.append(square)
        else:
            die.play()
    squares[:] = survivors
    return squares


def reborn(squares: list[Square], revive: pygame.Sound) -> list[Square]:
    while len(squares) < SQUARE_COUNT:
        # Centralized construction keeps spawn behavior consistent across the project.
        squares.append(Square())
        revive.play()
    return squares


def draw_scene(win: pygame.Surface, squares: list[Square]) -> None:
    """Render the current frame."""
    win.fill(BACKGROUND_COLOR)
    for square in squares:
        square.draw(win)


def handle_event() -> bool:
    """Handle input events and return False when the app should exit."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            return False
    return True


def draw_text(
    text: str,
    font: pygame.font.Font,
    text_col: tuple[int, int, int],
    x: int,
    y: int,
    screen: pygame.Surface,
) -> None:
    """Render a single text label at the given screen position."""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_squares() -> list[Square]:
    return [Square() for _ in range(SQUARE_COUNT)]


def update_window(
    squares: list[Square], dt: float, die: pygame.Sound, revive: pygame.Sound
) -> None:
    squares = filter_alive_squares(squares, die)
    squares = reborn(squares, revive)
    for square in squares:
        square.update(squares, dt)


# infinite loop
def main() -> None:
    pygame.init()
    pygame.mixer.init()
    revive = pygame.mixer.Sound("revive.mp3")
    die = pygame.mixer.Sound("death.mp3")
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Moving Squares")
    text_font = pygame.font.Font(None, 30)
    clock = pygame.time.Clock()

    squares = draw_squares()

    run = True
    while run:
        dt = clock.tick(FPS) / 1000
        run = handle_event()

        # Keep update->draw->flip order unchanged so simulation behavior stays stable.
        update_window(squares, dt, die, revive)
        draw_scene(win, squares)

        draw_text(
            f"FPS: {int(clock.get_fps())}", text_font, (255, 255, 255), 20, 10, win
        )
        draw_text("Press q to exit", text_font, (255, 255, 255), 20, 40, win)
        draw_text(
            f"Number of Squares: {SQUARE_COUNT}",
            text_font,
            (255, 255, 255),
            20,
            70,
            win,
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
