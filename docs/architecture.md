# Architecture Documentation

## Scope
This document describes the current architecture implemented in `main.py`.
The project is a single-file Pygame simulation with one domain class (`Square`) and top-level orchestration functions.

## 1) Module Dependency Graph

```mermaid
flowchart LR
    subgraph "Application Module"
        MAIN["main.py"]
        CLASS["Square Class"]
        F_MAIN["main()"]
        F_LOOP["update_window()"]
        F_DRAW["draw_scene()"]
        F_INPUT["handle_event()"]
    end

    PYGAME["pygame"]
    MATH["math"]
    RANDOM["random"]
    TIME["time"]

    MAIN --> CLASS
    MAIN --> F_MAIN
    MAIN --> F_LOOP
    MAIN --> F_DRAW
    MAIN --> F_INPUT

    MAIN --> PYGAME
    MAIN --> MATH
    MAIN --> RANDOM
    MAIN --> TIME

    CLASS --> PYGAME
    CLASS --> MATH
    CLASS --> RANDOM
    CLASS --> TIME
```

## 2) High-Level Runtime/System Flow

```mermaid
flowchart TD
    START["Program Start"] --> INIT["Initialize Pygame and Mixer"]
    INIT --> ASSETS["Load Sound Assets"]
    ASSETS --> WINDOW["Create Window and Clock"]
    WINDOW --> SPAWN["Create Initial Squares"]
    SPAWN --> LOOP["Main Loop"]

    LOOP --> TICK["Compute Delta Time with clock.tick(FPS)"]
    TICK --> INPUT["Handle Input Events"]
    INPUT -->|"Exit Requested"| EXIT["Quit Pygame"]
    INPUT -->|"Continue"| UPDATE["Update Simulation State"]

    UPDATE --> RENDER["Draw Scene and HUD Text"]
    RENDER --> FLIP["Flip Display Buffer"]
    FLIP --> LOOP
```

## 3) Function-Level Call Graph

```mermaid
flowchart TB
    subgraph "Top-Level Functions"
        MAIN["main()"]
        HANDLE["handle_event()"]
        UPDATE_WIN["update_window(squares, dt, die, revive)"]
        ALIVE_FN["alive(squares, die)"]
        REBORN_FN["reborn(squares, revive)"]
        DRAW_SCENE["draw_scene(win, squares)"]
        DRAW_TEXT["draw_text(...)"]
    end

    subgraph "Square Methods"
        SQ_UPDATE["Square.update(squares, dt)"]
        SQ_AGE["Square.aging_effects()"]
        SQ_RUN["Square.square_run_chase(squares, dt)"]
        SQ_FIND["Square.find_threat_prey(squares)"]
        SQ_MOVEV["Square.move_vect(threat, prey)"]
        SQ_CLAMP["Square.clamp_speed()"]
        SQ_MOVE["Square.square_movement(dt)"]
        SQ_JITTER["Square.jitter(dt)"]
        SQ_WALL["Square.wall_mech()"]
        SQ_DRAW["Square.draw(win)"]
        SQ_RECT["Square.rect()"]
        SQ_CX["Square.centerx()"]
        SQ_CY["Square.centery()"]
    end

    MAIN --> HANDLE
    MAIN --> UPDATE_WIN
    MAIN --> DRAW_SCENE
    MAIN --> DRAW_TEXT

    UPDATE_WIN --> ALIVE_FN
    UPDATE_WIN --> REBORN_FN
    UPDATE_WIN --> SQ_UPDATE

    DRAW_SCENE --> SQ_DRAW
    SQ_DRAW --> SQ_RECT

    SQ_UPDATE --> SQ_AGE
    SQ_UPDATE --> SQ_RUN
    SQ_UPDATE --> SQ_MOVE
    SQ_UPDATE --> SQ_WALL

    SQ_RUN --> SQ_FIND
    SQ_RUN --> SQ_MOVEV
    SQ_RUN --> SQ_CLAMP

    SQ_MOVE --> SQ_JITTER

    SQ_FIND --> SQ_CX
    SQ_FIND --> SQ_CY
    SQ_CX --> SQ_RECT
    SQ_CY --> SQ_RECT

    SQ_JITTER --> SQ_CLAMP
```

## 4) Primary Execution Path (Sequence Diagram)

```mermaid
sequenceDiagram
    participant BOOT as "Program Bootstrap"
    participant LOOP as "Main Loop"
    participant INPUT as "Input Handler"
    participant WORLD as "World Updater"
    participant LIFE as "Lifecycle Manager"
    participant ENTITY as "Square Entity"
    participant RENDER as "Renderer"
    participant DISPLAY as "Display System"

    BOOT->>BOOT: "pygame.init() and pygame.mixer.init()"
    BOOT->>BOOT: "Load revive.mp3 and death.mp3"
    BOOT->>DISPLAY: "Create window and set caption"
    BOOT->>LOOP: "Initialize clock, font, and square list"

    loop "Each Frame While run is True"
        LOOP->>LOOP: "dt = clock.tick(FPS) / 1000"
        LOOP->>INPUT: "handle_event()"

        alt "Quit Event or Q Key"
            INPUT-->>LOOP: "False"
            LOOP->>DISPLAY: "pygame.quit()"
        else "Continue Simulation"
            INPUT-->>LOOP: "True"
            LOOP->>WORLD: "update_window(squares, dt, die, revive)"
            WORLD->>LIFE: "alive(squares, die)"
            LIFE-->>WORLD: "filtered survivors"
            WORLD->>LIFE: "reborn(squares, revive)"
            LIFE-->>WORLD: "replenished list"

            loop "For Each Square"
                WORLD->>ENTITY: "square.update(squares, dt)"
                ENTITY->>ENTITY: "aging_effects()"
                ENTITY->>ENTITY: "square_run_chase()"
                ENTITY->>ENTITY: "square_movement()"
                ENTITY->>ENTITY: "wall_mech()"
            end

            LOOP->>RENDER: "draw_scene(win, squares)"
            RENDER->>ENTITY: "square.draw(win) for each square"
            LOOP->>RENDER: "draw_text() for FPS, controls, count"
            LOOP->>DISPLAY: "pygame.display.flip()"
        end
    end
```

