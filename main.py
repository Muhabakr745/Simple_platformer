import pygame
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 100
GRAVITY = 0.5
ACCELERATION = 0.3
MAX_SPEED = 7
JUMP_STRENGTH = -12
PLATFORMS = [(475, 500), (50, 400), (425, 275)]  # Platform positions for Level 01


class Direction(Enum):
    LEFT = -1
    RIGHT = 1


class Player(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()

        # Load the player image and set initial attributes
        original_image = pygame.image.load('models/hunter.png')
        self.original_image = pygame.transform.scale(original_image, (PLAYER_SIZE, PLAYER_SIZE))
        self.image = self.original_image.copy()  # Create a copy for image manipulation
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = 0
        self.level = level
        self.speed_x = 0
        self.direction = Direction.RIGHT
        self.is_jumping = False
        self.jump_buffer = False

    def update(self):
        self.apply_gravity()

        # Apply acceleration and deceleration for smoother movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = max(-MAX_SPEED, self.speed_x - ACCELERATION)
            self.direction = Direction.LEFT
        elif keys[pygame.K_RIGHT]:
            self.speed_x = min(MAX_SPEED, self.speed_x + ACCELERATION)
            self.direction = Direction.RIGHT
        else:
            self.speed_x = 0

        self.rect.x += self.speed_x
        self.handle_platform_collisions()

        if keys[pygame.K_UP] and (self.rect.bottom >= SCREEN_HEIGHT or self.jump_buffer):
            self.jump()

        self.rect.y += self.change_y
        self.handle_platform_collisions()

        # Update the player image's orientation
        if self.direction == Direction.LEFT:
            self.image = pygame.transform.flip(self.original_image, False, False)
        else:
            self.image = pygame.transform.flip(self.original_image, True, False)

    def apply_gravity(self):
        self.change_y += GRAVITY
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        self.change_y = JUMP_STRENGTH
        self.is_jumping = True
        self.jump_buffer = False

    def handle_platform_collisions(self):
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.change_y = 0
                self.is_jumping = False
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
                self.change_y = 0

            if not self.is_jumping:
                self.jump_buffer = True


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, has_star=False):
        super().__init__()

        self.image = pygame.image.load('models/platform.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.has_star = has_star

        self.star_image = pygame.image.load('models/star.png')
        self.star_rect = self.star_image.get_rect()
        self.star_rect.midtop = self.rect.centerx, self.rect.top - 50

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.has_star:
            screen.blit(self.star_image, self.star_rect)


class Level(object):
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.player = player

    def add_platform(self, x, y, has_star=False):
        platform = Platform(x, y, has_star)
        self.platform_list.add(platform)

    def draw(self, screen):
        background = pygame.image.load('models/bg.jpg')  # Load the background image
        screen.blit(background, (0, 0))
        for platform in self.platform_list:
            platform.draw(screen)


class Level01(Level):
    def __init__(self, player):
        super().__init__(player)
        for x, y in PLATFORMS:
            has_star = (x, y) == (425, 275)
            self.add_platform(x, y, has_star)


class MainMenu:
    def __init__(self, screen):
        self.quit_button = None
        self.start_button = None
        self.screen = screen
        self.background = pygame.image.load('models/menu_bg.jpg')
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.collidepoint(event.pos):
                        return True
                    elif self.quit_button.collidepoint(event.pos):
                        pygame.quit()
                        return False

            self.screen.blit(self.background, (0, 0))

            title_text = self.title_font.render("Eyup Sultan presents", True, (225, 255, 225))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(title_text, title_rect)

            self.start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
            pygame.draw.rect(self.screen, (255, 255, 255), self.start_button)
            start_text = self.button_font.render("Start Game", True, (0, 0, 0))
            start_text_rect = start_text.get_rect(center=self.start_button.center)
            self.screen.blit(start_text, start_text_rect)

            self.quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50)
            pygame.draw.rect(self.screen, (255, 255, 255), self.quit_button)
            quit_text = self.button_font.render("Quit", True, (0, 0, 0))
            quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
            self.screen.blit(quit_text, quit_text_rect)

            pygame.display.flip()


def run_game(screen):
    pygame.mixer.init()
    pygame.mixer.music.load('music/bg_music.mp3')
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    done = False

    player = Player(None)

    level_list = [Level01(player)]

    current_level_no = 0
    current_level = level_list[current_level_no]
    player.level = current_level

    active_sprite_list = pygame.sprite.Group()
    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed_x = -5
                elif event.key == pygame.K_RIGHT:
                    player.speed_x = 5
                elif event.key == pygame.K_UP:
                    player.jump()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.speed_x < 0:
                    player.speed_x = 0
                elif event.key == pygame.K_RIGHT and player.speed_x > 0:
                    player.speed_x = 0

        active_sprite_list.update()

        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH
        if player.rect.left < 0:
            player.rect.left = 0

        current_level.draw(screen)
        active_sprite_list.draw(screen)

        for platform in current_level.platform_list:
            if platform.has_star and player.rect.colliderect(platform.star_rect):
                done = True

        if done:
            font = pygame.font.Font(None, 36)
            text = font.render("You collected the star! You win!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(8000)
            break

        clock.tick(30)
        pygame.display.flip()


def main():
    pygame.init()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Platformer")

    pygame.mixer.init()

    main_menu = MainMenu(screen)
    start_game = main_menu.run()

    if start_game:
        run_game(screen)

    pygame.quit()


if __name__ == "__main__":
    main()
