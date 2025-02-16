import tkinter as tk
from tkinter import Canvas, Tk, messagebox, simpledialog
from PIL import Image, ImageTk

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Шахматы")

        try:
            self.root.iconbitmap("./favicon.ico")
        except tk.TclError:
            print("Файл логотипа не найден.")

        self.root.configure(bg="#F0F0F0")
        self.was_resetting = False

        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'
        self.selected_piece = None
        self.possible_moves = []
        self.en_passant = None
        self.castling_rights = {'white': {'K': True, 'Q': True}, 'black': {'K': True, 'Q': True}}

        self.status_label = tk.Label(
            root,
            text=f"Ход: {self.current_player}",
            font=("Arial", 14, "bold"),
            fg="black",
            bg="#F0F0F0"
        )
        self.status_label.pack(side=tk.TOP, pady=(10, 5))

        self.cell_size = 70
        self.padding = 20
        self.board_size = self.cell_size * 8
        self.canvas = Canvas(
            root,
            width=self.board_size,
            height=self.board_size,
            bg="#F0F0F0",
            highlightthickness=0
        )
        self.canvas.pack(pady=(0, self.padding))

        try:
            logo_image = Image.open("logo.png")
            logo_image = logo_image.resize((125, 125), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            self.logo_label = tk.Label(root, image=self.logo_photo, bg="#F0F0F0")
            self.logo_label.place(relx=1.0, rely=1.0, anchor="se")
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")

        self.init_board()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)

    def init_board(self):
        self.board[0] = [
            {'type': 'R', 'color': 'black'},
            {'type': 'N', 'color': 'black'},
            {'type': 'B', 'color': 'black'},
            {'type': 'Q', 'color': 'black'},
            {'type': 'K', 'color': 'black'},
            {'type': 'B', 'color': 'black'},
            {'type': 'N', 'color': 'black'},
            {'type': 'R', 'color': 'black'}
        ]
        self.board[1] = [{'type': 'P', 'color': 'black'} for _ in range(8)]
        self.board[6] = [{'type': 'P', 'color': 'white'} for _ in range(8)]
        self.board[7] = [
            {'type': 'R', 'color': 'white'},
            {'type': 'N', 'color': 'white'},
            {'type': 'B', 'color': 'white'},
            {'type': 'Q', 'color': 'white'},
            {'type': 'K', 'color': 'white'},
            {'type': 'B', 'color': 'white'},
            {'type': 'N', 'color': 'white'},
            {'type': 'R', 'color': 'white'}
        ]

    def draw_square(self, row, col, color, outline="black"):
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        self.canvas.create_rectangle(
            x1, y1, x1 + self.cell_size, y1 + self.cell_size,
            fill=color, outline=outline
        )

    def draw_piece(self, row, col):
        piece = self.board[row][col]
        if piece:
            x = col * self.cell_size + self.cell_size // 2
            y = row * self.cell_size + self.cell_size // 2
            symbol = '♜♞♝♛♚♟' if piece['color'] == 'black' else '♖♘♗♕♔♙'
            types = ['R', 'N', 'B', 'Q', 'K', 'P']
            idx = types.index(piece['type']) if piece['type'] in types else 5
            self.canvas.create_text(
                x, y, text=symbol[idx],
                font=("Arial", self.cell_size//2, "bold"),
                fill=piece['color']
            )

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                base_color = "#DDB88C" if (row + col) % 2 == 0 else "#A66D4F"
                cell_color = base_color
                outline_color = "black"

                if (row, col) == self.selected_piece:
                    cell_color = "#7FFFD4"
                elif (row, col) in self.possible_moves:
                    piece = self.board[row][col]
                    if piece and piece['color'] != self.current_player:
                        cell_color = "#FF0000"
                    else:
                        cell_color = "#4CAF50"
                self.draw_square(row, col, cell_color, outline=outline_color)
                self.draw_piece(row, col)
        
        self.status_label.config(text=f"Ход: {self.current_player}")

    def handle_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= row < 8 and 0 <= col < 8:
            if not self.selected_piece:
                self.select_piece(row, col)
            else:
                self.move_piece(row, col)

    def select_piece(self, row, col):
        piece = self.board[row][col]
        if piece and piece['color'] == self.current_player:
            self.selected_piece = (row, col)
            self.possible_moves = self.get_valid_moves(row, col)
            self.draw_board()

    def move_piece(self, row, col):
        if (row, col) in self.possible_moves:
            current_player_before = self.current_player
            opponent_color = 'black' if current_player_before == 'white' else 'white'
            
            self.execute_move(row, col)
            self.check_promotion(row, col)
            
            if not self.find_king(opponent_color):
                self.game_over(f"Король {opponent_color} повержен! Победил {current_player_before}!")
                return
                
            if self.is_checkmate(opponent_color):
                self.game_over(f"Мат! Победа {current_player_before}!")
                return
                
            self.current_player = opponent_color
            
            if self.is_stalemate(self.current_player):
                self.game_over("Пат! Ничья!")

        self.selected_piece = None
        self.possible_moves = []
        
        if self.was_resetting:
            self.current_player = "white"
        self.was_resetting = False
        self.draw_board()

    def execute_move(self, to_row, to_col):
        from_row, from_col = self.selected_piece
        piece = self.board[from_row][from_col]

        temp_board = [row.copy() for row in self.board]
        temp_piece = temp_board[from_row][from_col]
        temp_board[from_row][from_col] = None
        temp_board[to_row][to_col] = temp_piece

        king_pos = self.find_king(piece['color'], temp_board)
        if king_pos and self.is_square_under_attack(king_pos[0], king_pos[1], piece['color'], temp_board):
            return

        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        if piece['type'] == 'K' and abs(from_col - to_col) == 2:
            self.handle_castling(to_row, to_col)
        
        if piece['type'] == 'P' and (to_row, to_col) == self.en_passant:
            self.board[from_row][to_col] = None
        
        if piece['type'] == 'K':
            self.castling_rights[piece['color']]['K'] = False
            self.castling_rights[piece['color']]['Q'] = False
        elif piece['type'] == 'R':
            if from_col == 0: 
                self.castling_rights[piece['color']]['Q'] = False
            elif from_col == 7: 
                self.castling_rights[piece['color']]['K'] = False
        
        if piece['type'] == 'P' and abs(from_row - to_row) == 2:
            self.en_passant = (to_row + (1 if piece['color'] == 'white' else -1), to_col)
        else:
            self.en_passant = None

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if not piece or piece['color'] != self.current_player:
            return []
        
        raw_moves = self.get_raw_moves(row, col)
        valid_moves = []
        for move in raw_moves:
            if not self.move_exposes_king(row, col, move[0], move[1]):
                valid_moves.append(move)
        return valid_moves

    def get_raw_moves(self, row, col):
        piece = self.board[row][col]
        if not piece: 
            return []
        
        if piece['type'] == 'P': 
            return self.get_pawn_moves(row, col, piece['color'])
        elif piece['type'] == 'N': 
            return self.get_knight_moves(row, col, piece['color'])
        elif piece['type'] == 'B': 
            return self.get_bishop_moves(row, col, piece['color'])
        elif piece['type'] == 'R': 
            return self.get_rook_moves(row, col, piece['color'])
        elif piece['type'] == 'Q': 
            return self.get_queen_moves(row, col, piece['color'])
        elif piece['type'] == 'K': 
            return self.get_king_moves(row, col, piece['color'])
        return []

    def get_pawn_moves(self, row, col, color):
        moves = []
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        
        if 0 <= row + direction < 8 and self.board[row + direction][col] is None:
            moves.append((row + direction, col))
            if row == start_row and self.board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))
        
        for dx in [-1, 1]:
            if 0 <= col + dx < 8 and 0 <= row + direction < 8:
                target = self.board[row + direction][col + dx]
                if target and target['color'] != color:
                    moves.append((row + direction, col + dx))
                elif (row + direction, col + dx) == self.en_passant:
                    moves.append((row + direction, col + dx))
        return moves

    def get_knight_moves(self, row, col, color):
        moves = []
        candidates = [
            (row+2, col+1), (row+2, col-1),
            (row-2, col+1), (row-2, col-1),
            (row+1, col+2), (row+1, col-2),
            (row-1, col+2), (row-1, col-2)
        ]
        for r, c in candidates:
            if 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if not target or target['color'] != color:
                    moves.append((r, c))
        return moves

    def get_bishop_moves(self, row, col, color):
        moves = []
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if not target:
                    moves.append((r, c))
                else:
                    if target['color'] != color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves

    def get_rook_moves(self, row, col, color):
        moves = []
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if not target:
                    moves.append((r, c))
                else:
                    if target['color'] != color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves

    def get_queen_moves(self, row, col, color):
        return self.get_rook_moves(row, col, color) + self.get_bishop_moves(row, col, color)

    def get_king_moves(self, row, col, color):
        moves = []
        candidates = [
            (row+1, col), (row-1, col),
            (row, col+1), (row, col-1),
            (row+1, col+1), (row+1, col-1),
            (row-1, col+1), (row-1, col-1)
        ]
        for r, c in candidates:
            if 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if not target or target['color'] != color:
                    moves.append((r, c))
        
        if self.castling_rights[color]['K']:
            if self.board[row][5] is None and self.board[row][6] is None:
                if not self.is_square_under_attack(row, 5, color) and not self.is_square_under_attack(row, 6, color):
                    moves.append((row, 6))
        if self.castling_rights[color]['Q']:
            if self.board[row][3] is None and self.board[row][2] is None and self.board[row][1] is None:
                if not self.is_square_under_attack(row, 3, color) and not self.is_square_under_attack(row, 2, color):
                    moves.append((row, 2))
        return moves

    def move_exposes_king(self, from_row, from_col, to_row, to_col):
        original_piece = self.board[to_row][to_col]
        moving_piece = self.board[from_row][from_col]
        
        temp_board = [row.copy() for row in self.board]
        temp_board[from_row][from_col] = None
        temp_board[to_row][to_col] = moving_piece
        
        king_pos = self.find_king(moving_piece['color'], temp_board)
        if not king_pos:
            return False
            
        return self.is_square_under_attack(king_pos[0], king_pos[1], moving_piece['color'], temp_board)

    def find_king(self, color, board=None):
        board = board or self.board
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece['type'] == 'K' and piece['color'] == color:
                    return (row, col)
        return None

    def is_square_under_attack(self, row, col, color, board=None):
        board = board or self.board
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece['color'] != color:
                    if piece['type'] == 'P':
                        pawn_dir = -1 if piece['color'] == 'white' else 1
                        if (r + pawn_dir == row and abs(c - col) == 1):
                            return True
                    else:
                        moves = self.get_possible_moves(r, c, board)
                        if (row, col) in moves:
                            return True
        return False

    def get_possible_moves(self, row, col, board=None):
        board = board or self.board
        piece = board[row][col]
        if not piece: 
            return []
        
        if piece['type'] == 'P':
            moves = []
            direction = -1 if piece['color'] == 'white' else 1
            for dx in [-1, 1]:
                attack_row = row + direction
                attack_col = col + dx
                if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                    if board[attack_row][attack_col] or (attack_row, attack_col) == self.en_passant:
                        moves.append((attack_row, attack_col))
            return moves
        elif piece['type'] == 'N': 
            return self.get_knight_moves(row, col, piece['color'])
        elif piece['type'] == 'B': 
            return self.get_bishop_moves(row, col, piece['color'])
        elif piece['type'] == 'R': 
            return self.get_rook_moves(row, col, piece['color'])
        elif piece['type'] == 'Q': 
            return self.get_queen_moves(row, col, piece['color'])
        elif piece['type'] == 'K': 
            return self.get_king_moves(row, col, piece['color'])
        return []

    def is_checkmate(self, color):
        if not self.is_king_in_check(color):
            return False
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece['color'] == color:
                    raw_moves = self.get_raw_moves(row, col)
                    for move in raw_moves:
                        if not self.move_exposes_king(row, col, move[0], move[1]):
                            return False
        return True

    def is_stalemate(self, color):
        if self.is_king_in_check(color):
            return False
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece['color'] == color:
                    if self.get_valid_moves(row, col):
                        return False
        return True

    def handle_castling(self, to_row, to_col):
        from_row, from_col = self.selected_piece
        rook_col = 7 if to_col > from_col else 0
        new_rook_col = 5 if to_col > from_col else 3
        
        rook = self.board[from_row][rook_col]
        self.board[from_row][new_rook_col] = rook
        self.board[from_row][rook_col] = None

    def check_promotion(self, row, col):
        piece = self.board[row][col]
        if piece and piece['type'] == 'P' and row in (0, 7):
            choice = simpledialog.askstring(
                "Превращение пешки", 
                "Выберите фигуру (Q/R/B/N):", 
                parent=self.root
            )
            if choice and choice.upper() in ['Q', 'R', 'B', 'N']:
                piece['type'] = choice.upper()

    def game_over(self, message):
        play_again = messagebox.askyesno("Игра окончена", f"{message}\nНовая игра?")
        if play_again:
            self.reset_game()
        else:
            self.root.quit()

    def reset_game(self):
        self.was_resetting = True
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.init_board()
        self.current_player = 'white'
        self.selected_piece = None
        self.possible_moves = []
        self.en_passant = None
        self.castling_rights = {'white': {'K': True, 'Q': True}, 'black': {'K': True, 'Q': True}}
        
        self.draw_board()
        self.status_label.config(text=f"Ход: {self.current_player}")
        self.root.update_idletasks()

    def is_king_in_check(self, color):
        king_pos = self.find_king(color)
        return self.is_square_under_attack(king_pos[0], king_pos[1], color)

if __name__ == "__main__":
    root = Tk()
    ChessGame(root)
    root.mainloop()