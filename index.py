import tkinter as tk
from tkinter import Canvas, Tk, messagebox
from PIL import Image, ImageTk

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Шахматы")
        try:
            self.root.iconbitmap("./favicon.ico")  # Укажите путь к вашему файлу .ico
        except tk.TclError:
            print("Файл логотипа не найден или формат не поддерживается.")
        
        # Инициализация игровых переменных
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'
        self.selected_piece = None
        self.possible_moves = []
        self.en_passant = None
        self.castling_rights = {'white': {'K': True, 'Q': True}, 'black': {'K': True, 'Q': True}}
        
        # Размеры окна и доски
        self.cell_size = 80  # Размер клетки
        self.padding = 20    # Отступ от краев
        self.board_size = self.cell_size * 8  # Размер доски
        self.window_width = self.board_size + 2 * self.padding  # Ширина окна
        self.window_height = self.board_size + 2 * self.padding + 50  # Высота окна (с учетом статусной панели)

        # Установка размеров окна
        self.root.geometry(f"{self.window_width}x{self.window_height}")

        # Создание элементов интерфейса
        self.canvas = Canvas(root, width=self.board_size, height=self.board_size, bg="#F0F0F0")
        self.canvas.pack(pady=(self.padding, 0))  # Отступ сверху для статусной панели
        
        self.status_label = tk.Label(
            root, 
            text=f"Ход: {self.current_player}", 
            font=("Arial", 14)
        )
        self.status_label.pack(pady=(10, 0))  # Отступ сверху для статусной панели

        try:
            logo_image = Image.open("logo.png")  # Загрузите изображение
            logo_image = logo_image.resize((125, 125), Image.Resampling.LANCZOS)  # Измените размер (по желанию)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            self.logo_label = tk.Label(root, image=self.logo_photo, bg="#F0F0F0")
            self.logo_label.place(relx=1.0, rely=1.0, anchor="se")  # Размещение в правом нижнем углу
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")

        self.init_board()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)

    def init_board(self):
        # Инициализация чёрных фигур
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
        self.board[1] = [{'type': 'P', 'color': 'black'} for _ in range(8)]  # Чёрные пешки

        # Инициализация белых фигур
        self.board[6] = [{'type': 'P', 'color': 'white'} for _ in range(8)]  # Белые пешки
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

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                # Цвет клетки
                color = "#DDB88C" if (row + col) % 2 == 0 else "#A66D4F"
                
                # Подсветка возможных ходов
                if (row, col) in self.possible_moves:
                    # Если на клетке есть фигура противника, подсвечиваем её красным
                    target_piece = self.board[row][col]
                    if target_piece and target_piece['color'] != self.current_player:
                        color = "#FF0000"  # Красный цвет для фигур, которые можно уничтожить
                    else:
                        color = "#B0E57C"  # Зелёный цвет для пустых клеток
                
                # Подсветка выбранной фигуры
                elif (row, col) == self.selected_piece:
                    color = "#4CAF50"  # Зелёный цвет для выбранной фигуры
                
                # Отрисовка клетки
                self.draw_square(row, col, color)
                
                # Отрисовка фигуры
                self.draw_piece(row, col)
        
        # Обновление статусной панели
        self.status_label.config(text=f"Ход: {self.current_player}")

    def draw_square(self, row, col, color):
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        self.canvas.create_rectangle(x1, y1, x1 + self.cell_size, y1 + self.cell_size, 
                                   fill=color, outline="black")

    def draw_piece(self, row, col):
        piece = self.board[row][col]
        if piece:
            x = col * self.cell_size + self.cell_size // 2
            y = row * self.cell_size + self.cell_size // 2
            symbol = self.get_symbol(piece)
            self.canvas.create_text(x, y, text=symbol, 
                                   font=("Arial", self.cell_size // 2, "bold"), 
                                   fill=piece['color'])

    def get_symbol(self, piece):
        symbols = {
            'R': '♜', 'N': '♞', 'B': '♝', 
            'Q': '♛', 'K': '♚', 'P': '♟'
        }
        return symbols[piece['type']] if piece['color'] == 'black' else chr(ord(symbols[piece['type']]) + 6)

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
            # Сохраняем текущего игрока перед сменой
            current_player_before_move = self.current_player

            # Выполняем ход
            self.execute_move(row, col)
            self.check_promotion(row, col)

            # Передаем ход противнику
            self.current_player = 'black' if self.current_player == 'white' else 'white'

            # Проверяем мат/пат для противника (нового текущего игрока)
            opponent_color = self.current_player
            if self.is_checkmate(opponent_color):
                self.game_over(f"Мат! Победили {current_player_before_move}!")
            elif self.is_stalemate(opponent_color):
                self.game_over("Пат! Ничья!")

        # Сброс выделения и обновление доски
        self.selected_piece = None
        self.possible_moves = []
        self.draw_board()

    def execute_move(self, to_row, to_col):
        from_row, from_col = self.selected_piece
        piece = self.board[from_row][from_col]
        
        if not piece:  # Если фигуры нет, ничего не делаем
            return
        
        # Рокировка
        if piece['type'] == 'K' and abs(from_col - to_col) == 2:
            self.handle_castling(to_row, to_col)
            return
        
        # Взятие на проходе
        if piece['type'] == 'P' and (to_row, to_col) == self.en_passant:
            self.board[from_row][to_col] = None  # Удаляем пешку, которая была взята на проходе
        
        # Обновление позиции фигуры
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Обновление флагов рокировки
        if piece['type'] == 'K':
            self.castling_rights[piece['color']]['K'] = False
            self.castling_rights[piece['color']]['Q'] = False
        elif piece['type'] == 'R':
            if from_col == 0:
                self.castling_rights[piece['color']]['Q'] = False
            elif from_col == 7:
                self.castling_rights[piece['color']]['K'] = False
        
        # Обновление en passant
        if piece['type'] == 'P' and abs(from_row - to_row) == 2:
            self.en_passant = (to_row + (1 if piece['color'] == 'white' else -1), to_col)
        else:
            self.en_passant = None

    def get_valid_moves(self, row, col):
    # Для фигур противника не фильтруем ходы (чтобы шах работал)
        piece = self.board[row][col]
        if piece['color'] != self.current_player:
            return self.get_raw_moves(row, col)

        # Для текущего игрока проверяем безопасность ходов
        moves = self.get_raw_moves(row, col)
        return [move for move in moves if not self.move_exposes_king(row, col, *move)]

    def move_exposes_king(self, from_row, from_col, to_row, to_col):
        # Временное перемещение для проверки шаха
        original = self.board[to_row][to_col]
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        
        king_pos = self.find_king(self.current_player)
        in_check = self.is_square_under_attack(king_pos[0], king_pos[1], self.current_player)
        
        # Восстановление позиции
        self.board[from_row][from_col] = self.board[to_row][to_col]
        self.board[to_row][to_col] = original
        
        return in_check

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece['type'] == 'K' and piece['color'] == color:
                    return (row, col)
        return None

    def is_square_under_attack(self, row, col, color):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece['color'] != color:
                    # Получаем возможные ходы фигуры без учета шаха
                    moves = self.get_raw_moves(r, c)
                    if (row, col) in moves:
                        return True
        return False
    
    def get_raw_moves(self, row, col):
        piece = self.board[row][col]
        if not piece:
            return []

        moves = []
        type_p = piece['type']

        # Логика для каждой фигуры (без фильтрации через move_exposes_king)
        if type_p == 'P':
            moves = self.get_pawn_moves(row, col, piece['color'])
        elif type_p == 'N':
            moves = self.get_knight_moves(row, col, piece['color'])
        elif type_p == 'B':
            moves = self.get_bishop_moves(row, col, piece['color'])
        elif type_p == 'R':
            moves = self.get_rook_moves(row, col, piece['color'])
        elif type_p == 'Q':
            moves = self.get_queen_moves(row, col, piece['color'])
        elif type_p == 'K':
            moves = self.get_king_moves(row, col, piece['color'])

        return moves

    def is_king_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        return self.is_square_under_attack(king_pos[0], king_pos[1], color)

    def is_checkmate(self, color):
        # Проверяем, находится ли король под шахом
        if not self.is_king_in_check(color):
            return False

        # Проверяем, есть ли хотя бы один допустимый ход для любой фигуры
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece['color'] == color:
                    valid_moves = self.get_valid_moves(row, col)
                    if valid_moves:
                        return False
        return True  # Нет допустимых ходов — мат

    def is_stalemate(self, color):
        if self.is_king_in_check(color):
            return False

        # Проверяем, есть ли допустимые ходы
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece['color'] == color:
                    if self.get_valid_moves(row, col):
                        return False
        return True

    def get_possible_moves(self, row, col, board=None):
        if board is None:
            board = self.board
        piece = board[row][col]
        

        if not piece:
            return []
        
        moves = []
        color = piece['color']
        type_p = piece['type']

        if type_p == 'P':
            moves = self.get_pawn_moves(row, col, color)
        elif type_p == 'N':
            moves = self.get_knight_moves(row, col, color)
        elif type_p == 'B':
            moves = self.get_bishop_moves(row, col, color)
        elif type_p == 'R':
            moves = self.get_rook_moves(row, col, color)
        elif type_p == 'Q':
            moves = self.get_queen_moves(row, col, color)
        elif type_p == 'K':
            moves = self.get_king_moves(row, col, color)
            
        return moves

    def get_pawn_moves(self, row, col, color):
        moves = []
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        
        # Обычный ход
        if 0 <= row + direction < 8 and self.board[row + direction][col] is None:
            moves.append((row + direction, col))
            if row == start_row and self.board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))
        
        # Взятие
        for dx in [-1, 1]:
            if 0 <= col + dx < 8 and 0 <= row + direction < 8:
                target = self.board[row + direction][col + dx]
                if target and target['color'] != color:
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
        moves = []
        directions = [(-1,-1), (-1,1), (1,-1), (1,1),
                      (-1,0), (1,0), (0,-1), (0,1)]
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
        return moves
    
    def is_square_attacked(self, row, col, color, temp_board):
        for r in range(8):
            for c in range(8):
                piece = temp_board[r][c]
                if piece and piece['color'] != color:
                    # Для королей проверяем только соседние клетки
                    if piece['type'] == 'K':
                        if abs(r - row) <= 1 and abs(c - col) <= 1:
                            return True
                    else:
                        moves = self.get_possible_moves(r, c, temp_board)
                        if (row, col) in moves:
                            return True
        return False

    def handle_castling(self, to_row, to_col):
        from_row, from_col = self.selected_piece
        king = self.board[from_row][from_col]
        rook_col = 7 if to_col > from_col else 0
        new_king_col = 6 if to_col > from_col else 2
        new_rook_col = 5 if to_col > from_col else 3
        
        # Перемещение короля
        self.board[to_row][new_king_col] = king
        self.board[from_row][from_col] = None
        
        # Перемещение ладьи
        rook = self.board[from_row][rook_col]
        self.board[from_row][new_rook_col] = rook
        self.board[from_row][rook_col] = None

    def check_promotion(self, row, col):
        piece = self.board[row][col]
        if piece and piece['type'] == 'P' and row in (0, 7):
            new_piece = 'Q'  # Автоматическое превращение в ферзя
            self.board[row][col]['type'] = new_piece

    def game_over(self, message):
        play_again = messagebox.askyesno("Игра окончена", f"{message}\nХотите начать заново?")
        if play_again:
            self.reset_game()  # Сброс игры
        else:
            self.root.quit()  # Закрытие приложения

    def reset_game(self):
        # Сброс доски
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.init_board()

        # Сброс игровых переменных
        self.current_player = 'white'
        self.selected_piece = None
        self.possible_moves = []
        self.en_passant = None
        self.castling_rights = {'white': {'K': True, 'Q': True}, 'black': {'K': True, 'Q': True}}

        # Обновление интерфейса
        self.draw_board()
        self.status_label.config(text=f"Ход: {self.current_player}")

if __name__ == "__main__":
    root = Tk()
    ChessGame(root)
    root.mainloop()