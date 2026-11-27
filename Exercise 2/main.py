# Developed with assistance from Gemini (AI tool).
# Prompt used: "can you use a better font for all text" (updating UI text fonts to Segoe UI while keeping star icons legible).

from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import random

base_dir = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("Alexa Tell Me a Joke")
root.geometry("800x500")
root.resizable(0, 0)
root.config(bg="#000000")

icon_path = os.path.join(base_dir, "joke.png")
icon_img = ImageTk.PhotoImage(Image.open(icon_path))
root.iconphoto(False, icon_img)

app_frame = Frame(root, width=800, height=500, bg="#000000")
app_frame.place(x=0, y=0)

bg_open = Image.open(os.path.join(base_dir, "alexa_background_v4_clean.png"))
bg_resized = bg_open.resize((800, 500))
bg_img = ImageTk.PhotoImage(bg_resized)

bg_label = Label(app_frame, image=bg_img, bd=0)
bg_label.place(x=0, y=0)

jokes = []
last_index = -1
current_punchline = ""
jokes_told = 0
can_rate = False
has_rated = False
waiting_punchline = False
rating_total = 0
rating_count = 0
after_id = None
slices = []


def crop_bg(x, y, w, h):
    box = (max(0, x), max(0, y), max(1, x + w), max(1, y + h))
    part = bg_resized.crop(box)
    if part.size != (w, h) and w > 0 and h > 0:
        part = part.resize((w, h))
    img = ImageTk.PhotoImage(part)
    slices.append(img)
    return img


