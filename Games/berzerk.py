import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions and setup.
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Berzerk")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Colors
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
BLUE   = (0, 0, 255)
RED    = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY   = (100, 100, 100)

# Object dimensions
PLAYER_SIZE = 20
ENEMY_SIZE  = 20
BULLET_SIZE = 5

# -------------------------------
# Game Object Classes
# -------------------------------

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = 3
        self.lives = 3
        self.facing = "up"  # initial shooting direction
        self.invulnerability = 0  # frames remaining invulnerable

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)

    def update(self, walls):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        # Determine movement and update facing direction.
        if keys[pygame.K_UP]:
            dy = -self.speed
            self.facing = "up"
        if keys[pygame.K_DOWN]:
            dy = self.speed
            self.facing = "down"
        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.facing = "left"
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.facing = "right"

        # Move horizontally and check collisions with walls.
        self.x += dx
        rect = self.get_rect()
        for wall in walls:
            if rect.colliderect(wall):
                if dx > 0:
                    self.x = wall.left - PLAYER_SIZE
                elif dx < 0:
                    self.x = wall.right
                rect = self.get_rect()

        # Move vertically and check collisions with walls.
        self.y += dy
        rect = self.get_rect()
        for wall in walls:
            if rect.colliderect(wall):
                if dy > 0:
                    self.y = wall.top - PLAYER_SIZE
                elif dy < 0:
                    self.y = wall.bottom
                rect = self.get_rect()

        # Decrease invulnerability timer if active.
        if self.invulnerability > 0:
            self.invulnerability -= 1

    def draw(self, surface):
        # If invulnerable, draw in yellow; otherwise blue.
        color = YELLOW if self.invulnerability > 0 else BLUE
        pygame.draw.rect(surface, color, self.get_rect())


class Enemy:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = 2
        # Start with an arbitrary velocity.
        self.vx = random.choice([-1, 1]) * self.speed
        self.vy = random.choice([-1, 1]) * self.speed

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), ENEMY_SIZE, ENEMY_SIZE)

    def update(self, player, walls):
        # Compute vector from enemy to player.
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx /= distance
            dy /= distance
        # Set velocity toward the player.
        self.vx = dx * self.speed
        self.vy = dy * self.speed

        # Move horizontally and check collisions.
        self.x += self.vx
        rect = self.get_rect()
        for wall in walls:
            if rect.colliderect(wall):
                if self.vx > 0:
                    self.x = wall.left - ENEMY_SIZE
                elif self.vx < 0:
                    self.x = wall.right
                self.vx = -self.vx
                rect = self.get_rect()

        # Move vertically and check collisions.
        self.y += self.vy
        rect = self.get_rect()
        for wall in walls:
            if rect.colliderect(wall):
                if self.vy > 0:
                    self.y = wall.top - ENEMY_SIZE
                elif self.vy < 0:
                    self.y = wall.bottom
                self.vy = -self.vy
                rect = self.get_rect()

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.get_rect())


class Bullet:
    def __init__(self, x, y, direction):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.speed = 8
        self.lifetime = 60  # frames bullet remains alive

        # Set velocity based on shooting direction.
        if direction == "up":
            self.vx, self.vy = 0, -self.speed
        elif direction == "down":
            self.vx, self.vy = 0, self.speed
        elif direction == "left":
            self.vx, self.vy = -self.speed, 0
        elif direction == "right":
            self.vx, self.vy = self.speed, 0
        else:
            self.vx, self.vy = 0, -self.speed

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), BULLET_SIZE, BULLET_SIZE)

    def update(self, walls):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        # If bullet hits a wall, mark it to be removed.
        rect = self.get_rect()
        for wall in walls:
            if rect.colliderect(wall):
                self.lifetime = 0

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.get_rect())


# -------------------------------
# Maze (Wall) Setup
# -------------------------------

def generate_maze():
    walls = []
    wall_thickness = 10
    # Border walls.
    walls.append(pygame.Rect(0, 0, WIDTH, wall_thickness))                    # top
    walls.append(pygame.Rect(0, HEIGHT - wall_thickness, WIDTH, wall_thickness))   # bottom
    walls.append(pygame.Rect(0, 0, wall_thickness, HEIGHT))                     # left
    walls.append(pygame.Rect(WIDTH - wall_thickness, 0, wall_thickness, HEIGHT))   # right

    # Interior walls (a few fixed rectangles to simulate a maze).
    walls.append(pygame.Rect(150, 100, 10, 300))
    walls.append(pygame.Rect(300, 50, 10, 200))
    walls.append(pygame.Rect(450, 150, 10, 300))
    walls.append(pygame.Rect(600, 100, 10, 250))
    walls.append(pygame.Rect(200, 400, 300, 10))
    walls.append(pygame.Rect(100, 250, 200, 10))
    return walls


# -------------------------------
# Game Over Screen
# -------------------------------

def game_over_screen(score):
    while True:
        screen.fill(BLACK)
        text1 = font.render("Game Over!", True, WHITE)
        text2 = font.render(f"Final Score: {score}", True, WHITE)
        text3 = font.render("Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    return False


# -------------------------------
# Main Game Function
# -------------------------------

def main():
    # Initialize game objects.
    player = Player(WIDTH // 2, HEIGHT // 2)
    walls = generate_maze()
    bullets = []
    enemies = []
    score = 0

    # Spawn a few enemies at random locations (ensuring they aren’t too close to the player).
    for i in range(5):
        ex = random.randint(50, WIDTH - 50)
        ey = random.randint(50, HEIGHT - 50)
        if math.hypot(ex - player.x, ey - player.y) < 100:
            ex += 100
            ey += 100
        enemies.append(Enemy(ex, ey))

    running = True
    while running:
        clock.tick(60)  # 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Create a bullet at the center of the player.
                    bx = player.x + PLAYER_SIZE // 2 - BULLET_SIZE // 2
                    by = player.y + PLAYER_SIZE // 2 - BULLET_SIZE // 2
                    bullets.append(Bullet(bx, by, player.facing))

        # Update game objects.
        player.update(walls)
        for enemy in enemies:
            enemy.update(player, walls)
        for bullet in bullets[:]:
            bullet.update(walls)
            if bullet.lifetime <= 0:
                bullets.remove(bullet)

        # Check for bullet–enemy collisions.
        for bullet in bullets[:]:
            bullet_rect = bullet.get_rect()
            for enemy in enemies[:]:
                if bullet_rect.colliderect(enemy.get_rect()):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 100
                    # Respawn a new enemy.
                    new_ex = random.randint(50, WIDTH - 50)
                    new_ey = random.randint(50, HEIGHT - 50)
                    enemies.append(Enemy(new_ex, new_ey))
                    break

        # Check for enemy–player collisions.
        for enemy in enemies:
            if enemy.get_rect().colliderect(player.get_rect()):
                if player.invulnerability == 0:
                    player.lives -= 1
                    player.invulnerability = 120  # ~2 seconds of invulnerability
                    # Reset the player's position.
                    player.x = WIDTH // 2
                    player.y = HEIGHT // 2
                    if player.lives <= 0:
                        if game_over_screen(score):
                            main()  # Restart the game
                        else:
                            running = False
                            return

        # Drawing section.
        screen.fill(BLACK)
        for wall in walls:
            pygame.draw.rect(screen, GRAY, wall)
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)

        # Draw score and lives.
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
