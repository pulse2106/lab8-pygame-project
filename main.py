import pygame
import math
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

    def rect(self) -> pygame.Rect:
        square_rect = pygame.Rect(self.vector.x, self.vector.y, self.size, self.size)
        return square_rect
    
    def draw(self, win):
        pygame.draw.rect(win, SQUARE_COLOR, self.rect())

    def centerx(self) -> float:
        return self.rect().centerx
    
    def centery(self) -> float:
        return self.rect().centery

    def random_velocity(self) -> float:
        return self.square_speed if random.choice([True, False]) else -self.square_speed

    def clamp_speed(self) -> None:
        self.vx = max(-self.max_speed, min(self.vx, self.max_speed))
        self.vy = max(-self.max_speed, min(self.vy, self.max_speed))

    def life_span(self) -> None:
        pass

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

    def find_threat_prey(self, squares: list[Square]) -> tuple[Square | None, Square | None]:
        
        def distance(other: Square) -> float:
            return ((other.centerx() - self.centerx())**2 + (other.centery() - self.centerx())**2)
        
        threat = None
        min_threat_distance = math.inf
        prey = None
        min_prey_distance = math.inf

        for other in squares:
            if other is self:
                continue
            dist = distance(other)
            if other.size > self.size and dist < min_threat_distance:
                threat, min_threat_distance = other, dist
            
            elif other.size < self.size and dist < min_prey_distance:
                prey, min_prey_distance = other, dist

        return threat, prey

    def move_vect(self, threat: Square | None, prey: Square | None) -> pygame.Vector2:
        run_vect = pygame.Vector2()
        chase_vect = pygame.Vector2()
        danger = 0.5

        if threat:
            run_vect = pygame.math.Vector2((self.vector.x - threat.vector.x), (self.vector.y - threat.vector.y))
            movement_force = threat.size / 10

            dist = run_vect.length_squared()
            danger = (movement_force * (threat.size * threat.size)/(dist + EPSILLON))
            if danger > 1:
                danger = 1
            else:
                danger = 0

        if prey:
            chase_vect = pygame.Vector2((self.vector.x - prey.vector.x), (self.vector.y - prey.vector.y))

        prey_dist = chase_vect.length()
        threat_dist = run_vect.length()
        if prey_dist:
            chase_vect = chase_vect.normalize()
        elif threat_dist:
            run_vect.normalize()

        movement_vect = chase_vect + run_vect
        if movement_vect.length():
            movement_vect.normalize()

        return ((1 - danger) * self.vector) + (danger * movement_vect)

    def square_run_chase(self, squares: list[Square]) -> None:
        threat, prey = self.find_threat_prey(squares)
        movement_vect = self.move_vect(threat, prey)
        self.vx += movement_vect.x
        self.vy += movement_vect.y

        self.clamp_speed()

    def square_movement(self, dt: float) -> None:
        self.jitter()
        self.vector.x += self.vx * dt
        self.vector.y += self.vy * dt

    def update(self, squares: list[Square], dt: float) -> None:
        self.square_run_chase(squares)
        self.square_movement(dt)
        self.wall_mech()

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