import pygame
import random
import math

# Initialize pygame and set up the display.
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- Game Object Classes ---

class Spaceship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # in degrees
        self.velocity_x = 0
        self.velocity_y = 0
        self.radius = 15
        self.invulnerability = 0  # frames of invulnerability after respawn

    def update(self):
        # Update position using current velocity.
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Apply friction.
        self.velocity_x *= 0.99
        self.velocity_y *= 0.99

        # Decrement invulnerability timer if active.
        if self.invulnerability > 0:
            self.invulnerability -= 1

        # Screen wrap-around.
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0

    def accelerate(self):
        # Accelerate in the direction the spaceship is facing.
        rad = math.radians(self.angle)
        self.velocity_x += math.cos(rad) * 0.2
        self.velocity_y += math.sin(rad) * 0.2

    def rotate(self, direction):
        # Rotate the spaceship. Direction: -1 (left), 1 (right).
        self.angle += direction * 5  # Rotate 5 degrees per frame

    def draw(self, surface):
        # Optionally, make the spaceship blink if invulnerable.
        if self.invulnerability > 0:
            # Blink: only draw during some frames.
            if (self.invulnerability // 5) % 2 == 0:
                color = (200, 200, 200)  # a lighter gray
            else:
                color = BLACK  # skip drawing this frame
        else:
            color = WHITE

        if color != BLACK:
            rad = math.radians(self.angle)
            tip = (self.x + math.cos(rad) * self.radius,
                   self.y + math.sin(rad) * self.radius)
            left_rad = math.radians(self.angle + 140)
            right_rad = math.radians(self.angle - 140)
            left = (self.x + math.cos(left_rad) * self.radius,
                    self.y + math.sin(left_rad) * self.radius)
            right = (self.x + math.cos(right_rad) * self.radius,
                     self.y + math.sin(right_rad) * self.radius)
            pygame.draw.polygon(surface, color, [tip, left, right])


class Asteroid:
    def __init__(self, x, y, size, speed_factor=1.0):
        self.x = x
        self.y = y
        self.size = size  # radius of the asteroid
        angle = random.uniform(0, 360)
        speed = random.uniform(1, 3) * speed_factor
        self.velocity_x = math.cos(math.radians(angle)) * speed
        self.velocity_y = math.sin(math.radians(angle)) * speed

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Screen wrap-around.
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size, 1)


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        rad = math.radians(angle)
        speed = 8
        self.velocity_x = math.cos(rad) * speed
        self.velocity_y = math.sin(rad) * speed
        self.radius = 2
        self.lifetime = 60  # frames until the bullet disappears

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1

        # Screen wrap-around.
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)


# --- Helper Functions ---

def check_collision(obj1, obj2, radius1, radius2):
    """Return True if the two circular objects collide."""
    distance = math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
    return distance < (radius1 + radius2)

def spawn_asteroids(wave):
    """Spawn a list of asteroids based on the current wave.
       The number and speed of asteroids increase with each wave."""
    asteroids = []
    num_asteroids = wave + 3  # e.g., 4 asteroids in wave 1, 5 in wave 2, etc.
    speed_factor = 1 + (wave - 1) * 0.1  # slight speed increase with each wave
    for _ in range(num_asteroids):
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            x = random.randrange(0, WIDTH)
            y = 0
        elif edge == "bottom":
            x = random.randrange(0, WIDTH)
            y = HEIGHT
        elif edge == "left":
            x = 0
            y = random.randrange(0, HEIGHT)
        else:  # right
            x = WIDTH
            y = random.randrange(0, HEIGHT)
        size = random.randint(15, 30)
        asteroids.append(Asteroid(x, y, size, speed_factor))
    return asteroids

def game_over_screen(score):
    """Display the game over screen and return True to restart or False to quit."""
    game_over = True
    while game_over:
        screen.fill(BLACK)
        over_text = font.render("Game Over!", True, WHITE)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_r:
                    return True

def reset_game_state():
    """Initialize game objects and state variables."""
    spaceship = Spaceship(WIDTH / 2, HEIGHT / 2)
    bullets = []
    wave = 1
    score = 0
    asteroids = spawn_asteroids(wave)
    lives = 3
    return spaceship, bullets, wave, score, asteroids, lives

def run_game():
    spaceship, bullets, wave, score, asteroids, lives = reset_game_state()
    running = True

    while running:
        clock.tick(60)  # 60 FPS

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit the game entirely

        # --- Keyboard Input ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            spaceship.rotate(-1)
        if keys[pygame.K_RIGHT]:
            spaceship.rotate(1)
        if keys[pygame.K_UP]:
            spaceship.accelerate()
        if keys[pygame.K_SPACE]:
            if len(bullets) < 5:
                bullets.append(Bullet(spaceship.x, spaceship.y, spaceship.angle))

        # --- Update Game Objects ---
        spaceship.update()
        for asteroid in asteroids:
            asteroid.update()
        for bullet in bullets[:]:
            bullet.update()
            if bullet.lifetime <= 0:
                bullets.remove(bullet)

        # --- Bullet-Asteroid Collisions ---
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if check_collision(bullet, asteroid, bullet.radius, asteroid.size):
                    bullets.remove(bullet)
                    if asteroid in asteroids:
                        asteroids.remove(asteroid)
                    score += 10
                    # Split larger asteroids into two smaller ones.
                    if asteroid.size > 15:
                        for _ in range(2):
                            new_size = asteroid.size // 2
                            asteroids.append(Asteroid(asteroid.x, asteroid.y, new_size))
                    break

        # --- Spaceship-Asteroid Collisions (only if not invulnerable) ---
        if spaceship.invulnerability == 0:
            collision_occurred = False
            for asteroid in asteroids:
                if check_collision(spaceship, asteroid, spaceship.radius, asteroid.size):
                    collision_occurred = True
                    break

            if collision_occurred:
                lives -= 1
                if lives > 0:
                    # Reset spaceship and grant temporary invulnerability.
                    spaceship = Spaceship(WIDTH / 2, HEIGHT / 2)
                    spaceship.invulnerability = 120  # About 2 seconds at 60 FPS
                    bullets = []  # Clear active bullets.
                else:
                    # No lives left; end the game loop.
                    running = False

        # --- Wave Completion ---
        if not asteroids:
            wave += 1
            asteroids = spawn_asteroids(wave)

        # --- Drawing ---
        screen.fill(BLACK)
        spaceship.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        # Draw score, wave, and lives.
        score_text = font.render(f"Score: {score}", True, WHITE)
        wave_text = font.render(f"Wave: {wave}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(wave_text, (10, 40))
        screen.blit(lives_text, (10, 70))
        pygame.display.flip()

    # Game over: show the game over screen.
    return game_over_screen(score)

def main():
    restart = True
    while restart:
        restart = run_game()
    pygame.quit()

if __name__ == "__main__":
    main()
