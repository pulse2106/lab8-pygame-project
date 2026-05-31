# Python-to-JavaScript Porting Plan: Squares Simulation

## Overview

This document maps the Python/Pygame-based squares simulation into an equivalent JavaScript/HTML5 Canvas implementation. The plan maintains **structural parity**—every Python class, function, and variable will have a direct JavaScript equivalent using camelCase naming conventions where appropriate for JS idioms.

**Target Output:** Single `index.html` file containing the complete simulation  
**Output Location:** `web/` directory

---

## 1. Architecture Summary

### Python Structure
```
main.py
├── Constants (WINDOW_WIDTH, WINDOW_HEIGHT, etc.)
├── Helper Functions (safe_normalize, blend_color, sizes)
├── Square Class (main simulation entity)
├── Application Functions (filter_alive_squares, draw_scene, etc.)
└── main() loop (pygame init → draw_squares → while loop → update → draw → flip)
```

### JavaScript Target Structure
```
index.html
├── HTML (canvas element + CSS)
├── JavaScript
│   ├── Constants
│   ├── Helper Functions
│   ├── Square Class
│   ├── Application Functions
│   └── requestAnimationFrame loop (setup → animate)
```

---

## 2. Constants Mapping

| Python | JavaScript | Type | Notes |
|--------|------------|------|-------|
| `WINDOW_WIDTH: int = 1680` | `const WINDOW_WIDTH = 1680;` | number | Canvas width |
| `WINDOW_HEIGHT: int = 920` | `const WINDOW_HEIGHT = 920;` | number | Canvas height |
| `BACKGROUND_COLOR: tuple[int, int, int] = (20, 20, 20)` | `const BACKGROUND_COLOR = { r: 20, g: 20, b: 20 };` | object | RGB tuple → object |
| `SQUARE_COLOR: tuple[int, int, int] = (40, 180, 255)` | `const SQUARE_COLOR = { r: 40, g: 180, b: 255 };` | object | Blue default color |
| `SQUARE_COUNT: int = 45` | `const SQUARE_COUNT = 45;` | number | Initial population |
| `FPS: int = 60` | `const FPS = 60;` | number | Target frames per second |
| `TEST_MODE_ON: bool = True` | `const TEST_MODE_ON = true;` | boolean | Currently unused but preserve |
| `GROWTH_SPEED: int = 500` | `const GROWTH_SPEED = 500;` | number | Unused; retain for parity |
| `MIN_SPEED: float = 100.0` | `const MIN_SPEED = 100.0;` | number | Minimum movement speed |
| `MAX_BASE_SPEED: float = 450.0` | `const MAX_BASE_SPEED = 450.0;` | number | Base max speed before size adjustment |
| `SIZE_SPEED_FACTOR: float = 300.0` | `const SIZE_SPEED_FACTOR = 300.0;` | number | Speed reduction per size increase |
| `WALL_MARGIN: int = 75` | `const WALL_MARGIN = 75;` | number | Distance from walls for evasion |
| `JITTER_STRENGTH: float = 20.0` | `const JITTER_STRENGTH = 20.0;` | number | Random movement variance |
| `MIN_LIFE_SPAN: int = 30` | `const MIN_LIFE_SPAN = 30;` | number | Minimum lifespan (seconds) |
| `MAX_LIFE_SPAN: int = 60` | `const MAX_LIFE_SPAN = 60;` | number | Maximum lifespan (seconds) |
| `TRAILS_LENGTH: int = 30` | `const TRAILS_LENGTH = 30;` | number | Trail line length |
| `MAX_SIZE: float = 25.0` | `const MAX_SIZE = 25.0;` | number | Largest square size |
| `MEDIUM_SIZE: float = 10.0` | `const MEDIUM_SIZE = 10.0;` | number | Medium square size |
| `MIN_SIZE: float = 4.0` | `const MIN_SIZE = 4.0;` | number | Smallest square size |

---

## 3. Global State & Data Structures

### Python
```python
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
```

### JavaScript Equivalent
```javascript
let SIZE_LIST = [];

function sizes() {
    for (let i = 0; i < 30; i++) {
        SIZE_LIST.push(MIN_SIZE);
    }
    for (let i = 0; i < 10; i++) {
        SIZE_LIST.push(MEDIUM_SIZE);
    }
    for (let i = 0; i < 5; i++) {
        SIZE_LIST.push(MAX_SIZE);
    }
    return SIZE_LIST;
}

sizes();
```

