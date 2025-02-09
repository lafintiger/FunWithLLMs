import pygame
import random
import math
import sys

# ------------------------------
# Global Constants and Settings
# ------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# Define Colors
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
GRAY   = (100, 100, 100)

# ------------------------------
# Game Object Classes
# ------------------------------

class City:
    """A city to be defended at the bottom of the screen."""
    def __init__(self, x, y, width=40, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alive = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        color = GREEN if self.alive else GRAY
        pygame.draw.rect(surface, color, self.get_rect())


class EnemyMissile:
    """
    An enemy missile spawns at the top and travels in a straight line
    toward a target city. If it reaches the city, that city is destroyed.
    """
    def __init__(self, start_x, start_y, target_x, target_y, target_city, speed=2):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.target_city = target_city
        self.speed = speed
        # Compute a normalized velocity vector toward the target.
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        self.active = True

    def update(self):
        if self.active:
            self.x += self.vx
            self.y += self.vy
            # If the missile is close enough to its target, consider it arrived.
            if math.hypot(self.x - self.target_x, self.y - self.target_y) < self.speed:
                self.active = False
                # Destroy the city if it is still alive.
                if self.target_city and self.target_city.alive:
                    self.target_city.alive = False

    def draw(self, surface):
        if self.active:
            # Draw as a short line in the direction of travel.
            tail_x = self.x - self.vx * 3
            tail_y = self.y - self.vy * 3
            pygame.draw.line(surface, RED, (self.x, self.y), (tail_x, tail_y), 2)


class CounterMissile:
    """
    A counter missile is launched from a fixed battery (bottom center) when the player clicks.
    It flies toward the clicked target and then explodes. During the explosion phase,
    its radius expands and then contracts. Any enemy missile caught in the explosion is destroyed.
    """
    def __init__(self, start_x, start_y, target_x, target_y, speed=5):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.state = "flying"  # "flying" or "exploding"
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        self.explosion_timer = 30  # explosion lasts 30 frames
        self.max_explosion_radius = 50
        self.current_explosion_radius = 0

    def update(self):
        if self.state == "flying":
            self.x += self.vx
            self.y += self.vy
            # If we are near the target, switch to exploding.
            if math.hypot(self.x - self.target_x, self.y - self.target_y) < self.speed:
                self.state = "exploding"
        elif self.state == "exploding":
            self.explosion_timer -= 1
            # Explosion expands for the first half then contracts.
            if self.explosion_timer > 15:
                self.current_explosion_radius = self.max_explosion_radius * ((30 - self.explosion_timer) / 15)
            else:
                self.current_explosion_radius = self.max_explosion_radius * (self.explosion_timer / 15)

    def finished(self):
        """Return True if the explosion is finished."""
        return self.state == "exploding" and self.explosion_timer <= 0

    def draw(self, surface):
        if self.state == "flying":
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 3)
        elif self.state == "exploding":
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(self.current_explosion_radius), 2)

# ------------------------------
# Main Game Loop and Functions
# ------------------------------

def game_over_screen(score, screen, font):
    """Display the game over screen and offer restart or quit."""
    while True:
        screen.fill(BLACK)
        over_text = font.render("Game Over", True, WHITE)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()  # Restart the game
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Missile Command")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Create a set of cities along the bottom.
    cities = []
    num_cities = 6
    margin = 50
    spacing = (WIDTH - 2 * margin) // (num_cities - 1)
    for i in range(num_cities):
        x = margin + i * spacing - 20  # Center the city (width = 40)
        y = HEIGHT - 40
        cities.append(City(x, y))

    enemy_missiles = []
    counter_missiles = []
    score = 0

    enemy_spawn_timer = 0
    enemy_spawn_interval = 120  # frames between spawns (adjusts with difficulty)

    running = True
    while running:
        clock.tick(FPS)

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Launch a counter missile from a fixed battery at the bottom center.
                battery_x = WIDTH // 2
                battery_y = HEIGHT  # slightly off-screen so the missile emerges from the bottom
                target_x, target_y = pygame.mouse.get_pos()
                counter_missiles.append(CounterMissile(battery_x, battery_y, target_x, target_y))

        # --- Spawn Enemy Missiles ---
        enemy_spawn_timer += 1
        # Gradually decrease the interval to increase difficulty.
        current_interval = max(30, enemy_spawn_interval - (score // 100) * 10)
        if enemy_spawn_timer >= current_interval:
            enemy_spawn_timer = 0
            # Only spawn if there is at least one live city.
            alive_cities = [city for city in cities if city.alive]
            if alive_cities:
                target_city = random.choice(alive_cities)
                target_x = target_city.x + target_city.width / 2
                target_y = target_city.y + target_city.height / 2
                start_x = random.randint(0, WIDTH)
                start_y = 0  # spawn along the top
                enemy_missiles.append(EnemyMissile(start_x, start_y, target_x, target_y, target_city))

        # --- Update Enemy Missiles ---
        for missile in enemy_missiles:
            missile.update()
        # Remove missiles that have reached their target.
        enemy_missiles = [m for m in enemy_missiles if m.active]

        # --- Update Counter Missiles ---
        for missile in counter_missiles:
            missile.update()
        # Remove counter missiles whose explosion is finished.
        counter_missiles = [m for m in counter_missiles if not m.finished()]

        # --- Collision Detection ---
        # Check each counter missile explosion against enemy missiles.
        for c_missile in counter_missiles:
            if c_missile.state == "exploding":
                for enemy in enemy_missiles[:]:
                    dist = math.hypot(c_missile.x - enemy.x, c_missile.y - enemy.y)
                    if dist <= c_missile.current_explosion_radius:
                        enemy_missiles.remove(enemy)
                        score += 100

        # --- Check for Game Over ---
        # Game over if all cities are destroyed.
        if not any(city.alive for city in cities):
            running = False

        # --- Drawing ---
        screen.fill(BLACK)
        # Draw cities.
        for city in cities:
            city.draw(screen)
        # Draw enemy missiles.
        for missile in enemy_missiles:
            missile.draw(screen)
        # Draw counter missiles.
        for missile in counter_missiles:
            missile.draw(screen)
        # Draw score.
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

    # Game Over Screen
    game_over_screen(score, screen, font)


if __name__ == "__main__":
    main()
