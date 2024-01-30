import pygame
import execution

class Menu():
    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h = self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = - 200

    def draw_cursor(self):
        self.game.draw_text('*', 40, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0, 0))
        pygame.display.update()
        self.game.reset_keys()

class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Tutorial"
        self.startx, self.starty = self.mid_w, self.mid_h + 50
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 90
        self.singleplayerx, self.singleplayery = self.mid_w, self.mid_h + 130
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 170
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text('Brain Command', 70, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 100)
            self.game.draw_text("Tutorial", 40, self.startx, self.starty)
            self.game.draw_text("Competitivo", 40, self.optionsx, self.optionsy)
            self.game.draw_text("Solo", 40, self.singleplayerx, self.singleplayery)
            self.game.draw_text("Créditos", 40, self.creditsx, self.creditsy)
            self.draw_cursor()
            self.blit_screen()


    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == 'Tutorial':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Multiplayer'
            elif self.state == 'Multiplayer':
                self.cursor_rect.midtop = (self.singleplayerx + self.offset, self.singleplayery)
                self.state = 'Singleplayer'
            elif self.state == 'Singleplayer':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Tutorial'
        elif self.game.UP_KEY:
            if self.state == 'Tutorial':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Multiplayer':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Tutorial'
            elif self.state == 'Singleplayer':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Multiplayer'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.singleplayerx + self.offset, self.singleplayery)
                self.state = 'Singleplayer'

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            if self.state == 'Tutorial':
                self.game.playing = True
                execution.play_game()
            elif self.state == 'Multiplayer':
                self.game.playing = True
                execution.play_game()
            elif self.state == 'Singleplayer':
                self.game.playing = True
                execution.play_game()
            elif self.state == 'Credits':
                self.game.curr_menu = self.game.credits
            self.run_display = False

class CreditsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY or self.game.BACK_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text('Créditos', 70, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 100)
            self.game.draw_text('Hecho por AlmaCuevas', 40, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 + 30)
            self.blit_screen()