**Mapping Notes:**
- Python `list` → JavaScript `Array`
- Python `append()` → JavaScript `push()`
- Python `for i in range(n)` → JavaScript `for (let i = 0; i < n; i++)`

---

## 4. Utility Functions Mapping

### 4.1 `safe_normalize(vector: pygame.Vector2) → pygame.Vector2`

**Python:**
```python
def safe_normalize(vector: pygame.Vector2) -> pygame.Vector2:
    return vector.normalize() if vector.length_squared() > 0 else vector
```

**JavaScript:** Create a 2D vector utility
```javascript
// Represents a 2D vector with x, y components
class Vector2 {
    constructor(x = 0, y = 0) {
        this.x = x;
        this.y = y;
    }

    // Equivalent to pygame.Vector2.length_squared()
    lengthSquared() {
        return this.x * this.x + this.y * this.y;
    }

    // Equivalent to pygame.Vector2.length()
    length() {
        return Math.sqrt(this.lengthSquared());
    }

    // Equivalent to pygame.Vector2.normalize()
    normalize() {
        const len = this.length();
        if (len === 0) return new Vector2(0, 0);
        return new Vector2(this.x / len, this.y / len);
    }

    // Safe normalize: returns unchanged if zero-length
    safeNormalize() {
        return this.lengthSquared() > 0 ? this.normalize() : this;
    }

    // Vector addition
    add(other) {
        return new Vector2(this.x + other.x, this.y + other.y);
    }

    // Vector subtraction
    subtract(other) {
        return new Vector2(this.x - other.x, this.y - other.y);
    }

    // Scalar multiplication
    multiply(scalar) {
        return new Vector2(this.x * scalar, this.y * scalar);
    }

    // In-place addition
    addInPlace(other) {
        this.x += other.x;
        this.y += other.y;
        return this;
    }
}
```

### 4.2 `blend_color(start, end, ratio) → tuple`

**Python:**
```python
def blend_color(
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    ratio: float,
) -> tuple[int, int, int]:
    return (
        int((start[0] * (1.0 - ratio)) + (end[0] * ratio)),
        int((start[1] * (1.0 - ratio)) + (end[1] * ratio)),
        int((start[2] * (1.0 - ratio)) + (end[2] * ratio)),
    )
```

**JavaScript:**
```javascript
function blendColor(start, end, ratio) {
    // Equivalent to pygame.draw with color interpolation
    return {
        r: Math.round((start.r * (1.0 - ratio)) + (end.r * ratio)),
        g: Math.round((start.g * (1.0 - ratio)) + (end.g * ratio)),
        b: Math.round((start.b * (1.0 - ratio)) + (end.b * ratio))
    };
}
```

---

## 5. Square Class Mapping

### Python Class Structure
```python
class Square:
    def __init__(self) -> None:
        # Constructor: initialize position, velocity, size, timers
        
    def rect(self) -> pygame.Rect:
        # Equivalent to bounding box
        
    def collision(self, other: Square) -> bool:
        # Rectangle collision detection
        
    def center(self) -> pygame.Vector2:
        # Get center point of square
        
    def aging_effects(self) -> None:
        # Update color based on age
        
    def random_velocity(self) -> float:
        # Generate random ±speed
        
    def clamp_speed(self) -> None:
        # Limit velocity magnitude
        
    def jitter(self, dt: float) -> None:
        # Add random movement variance
        
    def clamp_size(self) -> None:
        # Constrain size bounds
        
    def wrapping(self) -> None:
        # Screen wrapping (unused fallback)
        
    def wall_mech(self) -> None:
        # Bounce off walls
        
    def find_threat_prey(self, squares) -> tuple:
        # AI: identify predator and prey
        
    def move_vect(self, threat, prey) -> pygame.Vector2:
        # AI: compute steering force
        
    def square_run_chase(self, squares, dt) -> None:
        # AI behavior update
        
    def eating_check(self, other) -> bool:
        # Check if this square eats another
        
    def eating(self, squares) -> None:
        # Handle collision-based eating
        
    def square_movement(self, dt) -> None:
        # Update position from velocity
        
    def update(self, squares, dt) -> None:
        # Main update cycle
        
    def draw(self, win) -> None:
        # Render square and trail
```

