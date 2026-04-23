# Pygame Moving Squares

This project is a small Pygame simulation where multiple colored squares move around the screen, bounce off the window edges, and react to nearby squares with a mix of chase, dodge, and jitter behavior.

## What It Does

- Spawns a set of squares with random sizes and speeds.
- Moves each square every frame using delta time.
- Makes squares bounce when they hit the window boundaries.
- Adds jitter so the motion feels less robotic.
- Uses size-based interaction so smaller and larger squares influence one another.

## Requirements

- Python 3.10+ recommended
- `pygame`

Install the dependency with:

```bash
pip install pygame-ce
```

## Run the Project

From the repository root:

```bash
python main.py
```

If you are using a virtual environment, activate it first and then run the same command.

## Controls

- `Q` or close the window: quit the application.

## Project Structure

- `main.py` - Main simulation, square behavior, rendering, and event loop.
- `docs/code_explorer.html` - Generated learning dashboard for the project.
- `REPORT.md` - Reflection notes about the AI-assisted development process.
- `JOURNAL.md` - Chronological log of repository interactions.

## How It Works

Each `Square` stores its own position, size, movement vector, and life-related state. On every frame, the program:

1. Reads keyboard and window events.
2. Updates each square's motion.
3. Applies wall collision logic.
4. Renders the updated frame.

The simulation keeps the code compact by putting the movement logic inside the `Square` class while leaving drawing and the main loop as separate functions.

## Notes

- The motion system is intentionally experimental and is a good place to keep iterating on vector math and interactions.
- You can tweak values like `SQUARE_COUNT`, `FPS`, or the square speed limits in `main.py` to change the feel of the simulation.
