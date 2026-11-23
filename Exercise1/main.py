
import tkinter as tk
from tkinter import messagebox
import random
import os
import tkinter.font as tkfont
from PIL import Image, ImageTk
# ---------------- WINDOW SETUP ----------------

window = tk.Tk()
window.title("Maths Quiz")
window.geometry("900x550")
window.resizable(False, False)

BASE_WIDTH = 900
BASE_HEIGHT = 550

folderPath = os.path.dirname(os.path.abspath(__file__))

# Set the small feather logo as the application/window icon.
# Keep iconImage as a variable so Tkinter does not discard the image.
# Set the calculator logo in the Windows title bar
# Load calculator icon for the window title bar
iconPath = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "app_icon.ico"
)

window.iconbitmap(iconPath) 

mainImage = tk.PhotoImage(
    file=os.path.join(folderPath, "background.png")
)

quizImage = tk.PhotoImage(
    file=os.path.join(folderPath, "quiz_background.png")
)

background = tk.Label(window, image=mainImage, bd=0)
background.place(x=0, y=0, width=BASE_WIDTH, height=BASE_HEIGHT)
currentBackgroundPath = os.path.join(folderPath, "background.png")
fullscreenBackground = None

# ---------------- COLOURS AND FONTS ----------------

PURPLE = "#A98AEF"
LIGHT_PURPLE = "#D8C8FF"
DARK_PURPLE = "#38245E"
DARK = "#211735"
WHITE = "#FFFFFF"
GREY = "#777777"
PALE_PURPLE = "#F1EAFE"

TITLE_FONT = ("Nunito", 35, "bold")
BUTTON_FONT = ("Nunito", 10, "bold")
QUESTION_FONT = ("Nunito", 25, "bold")

# ---------------- QUIZ VARIABLES ----------------

currentLevel = ""
correctAnswer = 0
attempts = 0
score = 0
questionNumber = 0
firstTryCorrect = 0
pendingQuestion = None

screenWidgets = []
difficultyButtons = []

answerEntry = None
submitButton = None
feedbackLabel = None
attemptLabel = None
scoreLabel = None
progressCanvas = None
isFullscreen = False


# ---------------- FULL SCREEN CONTROL ----------------

def getScaleFactors():
    """Return the current horizontal and vertical layout scale."""
    width = max(1, window.winfo_width())
    height = max(1, window.winfo_height())

    return width / BASE_WIDTH, height / BASE_HEIGHT


def resizeBackground():
    """Resize the active background image to cover the whole window."""
    global fullscreenBackground

    if isFullscreen:
        width = max(1, window.winfo_width())
        height = max(1, window.winfo_height())

        image = Image.open(currentBackgroundPath).convert("RGB")
        image = image.resize(
            (width, height),
            Image.Resampling.LANCZOS
        )

        fullscreenBackground = ImageTk.PhotoImage(image)
        background.config(image=fullscreenBackground)
        background.place(x=0, y=0, width=width, height=height)
    else:
        fullscreenBackground = None

        if os.path.basename(currentBackgroundPath) == "background.png":
            background.config(image=mainImage)
        else:
            background.config(image=quizImage)

        background.place(x=0, y=0, width=BASE_WIDTH, height=BASE_HEIGHT)


def scaleWidget(widget):
    """Apply scaled position, size, font and wrapping to one widget."""
    if not widget.winfo_exists():
        return

    scaleX, scaleY = getScaleFactors()
    fontScale = min(scaleX, scaleY)

    basePlace = getattr(widget, "_base_place", None)

    if basePlace:
        widget.place_configure(
            x=round(basePlace["x"] * scaleX),
            y=round(basePlace["y"] * scaleY),
            width=max(1, round(basePlace["width"] * scaleX)),
            height=max(1, round(basePlace["height"] * scaleY))
        )

    baseFont = getattr(widget, "_base_font", None)

    if baseFont:
        try:
            actual = tkfont.Font(root=window, font=baseFont).actual()
            scaledSize = max(7, round(abs(int(actual["size"])) * fontScale))

            widget.configure(font=(
                actual["family"],
                scaledSize,
                actual["weight"],
                actual["slant"],
                actual["underline"],
                actual["overstrike"]
            ))
        except (tk.TclError, TypeError, ValueError):
            pass

    baseWraplength = getattr(widget, "_base_wraplength", None)

    if baseWraplength is not None:
        try:
            widget.configure(
                wraplength=max(1, round(baseWraplength * scaleX))
            )
        except tk.TclError:
            pass


