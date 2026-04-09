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
        self.x = random.uniform(0, WINDOW_WIDTH - self.size)
        self.y = random.uniform(0, WINDOW_HEIGHT - self.size)
        self.vector_main = pygame.math.Vector2(self.x, self.y)
        self.vx = self.random_velocity()
        self.vy = self.random_velocity()
        self.jitter_strength = 0.30
        
    def random_velocity(self):
        return self.square_speed if random.choice([True, False]) else -  self.square_speed
    
    def clamp_speed(self):
        self.vx = max(-self.max_speed, min(self.vx, self.max_speed))
        self.vy = max(-self.max_speed, min(self.vy, self.max_speed))

    def soft_wall(self):
        if (self.x <= 0):
            change_in_x = abs(self.x - 0)
            self.vx += change_in_x

        elif (self.x >= (WINDOW_WIDTH - self.size)):
            change_in_x = abs(self.x - (WINDOW_WIDTH-self.size))
            self.vx += change_in_x
        
        if (self.y <= 0):
            change_in_y = abs(self.y - 0)
            self.vy += change_in_y

        elif (self.y >= (WINDOW_HEIGHT - self.size)):
            change_in_y = abs(self.y - (WINDOW_HEIGHT-self.size))
            self.vy += change_in_y

        self.clamp_speed()


    def jitter(self):
        self.vx += random.choice([-self.jitter_strength, +self.jitter_strength])
        self.vy += random.choice([-self.jitter_strength, +self.jitter_strength])

        self.clamp_speed()

    # def collide(self, squares: list[Square]):
    #     for square in squares:
    #         if (self == square):
    #             continue
    #         elif (self.x == square.x):
    #             self.vx *= -1
    #             return self.vx
    #         elif (self.y == square.y):
    #             self.vy *= -1
    #             return self.vy

    def run_away(self, squares: list[Square]):
        for other in squares:
            size_dif = abs(self.size - other.size)
            if (self.size < other.size) and (25 < size_dif <= 55):
                distance = (self.vector_main - other.vector_main).length()
                if distance > 150 or distance < 0.0001:  # Or some small epsilon
                    continue

                direction = (self.vector_main - other.vector_main).normalize()
                size_dif = abs(self.size - other.size)
                escape_force = size_dif/10
                if 5 < size_dif <= 25:
                    escape_force = 1

                elif 25 < size_dif <= 55:
                    escape_force = 1.5
                
                self.vx += direction.x * escape_force
                self.vy += direction.y * escape_force

                self.clamp_speed()
    
    def update(self, squares: list[Square]) -> None:
        # self.collide(squares)
        self.run_away(squares)
        self.jitter()
        self.x += self.vx
        self.y += self.vy
        self.vector_main = pygame.math.Vector2(self.x, self.y)
        self.soft_wall()

        if self.x <= 0 or self.x >= WINDOW_WIDTH - self.size:
            self.vx *= -1
            self.x = max(0, min(self.x, WINDOW_WIDTH - self.size))

        if self.y <= 0 or self.y >= WINDOW_HEIGHT - self.size:
            self.vy *= -1
            self.y = max(0, min(self.y, WINDOW_HEIGHT - self.size))

    def draw(self, win):
        square_rect = pygame.Rect(self.x, self.y, self.size, self.size)
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
