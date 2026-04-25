import pygame
import math
import random
import time

WINDOW_WIDTH : int = 1680
WINDOW_HEIGHT : int = 920
BACKGROUND_COLOR : tuple = (20, 20, 20)
SQUARE_COLOR : tuple = (40, 180, 255)
SQUARE_COUNT : int = 10
FPS : int = 60
EPSILLON : float = 0.00001

class Square: 
    def __init__(self, alive) -> None:
        self.size = random.uniform(5, 60)
        size_ratio = (self.size - 5) / 55 
        self.max_speed = 450 - (size_ratio * 300) 
        self.square_speed = random.uniform(100, self.max_speed)
        self.vector = pygame.math.Vector2(random.uniform(0, WINDOW_WIDTH - self.size), random.uniform(0, WINDOW_HEIGHT - self.size))
        self.movement_vect = pygame.Vector2(self.random_velocity(), self.random_velocity())
        self.direction_vect = self.movement_vect.normalize()
        self.jitter_strength = 20
        self.birth_time = time.time()
        self.life_span = random.randint(30, 60)
        self.alive = alive
        self.age = time.time() - self.birth_time
        self.lived_ratio = self.age/self.life_span
        self.base_max_speed = self.max_speed
        self.current_color = SQUARE_COLOR

    def rect(self) -> pygame.Rect:
        square_rect = pygame.Rect(self.vector.x, self.vector.y, self.size, self.size)
        return square_rect
    
    def centerx(self):
        centerx = self.rect().centerx
        return centerx
    
    def centery(self):
        centery = self.rect().centery
        return centery
    
    def aging_effects(self) -> None:
        age = time.time() - self.birth_time
        lived_ratio = age / self.life_span
        
        life_ratio = max(0.0, 1.0 - lived_ratio)
        
        death_color = (255, 30, 30)
        
        # self.max_speed = max(30.0, self.base_max_speed * life_ratio)
        
        r = int((SQUARE_COLOR[0] * life_ratio) + (death_color[0] * lived_ratio))
        g = int((SQUARE_COLOR[1] * life_ratio) + (death_color[1] * lived_ratio))
        b = int((SQUARE_COLOR[2] * life_ratio) + (death_color[2] * lived_ratio))
        
        self.current_color = (r, g, b)

    def random_velocity(self) -> float:
        return self.square_speed if random.choice([True, False]) else -self.square_speed

    def clamp_speed(self) -> None:
        self.movement_vect.x = max(-self.max_speed, min(self.movement_vect.x, self.max_speed))
        self.movement_vect.y = max(-self.max_speed, min(self.movement_vect.y, self.max_speed))

    def jitter(self, dt: float) -> None:
        jitter_vect = pygame.Vector2(random.choice([-self.jitter_strength, self.jitter_strength]), random.choice([-self.jitter_strength, self.jitter_strength]))
        self.movement_vect += jitter_vect * dt
        self.clamp_speed()

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

    """NOTE: THIS PIECE OF CODE WAS INSPIRED BY ARTEM, I ADDED A FUNCTION IN OTHE TO MAKE USE OF THE INBUILT CENTER FUNCTION
    INHERITING FROM RECT CLASS WOULD BE NICE BUT IT WILL REQUIRE TOO MUCH WORK"""
    def find_threat_prey(self, squares: list[Square]) -> tuple[Square | None, Square | None]:
        def distance(other: Square) -> float:
            return ((other.centerx() - self.centerx())**2 + (other.centery() - self.centery())**2)
        
        threat = None
        min_threat_distance = math.inf
        prey = None
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
            run_vect = pygame.math.Vector2((self.vector.x - threat.vector.x), (self.vector.y - threat.vector.y))
            if run_vect.length():
                run_vect = run_vect.normalize()

        if prey:
            chase_vect = pygame.Vector2((prey.vector.x - self.vector.x), (prey.vector.y - self.vector.y))
            if chase_vect.length():
                chase_vect = chase_vect.normalize()

        movement_vect = chase_vect + run_vect

        wall_push = pygame.Vector2()
        margin = 75

        if self.vector.x < margin:
            wall_push.x = 1 
        elif self.vector.x > WINDOW_WIDTH - self.size - margin:
            wall_push.x = -1 
            
        if self.vector.y < margin:
            wall_push.y = 1
        elif self.vector.y > WINDOW_HEIGHT - self.size - margin:
            wall_push.y = -1 

        if wall_push.length():
            movement_vect += wall_push * 5

        if movement_vect.length():
            movement_vect = movement_vect.normalize()

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

    def square_movement(self, dt: float) -> None:
        self.jitter(dt)
        self.vector += self.movement_vect * dt

    def update(self, squares: list[Square], dt: float) -> None:
        self.aging_effects()

        self.square_run_chase(squares, dt)
        self.square_movement(dt)
        self.wall_mech()

    def draw(self, win):
        pygame.draw.rect(win, self.current_color, self.rect())

def alive(squares: list[Square], die: pygame.Sound) -> list[Square]:
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
        alive = True
        squares.append(Square(alive))
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

def draw_text(text: str, font: pygame.font.Font, text_col, x: int, y: int, screen: pygame.Surface):
    """Render a single text label at the given screen position."""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def update_window(squares: list[Square], dt: float, die: pygame.Sound, revive: pygame.Sound):
    squares = alive(squares, die)
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

    squares = [Square(True) for _ in range(SQUARE_COUNT)]

    run = True
    while run:
        dt = clock.tick(FPS)/1000
        run = handle_event()

        update_window(squares, dt, die, revive)
        draw_scene(win, squares)

        draw_text(f"FPS: {int(clock.get_fps())}", text_font, (255, 255, 255), 20, 10, win)
        draw_text("Press q to exit", text_font, (255, 255, 255), 20, 40, win)
        draw_text(f"Number of Squares: {SQUARE_COUNT}", text_font, (255, 255, 255), 20, 70, win)

        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()