def applyFullscreenLayout():
    """Scale every registered widget to fit the current screen."""
    resizeBackground()

    for widget in screenWidgets:
        scaleWidget(widget)

    if progressCanvas is not None and progressCanvas.winfo_exists():
        updateProgress()


def toggleFullscreen():
    """Switch between the original window and a screen-filling layout."""
    global isFullscreen

    isFullscreen = not isFullscreen

    if isFullscreen:
        window.attributes("-fullscreen", True)
    else:
        window.attributes("-fullscreen", False)
        window.geometry(f"{BASE_WIDTH}x{BASE_HEIGHT}")

    window.update_idletasks()
    applyFullscreenLayout()


def leaveFullscreen(event=None):
    """Allow Escape to leave fullscreen mode."""
    if isFullscreen:
        toggleFullscreen()


def addFullscreenButton():
    """Add the fullscreen toggle to the current screen."""
    button = tk.Button(
        window,
        text="⛶",
        command=toggleFullscreen,
        bg=PURPLE,
        fg=DARK,
        activebackground=LIGHT_PURPLE,
        font=("Arial", 13, "bold"),
        relief="flat",
        cursor="hand2"
    )

    button.place(x=850, y=5, width=38, height=28)
    addWidget(button)


# ---------------- SCREEN HELPERS ----------------

def addWidget(widget, trackPlace=True):
    screenWidgets.append(widget)

    if trackPlace:
        info = widget.place_info()

        if info and "x" in info and "y" in info:
            try:
                widget._base_place = {
                    "x": float(info.get("x", 0)),
                    "y": float(info.get("y", 0)),
                    "width": float(info.get("width", widget.winfo_reqwidth())),
                    "height": float(info.get("height", widget.winfo_reqheight()))
                }
            except (TypeError, ValueError):
                widget._base_place = None

    try:
        widget._base_font = widget.cget("font")
    except tk.TclError:
        widget._base_font = None

    try:
        wraplength = int(widget.cget("wraplength"))
        widget._base_wraplength = wraplength if wraplength > 0 else None
    except (tk.TclError, TypeError, ValueError):
        widget._base_wraplength = None

    if isFullscreen:
        scaleWidget(widget)

    return widget


def changeBackground(image):
    global currentBackgroundPath

    if image == mainImage:
        currentBackgroundPath = os.path.join(folderPath, "background.png")
    else:
        currentBackgroundPath = os.path.join(folderPath, "quiz_background.png")

    if isFullscreen:
        resizeBackground()
    else:
        background.config(image=image)


def clearScreen():

    global pendingQuestion, progressCanvas

    if pendingQuestion is not None:
        window.after_cancel(pendingQuestion)
        pendingQuestion = None

    for widget in screenWidgets:
        try:
            if widget.winfo_exists():
                widget.destroy()
        except tk.TclError:
            pass

    screenWidgets.clear()
    progressCanvas = None
    difficultyButtons.clear()


def makeButton(text, command, x, y, width, height):

    button = tk.Button(
        window,
        text=text,
        command=command,
        bg=PURPLE,
        fg=DARK,
        activebackground=LIGHT_PURPLE,
        activeforeground=DARK,
        font=BUTTON_FONT,
        relief="flat",
        cursor="hand2"
    )

    button.place(x=x, y=y, width=width, height=height)
    return addWidget(button)


def makeLabel(text, x, y, width, height,
              size=12, colour=DARK, bold=False,
              backgroundColour=WHITE, justify="left"):

    label = tk.Label(
        window,
        text=text,
        bg=backgroundColour,
        fg=colour,
        font=("Nunito", size, "bold" if bold else "normal"),
        justify=justify,
        anchor="center" if justify == "center" else "w",
        wraplength=width - 12
    )

    label.place(x=x, y=y, width=width, height=height)
    return addWidget(label)


# ---------------- MAIN MENU ----------------

