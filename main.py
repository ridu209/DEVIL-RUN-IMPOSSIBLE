
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse, Triangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
import random

if platform not in ("android", "ios"):
    Window.size = (960, 540)

Window.clearcolor = (0.025, 0.025, 0.06, 1)


class GameWorld(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.player_x = 100
        self.player_y = 0
        self.vy = 0
        self.speed = 260
        self.camera = 0
        self.score = 0
        self.dead = False
        self.won = False
        self.started = False

        self.left = False
        self.right = False
        self.jump_request = False

        self.level_length = 2600

        self.pits = [
            (520, 100),
            (1050, 120),
            (1680, 110),
            (2200, 130)
        ]

        self.spikes = [
            (350, 65),
            (780, 70),
            (1300, 65),
            (1500, 70),
            (1950, 75),
            (2450, 65)
        ]

        Clock.schedule_interval(self.update, 1 / 60)

    def reset(self):
        self.player_x = 100
        self.player_y = 0
        self.vy = 0
        self.camera = 0
        self.score = 0
        self.dead = False
        self.won = False
        self.started = True
        self.left = False
        self.right = False
        self.jump_request = False

    def ground_y(self):
        return self.y + self.height * 0.23

    def in_pit(self, x):
        return any(a < x < a + b for a, b in self.pits)

    def die(self):
        if not self.dead and not self.won:
            self.dead = True

    def update(self, dt):

        if not self.started or self.dead or self.won:
            return

        dt = min(dt, 0.04)

        move = 0

        if self.right:
            move += 1

        if self.left:
            move -= 1

        self.player_x += move * self.speed * dt
        self.player_x = max(0, self.player_x)

        if self.jump_request and self.player_y <= 0:
            self.vy = 610

        self.jump_request = False

        self.vy -= 1450 * dt
        self.player_y += self.vy * dt

        if self.player_y < 0:
            self.player_y = 0
            self.vy = 0

        if self.in_pit(self.player_x + 20):
            self.die()

        for x, width in self.spikes:
            if (
                x - 28 < self.player_x + 35
                and x + width > self.player_x
                and self.player_y < 40
            ):
                self.die()

        if self.player_y < -150:
            self.die()

        self.camera = max(
            0, self.player_x - self.width * 0.32
        )

        self.score = int(self.player_x / 10)

        if self.player_x >= self.level_length:
            self.won = True

        self.draw_world()

    def draw_world(self):

        self.canvas.clear()

        w = self.width
        h = self.height

        if w <= 0 or h <= 0:
            return

        floor = self.ground_y()
        cam = self.camera

        with self.canvas:

            # Background
            Color(0.025, 0.025, 0.075, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Stars
            random.seed(22)

            for i in range(45):
                sx = self.x + (i * 97) % int(w)
                sy = self.y + (i * 67) % int(h)

                Color(0.5, 0.4, 0.8, 0.55)
                Ellipse(
                    pos=(sx, sy),
                    size=(3, 3)
                )

            # Background glow
            Color(0.25, 0.025, 0.09, 0.35)
            Ellipse(
                pos=(self.x + w * 0.6, floor - 40),
                size=(w * 0.5, h * 0.65)
            )

            # Ground
            Color(0.12, 0.11, 0.19, 1)
            Rectangle(
                pos=(self.x, self.y),
                size=(w, floor - self.y)
            )

            # Lava
            for px, pw in self.pits:
                sx = self.x + px - cam

                Color(1, 0.12, 0.015, 1)
                Rectangle(
                    pos=(sx, self.y),
                    size=(pw, floor - self.y + 3)
                )

                Color(1, 0.65, 0.02, 1)
                Rectangle(
                    pos=(sx, floor - 8),
                    size=(pw, 7)
                )

            # Ground top
            Color(0.65, 0.08, 0.18, 1)
            Rectangle(
                pos=(self.x, floor),
                size=(w, 8)
            )

            # Spikes
            for px, pw in self.spikes:

                sx = self.x + px - cam

                Color(1, 0.08, 0.12, 1)

                for j in range(0, pw, 24):
                    Triangle(
                        points=[
                            sx + j, floor,
                            sx + j + 12, floor + 35,
                            sx + j + 24, floor
                        ]
                    )

            # Finish gate
            fx = self.x + self.level_length - cam

            Color(0.1, 0.8, 1, 1)
            Rectangle(
                pos=(fx, floor),
                size=(7, 145)
            )

            Color(0.6, 0.9, 1, 1)
            Ellipse(
                pos=(fx - 15, floor + 130),
                size=(38, 38)
            )

            # Player
            px = self.x + self.player_x - cam
            py = floor + self.player_y

            Color(0, 0, 0, 0.4)
            Ellipse(
                pos=(px - 4, floor - 5),
                size=(45, 10)
            )

            # Body
            Color(0.2, 0.05, 0.85, 1)
            Rectangle(
                pos=(px, py),
                size=(36, 48)
            )

            # Head
            Color(0.85, 0.75, 1, 1)
            Ellipse(
                pos=(px + 4, py + 38),
                size=(29, 29)
            )

            # Eyes
            Color(1, 0.05, 0.15, 1)
            Ellipse(
                pos=(px + 23, py + 52),
                size=(5, 5)
            )

            # Glow
            Color(0.45, 0.1, 1, 0.25)
            Ellipse(
                pos=(px - 8, py - 8),
                size=(53, 65)
            )

    def on_size(self, *args):
        self.draw_world()


class MenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()

        title = Label(
            text="[b]DEVIL RUN[/b]\n[color=ff1744]IMPOSSIBLE[/color]",
            markup=True,
            font_size="42sp",
            pos_hint={"center_x": 0.5, "center_y": 0.7},
            size_hint=(1, 0.3)
        )

        subtitle = Label(
            text="CAN YOU SURVIVE?",
            font_size="16sp",
            color=(0.7, 0.7, 0.85, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.48},
            size_hint=(1, 0.1)
        )

        play = Button(
            text="PLAY GAME",
            font_size="22sp",
            bold=True,
            size_hint=(0.55, 0.13),
            pos_hint={"center_x": 0.5, "center_y": 0.29},
            background_normal="",
            background_color=(0.65, 0.03, 0.15, 1)
        )

        play.bind(on_release=self.start_game)

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(play)

        self.add_widget(layout)

    def start_game(self, *args):
        self.manager.current = "game"
        self.manager.get_screen("game").start()


class GameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = FloatLayout()

        self.world = GameWorld(
            size_hint=(1, 1)
        )

        self.layout.add_widget(self.world)

        self.hud = Label(
            text="LEVEL 01   |   SCORE: 0",
            bold=True,
            font_size="18sp",
            pos_hint={"x": 0.02, "top": 0.98},
            size_hint=(0.5, 0.08)
        )

        self.layout.add_widget(self.hud)

        self.message = Label(
            text="",
            bold=True,
            font_size="32sp",
            color=(1, 0.15, 0.2, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint=(0.8, 0.15)
        )

        self.layout.add_widget(self.message)

        self.left_btn = Button(
            text="◀",
            font_size="32sp",
            size_hint=(0.16, 0.17),
            pos_hint={"x": 0.02, "y": 0.03},
            background_normal="",
            background_color=(0.3, 0.05, 0.5, 0.8)
        )

        self.right_btn = Button(
            text="▶",
            font_size="32sp",
            size_hint=(0.16, 0.17),
            pos_hint={"x": 0.20, "y": 0.03},
            background_normal="",
            background_color=(0.3, 0.05, 0.5, 0.8)
        )

        self.jump_btn = Button(
            text="JUMP",
            font_size="21sp",
            bold=True,
            size_hint=(0.2, 0.19),
            pos_hint={"right": 0.98, "y": 0.03},
            background_normal="",
            background_color=(0.75, 0.04, 0.12, 0.9)
        )

        self.left_btn.bind(
            on_press=lambda *a: self.set_left(True),
            on_release=lambda *a: self.set_left(False)
        )

        self.right_btn.bind(
            on_press=lambda *a: self.set_right(True),
            on_release=lambda *a: self.set_right(False)
        )

        self.jump_btn.bind(
            on_press=lambda *a: self.jump()
        )

        self.layout.add_widget(self.left_btn)
        self.layout.add_widget(self.right_btn)
        self.layout.add_widget(self.jump_btn)

        self.retry = Button(
            text="RESTART",
            size_hint=(0.3, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            background_normal="",
            background_color=(0.7, 0.04, 0.15, 1)
        )

        self.retry.bind(on_release=self.start)

        self.layout.add_widget(self.retry)
        self.retry.opacity = 0
        self.retry.disabled = True

        self.add_widget(self.layout)

        Clock.schedule_interval(self.refresh, 0.1)

    def start(self, *args):
        self.world.reset()
        self.message.text = ""
        self.retry.opacity = 0
        self.retry.disabled = True

    def set_left(self, value):
        self.world.left = value

    def set_right(self, value):
        self.world.right = value

    def jump(self):
        self.world.jump_request = True

    def refresh(self, dt):

        self.hud.text = (
            "LEVEL 01   |   SCORE: "
            + str(self.world.score)
        )

        if self.world.dead:
            self.message.text = "YOU DIED!"
            self.retry.opacity = 1
            self.retry.disabled = False

        elif self.world.won:
            self.message.text = "LEVEL COMPLETE!"
            self.retry.opacity = 1
            self.retry.disabled = False

        else:
            self.message.text = ""


class DevilRunApp(App):

    def build(self):

        self.title = "DEVIL RUN: IMPOSSIBLE"

        manager = ScreenManager()

        manager.add_widget(
            MenuScreen(name="menu")
        )

        manager.add_widget(
            GameScreen(name="game")
        )

        return manager


if __name__ == "__main__":
    DevilRunApp().run()