### JavaScript Class Structure
```javascript
class Square {
    constructor() {
        // Initialize all properties from Python __init__
        
        this.size = chooseFromArray(SIZE_LIST);
        // ... (see detailed mapping below)
    }

    rect() {
        // Return bounding box object
    }

    collision(other) {
        // Collision detection
    }

    center() {
        // Return center Vector2
    }

    agingEffects() {
        // Update color with age
    }

    randomVelocity() {
        // Generate ±speed
    }

    clampSpeed() {
        // Limit velocity
    }

    jitter(dt) {
        // Random movement
    }

    clampSize() {
        // Size bounds
    }

    wrapping() {
        // Screen wrapping
    }

    wallMech() {
        // Wall bounce
    }

    findThreatPrey(squares) {
        // AI search
    }

    moveVect(threat, prey) {
        // AI steering
    }

    squareRunChase(squares, dt) {
        // AI behavior
    }

    eatingCheck(other) {
        // Eating logic
    }

    eating(squares) {
        // Collision eating
    }

    squareMovement(dt) {
        // Position update
    }

    update(squares, dt) {
        // Main update
    }

    draw(ctx) {
        // Canvas rendering
    }
}
```

### Detailed Square Constructor Mapping

**Python:**
```python
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
```

**JavaScript:**
```javascript
constructor() {
    this.size = chooseFromArray(SIZE_LIST);
    const sizeRatio = (this.size - MIN_SIZE) / (MAX_SIZE - MIN_SIZE);
    this.maxSpeed = MAX_BASE_SPEED - (sizeRatio * SIZE_SPEED_FACTOR);
    this.squareSpeed = randomUniform(MIN_SPEED, this.maxSpeed);
    
    // Equivalent to pygame.Vector2(x, y)
    this.vector = new Vector2(
        randomUniform(0, WINDOW_WIDTH - this.size),
        randomUniform(0, WINDOW_HEIGHT - this.size)
    );
    
    this.movementVect = new Vector2(
        this.randomVelocity(),
        this.randomVelocity()
    );
    
    this.jitterStrength = JITTER_STRENGTH;
    this.birthTime = Date.now() / 1000; // Current time in seconds
    this.lifeSpan = randomInt(MIN_LIFE_SPAN, MAX_LIFE_SPAN);
    this.baseMaxSpeed = this.maxSpeed;
    this.currentColor = SQUARE_COLOR;
}
```

### Key Method Mappings

#### Python `rect()` → JavaScript `rect()`
**Python:** Returns `pygame.Rect(self.vector.x, self.vector.y, self.size, self.size)`

**JavaScript:**
```javascript
rect() {
    return {
        x: this.vector.x,
        y: this.vector.y,
        width: this.size,
        height: this.size
    };
}
```

#### Python `collision()` → JavaScript `collision()`
**Python:**
```python
def collision(self, other: Square) -> bool:
    return self.rect().colliderect(other)
```

**JavaScript:**
```javascript
collision(other) {
    const r1 = this.rect();
    const r2 = other.rect();
    return !(r1.x + r1.width < r2.x ||
             r2.x + r2.width < r1.x ||
             r1.y + r1.height < r2.y ||
             r2.y + r2.height < r1.y);
}
```

#### Python `center()` → JavaScript `center()`
**Python:**
```python
def center(self) -> pygame.Vector2:
    rect_center = self.rect().center
    return pygame.Vector2(rect_center[0], rect_center[1])
```

**JavaScript:**
```javascript
center() {
    const r = this.rect();
    return new Vector2(r.x + r.width / 2, r.y + r.height / 2);
}
```

#### Python `aging_effects()` → JavaScript `agingEffects()`
**Python:**
```python
def aging_effects(self) -> None:
    age = time.time() - self.birth_time
    life_span = max(1, self.life_span)
    lived_ratio = max(0.0, min(1.0, age / life_span))
    death_color = (255, 30, 30)
    self.current_color = blend_color(SQUARE_COLOR, death_color, lived_ratio)
```

