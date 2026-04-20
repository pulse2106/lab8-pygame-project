import pygame
import random

WINDOW_WIDTH = 1680
WINDOW_HEIGHT = 920
BACKGROUND_COLOR = (20, 20, 20)
SQUARE_COLOR = (40, 180, 255)
SQUARE_COUNT = 25
FPS = 60
EPSILLON = 0.00001

CLOCK = pygame.time.Clock()

class Square:
    def __init__(self) -> None:
        self.size = random.uniform(5, 60)
        self.max_speed = 2500 / (self.size)
        self.square_speed = random.uniform(200, self.max_speed)
        self.vector = pygame.math.Vector2(random.uniform(0, WINDOW_WIDTH - self.size), random.uniform(0, WINDOW_HEIGHT - self.size))
        self.vx = self.random_velocity()
        self.vy = self.random_velocity()
        self.jitter_strength = 0.30

    def random_velocity(self) -> float:
        return self.square_speed if random.choice([True, False]) else -self.square_speed

    def clamp_speed(self) -> None:
        self.vx = max(-self.max_speed, min(self.vx, self.max_speed))
        self.vy = max(-self.max_speed, min(self.vy, self.max_speed))

    def jitter(self) -> None:
        self.vx += random.choice([-self.jitter_strength, self.jitter_strength])
        self.vy += random.choice([-self.jitter_strength, self.jitter_strength])
        self.clamp_speed()

    def wall_mech(self) -> None:
        if self.vector.x <= 0:
            self.vx *= -1
            self.vector.x = 0
        elif self.vector.x >= WINDOW_WIDTH - self.size:
            self.vx *= -1
            self.vector.x = WINDOW_WIDTH - self.size

        if self.vector.y <= 0:
            self.vy *= -1
            self.vector.y = 0
        elif self.vector.y >= WINDOW_HEIGHT - self.size:
            self.vy *= -1
            self.vector.y = WINDOW_HEIGHT - self.size

    # def collide(self, squares: list[Square]) -> None:
    #     for other in squares:
    #         if other is self:
    #             continue
            
    #         direction = (self.vector - other.vector).normalize()
    #         size_dif = abs(self.size - other.size)
    #         repel_force = size_dif/10
    #         if(self.vector.x == other.vector.x):
    #             self.vx += direction.x * repel_force

    #         if (self.vector.y == other.vector.y):
    #             self.vy += direction.y * repel_force

    def run_away(self, squares: list["Square"]) -> None:
        for other in squares:
            if other is self:
                continue

            size_dif = abs(self.size - other.size)
            if (self.size < other.size) and (10 < size_dif <= 55):
                distance = (self.vector - other.vector).length()
                if distance > 150 or distance < EPSILLON:
                    continue

                direction = (self.vector - other.vector).normalize()
                escape_force = size_dif / 10

                self.vx += direction.x * escape_force
                self.vy += direction.y * escape_force

                self.clamp_speed()
    
    def chase(self, squares: list["Square"]) -> None:
        for other in squares:
            if other is self:
                continue

            size_dif = abs(self.size - other.size)
            if (self.size > other.size) and (15 < size_dif <= 55):
                distance = (self.vector - other.vector).length()
                if distance > 100 or distance < EPSILLON:
                    continue

                direction = (other.vector).normalize()
                chase_force = size_dif

                self.vx += direction.x * chase_force
                self.vy += direction.y * chase_force

                self.clamp_speed()

    def square_actions(self, squares: list["Square"]) -> None:
        self.run_away(squares)
        # self.collide(squares)
        self.chase(squares)

    def square_movement(self, dt: float) -> None:
        self.jitter()
        self.vector.x += self.vx * dt
        self.vector.y += self.vy * dt

    def update(self, squares: list["Square"], dt: float) -> None:
        self.square_actions(squares)
        self.square_movement(dt)
        self.wall_mech()

    def draw(self, win) -> None:
        square_rect = pygame.Rect(self.vector.x, self.vector.y, self.size, self.size)
        pygame.draw.rect(win, SQUARE_COLOR, square_rect)

def draw_scene(win: pygame.Surface, squares: list[Square]) -> None:
    """Render the current frame."""
    win.fill(BACKGROUND_COLOR)
    for square in squares:
        square.draw(win)
    pygame.display.flip()

# infinite loop
def main() -> None:
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # setting title to the window
    pygame.display.set_caption("Moving Squares")

    squares = [Square() for _ in range(SQUARE_COUNT)]

    run = True
    while run:
        dt = CLOCK.tick(FPS)/1000
        pygame.font.Font().render(f"FPS = {dt}", True, (0,0,0), None)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for square in squares:
            square.update(squares, dt)
        draw_scene(win, squares)
        
    pygame.quit()

if __name__ == "__main__":
    main()