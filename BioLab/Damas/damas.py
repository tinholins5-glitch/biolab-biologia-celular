import sys

import pygame


BOARD_SIZE = 8
WINDOW_WIDTH = 920
WINDOW_HEIGHT = 720
BOARD_LEFT = 54
BOARD_TOP = 74
SQUARE_SIZE = 72
BOARD_PIXELS = BOARD_SIZE * SQUARE_SIZE

LIGHT_SQUARE = (239, 220, 184)
DARK_SQUARE = (139, 91, 55)
BACKGROUND = (24, 31, 42)
PANEL = (34, 43, 57)
TEXT = (246, 241, 231)
MUTED_TEXT = (174, 183, 194)
GOLD = (244, 190, 74)
HIGHLIGHT = (77, 178, 126)
CAPTURE = (224, 92, 80)
WHITE_PIECE = (245, 239, 223)
BLACK_PIECE = (37, 42, 50)


class CheckersGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for row in range(3):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.board[row][col] = make_piece("black")
        for row in range(5, BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.board[row][col] = make_piece("white")
        self.turn = "white"
        self.selected = None
        self.valid_moves = []
        self.must_continue = False
        self.winner = None
        self.message = "Vez das brancas"

    @staticmethod
    def opponent(player):
        return "black" if player == "white" else "white"

    @staticmethod
    def directions(piece):
        if piece["king"]:
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        forward = -1 if piece["color"] == "white" else 1
        return [(forward, -1), (forward, 1)]

    @staticmethod
    def capture_directions():
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def get_moves(self, row, col, captures_only=False):
        piece = self.board[row][col]
        if piece is None:
            return []
        moves = []
        directions = self.capture_directions() if captures_only else self.directions(piece)
        for row_step, col_step in directions:
            next_row, next_col = row + row_step, col + col_step
            if not (0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE):
                continue
            if self.board[next_row][next_col] is None and not captures_only:
                moves.append({"to": (next_row, next_col), "capture": None})
            elif self.board[next_row][next_col] is not None:
                jumped = self.board[next_row][next_col]
                landing_row, landing_col = next_row + row_step, next_col + col_step
                if (jumped["color"] != piece["color"]
                        and 0 <= landing_row < BOARD_SIZE
                        and 0 <= landing_col < BOARD_SIZE
                        and self.board[landing_row][landing_col] is None):
                    moves.append({"to": (landing_row, landing_col), "capture": (next_row, next_col)})
        return moves

    def player_has_capture(self, color):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece["color"] == color and self.get_moves(row, col, True):
                    return True
        return False

    def all_moves(self, color):
        captures = self.player_has_capture(color)
        moves = {}
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    piece_moves = self.get_moves(row, col, captures)
                    if piece_moves:
                        moves[(row, col)] = piece_moves
        return moves

    def select(self, position):
        if self.winner:
            return
        row, col = position
        if self.selected and any(move["to"] == position for move in self.valid_moves):
            self.move(position)
            return
        piece = self.board[row][col]
        if piece and piece["color"] == self.turn:
            available = self.all_moves(self.turn)
            if position in available:
                self.selected = position
                self.valid_moves = available[position]
                return
        self.selected = None
        self.valid_moves = []

    def move(self, destination):
        start_row, start_col = self.selected
        piece = self.board[start_row][start_col]
        selected_move = next(move for move in self.valid_moves if move["to"] == destination)
        end_row, end_col = destination
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        if selected_move["capture"]:
            captured_row, captured_col = selected_move["capture"]
            self.board[captured_row][captured_col] = None

        promoted = ((piece["color"] == "white" and end_row == 0)
                    or (piece["color"] == "black" and end_row == BOARD_SIZE - 1))
        if promoted:
            piece["king"] = True

        if selected_move["capture"]:
            next_captures = self.get_moves(end_row, end_col, True)
            if next_captures:
                self.selected = destination
                self.valid_moves = next_captures
                self.must_continue = True
                self.message = "Continue a captura"
                return

        self.must_continue = False
        self.selected = None
        self.valid_moves = []
        self.turn = self.opponent(self.turn)
        if not self.all_moves(self.turn):
            self.winner = self.opponent(self.turn)
            self.message = "Brancas venceram!" if self.winner == "white" else "Pretas venceram!"
        else:
            self.message = "Vez das brancas" if self.turn == "white" else "Vez das pretas"


def make_piece(color, king=False):
    return {"color": color, "king": king}


def draw_text(surface, font, text, position, color=TEXT):
    surface.blit(font.render(text, True, color), position)


def draw_game(screen, game, title_font, body_font, small_font):
    screen.fill(BACKGROUND)
    draw_text(screen, title_font, "DAMAS", (BOARD_LEFT, 18))
    draw_text(screen, small_font, "Dois jogadores no mesmo notebook", (BOARD_LEFT + 178, 29), MUTED_TEXT)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            square_color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            rect = pygame.Rect(BOARD_LEFT + col * SQUARE_SIZE, BOARD_TOP + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, square_color, rect)

    if game.selected:
        row, col = game.selected
        selected_rect = pygame.Rect(BOARD_LEFT + col * SQUARE_SIZE, BOARD_TOP + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, GOLD, selected_rect, 5)
        for move in game.valid_moves:
            move_row, move_col = move["to"]
            center = (BOARD_LEFT + move_col * SQUARE_SIZE + SQUARE_SIZE // 2,
                      BOARD_TOP + move_row * SQUARE_SIZE + SQUARE_SIZE // 2)
            color = CAPTURE if move["capture"] else HIGHLIGHT
            pygame.draw.circle(screen, color, center, 12)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = game.board[row][col]
            if piece is None:
                continue
            center = (BOARD_LEFT + col * SQUARE_SIZE + SQUARE_SIZE // 2,
                      BOARD_TOP + row * SQUARE_SIZE + SQUARE_SIZE // 2)
            fill = WHITE_PIECE if piece["color"] == "white" else BLACK_PIECE
            edge = (205, 72, 64) if piece["color"] == "black" else (112, 78, 44)
            pygame.draw.circle(screen, (19, 22, 29), center, 29)
            pygame.draw.circle(screen, fill, center, 26)
            pygame.draw.circle(screen, edge, center, 26, 3)
            if piece["king"]:
                pygame.draw.circle(screen, GOLD, center, 13, 3)
                draw_text(screen, small_font, "D", (center[0] - 7, center[1] - 9), GOLD)

    panel_x = BOARD_LEFT + BOARD_PIXELS + 32
    pygame.draw.rect(screen, PANEL, (panel_x, BOARD_TOP, 230, BOARD_PIXELS), border_radius=10)
    draw_text(screen, small_font, "STATUS", (panel_x + 20, BOARD_TOP + 22), MUTED_TEXT)
    status_color = GOLD if not game.winner else HIGHLIGHT
    draw_text(screen, body_font, game.message, (panel_x + 20, BOARD_TOP + 48), status_color)
    draw_text(screen, small_font, "Regras", (panel_x + 20, BOARD_TOP + 112), MUTED_TEXT)
    rules = ["Captura e obrigatoria", "D = peca promovida", "Capturas continuam", "ate nao haver outra"]
    for index, rule in enumerate(rules):
        draw_text(screen, small_font, rule, (panel_x + 20, BOARD_TOP + 140 + index * 24))

    button_rect = pygame.Rect(panel_x + 20, BOARD_TOP + BOARD_PIXELS - 62, 190, 40)
    pygame.draw.rect(screen, GOLD, button_rect, border_radius=6)
    draw_text(screen, small_font, "R  reiniciar partida", (button_rect.x + 28, button_rect.y + 11), BACKGROUND)
    draw_text(screen, small_font, "Clique uma peca e depois o destino", (BOARD_LEFT, BOARD_TOP + BOARD_PIXELS + 18), MUTED_TEXT)


def main():
    pygame.init()
    pygame.display.set_caption("Damas - dois jogadores")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    title_font = pygame.font.Font(None, 42)
    body_font = pygame.font.Font(None, 25)
    small_font = pygame.font.Font(None, 20)
    game = CheckersGame()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                board_x = mouse_x - BOARD_LEFT
                board_y = mouse_y - BOARD_TOP
                if 0 <= board_x < BOARD_PIXELS and 0 <= board_y < BOARD_PIXELS:
                    game.select((board_y // SQUARE_SIZE, board_x // SQUARE_SIZE))

        draw_game(screen, game, title_font, body_font, small_font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
