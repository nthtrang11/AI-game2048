from tkinter import Frame, Label, CENTER, Tk, Button, Canvas, PhotoImage
import numpy as np
import game as game
import ai as ai
import config as c

config = c.Base()

class StartScreen(Frame):
    def __init__(self, master, start_game_callback):
        Frame.__init__(self, master)
        self.master = master
        self.start_game_callback = start_game_callback
        self.grid(row=0, column=0)
        
        # Tạo Canvas để hiển thị hình ảnh nền
        self.canvas = Canvas(self, width=844, height=780, highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        
        # Tải hình ảnh nền
        self.bg_image = PhotoImage(file="img/2.png")  # Thay bằng đường dẫn tới hình ảnh của bạn
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        
        self.create_widgets()
        
    def create_widgets(self):
        
       # Nút Start
        start_btn = Button(self, text="Start", font=("Verdana", 20, "bold"), 
                          width=10, command=self.start_game,
                          bg="#8f7a66", fg="#f9f6f2")
        start_btn.place(relx=0.75, rely=0.39, anchor=CENTER)  # Căn giữa nút Start
        
        # Nút Help
        help_btn = Button(self, text="Help", font=("Verdana", 20, "bold"), 
                         width=10, command=self.show_help,
                         bg="#8f7a66", fg="#f9f6f2")
        help_btn.place(relx=0.75, rely=0.5, anchor=CENTER)  # Đặt dưới nút Start
        
        # Nút Exit
        exit_btn = Button(self, text="Exit", font=("Verdana", 20, "bold"), 
                         width=10, command=self.master.quit,
                         bg="#8f7a66", fg="#f9f6f2")
        exit_btn.place(relx=0.75, rely=0.61, anchor=CENTER)  # Đặt dưới nút Help
    
    def start_game(self):
        self.grid_forget()
        self.start_game_callback()
        
    def show_help(self):
        self.grid_forget()
        HelpScreen(self.master, self.show_start_screen)
        
    def show_start_screen(self):
        self.grid()

class HelpScreen(Frame):
    def __init__(self, master, back_callback):
        Frame.__init__(self, master)
        self.master = master
        self.back_callback = back_callback
        self.grid(row=0, column=0)
        
        # Tạo Canvas để hiển thị hình ảnh nền
        self.canvas = Canvas(self, width=844, height=780)
        self.canvas.grid(row=0, column=0)
        
        # Tải hình ảnh nền
        self.bg_image = PhotoImage(file="img/1.png")  # Sử dụng cùng hình ảnh với StartScreen
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Quy tắc trò chơi
        rules = (
            "HOW TO PLAY:\n"
            "1. Use W, A, S, D or arrow keys to move the tiles.\n"
            "2. Merge tiles with the same number.\n"
            "3. Reach 2048 to win.\n"
            "4. Game over when no moves are left or time runs out.\n"
            "5. Time limit: 10 minutes.\n"
            "\nHELP:\n"
            "Press 'AI Play' for AI assistance, press again to stop."
        )
        rules_label = Label(self.canvas, text=rules, font=("Verdana", 16), justify="left", bg='#ddd3c5', wraplength=500)
        self.canvas.create_window(422, 400, window=rules_label)  # Căn giữa ngang, khoảng giữa màn hình
        
        # Nút Back
        back_btn = Button(self.canvas, text="Back", font=("Verdana", 20, "bold"), 
                         width=10, command=self.go_back,
                         bg="#8f7a66", fg="#f9f6f2")
        self.canvas.create_window(422, 650, window=back_btn)  # Căn giữa ngang, gần đáy
    
    def go_back(self):
        self.grid_forget()
        self.back_callback()

class GameGrid(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.master.title('2048')
        self.master.geometry("844x780+300+80")  # Giữ nguyên kích thước màn hình
        self.master.bind("<Key>", self.key_down)  # Bind phím
        self.master.focus_set()  # Đảm bảo focus

        self.commands = {
            "w": "U", "Up": "U",
            "s": "D", "Down": "D",
            "a": "L", "Left": "L",
            "d": "R", "Right": "R",
        }

        self.score = 0
        self.best_score = self.load_best_score()
        self.time_left = 600  # Thời gian ban đầu: 300 giây (5 phút)
        self.grid_cells = []
        self.init_grid()
        self.game = game.Game(config.SIZE)
        self.game.grid.max_tile = 2048
        self.game.start()  # Bắt đầu game
        self.ai = ai.Ai()
        self.matrix = self.game.grid.tiles
        self.history_matrixs = []
        self.is_ai_running = False
        self.update_grid_cells()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.start_timer()  # Bắt đầu đếm ngược thời gian
        self.ai_loop()
        self.mainloop()

    def load_best_score(self):
        try:
            with open("best_score.txt", "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def save_best_score(self):
        with open("best_score.txt", "w") as f:
            f.write(str(self.best_score))

    def update_score_display(self):
        self.score_label.configure(text=f"Your score: {self.score}")
        self.best_label.configure(text=f"Best score: {self.best_score}")
        # Hiển thị thời gian theo định dạng phút:giây
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.time_label.configure(text=f"Time left: {minutes:02d}:{seconds:02d}")

    def init_grid(self):
        background = Frame(self, bg="#92877d", width=400, height=400)
        background.grid()
        self.score_label = Label(background, text="Your score: 0", font=("Verdana", 20, "bold"), bg="#92877d")
        self.score_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        restart_btn = Button(background, text="New game", font=("Verdana", 16, "bold"), width=12, command=self.restart_game)
        restart_btn.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.best_label = Label(background, text=f"Best Score: {self.best_score}", font=("Verdana", 20, "bold"), bg="#92877d")
        self.best_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        self.ai_btn = Button(background, text="AI Play", font=("Verdana", 16, "bold"), width=12, command=self.toggle_ai)
        self.ai_btn.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        # Thêm nhãn thời gian thẳng cột với điểm số
        self.time_label = Label(background, text="Time left: 05:00", font=("Verdana", 20, "bold"), bg="#92877d")
        self.time_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        # Thêm nút Exit tại hàng 3 cột 3
        exit_btn = Button(background, text="Exit", font=("Verdana", 16, "bold"), width=12, 
                        command=self.on_closing, bg="#8f7a66", fg="#f9f6f2")
        exit_btn.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        for i in range(config.SIZE):
            grid_row = []
            for j in range(config.SIZE):
                cell = Frame(background, bg="#9e948a", width=400/config.SIZE, height=400/config.SIZE)
                cell.grid(row=i+3, column=j, padx=10, pady=10)  # Dịch xuống 1 hàng để nhường chỗ cho time_label
                t = Label(master=cell, text="", bg="#9e948a", justify=CENTER, font=("Verdana", 40, "bold"), width=5, height=2)
                t.grid()
                grid_row.append(t)
            self.grid_cells.append(grid_row)

    def start_timer(self):
        """Bắt đầu đếm ngược thời gian"""
        if self.game.state not in ['win', 'over'] and self.time_left > 0:
            self.time_left -= 1
            self.update_score_display()
            if self.time_left <= 0 and 2048 not in self.matrix:  # Hết giờ và chưa đạt 2048
                self.game.state = 'over'
                self.check_game_state()
            self.master.after(1000, self.start_timer)  # Gọi lại sau 1 giây

    def update_grid_cells(self):
        for i in range(config.SIZE):
            for j in range(config.SIZE):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="", bg="#9e948a")
                else:
                    color_key = str(int(new_number)) if new_number <= 2048 else "2048"
                    self.grid_cells[i][j].configure(
                        text=str(new_number),
                        bg=f"#{''.join(format(c, '02x') for c in config.COLORS[color_key])}",
                        fg="#776e65" if new_number <= 4 else "#f9f6f2"
                    )
        self.update_score_display()
        self.update_idletasks()

    def key_down(self, event):
        if self.is_ai_running or self.game.state in ['win', 'over']:
            return
        key = event.keysym
        if key == "Escape":
            self.on_closing()
            exit()
        elif key in self.commands:
            direction = self.commands[key]
            old_matrix = self.matrix.copy()
            self.game.run(direction)
            if not (self.matrix == old_matrix).all():
                self.score = self.game.score
                if self.score > self.best_score:
                    self.best_score = self.score
                    self.save_best_score()
                self.matrix = self.game.grid.tiles
                self.history_matrixs.append(self.matrix.copy())
                self.update_grid_cells()
            if 2048 in self.matrix:
                self.game.state = 'win'
            elif self.game.grid.is_over():
                self.game.state = 'over'
            self.check_game_state()

    def ai_loop(self):
        if not self.is_ai_running:
            return
        self.check_game_state()
        if self.game.state in ['win', 'over']:
            self.is_ai_running = False
            self.ai_btn.configure(text="Tự động chơi")
            return
        directions = ['U', 'D', 'L', 'R']
        any_valid_move = False
        old_matrix = self.matrix.copy()
        for direction in directions:
            temp_grid = game.Grid(config.SIZE)
            temp_grid.tiles = self.matrix.copy()
            score_change = temp_grid.run(direction)
            if score_change > 0 or not (temp_grid.tiles == old_matrix).all():
                any_valid_move = True
                break
        if not any_valid_move:
            self.game.state = 'over'
            self.check_game_state()
            self.is_ai_running = False
            self.ai_btn.configure(text="Tự động chơi")
            return
        direction, _ = self.ai.get_next(self.matrix)
        self.game.run(direction)
        if not (self.matrix == old_matrix).all():
            self.score = self.game.score
            if self.score > self.best_score:
                self.best_score = self.score
                self.save_best_score()
            self.matrix = self.game.grid.tiles
            self.history_matrixs.append(self.matrix.copy())
            self.update_grid_cells()
        if 2048 in self.matrix:
            self.game.state = 'win'
        self.check_game_state()
        self.master.after(600, self.ai_loop)

    def restart_game(self):
        self.game = game.Game(config.SIZE)
        self.game.grid.max_tile = 2048
        self.game.start()
        self.score = 0
        self.time_left = 600  # Reset thời gian về 5 phút
        self.is_ai_running = False
        self.matrix = self.game.grid.tiles
        self.history_matrixs = []
        self.update_grid_cells()
        self.update_score_display()
        self.start_timer()  # Bắt đầu lại đếm ngược

    def toggle_ai(self):
        if self.game.state in ['win', 'over']:
            self.restart_game()
        self.is_ai_running = not self.is_ai_running
        if self.is_ai_running:
            self.ai_btn.configure(text="Manual")
            self.ai_loop()
        else:
            self.ai_btn.configure(text="AI Play")

    def check_game_state(self):
        if self.game.state == 'win':
            self.grid_cells[1][1].configure(text="You", bg="#9e948a")
            self.grid_cells[1][2].configure(text="Win!", bg="#9e948a")
        elif self.game.state == 'over':
            if self.time_left <= 0:  # Hiển thị "Time Up!" khi hết giờ
                self.grid_cells[1][1].configure(text="Time", bg="#9e948a")
                self.grid_cells[1][2].configure(text="Up!", bg="#9e948a")
            else:
                self.grid_cells[1][1].configure(text="You", bg="#9e948a")
                self.grid_cells[1][2].configure(text="Lose!", bg="#9e948a")

    def on_closing(self):
        self.save_best_score()
        self.master.destroy()

def start_game_grid(master):
    game_grid = GameGrid(master)
    game_grid.pack()

def main():
    root = Tk()
    root.geometry("844x780+300+80")
    root.title('2048')
    StartScreen(root, lambda: start_game_grid(root))
    root.mainloop()

if __name__ == "__main__":
    main()