**JavaScript:**
```javascript
agingEffects() {
    const age = (Date.now() / 1000) - this.birthTime;
    const lifeSpan = Math.max(1, this.lifeSpan);
    const livedRatio = Math.max(0.0, Math.min(1.0, age / lifeSpan));
    
    const deathColor = { r: 255, g: 30, b: 30 };
    this.currentColor = blendColor(SQUARE_COLOR, deathColor, livedRatio);
}
```

#### Python `find_threat_prey()` → JavaScript `findThreatPrey()`
**Python:**
```python
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
```

**JavaScript:**
```javascript
findThreatPrey(squares) {
    const selfCenter = this.center();
    
    let threat = null;
    let minThreatDistance = Infinity;
    let prey = null;
    let minPreyDistance = Infinity;

    for (const other of squares) {
        if (other === this) continue;

        const distVec = other.center().subtract(selfCenter);
        const dist = distVec.lengthSquared();
        const visionRadiusSquared = (other.size * 10) ** 2;

        if (dist < visionRadiusSquared) {
            if (other.size > this.size && dist < minThreatDistance) {
                threat = other;
                minThreatDistance = dist;
            } else if (other.size < this.size && dist < minPreyDistance) {
                prey = other;
                minPreyDistance = dist;
            }
        }
    }

    return { threat, prey };
}
```

#### Python `move_vect()` → JavaScript `moveVect()`
**Complex method mapping:** See the Python source for full logic. JavaScript translation:

```javascript
moveVect(threat, prey) {
    let runVect = new Vector2(0, 0);
    let chaseVect = new Vector2(0, 0);

    if (threat) {
        runVect = this.vector.subtract(threat.vector).safeNormalize();
    }

    if (prey) {
        chaseVect = prey.vector.subtract(this.vector).safeNormalize();
    }

    let movementVect = chaseVect.add(runVect);

    let wallPush = new Vector2(0, 0);

    if (this.vector.x < WALL_MARGIN) {
        wallPush.x = 1;
    } else if (this.vector.x > WINDOW_WIDTH - this.size - WALL_MARGIN) {
        wallPush.x = -1;
    }

    if (this.vector.y < WALL_MARGIN) {
        wallPush.y = 1;
    } else if (this.vector.y > WINDOW_HEIGHT - this.size - WALL_MARGIN) {
        wallPush.y = -1;
    }

    if (wallPush.lengthSquared() > 0) {
        movementVect = movementVect.add(wallPush.multiply(5));
    }

    movementVect = movementVect.safeNormalize();

    let steeringMultiplier = 4.0;

    if (threat) {
        const sizeDifference = threat.size - this.size;
        const fearFactor = 1 + (sizeDifference / 10);
        steeringMultiplier *= fearFactor;
    }

    return movementVect.multiply(this.maxSpeed * steeringMultiplier);
}
```

#### Python `draw()` → JavaScript `draw(ctx)`
**Python:**
```python
def draw(self, win: pygame.Surface) -> None:
    pygame.draw.rect(win, self.current_color, self.rect())
    start_pos: tuple = (self.vector.x, self.vector.y)
    end_pos: tuple = (self.vector.x + TRAILS_LENGTH, self.vector.y + TRAILS_LENGTH)
    width: int = 2
    pygame.draw.line(win, self.current_color, start_pos, end_pos, width)
```

**JavaScript (using Canvas Context):**
```javascript
draw(ctx) {
    // Equivalent to pygame.draw.rect()
    const r = this.rect();
    ctx.fillStyle = rgbToString(this.currentColor);
    ctx.fillRect(r.x, r.y, r.width, r.height);

    // Equivalent to pygame.draw.line()
    ctx.strokeStyle = rgbToString(this.currentColor);
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(this.vector.x, this.vector.y);
    ctx.lineTo(this.vector.x + TRAILS_LENGTH, this.vector.y + TRAILS_LENGTH);
    ctx.stroke();
}
```

---

## 6. Application Functions Mapping

### 6.1 `filter_alive_squares()` → `filterAliveSquares()`

**Python:**
```python
def filter_alive_squares(squares: list[Square], die: pygame.Sound) -> list[Square]:
    survivors = []
    for square in squares:
        if time.time() - square.birth_time < square.life_span:
            survivors.append(square)
        else:
            die.play()
    squares[:] = survivors
    return squares
```

