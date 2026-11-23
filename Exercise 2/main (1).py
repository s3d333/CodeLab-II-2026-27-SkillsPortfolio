
import random
import tkinter as tk
from tkinter import messagebox
from pathlib import Path


# Find files relative to this Python file, so the project works from any
# working directory as long as the folder structure is kept the same.
PROJECT_FOLDER = Path(__file__).resolve().parent
BACKGROUND_FILE = PROJECT_FOLDER / "alexa_background_v2_clean.png"
# The program checks the usual resources folder first, then the project
# folder itself. It also searches subfolders if the file is elsewhere.
JOKE_FILE_CANDIDATES = [
    PROJECT_FOLDER / "resources" / "randomJokes.txt",
    PROJECT_FOLDER / "Resources" / "randomJokes.txt",
    PROJECT_FOLDER / "randomJokes.txt",
]

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 550

# Colours taken from the Canva design.
TEXT_COLOUR = "#F4F5FF"
MUTED_COLOUR = "#AAB8D6"
BLUE = "#586BDD"
BLUE_HOVER = "#7182F0"
DARK_BUTTON = "#3B4D80"
RED = "#A3424B"
RED_HOVER = "#BD5962"


class AlexaJokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alexa - Tell Me a Joke")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#080713")

        self.canvas = tk.Canvas(
            root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Keep a reference to the image so Tkinter does not remove it.
        try:
            self.background_image = tk.PhotoImage(file=str(BACKGROUND_FILE))
            self.canvas.create_image(
                0, 0, image=self.background_image, anchor="nw"
            )
        except tk.TclError:
            messagebox.showerror(
                "Background image not found",
                "Could not load alexa_background_v2_clean.png.\n\n"
                "Place the image in the same folder as main.py."
            )
            self.root.destroy()
            return

        self.jokes = self.load_jokes()
        self.remaining_jokes = []
        self.current_joke = None
        self.jokes_viewed = 0

        self.create_interface()
        self.show_initial_text()


    def load_jokes(self):
        """Find randomJokes.txt, read it and split each joke into two parts."""
        loaded_jokes = []
        jokes_path = next(
            (path for path in JOKE_FILE_CANDIDATES if path.is_file()),
            None
        )

        # If it was not in the usual locations, look inside project folders.
        if jokes_path is None:
            matches = list(PROJECT_FOLDER.rglob("randomJokes.txt"))
            if matches:
                jokes_path = matches[0]

        if jokes_path is None:
            checked_locations = "\n".join(
                str(path) for path in JOKE_FILE_CANDIDATES
            )
            messagebox.showerror(
                "Joke file not found",
                "I could not find randomJokes.txt.\n\n"
                "Put it in a resources folder beside main.py, or directly "
                "beside main.py.\n\n"
                f"Locations checked:\n{checked_locations}"
            )
            return loaded_jokes

        try:
            # utf-8-sig also handles text files saved with a UTF-8 BOM.
            with open(jokes_path, "r", encoding="utf-8-sig") as joke_file:
                for line_number, line in enumerate(joke_file, start=1):
                    line = line.strip()

                    if not line or "?" not in line:
                        continue

                    setup, punchline = line.split("?", 1)
                    setup = setup.strip() + "?"
                    punchline = punchline.strip()

                    if setup != "?" and punchline:
                        loaded_jokes.append((setup, punchline))

            if not loaded_jokes:
                messagebox.showwarning(
                    "No valid jokes",
                    f"The file was found at:\n{jokes_path}\n\n"
                    "However, no valid jokes were found. Each line should "
                    "contain a setup and punchline separated by a question mark."
                )

        except (OSError, UnicodeError) as error:
            messagebox.showerror(
                "File error",
                f"Could not read this file:\n{jokes_path}\n\n{error}"
            )

        return loaded_jokes

    def create_interface(self):
        """Create the text, labels and buttons over the background image."""

        # Header
        self.canvas.create_text(
            450, 57,
            text="■  ALEXA  JOKES",
            fill="#282047",
            font=("Courier New", 14, "bold")
        )

        # Left-hand panel
        self.canvas.create_text(
            171, 293,
            text="ALEXA",
            fill="#91A0FF",
            font=("Courier New", 28, "bold")
        )

        self.canvas.create_text(
            171, 329,
            text="Let's Have a Laugh!",
            fill=TEXT_COLOUR,
            font=("Courier New", 13, "bold")
        )

        self.canvas.create_text(
            171, 365,
            text="Your personal",
            fill=MUTED_COLOUR,
            font=("Courier New", 12)
        )

        self.canvas.create_text(
            171, 384,
            text="joke-telling assistant",
            fill=MUTED_COLOUR,
            font=("Courier New", 12)
        )

        # Setup and punchline headings
        self.canvas.create_text(
            340, 113,
            text="SETUP",
            anchor="w",
            fill="#91A0FF",
            font=("Courier New", 9, "bold")
        )

        self.canvas.create_text(
            340, 229,
            text="PUNCHLINE",
            anchor="w",
            fill="#91A0FF",
            font=("Courier New", 9, "bold")
        )

        # Joke text
        self.setup_text = self.canvas.create_text(
            569, 153,
            text="",
            fill=TEXT_COLOUR,
            font=("Courier New", 15, "bold"),
            width=465,
            justify="center"
        )

        self.punchline_text = self.canvas.create_text(
            569, 265,
            text="",
            fill=MUTED_COLOUR,
            font=("Courier New", 14),
            width=465,
            justify="center"
        )

        # Main button
        self.create_button(
            x1=318, y1=320, x2=820, y2=365,
            text="Alexa, tell me a Joke",
            command=self.tell_joke,
            fill=BLUE,
            hover_fill=BLUE_HOVER,
            font=("Courier New", 14, "bold")
        )

        # Show punchline and next joke buttons
        self.create_button(
            x1=318, y1=378, x2=562, y2=418,
            text="Show Punchline",
            command=self.show_punchline,
            fill=BLUE,
            hover_fill=BLUE_HOVER,
            font=("Courier New", 12, "bold")
        )

        self.create_button(
            x1=576, y1=378, x2=820, y2=418,
            text="Next Joke",
            command=self.next_joke,
            fill=BLUE,
            hover_fill=BLUE_HOVER,
            font=("Courier New", 12, "bold")
        )

        # Optional reaction button
        self.create_button(
            x1=318, y1=440, x2=458, y2=479,
            text="Funny!",
            command=self.funny_reaction,
            fill=DARK_BUTTON,
            hover_fill="#50649B",
            font=("Courier New", 12, "bold")
        )

        # Small footer text
        self.footer_text = self.canvas.create_text(
            733, 460,
            text="Jokes make life better  :D",
            fill=MUTED_COLOUR,
            font=("Courier New", 10)
        )

        # Quit button
        self.create_button(
            x1=82, y1=452, x2=260, y2=489,
            text="Quit",
            command=self.root.destroy,
            fill=RED,
            hover_fill=RED_HOVER,
            font=("Courier New", 12, "bold")
        )

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=22, **kwargs):
        """Draw a rounded rectangle on the Canvas."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=24,
            **kwargs
        )

    def create_button(
        self, x1, y1, x2, y2, text, command,
        fill, hover_fill, font
    ):
        """Create a rounded, clickable Canvas button."""
        tag = f"button_{text.replace(' ', '_').replace('!', '')}"

        self.create_rounded_rectangle(
            x1, y1, x2, y2,
            radius=22,
            fill=fill,
            outline="",
            tags=(tag, f"{tag}_shape")
        )

        self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=text,
            fill="white",
            font=font,
            tags=(tag, f"{tag}_label")
        )

        self.canvas.tag_bind(tag, "<Button-1>", lambda event: command())
        self.canvas.tag_bind(
            tag, "<Enter>",
            lambda event: self.canvas.itemconfigure(
                f"{tag}_shape", fill=hover_fill
            )
        )
        self.canvas.tag_bind(
            tag, "<Leave>",
            lambda event: self.canvas.itemconfigure(
                f"{tag}_shape", fill=fill
            )
        )
        self.canvas.tag_bind(
            tag, "<Enter>",
            lambda event: self.canvas.configure(cursor="hand2"),
            add="+"
        )
        self.canvas.tag_bind(
            tag, "<Leave>",
            lambda event: self.canvas.configure(cursor=""),
            add="+"
        )

    def show_initial_text(self):
        self.canvas.itemconfigure(
            self.setup_text,
            text="Press 'Alexa, tell me a Joke' to begin!"
        )
        self.canvas.itemconfigure(
            self.punchline_text,
            text="Your joke will appear here..."
        )

    def get_random_joke(self):
        """Get a random joke without repeating until the list is exhausted."""
        if not self.jokes:
            messagebox.showwarning(
                "No jokes available",
                "Please add valid jokes to resources/randomJokes.txt."
            )
            return None

        if not self.remaining_jokes:
            self.remaining_jokes = self.jokes.copy()
            random.shuffle(self.remaining_jokes)

        return self.remaining_jokes.pop()

    def tell_joke(self):
        """Load and display a new random joke setup."""
        joke = self.get_random_joke()

        if joke is None:
            return

        self.current_joke = joke
        self.jokes_viewed += 1

        self.canvas.itemconfigure(
            self.setup_text,
            text=self.current_joke[0]
        )
        self.canvas.itemconfigure(
            self.punchline_text,
            text="Click 'Show Punchline' to reveal the answer."
        )
        self.canvas.itemconfigure(
            self.footer_text,
            text=f"Jokes viewed: {self.jokes_viewed}"
        )

    def show_punchline(self):
        """Reveal the punchline for the current joke."""
        if self.current_joke is None:
            messagebox.showinfo(
                "No joke yet",
                "Click 'Alexa, tell me a Joke' first!"
            )
            return

        self.canvas.itemconfigure(
            self.punchline_text,
            text=self.current_joke[1],
            fill=TEXT_COLOUR
        )

    def next_joke(self):
        """Load the next random joke."""
        self.tell_joke()

    def funny_reaction(self):
        """Give the user a small reaction when they click Funny!."""
        if self.current_joke is None:
            messagebox.showinfo(
                "Ready for a laugh?",
                "Get a joke first, then let Alexa know if it was funny!"
            )
            return

        self.canvas.itemconfigure(
            self.footer_text,
            text="Glad you laughed!  :D"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = AlexaJokeApp(root)
    root.mainloop()
