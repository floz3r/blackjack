import pygame
import os
import math
import time
import random


class Player:
    def __init__(self):
        self.cards = []
        self.card_rects = [(300, 375)]
        self.chosen_cards = []
        self.position = None

    def hit(self):
        self.card_rects.append(
            (self.card_rects[-1][0] + 30, self.card_rects[-1][1] + 25)
        )
        position = self.card_rects[-1]
        print(f"Hit! : {self.card_rects}")
        return position

    def deal(self):
        self.card_rects.append(
            (self.card_rects[-1][0] + 30, self.card_rects[-1][1] + 25)
        )

    def check_score(self):
        s = 0
        ace_counter = 0
        for i in self.cards:
            if self.score(i) == 11:
                ace_counter += 1
            s += self.score(i)

        while ace_counter != 0 and s > 21:
            ace_counter -= 1
            s -= 10

        return s

    def score(self, value):
        while value > 12:
            value -= 13
        value += 1
        if value >= 10:
            value = 10
        elif value == 1:
            value = 11
        return value


class Dealer:
    def __init__(self):
        self.cards = []
        self.card_rects = [(300, 100)]
        self.chosen_cards = []
        self.position = None

    def hit(self):
        self.card_rects.append(
            (self.card_rects[-1][0] + 30, self.card_rects[-1][1] + 25)
        )
        position = self.card_rects[-1]
        print(f"Hit! : {self.card_rects}")
        return position

    def deal(self):
        self.card_rects.append(
            (self.card_rects[-1][0] + 30, self.card_rects[-1][1] + 25)
        )

    def check_score(self):
        s = 0
        ace_counter = 0
        for i in self.cards:
            if self.score(i) == 11:
                ace_counter += 1
            s += self.score(i)

        while ace_counter != 0 and s > 21:
            ace_counter -= 1
            s -= 10

        return s

    def check_score_face_down_card(self):
        return self.score(self.cards[0])

    def score(self, value):
        while value > 12:
            value -= 13
        value += 1
        if value >= 10:
            value = 10
        elif value == 1:
            value = 11
        return value


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width * scale), (int(height * scale)))
        )
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Blackjack:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        image = pygame.image.load(os.path.join("images/background.png"))
        image = pygame.transform.scale(image, (800, 600))

        self.background = image
        self.sprite_sheet = pygame.image.load("images/cards_spritesheet.png")

        self.back_side = pygame.Rect(13 * 40, 3 * 60, 40, 60)
        self.card_rectangles = []
        for row in range(4):
            for column in range(13):
                self.card_rectangles.append(pygame.Rect(column * 40, row * 60, 40, 60))
        self.card_positions = [(150, 400), (150, 100), (200, 400), (200, 100)]
        self.card_scale_factor = 2

        self.running = True
        self.scaled_front_card_images = [
            pygame.transform.scale(
                self.sprite_sheet.subsurface(card_rect),
                (
                    card_rect.width * self.card_scale_factor,
                    card_rect.height * self.card_scale_factor,
                ),
            )
            for card_rect in self.card_rectangles
        ]
        self.scaled_back_side_image = self.scale_card(
            self.sprite_sheet.subsurface(self.back_side), self.back_side
        )
        self.scaled_back_side_image_rect = self.scaled_back_side_image.get_rect().center
        self.angle = 90
        self.pos = self.scaled_back_side_image.get_rect()
        self.pos.right = 600

        self.is_moving = True
        self.is_flipping = False

        self.animation_duration = 60
        self.current_frame = 0

        self.current_card_indexes = []

        self.flipped_card_positions = []
        self.flipped_card_index = 0

        self.chosen_card = self.generate()
        self.player = Player()
        self.dealer = Dealer()
        self.position = None
        self.pressed = False
        self.hit_pressed = False
        self.stand_pressed = False
        self.evaluate = False
        self.reveal_dealer_card = False

        start_img = pygame.image.load("images/hit2.png").convert_alpha()
        stand_img = pygame.image.load("images/stand_btn.png").convert_alpha()
        play_again_img = pygame.image.load("images/playagain.png").convert_alpha()

        self.hit_button = Button(325, 550, start_img, 0.1)
        self.stand_button = Button(395, 550, stand_img, 0.1)
        button_width = play_again_img.get_width() // 2
        button_height = play_again_img.get_height() // 2
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        print(screen_height, screen_width, button_width, button_height)

        button_x = (screen_width - button_width) // 2
        button_y = (screen_height - button_height) // 2
        self.play_again_button = Button(button_x, button_y, play_again_img, 0.5)

    def reset_game(self):
        self.gameover = False
        self.angle = 90
        self.flipped_card_positions = []
        self.flipped_card_index = 0
        self.chosen_card = self.generate()
        self.player = Player()
        self.dealer = Dealer()
        self.position = None
        self.pressed = False
        self.hit_pressed = False
        self.current_card_indexes = []
        self.stand_pressed = False
        self.reveal_dealer_card = False

    def scale_card(self, card_image, card_rect):
        scaled_card_image = pygame.transform.scale(
            card_image,
            (
                card_rect.width * self.card_scale_factor,
                card_rect.height * self.card_scale_factor,
            ),
        )
        return scaled_card_image

    def generate(self):
        self.chosen_card = random.choice(self.card_rectangles)
        return self.chosen_card

    def slide_card(self):
        progress_ratio = self.current_frame / self.animation_duration
        current_x = int(self.pos.x + (self.position[0] - self.pos.x) * progress_ratio)
        current_y = int(self.pos.y + (self.position[1] - self.pos.y) * progress_ratio)

        self.pos.topleft = (current_x, current_y)

        self.screen.blit(self.scaled_back_side_image, self.pos)

        self.current_frame += 1
        if self.current_frame > self.animation_duration:
            self.is_moving = False
            self.is_flipping = True

    def flip_card(self, flip, cr=None):
        if cr == None:
            cr = self.chosen_card
        front_card_image = self.sprite_sheet.subsurface(cr)
        # front_card_rect = front_card_image.get_rect(center=cr.center)
        scaled_card_image = pygame.transform.scale(
            front_card_image,
            (
                cr.width * self.card_scale_factor,
                cr.height * self.card_scale_factor,
            ),
        )

        new_width = round(
            math.sin(math.radians(self.angle)) * self.scaled_back_side_image.get_width()
        )
        if flip:
            if self.angle < 270:
                self.angle += 5

            rot_card = (
                self.scaled_back_side_image if new_width >= 0 else scaled_card_image
            )

            rot_card = pygame.transform.scale(
                rot_card, (abs(new_width), self.scaled_back_side_image.get_height())
            )
            self.screen.blit(
                rot_card,
                rot_card.get_rect(topleft=self.position),
            )
            return cr
        else:
            self.angle = 270
            return cr

    def flip_animation(self):
        for flipped_position in self.flipped_card_positions:
            self.screen.blit(
                self.scaled_front_card_images[
                    self.current_card_indexes[
                        self.flipped_card_positions.index(flipped_position)
                    ]
                ],
                flipped_position,
            )

    def reset(self):
        self.pos.x = 600
        self.pos.y = 0
        self.is_flipping = False
        self.is_moving = True
        self.angle = 90
        self.cmd = ""
        self.current_frame = 0

    def clear_screen(self):
        self.screen.fill((15, 33, 46))

    def show_score_on_screen(self, player_type, player_stand=False):
        rect_size = (50, 20)

        positions = {"dealer": (400, 70), "player": (400, 345)}
        score_colours = {
            "blackjack": (34, 196, 0),
            "under": (34, 56, 68),
            "over": (237, 0, 50),
            "push": (249, 142, 0),
        }
        x, y = positions[player_type]
        rect = pygame.Rect(x, y, *rect_size)
        if player_type == "dealer":
            player = self.dealer
        else:
            player = self.player
        score = player.check_score()
        if player_stand and player_type == "dealer":
            score = player.check_score_face_down_card()
        if score < 21:
            pygame.draw.rect(self.screen, score_colours["under"], rect, 0, 4)
        elif score == 21:
            pygame.draw.rect(self.screen, score_colours["blackjack"], rect, 0, 4)
        else:
            pygame.draw.rect(self.screen, score_colours["over"], rect, 0, 4)

        font = pygame.font.Font(None, 24)
        score_text = font.render(str(score), True, "white")
        text_width, text_height = score_text.get_size()
        text_x = x + (rect_size[0] - text_width) // 2
        text_y = y + (rect_size[1] - text_height) // 2
        return self.screen.blit(score_text, (text_x, text_y))

    def play(self):
        current_turn = "player"
        self.deal = True
        self.gameover = False
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.screen.blit(self.background, (0, 0))

            self.screen.blit(self.scaled_back_side_image, (700, -50))
            self.screen.blit(self.scaled_back_side_image, (690, -50))

            if self.deal:
                self.flip_animation()
                if current_turn == "player" and len(self.player.cards) < 2:
                    self.position = self.player.card_rects[-1]
                elif current_turn == "dealer" and len(self.dealer.cards) < 2:
                    self.position = self.dealer.card_rects[-1]
                else:
                    self.reset()
                    self.deal = False
                    continue

                if self.is_moving:
                    self.slide_card()

                elif self.is_flipping:
                    if self.flipped_card_index == 3:
                        card_rect = self.flip_card(False)
                        self.dealer.cards.append(self.card_rectangles.index(card_rect))
                        self.dealer.chosen_cards.append(self.chosen_card)
                        self.screen.blit(self.scaled_back_side_image, self.position)

                    else:
                        card_rect = self.flip_card(True)
                        if self.angle >= 270:
                            self.flipped_card_positions.append(self.position)
                            self.current_card_indexes.append(
                                self.card_rectangles.index(card_rect)
                            )
                            self.flipped_card_index += 1
                            self.reset()
                            if current_turn == "dealer":
                                self.dealer.cards.append(
                                    self.card_rectangles.index(card_rect)
                                )
                                self.dealer.chosen_cards.append(self.chosen_card)
                                current_turn = "player"
                                if len(self.dealer.card_rects) < 2:
                                    self.dealer.deal()
                            elif current_turn == "player":
                                self.player.chosen_cards.append(self.chosen_card)
                                self.player.cards.append(
                                    self.card_rectangles.index(card_rect)
                                )
                                current_turn = "dealer"
                                if len(self.player.card_rects) < 2:
                                    self.player.deal()
                            self.generate()
                pygame.display.flip()
                self.clock.tick(60)
            elif self.gameover == False:
                self.flip_animation()
                if not self.pressed:
                    self.screen.blit(
                        self.scaled_back_side_image, self.dealer.card_rects[-1]
                    )
                    self.show_score_on_screen("dealer", True)
                    self.show_score_on_screen("player", True)
                    if self.player.check_score() == 21:
                        self.pressed = True
                        current_turn = "dealer"
                        self.position = self.dealer.card_rects[-1]
                        self.is_moving = False
                        self.is_flipping = True
                        self.reveal_dealer_card = True

                    elif self.hit_button.draw(self.screen):
                        self.hit_pressed = True
                        self.pressed = True
                        current_turn = "player"
                        self.position = self.player.hit()
                        self.generate()
                        self.player.chosen_cards.append(self.chosen_card)
                        self.player.cards.append(
                            self.card_rectangles.index(self.player.chosen_cards[-1])
                        )

                    elif self.stand_button.draw(self.screen):
                        self.pressed = True
                        self.stand_pressed = True
                        current_turn = "dealer"
                        self.position = self.dealer.card_rects[-1]
                        self.is_moving = False
                        self.is_flipping = True

                if self.stand_pressed:
                    if self.is_moving:
                        self.slide_card()
                    elif self.is_flipping:
                        card_rect = self.flip_card(True, self.dealer.chosen_cards[-1])
                        if self.angle >= 270:
                            self.flipped_card_positions.append(
                                self.dealer.card_rects[-1]
                            )
                            self.current_card_indexes.append(
                                self.card_rectangles.index(card_rect)
                            )
                            self.flipped_card_index += 1
                            self.reset()
                            if self.dealer.check_score() < 17:
                                time.sleep(0.5)
                                self.position = self.dealer.hit()
                                self.generate()
                                self.dealer.chosen_cards.append(self.chosen_card)
                                self.dealer.cards.append(
                                    self.card_rectangles.index(
                                        self.dealer.chosen_cards[-1]
                                    )
                                )
                                self.stand_pressed = True
                            else:
                                time.sleep(2)
                                self.stand_pressed = False
                                self.gameover = True
                        self.show_score_on_screen("dealer")
                        self.show_score_on_screen("player")

                if self.hit_pressed:
                    self.screen.blit(
                        self.scaled_back_side_image, self.dealer.card_rects[-1]
                    )
                    if self.is_moving:
                        self.slide_card()
                    elif self.is_flipping:
                        card_rect = self.flip_card(True, self.player.chosen_cards[-1])
                        if self.angle >= 270:
                            self.flipped_card_positions.append(
                                self.player.card_rects[-1]
                            )
                            self.current_card_indexes.append(
                                self.card_rectangles.index(card_rect)
                            )
                            self.flipped_card_index += 1
                            self.reset()
                            self.hit_pressed = False
                            self.pressed = False
                            if (
                                self.player.check_score() > 21
                                or self.player.check_score() == 21
                            ):
                                self.pressed = True
                                current_turn = "dealer"
                                self.position = self.dealer.card_rects[-1]
                                self.is_moving = False
                                self.is_flipping = True
                                self.reveal_dealer_card = True
                        self.show_score_on_screen("dealer")
                        self.show_score_on_screen("player")
                if self.reveal_dealer_card:
                    if self.is_moving:
                        self.slide_card()
                    elif self.is_flipping:
                        card_rect = self.flip_card(True, self.dealer.chosen_cards[-1])
                        if self.angle >= 270:
                            self.flipped_card_positions.append(
                                self.dealer.card_rects[-1]
                            )
                            self.current_card_indexes.append(
                                self.card_rectangles.index(card_rect)
                            )
                            self.flipped_card_index += 1
                            self.reset()
                            self.gameover = True
                            time.sleep(3)
                        self.show_score_on_screen("dealer")
                        self.show_score_on_screen("player")
                pygame.display.flip()
                self.clock.tick(60)

            else:
                self.clear_screen()
                if self.play_again_button.draw(self.screen):
                    self.reset_game()
                    self.play()
                pygame.display.flip()
                self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    blackjack = Blackjack()
    blackjack.play()