**JavaScript (note: audio omitted initially; see Audio section):**
```javascript
function filterAliveSquares(squares) {
    const currentTime = Date.now() / 1000;
    const survivors = [];
    
    for (const square of squares) {
        if (currentTime - square.birthTime < square.lifeSpan) {
            survivors.append(square);
        } else {
            // Equivalent to die.play() - see audio handling section
            playDeathSound();
        }
    }
    
    // Clear and repopulate original array (equivalent to squares[:] = survivors)
    squares.length = 0;
    squares.push(...survivors);
    return squares;
}
```

### 6.2 `reborn()` → `reborn()`

**Python:**
```python
def reborn(squares: list[Square], revive: pygame.Sound) -> list[Square]:
    while len(squares) < SQUARE_COUNT:
        squares.append(Square())
        revive.play()
    return squares
```

**JavaScript:**
```javascript
function reborn(squares) {
    while (squares.length < SQUARE_COUNT) {
        squares.push(new Square());
        // playReviveSound(); // See audio section
    }
    return squares;
}
```

### 6.3 `draw_scene()` → `drawScene()`

**Python:**
```python
def draw_scene(win: pygame.Surface, squares: list[Square]) -> None:
    win.fill(BACKGROUND_COLOR)
    for square in squares:
        square.draw(win)
```

**JavaScript (Canvas):**
```javascript
function drawScene(ctx, squares) {
    // Equivalent to pygame fill (clear canvas and set background)
    ctx.fillStyle = rgbToString(BACKGROUND_COLOR);
    ctx.fillRect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);
    
    // Draw all squares
    for (const square of squares) {
        square.draw(ctx);
    }
}
```

### 6.4 `handle_event()` → `handleEvent()`

**Python:**
```python
def handle_event() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            return False
    return True
```

**JavaScript (using DOM events):**
```javascript
let shouldRun = true;

function handleEvent() {
    // Register keyboard listeners during setup
    // This is called once to set up event listeners, not every frame
}

// Listeners (setup once at initialization)
document.addEventListener('keydown', (event) => {
    if (event.key.toLowerCase() === 'q') {
        shouldRun = false;
    }
});

window.addEventListener('beforeunload', () => {
    shouldRun = false;
});
```

### 6.5 `draw_text()` → `drawText()`

**Python:**
```python
def draw_text(
    text: str,
    font: pygame.font.Font,
    text_col: tuple[int, int, int],
    x: int,
    y: int,
    screen: pygame.Surface,
) -> None:
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
```

**JavaScript (Canvas Text):**
```javascript
function drawText(ctx, text, font, textColor, x, y) {
    // Equivalent to pygame.font.render() + blit()
    ctx.font = font; // e.g., "30px Arial"
    ctx.fillStyle = rgbToString(textColor);
    ctx.fillText(text, x, y);
}
```

### 6.6 `draw_squares()` → `drawSquares()`

**Python:**
```python
def draw_squares() -> list[Square]:
    return [Square() for _ in range(SQUARE_COUNT)]
```

**JavaScript:**
```javascript
function drawSquares() {
    const squares = [];
    for (let i = 0; i < SQUARE_COUNT; i++) {
        squares.push(new Square());
    }
    return squares;
}
```

### 6.7 `update_window()` → `updateWindow()`

**Python:**
```python
def update_window(
    squares: list[Square], dt: float, die: pygame.Sound, revive: pygame.Sound
) -> None:
    squares = filter_alive_squares(squares, die)
    squares = reborn(squares, revive)
    for square in squares:
        square.update(squares, dt)
```

**JavaScript:**
```javascript
function updateWindow(squares, dt) {
    filterAliveSquares(squares);
    reborn(squares);
    for (const square of squares) {
        square.update(squares, dt);
    }
}
```

---

## 7. Main Loop Transformation

### Python Main Loop (pygame-based)
```python
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
        dt = clock.tick(FPS) / 1000  # Delta time in seconds
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
```

### JavaScript Main Loop (requestAnimationFrame-based)

**Key Timing Transformation:**
- **Python:** `clock.tick(FPS)` blocks until enough time has passed for FPS limiting, returns milliseconds since last tick
- **JavaScript:** `requestAnimationFrame()` is called by the browser at ~60 Hz, we calculate `dt` manually

