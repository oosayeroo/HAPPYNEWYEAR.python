import os
import sys
import time
import math
import random

BANNER_LINES = ["HAPPY NEW YEAR", "FROM TSS"]
BANNER_COLOR = "\x1b[97m"


COLORS = [
    "\x1b[31m",  # red
    "\x1b[32m",  # green
    "\x1b[33m",  # yellow
    "\x1b[34m",  # blue
    "\x1b[35m",  # magenta
    "\x1b[36m",  # cyan
    "\x1b[91m",  #bright red
    "\x1b[92m",  # bright green
    "\x1b[94m",  # bright blue
    "\x1b[95m", # bright magenta
]
RESET = "\x1b[0m"

def enable_ansi_on_windows():
    if os.name == "nt":
        os.system("") 

def clear_screen():
    sys.stdout.write("\x1b[2J\x1b[H")

def hide_cursor():
    sys.stdout.write("\x1b[?25l")

def show_cursor():
    sys.stdout.write("\x1b[?25h")

def flush():
    sys.stdout.flush()

WIDTH = 90
HEIGHT = 28
FPS = 30
DT = 1.0 / FPS

FADE_CHARS = ["✦", "✧", "*", "+", ".", " "]
TRAIL_CHARS = ["|", ":", ".", " "]

GRAVITY = 12.0       
AIR_DRAG = 0.985     
SPARK_LIFE = 1.8     
TRAIL_LIFE = 0.6     

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "age", "life", "kind", "color")
    def __init__(self, x, y, vx, vy, life, kind, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.age = 0.0
        self.life = life
        self.kind = kind
        self.color = color

    def alive(self):
        return self.age < self.life


def clamp(n, a, b):
    return a if n < a else (b if n > b else n)

def fade_char(t, kind):
    idx = int(t * (len(FADE_CHARS) - 1))
    idx = clamp(idx, 0, len(FADE_CHARS) - 1)
    return FADE_CHARS[idx] if kind == "spark" else TRAIL_CHARS[min(idx, len(TRAIL_CHARS)-1)]

def spawn_firework(particles):
    start_x = random.randint(10, WIDTH - 10)
    start_y = HEIGHT - 2

    peak_y = random.randint(5, HEIGHT // 2) 
    rocket = {
        "x": float(start_x),
        "y": float(start_y),
        "vx": random.uniform(-3.0, 3.0),
        "vy": random.uniform(-28.0, -22.0),
        "peak_y": float(peak_y),
        "trail_timer": 0.0,
        "exploded": False
    }
    return rocket

def explode(rocket, particles):
    cx, cy = rocket["x"], rocket["y"]
    color = random.choice(COLORS)

    count = random.randint(60, 110)

    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(6.0, 20.0)

        if random.random() < 0.35:
            speed *= random.uniform(0.3, 0.6)

        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - random.uniform(1.5, 4.0)

        life = random.uniform(1.1, SPARK_LIFE)
        particles.append(
            Particle(cx, cy, vx, vy, life, "spark", color)
        )

    for _ in range(random.randint(8, 16)):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2.0, 6.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - random.uniform(2.0, 5.0)
        particles.append(
            Particle(cx, cy, vx, vy, random.uniform(0.6, 1.0), "spark", color)
        )

def update_rocket(rocket, particles, dt):
    if rocket is None:
        return None

    rocket["x"] += rocket["vx"] * dt
    rocket["y"] += rocket["vy"] * dt

    rocket["vy"] += GRAVITY * 0.35 * dt
    rocket["vx"] *= AIR_DRAG
    rocket["vy"] *= AIR_DRAG

    rocket["x"] = clamp(rocket["x"], 1, WIDTH - 2)

    rocket["trail_timer"] += dt
    if rocket["trail_timer"] >= 0.03:
        rocket["trail_timer"] = 0.0
        for _ in range(2):
            particles.append(
                Particle(
                    rocket["x"] + random.uniform(-0.2, 0.2),
                    rocket["y"] + random.uniform(0.0, 0.5),
                    random.uniform(-1.0, 1.0),
                    random.uniform(2.0, 5.0),
                    TRAIL_LIFE,
                    "trail",
                    "\x1b[90m"  
                )
            )

    if (not rocket["exploded"]) and rocket["y"] <= rocket["peak_y"]:
        rocket["exploded"] = True
        explode(rocket, particles)
        return None 

    if rocket["y"] < 0:
        return None

    return rocket

def update_particles(particles, dt):
    alive = []
    for p in particles:
        p.age += dt
        if not p.alive():
            continue

        if p.kind == "spark":
            p.vy += GRAVITY * dt
            p.vx *= AIR_DRAG
            p.vy *= AIR_DRAG
        else:
            p.vy += GRAVITY * 0.15 * dt
            p.vx *= 0.98
            p.vy *= 0.98

        p.x += p.vx * dt
        p.y += p.vy * dt

        if 0 <= p.x < WIDTH and 0 <= p.y < HEIGHT:
            alive.append(p)

    return alive

def render(rocket, particles):
    grid = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for p in sorted(particles, key=lambda z: 0 if z.kind == "trail" else 1):
        ix, iy = int(p.x), int(p.y)
        if 0 <= ix < WIDTH and 0 <= iy < HEIGHT:
            t = p.age / p.life
            ch = fade_char(t, p.kind)
            if ch != " ":
                grid[iy][ix] = f"{p.color}{ch}{RESET}"

    if rocket is not None:
        ix, iy = int(rocket["x"]), int(rocket["y"])
        if 0 <= ix < WIDTH and 0 <= iy < HEIGHT:
            grid[iy][ix] = "\x1b[97m•\x1b[0m"

    start_y = HEIGHT // 2 - len(BANNER_LINES) // 2
    for row, line in enumerate(BANNER_LINES):
        y = start_y + row
        x0 = (WIDTH - len(line)) // 2
        for i, ch in enumerate(line):
            x = x0 + i
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                grid[y][x] = f"{BANNER_COLOR}{ch}{RESET}"


    sys.stdout.write("\x1b[H")
    sys.stdout.write("\n".join("".join(row) for row in grid))
    sys.stdout.write("\n")
    flush()


def main():
    enable_ansi_on_windows()
    hide_cursor()
    clear_screen()

    particles = []
    rocket = None
    next_launch = 0.0

    t0 = time.perf_counter()
    last = t0

    try:
        while True:
            now = time.perf_counter()
            dt = now - last
            last = now

            dt = min(dt, 0.05)

            next_launch -= dt
            if rocket is None and next_launch <= 0.0:
                rocket = spawn_firework(particles)
                next_launch = random.uniform(0.4, 1.2)

            rocket = update_rocket(rocket, particles, dt)
            particles[:] = update_particles(particles, dt)

            render(rocket, particles)

            elapsed = time.perf_counter() - now
            sleep_for = max(0.0, DT - elapsed)
            time.sleep(sleep_for)

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        sys.stdout.write("\nBye ✨\n")
        flush()

if __name__ == "__main__":
    main()
