import pygame
import math
import random

WINDOW_WIDTH : int = 1680
WINDOW_HEIGHT : int = 920
BACKGROUND_COLOR : tuple = (20, 20, 20)
SQUARE_COLOR : tuple = (40, 180, 255)
SQUARE_COUNT : int = 25
FPS : int = 60
EPSILLON : float = 0.00001

class Square: 
    def __init__(self) -> None:
        self.size = random.uniform(5, 60)
        self.max_speed = 2500 / (self.size)
        self.square_speed = random.uniform(200, self.max_speed)
        self.vector = pygame.math.Vector2(random.uniform(0, WINDOW_WIDTH - self.size), random.uniform(0, WINDOW_HEIGHT - self.size))
        self.movement_vect = pygame.Vector2(self.random_velocity(), self.random_velocity())
        self.center = pygame.Vector2((self.vector.x + self.size / 2), (self.vector.y + self.size / 2))
        self.direction_vect = self.movement_vect.normalize()
        self.jitter_strength = 20
        self.life = 5

    def rect(self) -> pygame.Rect:
        square_rect = pygame.Rect(self.vector.x, self.vector.y, self.size, self.size)
        return square_rect
    
    def draw(self, win):
        pygame.draw.rect(win, SQUARE_COLOR, self.rect())

    def random_velocity(self) -> float:
        return self.square_speed if random.choice([True, False]) else -self.square_speed

    def clamp_speed(self) -> None:
        self.movement_vect.x = max(-self.max_speed, min(self.movement_vect.x, self.max_speed))
        self.movement_vect.y = max(-self.max_speed, min(self.movement_vect.y, self.max_speed))

    # def alive(self, alive_squares: list[Square]) -> list[Square] :
    #     alive_squares.append(self)
    #     return alive_squares

    # def life_rebirth(self, alive_squares: list[Square]) -> list[Square | None]:
    #     if (self.life - 1) == 0:
    #         dead_square.append(self)
    #         return dead_square
    #     elif self in alive_squares and self.life > 5:
    #         self.life -= 1
    #         return alive_squares

    def jitter(self) -> None:
        self.movement_vect += pygame.Vector2(random.choice([-self.jitter_strength, self.jitter_strength]), random.choice([-self.jitter_strength, self.jitter_strength]))
        self.clamp_speed()

    def wall_mech(self) -> None:
        if self.vector.x <= 0:
            self.movement_vect.x *= -1
            self.vector.x = 0
        elif self.vector.x >= WINDOW_WIDTH - self.size:
            self.movement_vect.x *= -1
            self.vector.x = WINDOW_WIDTH - self.size

        if self.vector.y <= 0:
            self.movement_vect.y *= -1
            self.vector.y = 0
        elif self.vector.y >= WINDOW_HEIGHT - self.size:
            self.movement_vect.y *= -1
            self.vector.y = WINDOW_HEIGHT - self.size

    """NOTE: THIS PIECE OF CODE WAS INSPIRED BY ARTEM, I ADDED A FUNCTION IN OTHE TO MAKE USE OF THE INBUILT CENTER FUNCTION
    INHERITING FROM RECT CLASS WOULD BE NICE BUT IT WILL REQUIRE TOO MUCH WORK"""
    def find_threat_prey(self, squares: list[Square]) -> tuple[Square | None, Square | None]:
        
        def distance(other: Square) -> float:
            return ((other.center.x - self.center.x)**2 + (other.center.y - self.center.x)**2)
        
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

    def square_run_chase(self, squares: list[Square], dt: float) -> None:
        threat, prey = self.find_threat_prey(squares)
        dodging_vect = self.move_vect(threat, prey)
        self.movement_vect += dodging_vect * dt

        self.clamp_speed()

    def square_movement(self, dt: float) -> None:
        self.jitter()
        self.vector += self.movement_vect * dt

    def update(self, squares: list[Square], dt: float) -> None:
        self.square_run_chase(squares, dt)
        self.square_movement(dt)
        self.wall_mech()

        self.center = pygame.Vector2((self.vector.x + self.size)/2, (self.vector.y + self.size)/2)

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

def draw_text(text: str, font: pygame.font.Font, text_col, x: int, y: int, screen: pygame.Surface):
    """Render a single text label at the given screen position."""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# infinite loop
def main() -> None:
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Moving Squares")
    text_font = pygame.font.Font(None, 30)
    clock = pygame.time.Clock()

    squares = [Square() for _ in range(SQUARE_COUNT)]

    run = True
    while run:
        dt = clock.tick(FPS)/1000
        run = handle_event()

        for square in squares:
            square.update(squares, dt)
        draw_scene(win, squares)

        draw_text(f"FPS: {int(clock.get_fps())}", text_font, (255, 255, 255), 20, 10, win)
        draw_text("Press q to exit", text_font, (255, 255, 255), 20, 40, win)

        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()