```javascript
// Global animation state
let lastFrameTime = 0;
let shouldRun = true;
let squares = [];
let frameCount = 0;
let fpsCounter = 0;
let currentFPS = 0;

// Canvas and context setup
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Font setup (equivalent to pygame.font.Font(None, 30))
const textFont = '30px Arial';

// Timing constants
const FPS = 60;
const FRAME_TIME = 1000 / FPS; // milliseconds per frame

function init() {
    // Equivalent to pygame.init() and pygame.mixer.init()
    // Initialize sound system, load audio files (optional for MVP)
    
    canvas.width = WINDOW_WIDTH;
    canvas.height = WINDOW_HEIGHT;
    
    // Equivalent to draw_squares()
    squares = drawSquares();
    
    // Setup event listeners
    document.addEventListener('keydown', (event) => {
        if (event.key.toLowerCase() === 'q') {
            shouldRun = false;
        }
    });
    
    // Start animation loop
    requestAnimationFrame(animate);
}

function animate(currentTime) {
    if (!shouldRun) return;

    // Calculate delta time in seconds
    // Equivalent to: dt = clock.tick(FPS) / 1000
    let dt;
    if (lastFrameTime === 0) {
        dt = FRAME_TIME / 1000; // First frame
    } else {
        dt = (currentTime - lastFrameTime) / 1000; // Current delta
    }
    lastFrameTime = currentTime;

    // Clamp dt to prevent large jumps if tab is not focused
    dt = Math.min(dt, 0.1); // Max 100ms per frame

    // FPS counter
    fpsCounter++;
    if (currentTime - frameCount > 1000) {
        currentFPS = fpsCounter;
        fpsCounter = 0;
        frameCount = currentTime;
    }

    // Equivalent to: update_window(squares, dt, die, revive)
    updateWindow(squares, dt);

    // Equivalent to: draw_scene(win, squares)
    drawScene(ctx, squares);

    // Equivalent to: draw_text(...) calls
    drawText(ctx, `FPS: ${Math.round(currentFPS)}`, textFont, {r: 255, g: 255, b: 255}, 20, 10);
    drawText(ctx, 'Press q to exit', textFont, {r: 255, g: 255, b: 255}, 20, 40);
    drawText(ctx, `Number of Squares: ${SQUARE_COUNT}`, textFont, {r: 255, g: 255, b: 255}, 20, 70);

    // Continue animation loop
    requestAnimationFrame(animate);
}

// Start the simulation when the page loads
window.addEventListener('DOMContentLoaded', init);
```

---

## 8. Timing & Physics Equivalency

### Delta Time (dt) Calculation

**Python:**
```python
dt = clock.tick(FPS) / 1000  # Returns milliseconds; convert to seconds
```

**JavaScript:**
```javascript
// Method 1: Using requestAnimationFrame timestamps
let lastFrameTime = 0;
function animate(currentTime) {
    let dt;
    if (lastFrameTime === 0) {
        dt = FRAME_TIME / 1000;
    } else {
        dt = (currentTime - lastFrameTime) / 1000;
    }
    lastFrameTime = currentTime;
    // ...
}

// Method 2: Fixed timestep (alternative for more deterministic physics)
const fixedDt = 1.0 / FPS; // = 1/60 ≈ 0.0167 seconds
```

### FPS Monitoring

**Python:**
```python
clock.get_fps()  # Returns current FPS
```

**JavaScript:**
```javascript
let fpsCounter = 0;
let lastFpsTime = 0;
let currentFPS = 0;

function updateFPS(currentTime) {
    fpsCounter++;
    if (currentTime - lastFpsTime > 1000) {
        currentFPS = fpsCounter;
        fpsCounter = 0;
        lastFpsTime = currentTime;
    }
}
```

---

## 9. Graphics & Canvas Rendering

### Color Representation

**Python:** Tuples `(r, g, b)`
```python
BACKGROUND_COLOR: tuple[int, int, int] = (20, 20, 20)
```

**JavaScript:** Objects or strings
```javascript
const BACKGROUND_COLOR = { r: 20, g: 20, b: 20 };

// Helper to convert to CSS RGB string
function rgbToString(color) {
    return `rgb(${color.r}, ${color.g}, ${color.b})`;
}
```

### Drawing Operations

