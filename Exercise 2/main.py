import random
from tkinter import *
from tkinter import messagebox
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BG_FILE = BASE_DIR / "alexa_background_v2_clean.png"
JOKE_FILES = [
    BASE_DIR / "resources" / "randomJokes.txt",
    BASE_DIR / "Resources" / "randomJokes.txt",
    BASE_DIR / "randomJokes.txt",
]

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 550

TEXT_COLOR = "#F4F5FF"
MUTED_COLOR = "#AAB8D6"
BLUE = "#586BDD"
BLUE_HOVER = "#7182F0"
DARK_BTN = "#3B4D80"
RED = "#A3424B"
RED_HOVER = "#BD5962"


class AlexaJokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alexa - Tell Me a Joke")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(0, 0)
        self.root.configure(bg="#080713")

        self.canvas = Canvas(
            root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=BOTH, expand=YES)

        try:
            self.bg_image = PhotoImage(file=str(BG_FILE))
            self.canvas.create_image(0, 0, image=self.bg_image, anchor=NW)
        except TclError:
            messagebox.showerror(
                "Background image not found",
                "Could not load alexa_background_v2_clean.png.\n"
                "Place it in the same folder as this script.",
            )
            self.root.destroy()
            return

        self.jokes = self.load_jokes()
        self.joke_pool = []
        self.current_joke = None
        self.jokes_viewed = 0

        self.build_ui()
        self.reset_prompt()

    def find_joke_file(self):
        for path in JOKE_FILES:
            if path.is_file():
                return path
        matches = list(BASE_DIR.rglob("randomJokes.txt"))
        return matches[0] if matches else None

    def load_jokes(self):
        joke_path = self.find_joke_file()
        if joke_path is None:
            messagebox.showerror(
                "Joke file not found",
                "Could not find randomJokes.txt in resources/ or the project folder.",
            )
            return []

        jokes = []
        try:
            with open(joke_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if "?" not in line:
                        continue
                    setup, punchline = line.split("?", 1)
                    setup = setup.strip() + "?"
                    punchline = punchline.strip()
                    if setup != "?" and punchline:
                        jokes.append((setup, punchline))
        except (OSError, UnicodeError) as err:
            messagebox.showerror("File error", f"Could not read randomJokes.txt:\n{err}")

        if not jokes:
            messagebox.showwarning("No valid jokes", "No valid jokes found in randomJokes.txt.")
        return jokes

    def draw_rounded_box(self, x1, y1, x2, y2, r=22, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)

    def make_button(self, x1, y1, x2, y2, text, command, bg, hover_bg, font):
        tag = f"btn_{abs(hash((x1, y1, text)))}"
        self.draw_rounded_box(x1, y1, x2, y2, fill=bg, outline="", tags=(tag, f"{tag}_bg"))
        self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=text,
            fill="white",
            font=font,
            tags=tag,
        )

        self.canvas.tag_bind(tag, "<Button-1>", lambda event: command())
        self.canvas.tag_bind(
            tag,
            "<Enter>",
            lambda event: (
                self.canvas.itemconfigure(f"{tag}_bg", fill=hover_bg),
                self.canvas.configure(cursor="hand2"),
            ),
        )
        self.canvas.tag_bind(
            tag,
            "<Leave>",
            lambda event: (
                self.canvas.itemconfigure(f"{tag}_bg", fill=bg),
                self.canvas.configure(cursor=""),
            ),
        )

    def build_ui(self):
        self.canvas.create_text(
            450, 57, text="■  ALEXA  JOKES", fill="#282047", font=("Courier New", 14, "bold")
        )

        self.canvas.create_text(
            171, 293, text="ALEXA", fill="#91A0FF", font=("Courier New", 28, "bold")
        )
        self.canvas.create_text(
            171, 329, text="Let's Have a Laugh!", fill=TEXT_COLOR, font=("Courier New", 13, "bold")
        )
        self.canvas.create_text(
            171, 365, text="Your personal", fill=MUTED_COLOR, font=("Courier New", 12)
        )
        self.canvas.create_text(
            171, 384, text="joke-telling assistant", fill=MUTED_COLOR, font=("Courier New", 12)
        )

        self.canvas.create_text(
            340, 113, text="SETUP", anchor=W, fill="#91A0FF", font=("Courier New", 9, "bold")
        )
        self.canvas.create_text(
            340, 229, text="PUNCHLINE", anchor=W, fill="#91A0FF", font=("Courier New", 9, "bold")
        )

        self.setup_id = self.canvas.create_text(
            569, 153, text="", fill=TEXT_COLOR, font=("Courier New", 15, "bold"),
            width=465, justify=CENTER
        )
        self.punchline_id = self.canvas.create_text(
            569, 265, text="", fill=MUTED_COLOR, font=("Courier New", 14),
            width=465, justify=CENTER
        )

        self.make_button(
            318, 320, 820, 365, "Alexa, tell me a Joke", self.tell_joke,
            BLUE, BLUE_HOVER, ("Courier New", 14, "bold")
        )
        self.make_button(
            318, 378, 562, 418, "Show Punchline", self.show_punchline,
            BLUE, BLUE_HOVER, ("Courier New", 12, "bold")
        )
        self.make_button(
            576, 378, 820, 418, "Next Joke", self.tell_joke,
            BLUE, BLUE_HOVER, ("Courier New", 12, "bold")
        )
        self.make_button(
            318, 440, 458, 479, "Funny!", self.funny_reaction,
            DARK_BTN, "#50649B", ("Courier New", 12, "bold")
        )
        self.make_button(
            82, 452, 260, 489, "Quit", self.root.destroy,
            RED, RED_HOVER, ("Courier New", 12, "bold")
        )

        self.footer_id = self.canvas.create_text(
            733, 460, text="Jokes make life better  :D", fill=MUTED_COLOR, font=("Courier New", 10)
        )

    def reset_prompt(self):
        self.canvas.itemconfigure(
            self.setup_id, text="Press 'Alexa, tell me a Joke' to begin!", fill=TEXT_COLOR
        )
        self.canvas.itemconfigure(
            self.punchline_id, text="Your joke will appear here...", fill=MUTED_COLOR
        )

    def tell_joke(self):
        if not self.jokes:
            messagebox.showwarning("No jokes available", "Please add jokes to randomJokes.txt.")
            return

        if not self.joke_pool:
            self.joke_pool = self.jokes.copy()
            random.shuffle(self.joke_pool)

        self.current_joke = self.joke_pool.pop()
        self.jokes_viewed += 1

        self.canvas.itemconfigure(self.setup_id, text=self.current_joke[0], fill=TEXT_COLOR)
        self.canvas.itemconfigure(
            self.punchline_id,
            text="Click 'Show Punchline' to reveal the answer.",
            fill=MUTED_COLOR,
        )
        self.canvas.itemconfigure(self.footer_id, text=f"Jokes viewed: {self.jokes_viewed}")

    def show_punchline(self):
        if self.current_joke is None:
            messagebox.showinfo("No joke yet", "Click 'Alexa, tell me a Joke' first!")
            return
        self.canvas.itemconfigure(self.punchline_id, text=self.current_joke[1], fill=TEXT_COLOR)

    def funny_reaction(self):
        if self.current_joke is None:
            messagebox.showinfo("Ready for a laugh?", "Get a joke first, then let Alexa know if it was funny!")
            return
        self.canvas.itemconfigure(self.footer_id, text="Glad you laughed!  :D")


if __name__ == "__main__":
    root = Tk()
    app = AlexaJokeApp(root)
    root.mainloop()