def load_jokes():
    path = os.path.join(base_dir, "resources", "randomJokes.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip()
                if "?" in line:
                    parts = line.split("?", 1)
                    setup = parts[0].strip() + "?"
                    punch = parts[1].strip()
                    if punch:
                        jokes.append((setup, punch))
    except FileNotFoundError:
        messagebox.showerror("Error", "randomJokes.txt not found in resources folder!")


def type_step(label, text, i, speed):
    global after_id
    if i <= len(text):
        label.config(text=text[:i])
        after_id = root.after(speed, lambda: type_step(label, text, i + 1, speed))
    else:
        after_id = None


def type_text(label, text, fg, speed=25):
    global after_id
    if after_id is not None:
        root.after_cancel(after_id)
        after_id = None
    label.config(text="", fg=fg)
    type_step(label, text, 0, speed)


def avg_text(prefix):
    if rating_count == 0:
        return prefix
    avg = rating_total / rating_count
    return f"{prefix}  |  Avg: {avg:.1f} ({rating_count})"


def reset_stars():
    for b in stars:
        b.config(text="☆", fg="#6c7a99", state=DISABLED, cursor="arrow")
    rating_label.config(text=avg_text("Show punchline to rate"))


def new_joke():
    global last_index, current_punchline, jokes_told, can_rate, has_rated, waiting_punchline
    if len(jokes) == 0:
        messagebox.showwarning("Warning", "No jokes found.")
        return

    idx = random.randint(0, len(jokes) - 1)
    if len(jokes) > 1:
        while idx == last_index:
            idx = random.randint(0, len(jokes) - 1)

    last_index = idx
    setup, punch = jokes[idx]
    current_punchline = punch
    can_rate = False
    has_rated = False
    waiting_punchline = True

    joke_btn.config(text="Show Punchline", bg="#2e8b57", activebackground="#38a169")
    punchline_label.config(text="Your punchline will appear here...", fg="#8b9dc3")
    type_text(setup_label, setup, "#ffffff", 25)

    jokes_told += 1
    counter_label.config(text=f"Jokes told: {jokes_told}")
    reset_stars()


def reveal_punchline():
    global can_rate, waiting_punchline
    if current_punchline == "":
        messagebox.showinfo("Alexa", "Click 'Alexa tell me a Joke' first!")
        return

    type_text(punchline_label, current_punchline, "#ffffff", 25)
    can_rate = True
    waiting_punchline = False
    joke_btn.config(text="Alexa tell me a Joke", bg="#5368d5", activebackground="#687ce3")

    if not has_rated:
        for b in stars:
            b.config(fg="#d4af37", state=NORMAL, cursor="hand2")
        rating_label.config(text=avg_text("Not rated yet"))


def main_btn_click():
    if waiting_punchline:
        reveal_punchline()
    else:
        new_joke()


def give_rating(score):
    global rating_total, rating_count, has_rated
    if not can_rate or has_rated:
        return

    for i in range(5):
        if i < score:
            stars[i].config(text="★", fg="#ffd700")
        else:
            stars[i].config(text="☆", fg="#d4af37")

    for b in stars:
        b.config(state=DISABLED, cursor="arrow")

    has_rated = True
    rating_total += score
    rating_count += 1
    rating_label.config(text=avg_text(f"Rated {score}/5 (locked)"))


def set_ui_size(w, h):
    global bg_resized, bg_img
    slices.clear()
    app_frame.config(width=w, height=h)
    app_frame.place(x=0, y=0)

    bg_resized = bg_open.resize((w, h))
    bg_img = ImageTk.PhotoImage(bg_resized)
    bg_label.config(image=bg_img)
    bg_label.place(x=0, y=0, width=w, height=h)

    sx = w / 800
    sy = h / 500
    s = min(sx, sy)

    def place_lbl(lbl, x, y, bw, bh, font_name, font_size, weight=None, wrap=None):
        px, py = int(round(x * sx)), int(round(y * sy))
        pw, ph = max(1, int(round(bw * sx))), max(1, int(round(bh * sy)))
        f_sz = max(8, int(round(font_size * s)))
        fnt = (font_name, f_sz, weight) if weight else (font_name, f_sz)
        img = crop_bg(px, py, pw, ph)
        lbl.config(image=img, compound="center", font=fnt)
        if wrap is not None:
            lbl.config(wraplength=max(1, int(round(wrap * sx))))
        lbl.place(x=px, y=py, width=pw, height=ph)

    def place_btn(btn, x, y, bw, bh, font_name, font_size, weight=None):
        px, py = int(round(x * sx)), int(round(y * sy))
        pw, ph = max(1, int(round(bw * sx))), max(1, int(round(bh * sy)))
        f_sz = max(8, int(round(font_size * s)))
        fnt = (font_name, f_sz, weight) if weight else (font_name, f_sz)
        btn.config(font=fnt)
        btn.place(x=px, y=py, width=pw, height=ph)

    place_lbl(title_label, 270, 80, 320, 34, "Segoe UI", 17, "bold")
    place_lbl(setup_tag, 100, 138, 65, 20, "Segoe UI", 9, "bold")
    place_lbl(setup_label, 105, 164, 590, 64, "Segoe UI", 15, "bold", 580)
    place_lbl(punchline_label, 105, 232, 590, 36, "Segoe UI", 12, None, 580)
    place_lbl(rate_title, 82, 348, 112, 24, "Segoe UI", 10, "bold")
    place_lbl(rating_label, 200, 381, 285, 20, "Segoe UI", 9)
    place_lbl(counter_label, 92, 412, 110, 28, "Segoe UI", 9, "bold")
    place_lbl(shortcuts_label, 305, 416, 420, 20, "Segoe UI", 9)

    place_btn(joke_btn, 82, 288, 315, 38, "Segoe UI", 10, "bold")
    place_btn(next_btn, 415, 288, 303, 38, "Segoe UI", 10, "bold")
    for i in range(5):
        place_btn(stars[i], 200 + i * 46, 342, 38, 35, "Arial", 13)
    place_btn(fullscreen_btn, 497, 342, 115, 35, "Segoe UI", 10, "bold")
    place_btn(quit_btn, 626, 342, 92, 35, "Segoe UI", 10, "bold")


def toggle_fs():
    now_fs = not root.attributes("-fullscreen")
    root.attributes("-fullscreen", now_fs)
    root.update_idletasks()
    if now_fs:
        fullscreen_btn.config(text="Windowed")
        set_ui_size(root.winfo_screenwidth(), root.winfo_screenheight())
    else:
        fullscreen_btn.config(text="Full Screen")
        set_ui_size(800, 500)


def esc_fs(event):
    if root.attributes("-fullscreen"):
        toggle_fs()


def ask_quit():
    if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
        root.destroy()


def key_pressed(event):
    k = event.keysym.lower()
    if k == "return":
        main_btn_click()
    elif k == "n":
        new_joke()
    elif k == "p":
        reveal_punchline()
    elif k in ["1", "2", "3", "4", "5"]:
        give_rating(int(k))
    elif k == "f11":
        toggle_fs()
    elif k == "q":
        ask_quit()


title_label = Label(app_frame, text="ALEXA TELL ME A JOKE", fg="#7e9ef2", bd=0, highlightthickness=0, anchor=CENTER)
setup_tag = Label(app_frame, text="SETUP", fg="#7e9ef2", bd=0, highlightthickness=0, anchor=CENTER)
setup_label = Label(app_frame, text="Press the button and I will tell you a joke!", fg="#ffffff", bd=0, highlightthickness=0, anchor=CENTER, justify=CENTER)
punchline_label = Label(app_frame, text="Your punchline will appear here...", fg="#8b9dc3", bd=0, highlightthickness=0, anchor=CENTER, justify=CENTER)

joke_btn = Button(app_frame, text="Alexa tell me a Joke", bg="#5368d5", fg="#ffffff", activebackground="#687ce3", activeforeground="#ffffff", bd=0, command=main_btn_click)
next_btn = Button(app_frame, text="Next Joke", bg="#5368d5", fg="#ffffff", activebackground="#687ce3", activeforeground="#ffffff", bd=0, command=new_joke)

rate_title = Label(app_frame, text="Rate this joke", fg="#7e9ef2", bd=0, highlightthickness=0, anchor=CENTER)

stars = []
for i in range(5):
    s_btn = Button(
        app_frame,
        text="☆",
        bg="#313f5e",
        fg="#6c7a99",
        disabledforeground="#6c7a99",
        activebackground="#3e4f75",
        activeforeground="#ffd700",
        bd=0,
        state=DISABLED,
        command=lambda val=i + 1: give_rating(val)
    )
    stars.append(s_btn)

rating_label = Label(app_frame, text="Show punchline to rate", fg="#8b9dc3", bd=0, highlightthickness=0, anchor=CENTER)
fullscreen_btn = Button(app_frame, text="Full Screen", bg="#313f5e", fg="#ffffff", activebackground="#3e4f75", activeforeground="#ffffff", bd=0, command=toggle_fs)
quit_btn = Button(app_frame, text="Quit", bg="#8c3b42", fg="#ffffff", activebackground="#a64951", activeforeground="#ffffff", bd=0, command=ask_quit)
counter_label = Label(app_frame, text="Jokes told: 0", fg="#7e9ef2", bd=0, highlightthickness=0, anchor=CENTER, justify=CENTER)
shortcuts_label = Label(app_frame, text="Enter=joke/punch  P=punchline  N=next  1-5=rate  F11=full screen  Q=quit", fg="#8b9dc3", bd=0, highlightthickness=0, anchor=CENTER)

set_ui_size(800, 500)

root.bind("<Key>", key_pressed)
root.bind("<Escape>", esc_fs)

load_jokes()
root.mainloop()