| Pygame | Canvas API | Notes |
|--------|------------|-------|
| `pygame.draw.rect(surface, color, rect)` | `ctx.fillRect(x, y, w, h)` | Fill rectangle with solid color |
| `pygame.draw.line(surface, color, p1, p2, width)` | `ctx.strokeRect()` or `ctx.stroke()` | Draw line between points |
| `win.fill(color)` | `ctx.fillRect(0, 0, width, height)` with background color | Clear screen |
| `pygame.display.flip()` | Automatic in `requestAnimationFrame` | Canvas updates automatically |
| `font.render(text, aa, color)` + `screen.blit()` | `ctx.fillText(text, x, y)` | Draw text |

### Canvas Setup

```html
<!-- HTML -->
<canvas id="gameCanvas" width="1680" height="920" style="border: 1px solid black;"></canvas>

<!-- CSS -->
<style>
    #gameCanvas {
        display: block;
        margin: 10px auto;
        background-color: #141414;
    }
</style>

<!-- JavaScript -->
<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    canvas.width = WINDOW_WIDTH;
    canvas.height = WINDOW_HEIGHT;
</script>
```

---

## 10. Audio Handling

### Python Audio (pygame.mixer)

```python
pygame.mixer.init()
revive = pygame.mixer.Sound("revive.mp3")
die = pygame.mixer.Sound("death.mp3")
revive.play()
die.play()
```

### JavaScript Audio (Web Audio API)

**Option 1: Simple HTMLAudioElement (MVP approach)**
```javascript
const deathSound = new Audio('death.mp3');
const reviveSound = new Audio('revive.mp3');

function playDeathSound() {
    deathSound.currentTime = 0; // Reset to start
    deathSound.play().catch(err => console.log('Audio play failed:', err));
}

function playReviveSound() {
    reviveSound.currentTime = 0;
    reviveSound.play().catch(err => console.log('Audio play failed:', err));
}
```

**Option 2: Web Audio API (more robust)**
```javascript
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

async function loadAudio(url) {
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    return await audioContext.decodeAudioData(arrayBuffer);
}

let deathBuffer, reviveBuffer;

async function initAudio() {
    deathBuffer = await loadAudio('death.mp3');
    reviveBuffer = await loadAudio('revive.mp3');
}

function playDeathSound() {
    const source = audioContext.createBufferSource();
    source.buffer = deathBuffer;
    source.connect(audioContext.destination);
    source.start(0);
}
```

**Note:** Audio files (`death.mp3`, `revive.mp3`) must be present in the `web/` directory or audio will fail silently.

---

## 11. Data Structure Transformations Summary

| Python | JavaScript | Usage |
|--------|------------|-------|
| `list` | `Array` | `squares = []` |
| `dict` / tuple with names | `Object` | `{ r: 255, g: 0, b: 0 }` |
| `pygame.Vector2(x, y)` | `Vector2` class | Custom class for 2D math |
| `pygame.Rect(x, y, w, h)` | `{ x, y, width, height }` | Bounding box object |
| `time.time()` | `Date.now() / 1000` | Current time in seconds |
| `random.choice()` | `chooseFromArray()` | Pick random element |
| `random.uniform(a, b)` | `randomUniform(a, b)` | Random float in range |
| `random.randint(a, b)` | `randomInt(a, b)` | Random integer in range |

---

## 12. Helper Utility Functions (New for JS)

```javascript
// Choose random element from array (equivalent to random.choice)
function chooseFromArray(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

// Random float in range [min, max)
function randomUniform(min, max) {
    return min + Math.random() * (max - min);
}

// Random integer in range [min, max]
function randomInt(min, max) {
    return Math.floor(randomUniform(min, max + 1));
}

// Convert RGB object to CSS string
function rgbToString(color) {
    return `rgb(${Math.round(color.r)}, ${Math.round(color.g)}, ${Math.round(color.b)})`;
}
```

---

## 13. File Structure

### Target Output Structure
```
web/
├── index.html              (Complete single-file app)
├── js-port.md              (This planning document)
└── assets/                 (Optional)
    ├── death.mp3
    └── revive.mp3
```

