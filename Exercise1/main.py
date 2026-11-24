from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import random

try:
    import pygame
    pygame.mixer.init()
    audio_ok = True
except Exception:
    audio_ok = False

root = Tk()
root.title("Maths Quiz")
root.geometry("900x550")
root.resizable(0, 0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RES_DIR = os.path.join(BASE_DIR, "Resources")
AUDIO_DIR = os.path.join(RES_DIR, "Audio")
IMG_DIR = os.path.join(RES_DIR, "Images")

try:
    root.iconbitmap(os.path.join(BASE_DIR, "app_icon.ico"))
except Exception:
    pass

# Colours
PURPLE = "#A98AEF"
LIGHT_PURPLE = "#D8C8FF"
DARK_PURPLE = "#38245E"
DARK = "#211735"
WHITE = "#FFFFFF"
GREY = "#777777"
PALE_PURPLE = "#F1EAFE"

# Images
bg_open = Image.open(os.path.join(IMG_DIR, "background.png"))
main_bg = ImageTk.PhotoImage(bg_open.resize((900, 550)))

quiz_bg_open = Image.open(os.path.join(IMG_DIR, "quiz_background.png"))
quiz_bg = ImageTk.PhotoImage(quiz_bg_open.resize((900, 550)))

fs_icon = ImageTk.PhotoImage(
    Image.open(os.path.join(IMG_DIR, "logofullscreen_2.png")).resize((20, 20))
)

# Audio & background music
correct_sfx = None
wrong_sfx = None
music_ok = False

if audio_ok:
    try:
        correct_sfx = pygame.mixer.Sound(os.path.join(AUDIO_DIR, "correct.wav"))
        correct_sfx.set_volume(0.7)
    except Exception:
        pass
    try:
        wrong_sfx = pygame.mixer.Sound(os.path.join(AUDIO_DIR, "wrong.wav"))
        wrong_sfx.set_volume(0.7)
    except Exception:
        pass
    try:
        pygame.mixer.music.load(os.path.join(AUDIO_DIR, "background_music.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        music_ok = True
    except Exception:
        pass

# State
level = ""
answer = 0
attempts = 0
score = 0
q_num = 0
first_try = 0
is_fullscreen = False
syncing = False


def set_volume(val):
    global syncing
    if syncing:
        return
    vol = int(float(val))
    if audio_ok and music_ok:
        pygame.mixer.music.set_volume(vol / 100)
    syncing = True
    for s in sliders:
        if s.get() != vol:
            s.set(vol)
    syncing = False


def draw_progress(w=610, h=12):
    progress.delete("all")
    progress.create_rectangle(0, 0, w, h, fill=LIGHT_PURPLE, outline="")
    progress.create_rectangle(0, 0, w * q_num / 10, h, fill=PURPLE, outline="")


def place_ui(w, h):
    sx = w / 900
    sy = h / 550

    def p(widget, x, y, width=None, height=None):
        kw = {"x": int(x * sx), "y": int(y * sy)}
        if width is not None:
            kw["width"] = int(width * sx)
        if height is not None:
            kw["height"] = int(height * sy)
        widget.place(**kw)

    for frm in frames:
        frm.config(width=w, height=h)
    for bg_lbl in bg_labels:
        bg_lbl.place(x=0, y=0, width=w, height=h)

    # Menu
    p(welcome_lbl, 45, 85, 400, 35)
    p(title_lbl, 45, 115, 500, 65)
    p(line_frm, 48, 183, 230, max(2, int(5 * sy)) / sy)
    p(tagline_lbl, 45, 195, 420, 30)
    p(subtitle_lbl, 45, 235, 430, 30)
    p(start_btn, 45, 290, 160, 42)
    p(help_btn, 220, 290, 160, 42)
    p(exit_btn, 395, 290, 100, 42)
    p(info_title_lbl, 714, 65, 165, 35)
    p(info_body_lbl, 714, 105, 165, 190)
    p(btn_easy, 115, 439, 160, 20)
    p(btn_mod, 293, 439, 160, 20)
    p(btn_adv, 471, 439, 160, 20)
    p(example_lbl, 650, 345, 240, 130)

    # Help
    p(help_title_lbl, 45, 65, 450, 50)
    p(help_body_lbl, 50, 130, 560, 260)
    p(help_side_lbl, 718, 65, 165, 30)
    p(help_back_btn, 730, 265, 140, 32)

    # Quiz
    p(q_num_lbl, 50, 88, 250, 35)
    p(lvl_lbl, 475, 88, 190, 35)
    p(percent_lbl, 50, 125, 150, 20)
    bar_w = max(1, int(610 * sx))
    bar_h = max(4, int(12 * sy))
    progress.config(width=bar_w, height=bar_h)
    progress.place(x=int(50 * sx), y=int(148 * sy))
    draw_progress(bar_w, bar_h)
    p(q_panel, 55, 180, 610, 95)
    q_label.place(relx=0.5, rely=0.5, anchor=CENTER)
    p(enter_lbl, 55, 295, 170, 32)
    p(ans_entry, 225, 295, 150, 32)
    p(attempt_lbl, 55, 335, 200, 25)
    p(feedback_lbl, 55, 360, 420, 25)
    p(submit_btn, 495, 292, 150, 35)
    p(next_btn, 495, 335, 150, 32)
    p(quiz_side_lbl, 725, 55, 140, 25)
    p(score_lbl, 725, 95, 140, 48)
    p(done_lbl, 725, 150, 140, 60)
    p(quiz_back_btn, 735, 235, 120, 28)

    # Results
    p(res_title_lbl, 45, 65, 500, 50)
    p(res_sub_lbl, 45, 140, 250, 30)
    p(final_score_lbl, 45, 175, 300, 55)
    p(grade_lbl, 370, 175, 220, 45)
    p(first_try_lbl, 45, 245, 400, 35)
    p(diff_lbl, 45, 280, 300, 30)
    p(play_again_btn, 45, 335, 150, 40)
    p(res_menu_btn, 210, 335, 150, 40)
    p(res_exit_btn, 375, 335, 100, 40)

    # Bottom-right music slider + fullscreen button on every page
    btn_w, btn_h = int(36 * sx), int(30 * sy)
    sld_w, sld_h = int(135 * sx), max(32, int(38 * sy))
    lbl_h = int(18 * sy)

    fs_x = w - btn_w - int(12 * sx)
    fs_y = h - btn_h - int(12 * sy)
    sld_x = fs_x - sld_w - int(10 * sx)
    sld_y = h - sld_h - int(10 * sy)
    lbl_y = sld_y - lbl_h - int(2 * sy)

    for lbl, sld, btn in bottom_controls:
        lbl.place(x=sld_x, y=lbl_y, width=sld_w, height=lbl_h)
        sld.place(x=sld_x, y=sld_y, width=sld_w, height=sld_h)
        btn.place(x=fs_x, y=fs_y, width=btn_w, height=btn_h)


def toggle_fullscreen():
    global is_fullscreen, main_bg, quiz_bg
    is_fullscreen = not is_fullscreen

    if is_fullscreen:
        root.resizable(1, 1)
        root.attributes("-fullscreen", True)
        root.update_idletasks()
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    else:
        root.attributes("-fullscreen", False)
        root.geometry("900x550")
        root.resizable(0, 0)
        w, h = 900, 550

    main_bg = ImageTk.PhotoImage(bg_open.resize((w, h)))
    quiz_bg = ImageTk.PhotoImage(quiz_bg_open.resize((w, h)))
    menu_bg_lbl.config(image=main_bg)
    for bg_lbl in (help_bg_lbl, quiz_bg_lbl, results_bg_lbl):
        bg_lbl.config(image=quiz_bg)

    place_ui(w, h)


def switch_frame(frame):
    frame.tkraise()


def exit_quiz():
    if messagebox.askyesno("Exit Maths Quiz", "Are you sure you want to exit?"):
        root.destroy()


def go_to_menu():
    global level, score, q_num, attempts, first_try
    level = ""
    score = q_num = attempts = first_try = 0
    for b in (btn_easy, btn_mod, btn_adv):
        b.config(text="CONFIRM", bg=WHITE)
    example_lbl.config(text="")
    switch_frame(menu_frame)


def confirm_return():
    if messagebox.askyesno("Return to Menu", "Are you sure you want to return to the main menu?"):
        go_to_menu()


def select_level(chosen):
    global level
    level = chosen
    for b in (btn_easy, btn_mod, btn_adv):
        b.config(text="CONFIRM", bg=WHITE)

    examples = {
        "Easy": (btn_easy, "EASY\nAddition and subtraction\n\n8 + 5 = ?\nAnswer: 13"),
        "Moderate": (btn_mod, "MODERATE\nMultiplication and division\n\n48 ÷ 6 + 12 = ?\nAnswer: 20"),
        "Advanced": (btn_adv, "ADVANCED\nMulti-step BODMAS questions\n\n2400 ÷ 12 × 3 = ?\nAnswer: 600"),
    }
    btn, txt = examples[chosen]
    btn.config(text="SELECTED", bg=LIGHT_PURPLE)
    example_lbl.config(text=txt)


def get_number(lvl):
    if lvl == "Easy":
        return random.randint(1, 9)
    if lvl == "Moderate":
        return random.randint(10, 99)
    return random.randint(1000, 9999)


def get_operation(lvl):
    if lvl == "Easy":
        return random.choice(["+", "-"])
    if lvl == "Moderate":
        return random.choice(["+", "-", "*", "/"])
    return "mixed"


def load_question():
    global answer, attempts
    attempts = 0
    n1, n2 = get_number(level), get_number(level)
    op = get_operation(level)

    if op == "+":
        answer, q_text = n1 + n2, f"{n1} + {n2} = ?"
    elif op == "-":
        if n2 > n1:
            n1, n2 = n2, n1
        answer, q_text = n1 - n2, f"{n1} - {n2} = ?"
    elif op == "*":
        answer, q_text = n1 * n2, f"{n1} × {n2} = ?"
    elif op == "/":
        div = random.randint(2, 9)
        quot = get_number(level)
        answer, q_text = quot, f"{quot * div} ÷ {div} = ?"
    else:
        mult, div = random.randint(2, 9), random.randint(2, 9)
        answer, q_text = n1 * mult, f"{n1} × {mult * div} ÷ {div} = ?"

    q_label.config(text=q_text)
    q_num_lbl.config(text=f"QUESTION {q_num} / 10")
    lvl_lbl.config(text=f"{level.upper()} LEVEL")
    percent_lbl.config(text=f"{(q_num - 1) * 10}% COMPLETE")
    done_lbl.config(text=f"QUESTIONS\nCOMPLETED\n{q_num - 1} / 10")
    score_lbl.config(text=f"SCORE\n{score} / 100")
    attempt_lbl.config(text="ATTEMPT 1 OF 2")
    feedback_lbl.config(text="You have two chances. Good luck!", fg=GREY)

    ans_entry.config(state="normal")
    ans_entry.delete(0, END)
    ans_entry.focus()
    submit_btn.config(state="normal")
    next_btn.config(state="disabled")

    if is_fullscreen:
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        draw_progress(max(1, int(610 * (w / 900))), max(4, int(12 * (h / 550))))
    else:
        draw_progress(610, 12)


def start_quiz():
    global score, q_num, attempts, first_try
    if level == "":
        messagebox.showwarning("Choose Difficulty", "Please confirm a difficulty first.")
        return
    score = attempts = first_try = 0
    q_num = 1
    load_question()
    switch_frame(quiz_frame)


def next_question():
    global q_num
    q_num += 1
    if q_num > 10:
        show_results()
        switch_frame(results_frame)
    else:
        load_question()


def check_answer(event=None):
    global attempts, score, first_try
    if attempts >= 2:
        return

    try:
        user_ans = int(ans_entry.get())
    except ValueError:
        feedback_lbl.config(text="Please enter a whole number.", fg="red")
        return

    attempts += 1
    attempt_lbl.config(text=f"ATTEMPT {attempts} OF 2")

    if user_ans == answer:
        if audio_ok and correct_sfx:
            correct_sfx.play()
        pts = 10 if attempts == 1 else 5
        score += pts
        if attempts == 1:
            first_try += 1
        feedback_lbl.config(text=f"Correct! You earned {pts} points.", fg="green")
        score_lbl.config(text=f"SCORE\n{score} / 100")
        ans_entry.config(state="disabled")
        submit_btn.config(state="disabled")
        next_btn.config(state="normal")
    elif attempts == 1:
        if audio_ok and wrong_sfx:
            wrong_sfx.play()
        feedback_lbl.config(text="Not quite! Try one more time.", fg="red")
        ans_entry.delete(0, END)
        ans_entry.focus()
    else:
        if audio_ok and wrong_sfx:
            wrong_sfx.play()
        feedback_lbl.config(text=f"Incorrect! Answer: {answer}", fg="red")
        ans_entry.config(state="disabled")
        submit_btn.config(state="disabled")
        next_btn.config(state="normal")


def show_results():
    grades = [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D")]
    grade = next((g for cut, g in grades if score >= cut), "F")
    final_score_lbl.config(text=f"{score} / 100")
    grade_lbl.config(text=f"GRADE: {grade}")
    first_try_lbl.config(text=f"Correct on first attempt: {first_try} / 10")
    diff_lbl.config(text=f"Difficulty: {level}")


def play_again():
    global score, q_num, attempts, first_try
    score = attempts = first_try = 0
    q_num = 1
    load_question()
    switch_frame(quiz_frame)


def add_bottom_controls(parent):
    lbl = Label(parent, text="MUSIC VOLUME", bg=PURPLE, fg=DARK, font=("Nunito", 7, "bold"))
    sld = Scale(
        parent, from_=0, to=100, orient=HORIZONTAL, command=set_volume,
        bg=PURPLE, fg=DARK, troughcolor=LIGHT_PURPLE, activebackground=DARK_PURPLE,
        highlightthickness=0, relief="flat"
    )
    sld.set(50)
    btn = Button(parent, image=fs_icon, command=toggle_fullscreen, bg=PURPLE, activebackground=LIGHT_PURPLE, relief="flat")
    sliders.append(sld)
    bottom_controls.append((lbl, sld, btn))


frames = []
bg_labels = []
sliders = []
bottom_controls = []

# Frame 1: Menu
menu_frame = Frame(root, width=900, height=550)
menu_frame.place(x=0, y=0)
menu_bg_lbl = Label(menu_frame, image=main_bg, bd=0)
frames.append(menu_frame)
bg_labels.append(menu_bg_lbl)

welcome_lbl = Label(menu_frame, text="WELCOME TO", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 17, "bold"), anchor="w")
title_lbl = Label(menu_frame, text="MATHS QUIZ", bg=WHITE, fg=DARK, font=("Nunito", 35, "bold"), anchor="w")
line_frm = Frame(menu_frame, bg=PURPLE)
tagline_lbl = Label(menu_frame, text="TEST YOUR BRAIN. BEAT THE CHALLENGE.", bg=WHITE, fg=GREY, font=("Nunito", 10, "bold"), anchor="w")
subtitle_lbl = Label(menu_frame, text="Choose your difficulty below and get ready!", bg=WHITE, fg=DARK, font=("Nunito", 11), anchor="w")
start_btn = Button(menu_frame, text="START QUIZ", command=start_quiz, bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat")
help_btn = Button(menu_frame, text="HOW TO PLAY", command=lambda: switch_frame(help_frame), bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat")
exit_btn = Button(menu_frame, text="EXIT", command=exit_quiz, bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat")
info_title_lbl = Label(menu_frame, text="QUIZ INFORMATION", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 10, "bold"))
info_body_lbl = Label(menu_frame, text="10 QUESTIONS\n\nChoose a difficulty.\n\nYou get two attempts.\n\nEarn points for correct answers.", bg=WHITE, fg=DARK, font=("Nunito", 9))
btn_easy = Button(menu_frame, text="CONFIRM", command=lambda: select_level("Easy"), bg=WHITE, fg=DARK_PURPLE, activebackground=LIGHT_PURPLE, font=("Nunito", 8, "bold"), relief="flat")
btn_mod = Button(menu_frame, text="CONFIRM", command=lambda: select_level("Moderate"), bg=WHITE, fg=DARK_PURPLE, activebackground=LIGHT_PURPLE, font=("Nunito", 8, "bold"), relief="flat")
btn_adv = Button(menu_frame, text="CONFIRM", command=lambda: select_level("Advanced"), bg=WHITE, fg=DARK_PURPLE, activebackground=LIGHT_PURPLE, font=("Nunito", 8, "bold"), relief="flat")
example_lbl = Label(menu_frame, text="", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 12, "bold"), justify=CENTER)
add_bottom_controls(menu_frame)

# Frame 2: How to Play
help_frame = Frame(root, width=900, height=550)
help_frame.place(x=0, y=0)
help_bg_lbl = Label(help_frame, image=quiz_bg, bd=0)
frames.append(help_frame)
bg_labels.append(help_bg_lbl)

help_title_lbl = Label(help_frame, text="HOW TO PLAY", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 25, "bold"), anchor="w")
help_body_lbl = Label(
    help_frame,
    text=(
        "1. Choose Easy, Moderate or Advanced.\n"
        "2. Press START QUIZ.\n"
        "3. Answer all 10 questions.\n"
        "4. You get two attempts for each question.\n"
        "5. A correct first answer earns 10 points.\n"
        "6. A correct second answer earns 5 points.\n"
        "7. Try to get the highest score possible!"
    ),
    bg=WHITE, fg=DARK, font=("Nunito", 12), justify=LEFT, anchor="nw"
)
help_side_lbl = Label(help_frame, text="QUIZ MENU", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 10, "bold"))
help_back_btn = Button(help_frame, text="BACK TO MENU", command=lambda: switch_frame(menu_frame), bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat")
add_bottom_controls(help_frame)

# Frame 3: Quiz
quiz_frame = Frame(root, width=900, height=550)
quiz_frame.place(x=0, y=0)
quiz_bg_lbl = Label(quiz_frame, image=quiz_bg, bd=0)
frames.append(quiz_frame)
bg_labels.append(quiz_bg_lbl)

q_num_lbl = Label(quiz_frame, text="QUESTION 1 / 10", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 14, "bold"), anchor="w")
lvl_lbl = Label(quiz_frame, text="EASY LEVEL", bg=WHITE, fg=GREY, font=("Nunito", 11, "bold"))
percent_lbl = Label(quiz_frame, text="0% COMPLETE", bg=WHITE, fg=GREY, font=("Nunito", 9, "bold"), anchor="w")
progress = Canvas(quiz_frame, width=610, height=12, bg=WHITE, highlightthickness=0)
q_panel = Frame(quiz_frame, bg=PALE_PURPLE)
q_label = Label(q_panel, text="", bg=PALE_PURPLE, fg=DARK, font=("Nunito", 25, "bold"))
enter_lbl = Label(quiz_frame, text="ENTER YOUR ANSWER:", bg=WHITE, fg=DARK, font=("Nunito", 10, "bold"), anchor="w")
ans_entry = Entry(quiz_frame, font=("Nunito", 15), justify=CENTER)
ans_entry.bind("<Return>", check_answer)
attempt_lbl = Label(quiz_frame, text="ATTEMPT 1 OF 2", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 9, "bold"), anchor="w")
feedback_lbl = Label(quiz_frame, text="You have two chances. Good luck!", bg=WHITE, fg=GREY, font=("Nunito", 9), anchor="w")
submit_btn = Button(quiz_frame, text="SUBMIT ANSWER", command=check_answer, bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat")
next_btn = Button(quiz_frame, text="NEXT QUESTION", command=next_question, bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat", state="disabled")
quiz_side_lbl = Label(quiz_frame, text="QUIZ MENU", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 15, "bold"))
score_lbl = Label(quiz_frame, text="SCORE\n0 / 100", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 10, "bold"))
done_lbl = Label(quiz_frame, text="QUESTIONS\nCOMPLETED\n0 / 10", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 8, "bold"))
quiz_back_btn = Button(quiz_frame, text="BACK TO MENU", command=confirm_return, bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat")
add_bottom_controls(quiz_frame)

# Frame 4: Results
results_frame = Frame(root, width=900, height=550)
results_frame.place(x=0, y=0)
results_bg_lbl = Label(results_frame, image=quiz_bg, bd=0)
frames.append(results_frame)
bg_labels.append(results_bg_lbl)

res_title_lbl = Label(results_frame, text="QUIZ COMPLETED!", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 25, "bold"), anchor="w")
res_sub_lbl = Label(results_frame, text="YOUR FINAL SCORE", bg=WHITE, fg=GREY, font=("Nunito", 12, "bold"), anchor="w")
final_score_lbl = Label(results_frame, text="0 / 100", bg=WHITE, fg=DARK, font=("Nunito", 32, "bold"), anchor="w")
grade_lbl = Label(results_frame, text="GRADE: F", bg=WHITE, fg=DARK_PURPLE, font=("Nunito", 20, "bold"), anchor="w")
first_try_lbl = Label(results_frame, text="Correct on first attempt: 0 / 10", bg=WHITE, fg=DARK, font=("Nunito", 12), anchor="w")
diff_lbl = Label(results_frame, text="Difficulty: ", bg=WHITE, fg=DARK, font=("Nunito", 11), anchor="w")
play_again_btn = Button(results_frame, text="PLAY AGAIN", command=play_again, bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat")
res_menu_btn = Button(results_frame, text="MAIN MENU", command=go_to_menu, bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat")
res_exit_btn = Button(results_frame, text="EXIT", command=exit_quiz, bg=PURPLE, fg=DARK, activebackground=LIGHT_PURPLE, font=("Nunito", 10, "bold"), relief="flat")
add_bottom_controls(results_frame)

place_ui(900, 550)
switch_frame(menu_frame)
root.mainloop()