def displayMenu():

    global currentLevel, score, questionNumber
    global attempts, firstTryCorrect

    clearScreen()
    changeBackground(mainImage)

    currentLevel = ""
    score = 0
    questionNumber = 0
    attempts = 0
    firstTryCorrect = 0

    makeLabel("WELCOME TO", 45, 85, 400, 35,
              17, DARK_PURPLE, True)

    makeLabel("MATHS QUIZ", 45, 115, 500, 65,
              35, DARK, True)

    line = tk.Frame(window, bg=PURPLE)
    line.place(x=48, y=183, width=230, height=5)
    addWidget(line)

    makeLabel(
        "TEST YOUR BRAIN. BEAT THE CHALLENGE.",
        45, 195, 420, 30, 10, GREY, True
    )

    makeLabel(
        "Choose your difficulty below and get ready!",
        45, 235, 430, 30, 11, DARK
    )

    makeButton("START QUIZ", startQuiz, 45, 290, 160, 42)
    makeButton("HOW TO PLAY", howToPlay, 220, 290, 160, 42)
    makeButton("EXIT", exitQuiz, 395, 290, 100, 42)

    makeLabel(
        "QUIZ INFORMATION",
        714, 65, 165, 35, 10,
        DARK_PURPLE, True, WHITE, "center"
    )

    makeLabel(
        "10 QUESTIONS\n\nChoose a difficulty.\n\n"
        "You get two attempts.\n\nEarn points for correct answers.",
        714, 105, 165, 190, 9,
        DARK, False, WHITE, "center"
    )

    createDifficultyButtons()
    addFullscreenButton()


# ---------------- DIFFICULTY BUTTONS ----------------

def createDifficultyButtons():

    levels = ["Easy", "Moderate", "Advanced"]
    positions = [112, 290, 468]

    for i, level in enumerate(levels):

        button = tk.Button(
            window,
            text="CONFIRM",
            command=lambda selected=level: chooseDifficulty(selected),
            bg=WHITE,
            fg=DARK_PURPLE,
            activebackground=LIGHT_PURPLE,
            font=("Nunito", 8, "bold"),
            relief="flat",
            cursor="hand2"
        )

        button.place(x=positions[i] + 3, y=439, width=160, height=20)
        button.level = level

        addWidget(button)
        difficultyButtons.append(button)


def chooseDifficulty(level):

    global currentLevel

    currentLevel = level

    for button in difficultyButtons:
        if button.level == level:
            button.config(text="SELECTED", bg=LIGHT_PURPLE)
        else:
            button.config(text="CONFIRM", bg=WHITE)

    for widget in screenWidgets[:]:
        if getattr(widget, "quizInfo", False):
            widget.destroy()
            screenWidgets.remove(widget)

    examples = {
        "Easy": "EASY\nAddition and subtraction\n\n8 + 5 = ?\nAnswer: 13",
        "Moderate": "MODERATE\nMultiplication and division\n\n48 ÷ 6 + 12 = ?\nAnswer: 20",
        "Advanced": "ADVANCED\nMulti-step BODMAS questions\n\n2400 ÷ 12 × 3 = ?\nAnswer: 600"
    }

    info = tk.Label(
        window,
        text=examples[level],
        bg=WHITE,
        fg=DARK_PURPLE,
        font=("Nunito", 12, "bold"),
        justify="center",
        wraplength=225
    )

    info.place(x=650, y=345, width=240, height=130)
    info.quizInfo = True
    addWidget(info)


# ---------------- HOW TO PLAY ----------------

def howToPlay():

    clearScreen()
    changeBackground(quizImage)

    makeLabel("HOW TO PLAY", 45, 65, 450, 50,
              25, DARK_PURPLE, True)

    instructions = (
        "1. Choose Easy, Moderate or Advanced.\n\n"
        "2. Press START QUIZ.\n\n"
        "3. Answer all 10 questions.\n\n"
        "4. You get two attempts for each question.\n\n"
        "5. A correct first answer earns 10 points.\n\n"
        "6. A correct second answer earns 5 points.\n\n"
        "7. Try to get the highest score possible!"
    )

    makeLabel(instructions, 50, 125, 560, 240, 12, DARK)

    makeLabel(
        "QUIZ MENU", 718, 65, 165, 30,
        10, DARK_PURPLE, True, WHITE, "center"
    )

    makeButton("BACK TO MENU", displayMenu, 742, 265, 115, 30)
    addFullscreenButton()


# ---------------- EXIT ----------------

def exitQuiz():

    if messagebox.askyesno("Exit Maths Quiz", "Are you sure you want to exit?"):
        window.destroy()


# ---------------- RANDOM NUMBER GENERATOR ----------------

def randomInt(level):

    if level == "Easy":
        return random.randint(1, 9)
    elif level == "Moderate":
        return random.randint(10, 99)
    else:
        return random.randint(1000, 9999)


# ---------------- OPERATION GENERATOR ----------------

def decideOperation(level):

    if level == "Easy":
        return random.choice(["+", "-"])
    elif level == "Moderate":
        return random.choice(["+", "-", "*", "/"])
    else:
        return "mixed"


# ---------------- START QUIZ ----------------