### index.html Structure (Skeleton)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Squares Simulation</title>
    <style>
        /* Minimal CSS */
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #000;
            font-family: Arial, sans-serif;
        }

        #gameCanvas {
            border: 2px solid #333;
            display: block;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="1680" height="920"></canvas>

    <script>
        // === CONSTANTS ===
        const WINDOW_WIDTH = 1680;
        const WINDOW_HEIGHT = 920;
        // ... (all constants)

        // === VECTOR2 CLASS ===
        class Vector2 {
            // ... (implementation)
        }

        // === SQUARE CLASS ===
        class Square {
            // ... (implementation)
        }

        // === UTILITY FUNCTIONS ===
        function blendColor(...) { }
        function chooseFromArray(...) { }
        // ... (all helpers)

        // === APPLICATION FUNCTIONS ===
        function filterAliveSquares(...) { }
        function reborn(...) { }
        // ... (all app functions)

        // === MAIN LOOP ===
        function init() { }
        function animate(currentTime) { }

        // === STARTUP ===
        window.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
```

---

## 14. Implementation Checklist

- [ ] **Vector2 Class:** All vector operations (add, subtract, normalize, length, etc.)
- [ ] **Square Class Constructor:** Size, speed, position, velocity initialization
- [ ] **Square Methods:** All core methods (collision, center, aging, jitter, etc.)
- [ ] **AI Methods:** `findThreatPrey()`, `moveVect()`, `squareRunChase()`
- [ ] **Update & Draw:** `update()`, `draw()`, square movement logic
- [ ] **App Functions:** Filter, reborn, draw scene, FPS tracking
- [ ] **Main Loop:** `init()`, `animate()`, requestAnimationFrame integration
- [ ] **Canvas Rendering:** Color setup, text drawing, sprite drawing
- [ ] **Event Handling:** Keyboard listeners (Q to quit)
- [ ] **Audio (Optional):** Placeholder for death/revive sounds
- [ ] **HTML Structure:** Canvas element, styling, script embedding
- [ ] **Testing:** Verify simulation runs at 60 FPS, squares behave correctly

---

## 15. Common Pitfalls & Solutions

| Issue | Python Behavior | JavaScript Solution |
|-------|-----------------|---------------------|
| **Variable Scope** | Global variables easily accessed | Use module pattern or class properties |
| **Time Representation** | `time.time()` returns seconds | `Date.now()` returns milliseconds; divide by 1000 |
| **Random Generation** | `random.choice()`, `random.uniform()` | Create helper functions |
| **Vector Operations** | pygame.Vector2 has built-in methods | Implement Vector2 class with all operations |
| **Collision Detection** | `pygame.Rect.colliderect()` | Manual AABB check |
| **Audio Playback** | Synchronous `play()` | Use promises or check audio context state |
| **Frame Rate Limiting** | `clock.tick()` blocks | Calculate dt and clamp to prevent large jumps |
| **Canvas Clearing** | `win.fill()` in loop | `ctx.fillRect(0, 0, width, height)` each frame |

---

## 16. Educational Annotations (to add in code)

Throughout the JavaScript code, add JSDoc comments explaining pygame equivalents:

```javascript
// Equivalent to pygame.Vector2(x, y) - represents a 2D vector
class Vector2 { }

// Equivalent to pygame.Rect - represents a bounding box
rect() { 
    return {
        x: this.vector.x,
        y: this.vector.y,
        width: this.size,
        height: this.size
    };
}

// Equivalent to pygame.draw.rect(surface, color, rect)
// Uses Canvas API fillRect instead
ctx.fillRect(r.x, r.y, r.width, r.height);

// Equivalent to clock.tick(FPS) / 1000 - delta time in seconds
let dt = (currentTime - lastFrameTime) / 1000;

// Equivalent to pygame.display.flip() - happens automatically in requestAnimationFrame
requestAnimationFrame(animate);
```

---

## 17. Summary

This porting plan provides a 1-to-1 mapping from Python/Pygame to JavaScript/HTML5 Canvas:

1. **Constants** remain identical
2. **Data structures** map cleanly (lists→arrays, tuples→objects, pygame.Vector2→Vector2 class)
3. **Classes** translate directly with camelCase method names
4. **Physics & timing** preserve the original dt-based update model
5. **Graphics** use Canvas 2D Context instead of pygame drawing functions
6. **Main loop** replaces pygame's while+clock with requestAnimationFrame
7. **No refactoring:** Logic remains structurally identical to the Python original

The resulting `index.html` will be a self-contained, single-file simulation that maintains the exact behavior of the Python original.


