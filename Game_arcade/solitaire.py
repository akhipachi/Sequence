import arcade
from client import Client, Backend

# Screen title and size
SCREEN_WIDTH = 940
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sequence"

# Constants for sizing
CARD_SCALE = 0.6

# How big are the cards?
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

# How big is the mat we'll place the card on?
MAT_PERCENT_OVERSIZE = 1.25
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)

# How much space do we leave as a gap between the mats?
# Done as a percent of the mat size.
VERTICAL_MARGIN_PERCENT = 0.10
HORIZONTAL_MARGIN_PERCENT = 0.10

# The Y of the bottom row (2 piles)
BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The X of where to start putting things on the left side
START_X = MAT_WIDTH / 2 + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# The Y of the top row (4 piles)
TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The Y of the middle row (7 piles)
MIDDLE_Y = TOP_Y - MAT_HEIGHT - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT - 30
MIDDLE_Y2 = MIDDLE_Y - MAT_HEIGHT - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# How far apart each pile goes
X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# Card constants
CARD_VALUES = ["A", "2", "3", "4", "5",
               "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]

# If we fan out cards stacked on each other, how far apart to fan them?
CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3

# Constants that represent "what pile is what" for the game
PILE_COUNT = 20
BOTTOM_FACE_DOWN_PILE = 0
BOTTOM_FACE_UP_PILE = 1
PLAY_PILE_1 = 2
PLAY_PILE_2 = 3
PLAY_PILE_3 = 4
PLAY_PILE_4 = 5
PLAY_PILE_5 = 6
PLAY_PILE_6 = 7
PLAY_PILE_7 = 8
PLAY_PILE_8 = 9
PLAY_PILE_9 = 10
PLAY_PILE_10 = 11
PLAY_PILE_11 = 12
PLAY_PILE_12 = 13
PLAY_PILE_13 = 14
TOP_PILE_1 = 15
TOP_PILE_2 = 16
TOP_PILE_3 = 17
TOP_PILE_4 = 18
JOCKER_PILE = 19
BUTTON = 20


class Card(arcade.Sprite):
    """ Card sprite """

    def __init__(self, suit, value, scale=1):
        """ Card constructor """

        # Attributes for suit and value
        self.suit = suit
        self.value = value

        # Image to use for the sprite when face up
        self.image_file_name = f":resources:images/cards/card{self.suit}{self.value}.png"

        # Call the parent
        super().__init__(self.image_file_name, scale)

    def get_value(self):
        numbers = {'A': 1, 'J': 11, 'Q': 12, 'K': 13}
        if self.value in numbers:
            return numbers[self.value]
        else:
            return int(self.value)


class MenuView(arcade.View):
    """ Class that manages the 'menu' view. """

    def on_show(self):
        """ Called when switching to this view"""
        arcade.set_background_color(arcade.color.WHITE)
        self.id = Backend.get_instance().join()

    def on_draw(self):
        """ Draw the menu """
        arcade.start_render()
        arcade.draw_text("Click to start the game\nID: "+str(self.id), SCREEN_WIDTH/2, SCREEN_HEIGHT / 2,
                         arcade.color.BLACK, font_size=30, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ Use a mouse press to advance to the 'game' view. """
        game_view = MyGame()
        game_view.setup()
        self.window.show_view(game_view)


class EndView(arcade.View):
    """ Class that manages the 'menu' view. """

    def __init__(self, id):
        super().__init__()
        self.id = id

    def on_show(self):
        """ Called when switching to this view"""
        arcade.set_background_color(arcade.color.RED)

    def on_draw(self):
        """ Draw the menu """
        arcade.start_render()
        arcade.draw_text("Game won by ID: "+str(self.id), SCREEN_WIDTH/2, SCREEN_HEIGHT / 2,
                         arcade.color.BLACK, font_size=30, anchor_x="center")


class MyGame(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = None

        arcade.set_background_color(arcade.color.AMAZON)

        # List of cards we are dragging with the mouse
        self.held_cards = None

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = None

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list = None

        # Create a list of lists, each holds a pile of cards.
        self.piles = None

        self.natural_set = False
        self.jocker = None

        self.backend = Backend.get_instance()
        self.id = self.backend.id
        self.turn = False
        self.deck = 0

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # List of cards we are dragging with the mouse
        self.held_cards = []

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = []

        # ---  Create the mats the cards go on.

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Create the mats for the bottom face down and face up piles
        pile = arcade.SpriteSolidColor(
            MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X, TOP_Y
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(
            MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X + X_SPACING, TOP_Y
        self.pile_mat_list.append(pile)

        # Create the seven middle piles
        for i in range(8):
            pile = arcade.SpriteSolidColor(
                MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + i * X_SPACING, MIDDLE_Y
            self.pile_mat_list.append(pile)

        # Second middle row
        for i in range(5):
            pile = arcade.SpriteSolidColor(
                MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + (i+1) * X_SPACING, MIDDLE_Y2
            self.pile_mat_list.append(pile)

        # Create the top "play" piles
        for i in range(4):
            pile = arcade.SpriteSolidColor(
                MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + (i+4) * X_SPACING, TOP_Y
            self.pile_mat_list.append(pile)

        # Jocker pile
        pile = arcade.SpriteSolidColor(
            MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.YELLOW)
        pile.position = START_X + 2 * X_SPACING + 50,  TOP_Y
        self.pile_mat_list.append(pile)

        # Show Button
        button = arcade.SpriteSolidColor(
            MAT_WIDTH//2, MAT_HEIGHT//4, arcade.csscolor.GREY)
        button.position = START_X + 3 * X_SPACING,  BOTTOM_Y - 30
        self.pile_mat_list.append(button)

        # --- Create, shuffle, and deal the cards

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = arcade.SpriteList()

        # Cards list fetched from API
        cards = self.backend.start()
        self.backend.communication()

        # Create every card
        for i in cards:
            card = Card(i.split(' ')[1], i.split(' ')[0], CARD_SCALE)
            card.position = START_X, BOTTOM_Y
            self.card_list.append(card)

        # Create a list of lists, each holds a pile of cards.
        self.piles = [[] for _ in range(PILE_COUNT)]

        # # Put all the cards in the bottom face-down pile
        for card in self.card_list:
            self.piles[BOTTOM_FACE_DOWN_PILE].append(card)

        # - Pull from that pile into the middle piles, all face-down
        # Loop for each pile
        for pile_no in range(PLAY_PILE_1, PLAY_PILE_13 + 1):
            # Deal proper number of cards for that pile
            for j in range(1):
                # Pop the card off the deck we are dealing from
                card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                # Put in the proper pile
                self.piles[pile_no].append(card)
                # Move card to same position as pile we just put it in
                card.position = self.pile_mat_list[pile_no].position
                # Put on top in draw order
                self.pull_to_top(card)

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        arcade.start_render()

        # Draw the mats the cards go on to
        self.pile_mat_list.draw()
        arcade.draw_text('SHOW', START_X + 3 * X_SPACING, BOTTOM_Y-30,
                         arcade.color.BLACK, font_size=14,
                         width=MAT_WIDTH//2, align="center",
                         anchor_x="center", anchor_y="center")

        # Draw the cards
        self.card_list.draw()

        # self.backend.communication()

    def pull_to_top(self, card):
        """ Pull card to top of rendering order (last to render, looks on-top) """
        # Find the index of the card
        index = self.card_list.index(card)
        # Loop and pull all the other cards down towards the zero end
        for i in range(index, len(self.card_list) - 1):
            self.card_list[i] = self.card_list[i + 1]
        # Put this card at the right-side/top/size of list
        self.card_list[len(self.card_list) - 1] = card

    def validate(self):
        self.natural_set = False
        set_4 = False
        sets = 0
        for pile in range(TOP_PILE_1, TOP_PILE_4+1):
            cards = self.piles[pile]
            if len(cards) > 0 and len(cards) <= 4:
                same_value = True
                same_suit = True
                sequence = True
                values = []
                suits = []
                jockers = 0
                for card in cards:
                    if not self.jocker == None:
                        if self.jocker == card.value:
                            jockers += 1
                            continue
                    values.append(card.get_value())
                    suits.append(card.suit)
                values.sort()
                for i in range(1, len(values)):
                    if not values[i] == values[i-1]:
                        same_value = False
                    if not suits[i] == suits[i-1]:
                        same_suit = False
                    if not values[i] == values[i-1]+1:
                        if values[i] >= values[i-1]+jockers:
                            jockers -= 1
                        else:
                            sequence = False

                if same_value and not same_suit:
                    sets += 1
                if same_suit and sequence and not same_value:
                    sets += 1
                    self.natural_set = True
                    if len(cards) == 4:
                        set_4 = True

        if sets == 4 and set_4 and self.natural_set:
            return True
        else:
            return False

    def update(self, delta_time):
        # Message to the Server
        self.backend.client.message()
        # Reading message from server
        if self.backend.read.queue:
            # If revieved any msg
            msg = self.backend.read.get()
            if 'play' in msg or 'card' in msg:
                # Putting the recieved card into the deck
                i = msg.split(':')[1]
                card = Card(i.split(' ')[1], i.split(' ')[0], CARD_SCALE)
                card.position = self.pile_mat_list[BOTTOM_FACE_UP_PILE].position
                self.card_list.append(card)
                for cards in self.piles[BOTTOM_FACE_UP_PILE]:
                    self.remove_card_from_pile(cards)
                    cards.remove_from_sprite_lists()
                self.piles[BOTTOM_FACE_UP_PILE].append(card)
                self.turn = True
            if 'jocker' in msg:
                i = msg.split(':')[1]
                card = Card(i.split(' ')[1], i.split(' ')[0], CARD_SCALE)
                card.position = self.pile_mat_list[JOCKER_PILE].position
                self.card_list.append(card)
                self.piles[JOCKER_PILE].append(card)
                self.jocker = card.value

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """

        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)
        piles = arcade.get_sprites_at_point((x, y), self.pile_mat_list)
        if piles and self.pile_mat_list.index(piles[0]) == BOTTOM_FACE_DOWN_PILE:
            if self.turn and self.deck == 0 and len(self.piles[BOTTOM_FACE_UP_PILE]) == 1:
                self.backend.write.put('get')
                self.deck = 1

        if piles and self.pile_mat_list.index(piles[0]) == JOCKER_PILE:
            # Remember to add self.turn condition
            if len(self.piles[JOCKER_PILE]) == 0 and not self.turn:
                self.validate()
                if self.natural_set:
                    self.backend.write.put('jocker')
            return

        if piles and self.pile_mat_list.index(piles[0]) == BUTTON:
            result = self.validate()
            if result and self.turn:
                self.backend.write.put('won')
                end = EndView(self.id)
                self.window.show_view(end)
                # self.backend.client.s.close()
                self.backend.end()

        # Have we clicked on a card?
        if len(cards) > 0:

            # Might be a stack of cards, get the top one
            primary_card = cards[-1]
            # Figure out what pile the card is in
            pile_index = self.get_pile_for_card(primary_card)

            # All other cases, grab the face-up card we are clicking on
            self.held_cards = [primary_card]
            # Save the position
            self.held_cards_original_position = [self.held_cards[0].position]
            # Put on top in drawing order
            self.pull_to_top(self.held_cards[0])

            # Is this a stack of cards? If so, grab the other cards too
            card_index = self.piles[pile_index].index(primary_card)
            for i in range(card_index + 1, len(self.piles[pile_index])):
                card = self.piles[pile_index][i]
                self.held_cards.append(card)
                self.held_cards_original_position.append(card.position)
                self.pull_to_top(card)

    def remove_card_from_pile(self, card):
        """ Remove card from whatever pile it was in. """
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def get_pile_for_card(self, card):
        """ What pile is this card in? """
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def move_card_to_new_pile(self, card, pile_index):
        """ Move the card to a new pile """
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """

        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return

        # Find the closest pile, in case we are in contact with more than one
        pile, distance = arcade.get_closest_sprite(
            self.held_cards[0], self.pile_mat_list)
        reset_position = True

        # See if we are in contact with the closest pile
        if arcade.check_for_collision(self.held_cards[0], pile):

            # What pile is it?
            pile_index = self.pile_mat_list.index(pile)

            #  Is it the same pile we came from?
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                # If so, who cares. We'll just reset our position.
                pass

            # Is it on a middle play pile?
            elif PLAY_PILE_1 <= pile_index <= PLAY_PILE_13:
                # Are there already cards there?
                if len(self.piles[pile_index]) > 0:
                    # Move cards to proper position
                    top_card = self.piles[pile_index][-1]
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = top_card.center_x, \
                            top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)
                else:
                    # Are there no cards in the middle play pile?
                    for i, dropped_card in enumerate(self.held_cards):
                        # Move cards to proper position
                        dropped_card.position = pile.center_x, \
                            pile.center_y - CARD_VERTICAL_OFFSET * i

                for card in self.held_cards:
                    # Cards are in the right position, but we need to move them to the right list
                    self.move_card_to_new_pile(card, pile_index)

                # Success, don't reset position of cards
                reset_position = False

            # Release on top play pile? And only one card held?
            elif TOP_PILE_1 <= pile_index <= TOP_PILE_4:
                # Move position of card to pile
                # Move card to card list
                for card in self.held_cards:
                    card.position = pile.position
                    self.move_card_to_new_pile(card, pile_index)

                reset_position = False

            elif BOTTOM_FACE_UP_PILE == pile_index and len(self.held_cards) == 1 and self.turn:
                self.held_cards[0].position = pile.position
                # Move card to card list
                for card in self.held_cards:
                    self.remove_card_from_pile(card)
                    self.backend.write.put('done:'+card.value+' '+card.suit)
                    card.remove_from_sprite_lists()
                self.turn = False
                self.deck = 0
                reset_position = False

        if reset_position:
            # Where-ever we were dropped, it wasn't valid. Reset the each card's position
            # to its original spot.
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # We are no longer holding cards
        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()
    backend = Backend.get_instance()
    backend.end()


if __name__ == "__main__":
    main()
