## simpie solitaire card game
from functools import partial

from cards import Deck
from client import Backend
from exceptions import ErrorResponse
from games import Sequence
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform
from menu import SmartStartMenu

# main app


class Solitaire(App):
    game = ObjectProperty(None)
    font_size = NumericProperty(12)
    menu_height = NumericProperty(0.06 * Window.height)
    pad_by = NumericProperty(0.007 * Window.height)

    # initialise config file
    def build_config(self, config):
        config.setdefaults("piles", {})
        config.setdefaults(
            "settings",
            {
                "fps": 10,
                "font_size": 16,
                "help_font_size": 14,
                "popup_width": 0.4,
                "popup_height": 0.6,
            },
        )
        config.setdefaults("game", {"name": "Sequence", "won": False, "deck": []})
        config.setdefaults("Sequence", {"played": 0, "won": 0})
        config.setdefaults(
            "piles",
            {
                "tableau0": [],
                "tableau1": [],
                "tableau2": [],
                "tableau3": [],
                "tableau4": [],
                "tableau5": [],
                "tableau6": [],
                "tableau7": [],
                "tableau8": [],
                "tableau9": [],
                "tableau10": [],
                "tableau12": [],
                "foundation0": [],
                "foundation1": [],
                "foundation2": [],
                "foundation3": [],
                "waste0": [],
                "waste1": [],
                "jocker0": [],
            },
        )
        config.write()

    # settings panel
    def build_settings(self, settings):
        settings.add_json_panel(
            "Solitaire",
            self.config,
            data="""[
            { "type": "numeric", "title": "FPS",
              "desc": "animation frames per second",
              "section": "settings", "key": "fps" },
            { "type": "numeric", "title": "Font size",
              "desc": "size of font for main screen",
              "section": "settings", "key": "font_size" },
            { "type": "numeric", "title": "Help font size",
              "desc": "size of font for help text",
              "section": "settings", "key": "help_font_size" },
            { "type": "numeric", "title": "Popup width",
              "desc": "width of popup as fraction of screen",
              "section": "settings", "key": "popup_width" },
            { "type": "numeric", "title": "Popup height",
              "desc": "height of popup as fraction of screen",
              "section": "settings", "key": "popup_height" }
        ]""",
        )

    # user updated config
    def on_config_change(self, config, section, key, value):
        if config is self.config and section == "settings" and key == "font_size":
            self.font_size = int(value)

    # initialise new game
    def set_game(self, name):
        self.game = Sequence(
            root=self.root, on_move=self.on_move, menu_size=self.menu_height
        )
        self.game.build()
        conf = self.config
        if not conf.has_section(name):
            conf.add_section(name)
            conf.set(name, "played", 1)
            conf.set(name, "won", 0)
        conf.write()

    # shuffle the deck
    def shuffle(self, cards):
        self.deck = Deck(cards)
        self.deck.rewind()
        self.config.set("game", "won", False)
        self.config.set(self.game.name, "played", self.getval("played") + 1)
        self.config.write()

    # initialise the board
    def build(self):
        self.started = False
        self.icon = "icon.png"
        conf = self.config
        name = conf.get("game", "name")
        self.font_size = conf.getint("settings", "font_size")
        Logger.info("Cards: build game %s font size %d" % (name, self.font_size))
        self.set_game(name)
        self._starting = False
        if conf.has_option("game", "deck"):
            # restore where we left off
            self.deck = Deck(self.game.decks, config=conf)
            for pile in self.game.all_piles():
                pile.load(conf)
        else:
            # first time initialisation
            self.shuffle()
            for pile in self.game.all_piles():
                self.game.start(pile, self.deck)
        if platform == "android":
            from android.permissions import Permission, request_permissions

            request_permissions(
                [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
            )
            Window.bind(on_keyboard=self.hook_keyboard)
        Window.on_resize = self.resize
        delay = self.framerate()
        Logger.info("Cards: resize delay = %g", delay)
        self.resize_event = Clock.create_trigger(
            lambda dt: self.game.do_resize(), delay
        )
        self.id = None
        self.backend = None
        self.start_menu()

    def start_menu(self):
        sm = SmartStartMenu()
        sm.buildUp()

        def check_button(obj):
            if sm.buttonText == "Join":
                self.backend = Backend.get_instance()
                self.backend.host = "http://" + sm.txt.text
                try:
                    self.id = self.backend.join()
                except Exception as e:
                    if isinstance(e, ErrorResponse):
                        text = str(e)
                    else:
                        text = "Invalid IP Address"
                    self.error_popup(text)
            if sm.buttonText == "Start" and self.id is not None:
                self.root.remove_widget(sm)
                try:
                    self.new_game()
                except Exception as e:
                    self.start_menu()
                    self.error_popup(str(e))

        sm.bind(on_button_release=check_button)
        self.root.add_widget(sm)

    def error_popup(self, text):
        width = self.config.getfloat("settings", "popup_width") * Window.width / 2
        height = self.config.getfloat("settings", "popup_height") * Window.height / 3
        popup = Popup(
            title="Error",
            content=Label(text=text),
            size_hint=(None, None),
            size=(width, height),
        )
        popup.open()

    # bind android back key
    def hook_keyboard(self, window, key, *args):
        if key == 27:
            self.undo()
            return True

    # called on window resize
    def resize(self, width, height):
        if self.resize_event.is_triggered:
            self.resize_event.cancel()
        self.resize_event()

    # draws the cards on new game - animate this
    # have some hacky logic here so this is not called while it is running
    def start(self, index, *args):
        if index == 0:
            self._starting = True
        pile = (self.game.tableau() + self.game.waste() + self.game.jocker())[index]
        self.game.start(pile, self.deck)
        if (
            index + 1
            < self.game.num_tableau + self.game.num_waste + self.game.num_jocker
        ):
            Clock.schedule_once(partial(self.start, index + 1), self.framerate())
        else:
            self._starting = False

    def play_sound(self):
        self.sound = SoundLoader.load("play.wav")
        self.sound.play()

    def control(self, dt):
        if self.backend.read.queue:
            # If revieved any msg
            msg = self.backend.read.get()
            if "play" in msg or "card" in msg:
                # Putting the recieved card into the deck
                i = msg.split(":")[1]
                if self.game.piles["waste"][1].size() != 0:
                    self.game.piles["waste"][1].remove_cards()
                self.game.add_to_pile(i, "waste", 1)
                self.game.turn = True
                if "play" in msg:
                    self.play_sound()

            if "jocker" in msg:
                i = msg.split(":")[1]
                self.game.piles["jocker"][0].clear(1)
                self.game.add_to_pile(i, "jocker", 0)
                rank = i.split(" ")[0]
                numbers = {"A": 1, "J": 11, "Q": 12, "K": 13}
                if rank in numbers:
                    self.game.jocker_rank = numbers[rank]
                else:
                    self.game.jocker_rank = int(rank)
            if "won" in msg:
                i = msg.split(":")[1]
                self.game.won = True
                self.game.winner = int(i)
                self.check_score()

    def skip(self):
        if not self.started:
            return
        if self.game.piles["waste"][1].size() != 0 and self.game.turn:
            top = self.game.piles["waste"][1].widgets[-1]
            rank = top.images[0].card.rank
            suit = top.images[0].card.suit
            suits = {"c": "Clubs", "h": "Hearts", "s": "Spades", "d": "Diamonds"}
            suit = suits[suit]
            self.backend.write.put("done:" + str(rank) + " " + suit)
            self.game.turn = False
            self.game.cards = 0

    def quit(self):
        if self.backend is not None:
            self.backend.end()
        self.get_running_app().stop()
        # exit()

    def validate(self):
        if not self.started:
            return
        self.game.natural_set = False
        set_4 = False
        sets = 0
        for pile in self.game.piles["foundation"]:
            if len(pile.widgets) > 1:
                cards = pile.widgets[1].images
                if len(cards) >= 3 and len(cards) <= 4:
                    same_value = True
                    same_suit = True
                    sequence = True
                    values = []
                    suits = []
                    jockers = 0
                    for card in cards:
                        if not self.game.jocker_rank == None:
                            if self.game.jocker_rank == card.card.rank:
                                jockers += 1
                                continue
                        values.append(card.card.rank)
                        suits.append(card.card.suit)
                    values.sort()
                    for i in range(1, len(values)):
                        if not values[i] == values[i - 1]:
                            same_value = False
                        if not suits[i] == suits[i - 1]:
                            same_suit = False
                        if not values[i] == values[i - 1] + 1:
                            if values[i] >= values[i - 1] + jockers:
                                jockers -= 1
                            else:
                                sequence = False

                    if same_value and not same_suit and len(set(suits)) == len(suits):
                        jockers -= len(cards) - len(values)
                        sets += 1
                        if len(cards) == 4:
                            set_4 = True
                    if same_suit and sequence and not same_value:
                        sets += 1
                        if self.game.jocker_rank not in values:
                            self.game.natural_set = True
                        if len(cards) == 4:
                            set_4 = True
        if (
            sets == 4
            and set_4
            and self.game.natural_set
            and self.game.turn
            or jockers >= 2
        ):
            self.game.won = True
            self.game.winner = self.id
            self.backend.write.put("won")
            self.check_score()
            return True
        else:
            return False

    def jocker(self):
        # should change this to not
        if not self.started:
            return
        if self.game.jocker_rank is None:
            self.validate()
            if self.game.natural_set:
                self.backend.write.put("jocker")

    # app button callbacks
    def new_game(self):
        if self._starting:
            return
        cards = self.backend.start()
        self.game.clear(1)
        self.shuffle(cards)
        self.start(0)
        self.backend.communication()
        self.started = True
        self.schedule = Clock.schedule_interval(self.control, 0.5)

    def stats(self, title=""):
        if not title:
            title = "%s statistics" % self.game.name
        data = [
            "played",
            self.getval("played", "str"),
            "won",
            self.getval("won", "str"),
        ]
        self.popup = self.new_popup(title, (0.4, 0.1), data, self.font_size)
        self.popup.open()

    def new_popup(self, title, col_width, data, font_size):
        width = self.config.getfloat("settings", "popup_width") * Window.width
        height = self.config.getfloat("settings", "popup_height") * Window.height
        popup = AppPopup(title=title, size=(width, height))
        columns = len(col_width)
        popup.body.cols = columns
        fsize = str(font_size) + "sp"
        for i, el in enumerate(data):
            w = width * col_width[i % columns]
            popup.body.add_widget(Label(text=el, text_size=(w, None), font_size=fsize))
        return popup

    def dismiss(self):
        Clock.unschedule(self.schedule)
        self.backend.end()
        self.game.clear(1)
        self.build()
        self.popup.dismiss()

    # update stats and show popup on completed game
    def check_score(self):
        conf = self.config
        if self.game.won:
            if self.game.winner == self.id:
                name = self.game.name
                won = self.getval("won")
                conf.set(name, "won", won + 1)
                conf.write()
                self.stats(title="Congratulations! - you won :)")
                return True
            else:
                self.stats(title="Oh no! - player " + str(self.game.winner) + " won :(")

    # get value from config file
    def getval(self, key, typ="int"):
        if typ == "int":
            val = self.config.getint(self.game.name, key)
        elif typ == "float":
            val = self.config.getfloat(self.game.name, key)
        else:
            val = self.config.get(self.game.name, key)
        return val

    # logs the history and, if callback is set then defer drawing to animate
    def on_move(self, orig, dest, num, **args):
        do_callback = False
        if "callback" in args:
            do_callback = args["callback"] is not False
            callback = args["callback"]
            del args["callback"]
        args["src"] = orig.pid()
        args["dst"] = dest.pid()
        args["n"] = num
        # do it
        if do_callback:
            Clock.schedule_once(partial(self.draw, args, callback), self.framerate())
        else:
            self.do_move(args)

    # draw move from timer event
    def draw(self, move, callback, *args):
        self.do_move(move)
        if callback:
            callback()

    # execute move and update state

    def do_move(self, move, reverse=False, replay=False):
        orig, dest = self.game.do_move(move, reverse)
        # user callback
        if not replay:
            self.game.on_moved(move)

    # callbacks to allow android save and resume
    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def framerate(self):
        return 1.0 / self.config.getfloat("settings", "fps")


# defined in kv file


class AppPopup(Popup):
    pass


if __name__ == "__main__":
    try:
        Solitaire().run()
    finally:
        Backend.get_instance().end()