## Notes
- The simulation state is fully in memory.
- There is no networking, persistence, or multi-threading in the current source.
- `find_threat_prey()` scans all squares for each square, which gives pairwise interaction cost as population grows.
# Architecture Documentation

## Overview

This project is a compact Pygame simulation that animates a population of moving squares.
The application is centered on a single runtime loop in `main.py`, with a small set of helper
functions and one main domain class, `Square`.

Key characteristics:

- Single-process, real-time graphical application
- In-memory simulation state only
- Frame-based update/render loop driven by `pygame.time.Clock`
- Entity behavior combines random jitter, wall handling, lifetime aging, and size-based chase/escape logic

## Main Components

### `main()`

The entry point initializes Pygame, loads sounds, creates the window, and runs the main loop.
It is responsible for:

- setting up the display
- loading audio assets
- creating the initial square population
- ticking the clock each frame
- calling update and draw functions
- closing Pygame cleanly on exit

### `Square`

`Square` is the core simulation object. Each instance stores:

- position via `vector`
- velocity via `movement_vect`
- size and speed limits
- lifespan and birth time
- current color based on age

It also contains the logic for movement, steering, edge bouncing, and visual aging.

### Top-Level Helpers

- `handle_event()` reads quit events and exits when the window closes or `Q` is pressed.
- `alive()` removes expired squares and triggers the death sound.
- `reborn()` creates new squares until the population reaches `SQUARE_COUNT`.
- `update_window()` applies lifecycle updates and per-square simulation updates.
- `draw_scene()` clears the screen and draws every square.
- `draw_text()` renders the HUD overlay.

## Runtime Flow

```mermaid
flowchart TD
    A[main] --> B[pygame init]
    B --> C[load sounds and create window]
    C --> D[create initial squares]
    D --> E[game loop]
    E --> F[handle_event]
    E --> G[update_window]
    E --> H[draw_scene]
    E --> I[draw HUD]
    E --> J[display.flip]
    E --> K[clock.tick]
    F --> L[quit when requested]
    G --> M[alive]
    G --> N[reborn]
    G --> O[Square.update]
    O --> P[aging_effects]
    O --> Q[square_run_chase]
    O --> R[square_movement]
    O --> S[wall_mech]
```

## Sequence of a Frame

```mermaid
sequenceDiagram
    participant Loop as Main Loop
    participant Input as handle_event
    participant World as update_window
    participant Square as Square
    participant Render as draw_scene

    Loop->>Input: poll events
    Input-->>Loop: continue or exit
    Loop->>World: update_window(squares, dt, die, revive)
    World->>World: alive()
    World->>World: reborn()
    World->>Square: update(squares, dt)
    Square->>Square: aging_effects()
    Square->>Square: square_run_chase()
    Square->>Square: square_movement(dt)
    Square->>Square: wall_mech()
    Loop->>Render: draw_scene(win, squares)
    Loop->>Loop: draw_text() and flip display
```

## Square Behavior Details

### Aging

`aging_effects()` computes an age ratio from `birth_time` and `life_span`, then blends the
base square color toward a red tone.

### Steering

`find_threat_prey()` scans the full square list and picks:

- the closest larger square as a threat
- the closest smaller square as prey

`move_vect()` converts those relationships into a movement vector by combining:

- escape force from threats
- chase force toward prey
- wall push force near the edges

### Movement

`jitter(dt)` adds small random perturbations to the velocity.
`square_movement(dt)` applies the velocity to position using delta time.
`wall_mech()` clamps the square back inside the screen and flips direction when needed.

## Data Flow

1. `pygame.event.get()` determines whether the app keeps running.
2. `clock.tick(FPS)` produces frame time `dt`.
3. `update_window()` mutates the square list and each square's state.
4. `draw_scene()` renders the updated state.
5. `pygame.display.flip()` presents the frame.

This is a stateful loop with no persistence layer, no networking, and no background workers.

## Architectural Notes

- The code is intentionally simple and beginner-friendly.
- Most simulation behavior is inside `Square`, while application orchestration stays at module level.
- The design is easy to follow, but `find_threat_prey()` is O(n^2) across all squares per frame.
- The current file is a good candidate for splitting into rendering, simulation, and app bootstrap modules later.

## Suggested Next Steps

- Move `Square` into its own module if the simulation grows.
- Introduce a spatial grid to reduce neighbor scanning cost.
- Add a deterministic random seed option for testing.
- Extract sound and window setup into a small initialization function.
