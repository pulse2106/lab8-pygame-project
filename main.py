import pygame
import random

WINDOW_WIDTH = 1680
WINDOW_HEIGHT = 920
BACKGROUND_COLOR = (20, 20, 20)
SQUARE_COLOR = (40, 180, 255)
SQUARE_COUNT = 50
FPS = 60

class Square:
    def __init__(self) -> None:
        self.size = random.uniform(5, 60)
        self.max_speed = 120/self.size
        self.square_speed = random.uniform(2, self.max_speed)
        self.vector = pygame.math.Vector2((random.uniform(0, WINDOW_WIDTH - self.size)), (random.uniform(0, WINDOW_HEIGHT - self.size)))
        self.vx = self.random_velocity()
        self.vy = self.random_velocity()
        self.jitter_strength = 0.30
        
    def random_velocity(self):
        return self.square_speed if random.choice([True, False]) else -  self.square_speed
    
    def clamp_speed(self):
        self.vx = max(-self.max_speed, min(self.vx, self.max_speed))
        self.vy = max(-self.max_speed, min(self.vy, self.max_speed))

    def soft_wall(self):
        if (self.vector.x <= 0):
            change_in_x = abs(self.vector.x - 0)
            self.vx += change_in_x

        elif (self.vector.x >= (WINDOW_WIDTH - self.size)):
            change_in_x = abs(self.vector.x - (WINDOW_WIDTH-self.size))
            self.vx += change_in_x
        
        if (self.vector.y <= 0):
            change_in_y = abs(self.vector.y - 0)
            self.vy += change_in_y

        elif (self.vector.y >= (WINDOW_HEIGHT - self.size)):
            change_in_y = abs(self.vector.y - (WINDOW_HEIGHT-self.size))
            self.vy += change_in_y

        self.clamp_speed()


    def jitter(self):
        self.vx += random.choice([-self.jitter_strength, +self.jitter_strength])
        self.vy += random.choice([-self.jitter_strength, +self.jitter_strength])

        self.clamp_speed()

    def bounce_wall(self):
        if self.vector.x <= 0 or self.vector.x >= WINDOW_WIDTH - self.size:
            self.vx *= -1
            self.vector.x = max(0, min(self.vector.x, WINDOW_WIDTH - self.size))

        if self.vector.y <= 0 or self.vector.y >= WINDOW_HEIGHT - self.size:
            self.vy *= -1
            self.vector.y = max(0, min(self.vector.y, WINDOW_HEIGHT - self.size))

    # def collide(self, squares: list[Square]):
    #     for square in squares:
    #         if (self == square):
    #             continue
    #         elif (self.vector.x == square.x):
    #             self.vx *= -1
    #             return self.vx
    #         elif (self.vector.y == square.y):
    #             self.vy *= -1
    #             return self.vy

    def run_away(self, squares: list[Square]):
        for other in squares:
            size_dif = abs(self.size - other.size)
            if (self.size < other.size) and (25 < size_dif <= 55):
                distance = (self.vector - other.vector).length()
                if distance > 150 or distance < 0.0001:  # Or some small epsilon
                    continue

                direction = (self.vector - other.vector).normalize()
                size_dif = abs(self.size - other.size)
                escape_force = size_dif/10
                
                self.vx += direction.x * escape_force
                self.vy += direction.y * escape_force

                self.clamp_speed()
    
    def update(self, squares: list[Square]) -> None:
        # self.collide(squares)
        self.run_away(squares)
        self.jitter()
        self.vector.x += self.vx
        self.vector.y += self.vy
        self.soft_wall()
        self.bounce_wall()

    def draw(self, win):
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

    clock = pygame.time.Clock()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # setting title to the window
    pygame.display.set_caption("Moving Squares")

    squares = [Square() for _ in range(SQUARE_COUNT)]

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for square in squares:
            square.update(squares)
            
        draw_scene(win, squares)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