def startQuiz():

    global score, questionNumber, attempts, firstTryCorrect

    if currentLevel == "":
        messagebox.showwarning("Choose Difficulty", "Please confirm a difficulty first.")
        return

    clearScreen()
    changeBackground(quizImage)

    score = 0
    questionNumber = 0
    attempts = 0
    firstTryCorrect = 0

    nextQuestion()


# ---------------- NEXT QUESTION ----------------

def nextQuestion():

    global questionNumber, pendingQuestion

    pendingQuestion = None
    questionNumber += 1

    if questionNumber > 10:
        displayResults()
        return

    displayProblem()


# ---------------- PROGRESS BAR ----------------

def updateProgress():

    if progressCanvas is None or not progressCanvas.winfo_exists():
        return

    progressCanvas.delete("all")

    scaleX, scaleY = getScaleFactors()
    canvasWidth = max(1, round(610 * scaleX))
    canvasHeight = max(1, round(12 * scaleY))
    filledWidth = canvasWidth * questionNumber / 10

    progressCanvas.create_rectangle(
        0, 0, canvasWidth, canvasHeight,
        fill=LIGHT_PURPLE, outline=""
    )

    progressCanvas.create_rectangle(
        0, 0, filledWidth, canvasHeight,
        fill=PURPLE, outline=""
    )


# ---------------- DISPLAY QUESTION ----------------

def displayProblem():

    global correctAnswer, attempts
    global answerEntry, submitButton
    global feedbackLabel, attemptLabel
    global scoreLabel, progressCanvas

    attempts = 0
    clearScreen()
    changeBackground(quizImage)

    number1 = randomInt(currentLevel)
    number2 = randomInt(currentLevel)
    operation = decideOperation(currentLevel)

    if operation == "+":
        correctAnswer = number1 + number2
        questionText = str(number1) + " + " + str(number2)

    elif operation == "-":
        if number2 > number1:
            number1, number2 = number2, number1
        correctAnswer = number1 - number2
        questionText = str(number1) + " - " + str(number2)

    elif operation == "*":
        correctAnswer = number1 * number2
        questionText = str(number1) + " × " + str(number2)

    elif operation == "/":
        divisor = random.randint(2, 9)
        quotient = randomInt(currentLevel)
        number1 = quotient * divisor
        correctAnswer = quotient
        questionText = str(number1) + " ÷ " + str(divisor)

    else:
        number3 = random.randint(2, 9)
        multiplier = random.randint(2, 9)
        number2 = number3 * multiplier
        correctAnswer = number1 * multiplier
        questionText = str(number1) + " × " + str(number2) + " ÷ " + str(number3)

    # LEFT QUESTION PANEL

    makeLabel(
        "QUESTION " + str(questionNumber) + " / 10",
        50, 88, 250, 35, 14, DARK_PURPLE, True
    )

    makeLabel(
        currentLevel.upper() + " LEVEL",
        475, 88, 190, 35, 11, GREY, True, WHITE, "center"
    )

    makeLabel(
        str(questionNumber * 10) + "% COMPLETE",
        50, 125, 150, 20, 9, GREY, True
    )

    progressCanvas = tk.Canvas(
        window, width=610, height=12,
        bg=WHITE, highlightthickness=0
    )
    progressCanvas.place(x=50, y=148)
    addWidget(progressCanvas)
    updateProgress()

    questionPanel = tk.Frame(window, bg=PALE_PURPLE)
    questionPanel.place(x=55, y=180, width=610, height=95)
    addWidget(questionPanel)

    question = tk.Label(
        questionPanel,
        text=questionText + " = ?",
        bg=PALE_PURPLE,
        fg=DARK,
        font=QUESTION_FONT
    )
    question.place(relx=0.5, rely=0.5, anchor="center")
    addWidget(question, trackPlace=False)

    makeLabel(
        "ENTER YOUR ANSWER:",
        55, 295, 170, 32, 10, DARK, True
    )

    answerEntry = tk.Entry(
        window, font=("Nunito", 15),
        relief="solid", bd=1, justify="center"
    )
    answerEntry.place(x=225, y=295, width=150, height=32)
    addWidget(answerEntry)
    answerEntry.focus()

    attemptLabel = makeLabel(
        "ATTEMPT 1 OF 2",
        55, 335, 200, 25, 9, DARK_PURPLE, True
    )

    feedbackLabel = makeLabel(
        "You have two chances. Good luck!",
        55, 360, 390, 25, 9, GREY
    )

    # SUBMIT BUTTON MOVED TO BOTTOM RIGHT OF QUESTION PANEL

    submitButton = makeButton(
        "SUBMIT ANSWER",
        submitAnswer,
        495, 335, 150, 35
    )

    answerEntry.bind("<Return>", lambda event: submitAnswer())

    # RIGHT PANEL - SMALLER AND MOVED UP

    makeLabel(
        "QUIZ MENU",
        725, 55, 140, 25,
        15, DARK_PURPLE, True, WHITE, "center"
    )

    scoreLabel = makeLabel(
        "SCORE\n" + str(score) + " / 100",
        725, 95, 140, 48,
        10, DARK_PURPLE, True, WHITE, "center"
    )

    makeLabel(
        "QUESTIONS\nCOMPLETED\n" +
        str(questionNumber - 1) + " / 10",
        725, 150, 140, 60,
        8, DARK_PURPLE, True, WHITE, "center"
    )

    # BACK BUTTON MOVED UP AND MADE SMALLER

    makeButton(
        "BACK TO MENU",
        returnToMenu,
        740, 235, 115, 28
    )
    addFullscreenButton()


