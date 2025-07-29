from typing import List, Optional

import pygame
import random

pygame.init()
move_channel = pygame.mixer.Channel(1)

#globals
WIDTH = 1280
HEIGHT = 720
BG_COLOUR = (19, 87, 37)
LINE_COLOUR = (13, 71, 7)
FONT_COLOUR = (200, 210, 200)
CELL_SIZE = 40
WAIT = 200

#loading assets
food_image = pygame.image.load('food.png')
body_image = pygame.image.load('body.png')
bg = pygame.image.load('bg.png')
move_sfx = pygame.mixer.Sound('move.wav')
eat_sfx = pygame.mixer.Sound('eat_sfx.wav')
game_over_sfx = pygame.mixer.Sound('game_over.wav')
font_48 = pygame.font.Font('PressStart2P-vaV7.ttf', 48)

class SnakeBody:
    """
    A body part for a Snake.

    Attributes:
    hitbox: the hitbox of this <SnakeBody>
    """

    hitbox: pygame.rect

    def __init__(self) -> None:
        self.hitbox = pygame.Rect(((WIDTH // 2) // CELL_SIZE) * CELL_SIZE,
                                  ((HEIGHT // 2) // CELL_SIZE) * CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE)

    def draw(self, screen: pygame.display) -> None:
        screen.blit(body_image, self.hitbox)

    def move(self, x: int, y: int) -> None:
        self.hitbox = self.hitbox.move(x, y)

class Snake:
    """
    The Snake of this game.

    Attributes:
    body: the body of this <Snake>
    speed: the speed of this <Snake>
    last_touched: most reent direction this <Snake> went in
    """

    body: List[SnakeBody]
    speed: int
    last_touched: str

    def reset(self) -> None:
        tail = SnakeBody()
        torso = SnakeBody()
        torso.move(CELL_SIZE, 0)
        head = SnakeBody()
        head.move(CELL_SIZE * 2, 0)
        self.body = [tail, torso, head]
        self.last_touched = 'right'
        self.speed = CELL_SIZE

    def __init__(self) -> None:
        self.reset()

    def get_head(self) -> SnakeBody:
        return self.body[-1]

    def get_tail(self) -> SnakeBody:
        return self.body[0]

    def bounded(self) -> bool:
        if (self.get_head().hitbox.left >= 0 and self.get_head().hitbox.right <= WIDTH
        and self.get_head().hitbox.top >= 0 and self.get_head().hitbox.bottom <= HEIGHT):
            return True
        return False

    def check_keys(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.last_touched != 'down' and self.bounded():
            if self.last_touched in ['left', 'right']:
                move_channel.play(move_sfx)
            self.last_touched = 'up'
        if keys[pygame.K_s] and self.last_touched != 'up' and self.bounded():
            if self.last_touched in ['left', 'right']:
                move_channel.play(move_sfx)
            self.last_touched = 'down'
        if keys[pygame.K_a] and self.last_touched != 'right' and self.bounded():
            if self.last_touched in ['up', 'down']:
                move_channel.play(move_sfx)
            self.last_touched = 'left'
        if keys[pygame.K_d] and self.last_touched != 'left' and self.bounded():
            if self.last_touched in ['up', 'down']:
                move_channel.play(move_sfx)
            self.last_touched = 'right'

    def move(self) -> None:
        old_positions = [part.hitbox.topleft for part in self.body]

        if self.last_touched == 'up':
            if self.get_head().hitbox.bottom < 0:
                self.get_head().hitbox.y = HEIGHT
            self.get_head().move(0, -self.speed)
        elif self.last_touched == 'down':
            if self.get_head().hitbox.top > HEIGHT:
                self.get_head().hitbox.y = -CELL_SIZE
            self.get_head().move(0, self.speed)
        elif self.last_touched == 'left':
            if self.get_head().hitbox.right < 0:
                self.get_head().hitbox.left = WIDTH
            self.get_head().move(-self.speed, 0)
        elif self.last_touched == 'right':
            if self.get_head().hitbox.left > WIDTH:
                self.get_head().hitbox.right = -CELL_SIZE
            self.get_head().move(self.speed, 0)

        for i in range(len(self.body) - 1):
            self.body[i].hitbox.topleft = old_positions[i + 1]

    def draw(self, screen: pygame.display) -> None:
        """
        Draws this <Snake> onto <Screen>
        """
        for part in self.body:
            part.draw(screen)

    def increase_size(self) -> None:
        """
        Makes this <Snake> increase in size by one <SnakeBody>
        """
        tail = SnakeBody()
        tail.hitbox.topleft = self.get_tail().hitbox.topleft
        self.body.insert(0, tail)


class Food:
    """
    A piece of Food

    Attributes:
    hitbox: the htbox of this <Food>
    """
    hitbox: pygame.Rect

    def give_rand(self, x1, x2, y1, y2) -> None:
        # Calculate valid x and y ranges (in cell coordinates)
        max_x = (WIDTH // CELL_SIZE) - 2
        max_y = (HEIGHT // CELL_SIZE) - 2
        snake_positions = [(part.hitbox.x // CELL_SIZE, part.hitbox.y // CELL_SIZE)
                           for part in snake.body]
        while True:
            rand_x = random.randint(0, max_x)
            rand_y = random.randint(0, max_y)
            if (rand_x, rand_y) in snake_positions:
                continue
            self.hitbox = pygame.Rect(rand_x * CELL_SIZE, rand_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (0 <= self.hitbox.left < WIDTH and
                    0 <= self.hitbox.top < HEIGHT):
                break

    def __init__(self, snake: Snake) -> None:
        """
        Creates a new <Food> object
        """
        self.give_rand(snake.get_head().hitbox.x, snake.get_tail().hitbox.x,
                       snake.get_head().hitbox.y, snake.get_tail().hitbox.y)

    def draw(self, screen: pygame.display) -> None:
        screen.blit(food_image, self.hitbox)


def draw(screen: pygame.display, snake: Snake, food: Food) -> None:
    snake.draw(screen)
    food.draw(screen)

def collision(snake: Snake, food: Food) -> Optional[str]:
    if snake.get_head().hitbox.colliderect(food.hitbox):
        eat_sfx.play()
        snake.increase_size()
        food.give_rand(snake.get_head().hitbox.x, snake.get_tail().hitbox.x,
                       snake.get_head().hitbox.y, snake.get_tail().hitbox.y)
        return 'eat'
    for part in snake.body[:-1]:
        if snake.get_head().hitbox.colliderect(part.hitbox):
            game_over_sfx.play()
            return 'die'
    return None

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, LINE_COLOUR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, LINE_COLOUR, (0, y), (WIDTH, y))

def pause_menu(screen: pygame.display) -> None:
    pygame.mouse.set_visible(True)
    blur_layer = pygame.Surface((WIDTH, HEIGHT))
    blur_layer.set_alpha(128)
    blur_layer.fill(BG_COLOUR)
    screen.blit(blur_layer, (0, 0))
    text = font_48.render('PAUSED', True, FONT_COLOUR)
    screen.blit(text, ((WIDTH - text.get_rect().width) / 2, 250))

if __name__ == '__main__':
    running = True
    paused = False
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake')
    clock = pygame.time.Clock()
    snake = Snake()
    food = Food(snake)

    WAIT = 200
    MOVE_PLAYER = pygame.USEREVENT
    pygame.time.set_timer(MOVE_PLAYER, WAIT)

    while running:
        #Quitting the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    freeze_frame = screen.copy()
                    paused = not paused
                    if paused:
                        pygame.time.set_timer(MOVE_PLAYER, 0)
                    else:
                        pygame.time.set_timer(MOVE_PLAYER, WAIT)
            if event.type == MOVE_PLAYER:
                snake.move()

        if paused:
            screen.blit(freeze_frame, (0, 0))
            pause_menu(screen)

        else:
            screen.blit(bg, (0, 0))
            #draw_grid()
            pygame.mouse.set_visible(False)
            snake.check_keys()
            temp = collision(snake, food)
            if temp == 'eat':
                WAIT = int(WAIT * 0.95)
                WAIT = max(WAIT, 50)
                pygame.time.set_timer(MOVE_PLAYER, WAIT)
            elif temp == 'die':
                pygame.time.set_timer(MOVE_PLAYER, 0)
                pygame.time.delay(1000)
                snake.reset()
                food.give_rand(snake.get_head().hitbox.x, snake.get_tail().hitbox.x,
                       snake.get_head().hitbox.y, snake.get_tail().hitbox.y)
                WAIT = 200
                pygame.time.set_timer(MOVE_PLAYER, WAIT)
            draw(screen, snake, food)
        pygame.display.flip()
        clock.tick(60)
