import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

import sv_ttk
import pywinstyles

def open_add_game(parent, on_game_added=None): # Pass retive_data as a callback

   # -- Functions --

    def Save():

        # Retrieves data from entry boxes
        name = nameEntry.get()
        rating = spinval.get()
        description = descriptionEntry.get("1.0", "end-1c")  # Get text from Text widget
        genre = genre_selected.get()


        # Saves data to database
        connection = sqlite3.connect("database.db")

        with connection:
            try:
            
                connection.execute("INSERT INTO main(name,rating,description,genre) VALUES (?, ?, ?, ?);", (name, rating, description, genre))
                connection.commit()

                messagebox.showinfo(title=f"{name} Saved!", message=f"{name} has been saved successfully!")

                add_gameWin.destroy()  # Close the add game window

            except sqlite3.IntegrityError:
                messagebox.showerror(title="Data not saved!", message="The data you have entered has not been saved! Make sure you have filled in all fields")

        connection.close()

        if on_game_added:
            on_game_added()  # Call the callback after saving


    # -- Main Code --

    add_gameWin = tk.Toplevel(parent)
    add_gameWin.geometry("705x625")
    add_gameWin.resizable(False, False)
    add_gameWin.title("Add Game")
    add_gameWin.iconbitmap("img/blocks.ico")
    pywinstyles.apply_style(add_gameWin, "acrylic")
    sv_ttk.set_theme("dark")


    # -- Game Name Entry --    

    #Functions used to handle the default text in entry boxes
    def handle_focus_in(event, default_text):
        if nameEntryVar.get() == default_text:
            nameEntryVar.set("")
            nameEntry.configure(foreground="white")

    def handle_focus_out(event, default_text):
        if nameEntryVar.get() == "":
            nameEntryVar.set(default_text)
            nameEntry.configure(foreground="gray")



    nameEntryFrame = ttk.Frame(add_gameWin)
    nameEntryFrame.place(x=50, y=20, width=605, height= 60)

    nameEntryVar = tk.StringVar(value="Game Name")
    nameEntry = ttk.Entry(add_gameWin, textvariable = nameEntryVar, font = "Verdana 15", justify="center")
    nameEntry.configure(foreground="grey")  # Set initial to grey for placeholder

    nameEntry.bind("<FocusIn>", lambda event: handle_focus_in(event, "Game Name"))
    nameEntry.bind("<FocusOut>", lambda event: handle_focus_out(event, "Game Name"))
    nameEntry.place(x=55, y=25, width=430, height=50)


    # -- Rating Spinbox --

    spinbox_style = ttk.Style(add_gameWin)
    spinbox_style.configure("Rating.TSpinbox", fieldbackground="green")

    spinval = tk.StringVar()
    spinval.set("5.0")  # Set initial value to 0.0
    rating_spinbox = ttk.Spinbox(add_gameWin, from_=0.0, to=10.0, increment=0.1, textvariable=spinval, style="Rating.TSpinbox", justify="center")
    rating_spinbox.config(font="Verdana 23", width=20, state="readonly", wrap=False)
    rating_spinbox.place(x=490, y=25, width=160, height=50)


    def get_fade_color(val):
        # Clamp value between 0 and 10
        val = max(0, min(10, val))
        if val <= 5:
            # Fade from red (255,0,0) to black (0,0,0)
            ratio = val / 5
            r = int(20 * (1 - ratio))
            g = 0
            b = 0
        else:
            # Fade from black (0,0,0) to green (0,255,0)
            ratio = (val - 5) / 5
            r = 0
            g = int(20 * ratio)
            b = 0
        return f'#{r:02x}{g:02x}{b:02x}'

    def on_spinbox_change(*args):
        try:
            val = float(spinval.get())
        except ValueError:
            val = 0
        color = get_fade_color(val)
        add_gameWin.config(bg=color)
        spinbox_style.configure("Rating.TSpinbox", fieldbackground=color)

    spinval.trace_add("write", on_spinbox_change)


    # -- Description Entry --

    description_frame = ttk.Labelframe(add_gameWin, text="Description", padding=(5, 5))
    description_frame.place(x=50, y=150, width=605, height=150)

    descriptionEntry = tk.Text(description_frame, wrap="word", font="Verdana 15", fg="white", bg="#2C2C2C", relief="flat", highlightthickness=0)
    descriptionEntry.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    # -- Genre --

    genre_options = [ 
        "Select Genre",  # Default text
        "Action", 
        "Adventure",
        "RPGs",
        "Simulation",
        "Sports",
        "Puzzle",
        "Horror",
        "Platformer",
        "Fighting",
        "Racing",
        "Shooter",
        "Sandbox",
        "MMORPG",
        "MOBA",
        "Survival",
    ]

    genre_selected = tk.StringVar()
    genre_selected.set("Select Genre")  # Default text

    genre = ttk.OptionMenu(add_gameWin , genre_selected , *genre_options)
    genre.place(x=50, y=350, width = 605, height = 50)

    genre_menu = genre["menu"]
    genre_menu.config(font=("Segoe UI", 12)) # Change font of dropdown items


    # -- Save Button --

    save_button_style1 = ttk.Style(add_gameWin)
    save_button_style1.configure("Green.TButton", background="green", foreground="green", font="Verdana 18 bold")

    save_button_style2 = ttk.Style(add_gameWin)
    save_button_style2.configure("Grey.TButton", background="grey", foreground="grey", font="Verdana 18")

    def save_button_enter(event):
        save_button.configure(style="Green.TButton")  # Change button color on hover

    def save_button_leave(event):
        save_button.configure(style="Grey.TButton")  # Change button color on hover

    save_button = ttk.Button(add_gameWin, text="Save", command=Save, style="Grey.TButton")
    save_button.place(x=252.5, y=500, width=200, height=60)

    save_button.bind("<Enter>", lambda event: save_button_enter(event))
    save_button.bind("<Leave>", lambda event: save_button_leave(event)) 



    return add_gameWin #Returns the window status so that it can be closed later from logun window