# ---------------- SUBMIT ANSWER ----------------

def submitAnswer():

    global attempts, score, firstTryCorrect

    if attempts >= 2:
        return

    try:
        userAnswer = int(answerEntry.get())
    except ValueError:
        feedbackLabel.config(text="Please enter a whole number.", fg="red")
        return

    attempts += 1
    attemptLabel.config(text="ATTEMPT " + str(attempts) + " OF 2")

    if userAnswer == correctAnswer:

        if attempts == 1:
            score += 10
            firstTryCorrect += 1
            feedbackLabel.config(text="Correct! You earned 10 points.", fg="green")
        else:
            score += 5
            feedbackLabel.config(text="Correct! You earned 5 points.", fg="green")

        finishQuestion()

    elif attempts == 1:
        feedbackLabel.config(text="Not quite! Try one more time.", fg="red")
        answerEntry.delete(0, tk.END)
        answerEntry.focus()

    else:
        feedbackLabel.config(
            text="Incorrect! Answer: " + str(correctAnswer),
            fg="red"
        )
        finishQuestion()


# ---------------- FINISH QUESTION ----------------

def finishQuestion():

    answerEntry.config(state="disabled")
    submitButton.config(state="disabled")

    scoreLabel.config(
        text="SCORE\n" + str(score) + " / 100"
    )

    scheduleNext(1400)


def scheduleNext(delay):

    global pendingQuestion
    pendingQuestion = window.after(delay, nextQuestion)


# ---------------- BACK TO MENU ----------------

def returnToMenu():

    if messagebox.askyesno(
        "Return to Menu",
        "Are you sure you want to return to the main menu?"
    ):
        displayMenu()


# ---------------- RESULTS SCREEN ----------------

def displayResults():

    global pendingQuestion

    pendingQuestion = None
    clearScreen()
    changeBackground(quizImage)

    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 50:
        grade = "D"
    else:
        grade = "F"

    makeLabel("QUIZ COMPLETED!", 45, 65, 500, 50,
              25, DARK_PURPLE, True)

    makeLabel("YOUR FINAL SCORE", 45, 140, 250, 30,
              12, GREY, True)

    makeLabel(str(score) + " / 100", 45, 175, 300, 55,
              32, DARK, True)

    makeLabel("GRADE: " + grade, 370, 175, 220, 45,
              20, DARK_PURPLE, True)

    makeLabel(
        "Correct on first attempt: " + str(firstTryCorrect) + " / 10",
        45, 245, 400, 35, 12, DARK
    )

    makeLabel("Difficulty: " + currentLevel,
              45, 280, 300, 30, 11, DARK)

    makeButton("PLAY AGAIN", restartQuiz, 45, 335, 150, 40)
    makeButton("MAIN MENU", displayMenu, 210, 335, 150, 40)
    makeButton("EXIT", exitQuiz, 375, 335, 100, 40)
    addFullscreenButton()


# ---------------- RESTART QUIZ ----------------

def restartQuiz():

    global score, questionNumber, attempts, firstTryCorrect

    score = 0
    questionNumber = 0
    attempts = 0
    firstTryCorrect = 0

    clearScreen()
    changeBackground(quizImage)
    nextQuestion()


# ---------------- RUN PROGRAM ----------------

window.bind("<Escape>", leaveFullscreen)
window.bind("<F11>", lambda event: toggleFullscreen())
displayMenu()
window.mainloop()
