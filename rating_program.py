import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
from pathlib import Path

from add_game import open_add_game  # Import the function to open the add game window
from update_game import open_update_game  # Import the function to open the update game window

import sv_ttk
import pywinstyles


check = Path("database.db")

if not Path.is_file(check): # If the file is not found in the correct location

   connection = sqlite3.connect("database.db")
    
   # Main Table
   connection.execute("""
   CREATE TABLE "main" (
      "gameID"	INTEGER NOT NULL UNIQUE,
      "name"	TEXT NOT NULL,
      "rating"	REAL NOT NULL,
      "description"	TEXT,
      "genre"	TEXT,
      PRIMARY KEY("gameID")
   )
      """)
   
   messagebox.showinfo(title="Database not found!", message="'database.db' is not found, a new database has been created")

   connection.close()



# -- Functions --

def Add_Game():

   open_add_game(root, on_game_added=retrieve_data)

def delete_game():

   game_name = treeview.item(treeview.selection())['values'][0]
   choice = messagebox.askokcancel(title=f"Delete {game_name}", message=f"Are you sure you want to delete {game_name}? This action cannot be undone.")

   if not choice:
      return

   game_id = treeview.item(treeview.selection())['values'][2]

   with sqlite3.connect("database.db") as connection:

      connection.execute("DELETE FROM main WHERE gameID = ?", (game_id, ))
      connection.commit()

      #connection.close()

      retrieve_data()  # Refresh the treeview to reflect the deletion
   

# -- Main Code --

root = tk.Tk() # Create the main window

root.geometry("725x825")
root.title("Game Rating Program")
root.configure(background = "light blue")
root.resizable(False, False)
root.iconbitmap("img/blocks.ico")  # Set the icon for the window
pywinstyles.apply_style(root, "acrylic")


# -- Treeview --


# Function which returns a colour based on a rating value from 0 to 10
def get_fade_color(rating):
   # Clamp rating between 0 and 10
   rating = max(0, min(10, rating))
   if rating <= 5:
      # Fade from red (255,0,0) to black (0,0,0)
      ratio = rating / 5
      r = int(40 * (1 - ratio)) # Ajust max red value
      g = 0
      b = 0
   else:
      # Fade from black (0,0,0) to green (0,255,0)
      ratio = (rating - 5) / 5
      r = 0
      g = int(40 * ratio) # Ajust max green value
      b = 0
   return f'#{r:02x}{g:02x}{b:02x}' # Returns the colour in hex format


# Function detects if a selection is made in the treeview and enables/disables the delete button accordingly
def detect_selection(event):

   selected = treeview.selection()

   connection = sqlite3.connect("database.db")

   with connection:

      if selected:

         DeleteButton.configure(state="normal", image=red_minus_Img)

         cursor = connection.cursor()
         game_ID = treeview.item(treeview.selection())['values'][2]

         cursor.execute("SELECT description FROM main WHERE gameID = ?", (game_ID,))

         descriptionEntry.configure(state="normal")  # Make the text widget editable to update its content
         descriptionEntry.delete(1.0, tk.END)  # Clear existing text
         description = cursor.fetchone()
         if description and description[0]:  # Check if description is not None
            descriptionEntry.insert(tk.END, description[0])  # Insert the description into the text widget
         else:
            descriptionEntry.insert(tk.END, "No description available.")
         descriptionEntry.configure(state="disabled")  # Make the text widget read-only again

      else:
         DeleteButton.configure(state="disabled", image=grey_minus_Img)

         descriptionEntry.configure(state="normal")  # Make the text widget editable to update its content
         descriptionEntry.delete(1.0, tk.END)
         descriptionEntry.insert(tk.END, "")
         descriptionEntry.configure(state="disabled")  # Make the text widget read-only again


# Fetches data from the database and populates the treeview
def retrieve_data():

   # Default values
   game_added_count = 0
   average_rating = 0.0

   order_item = "rating"
   order_direction = "DESC"

   # Sort By
   sort_by = sort_selected.get()

   if sort_by == "Sort By":
      order_item = "rating"
      order_direction = "DESC"

   if sort_by ==  "Rating - Low to High" or sort_by ==  "Rating - High to Low":
      order_item = "rating"
   if sort_by == "Name - A-Z" or sort_by ==  "Name - Z-A":
      order_item = "name"

   if sort_by == "Rating - Low to High" or sort_by ==  "Name - A-Z":
      order_direction = "ASC"
   if sort_by == "Rating - High to Low" or sort_by ==  "Name - Z-A":
      order_direction = "DESC"

   # Genre Filter
   selected_genre = genre_selected.get()

   # Clear existing data in the treeview
   for item in treeview.get_children():
      treeview.delete(item)

   # Connect to the database and fetch data
   connection = sqlite3.connect("database.db")

   with connection:

      cursor = connection.cursor()

      if selected_genre == "All Genres" or selected_genre == "Filter By":
         string = str(f"SELECT * FROM main ORDER BY {order_item} {order_direction};")
         cursor.execute(string)

      else:
         string = str(f"SELECT * FROM main WHERE genre = ? ORDER BY {order_item} {order_direction};")
         cursor.execute(string, (selected_genre,))

      # Putting the fetched data into the treeview
      rows = cursor.fetchall()

      for row in rows:
         rating = float(row[2])  # Assuming row[2] is the rating
         tag_index = int(round(rating * 10))
         tag_name = f"rating_{tag_index}"
         treeview.insert("", "end", text=row[2], values=(row[1], row[4], row[0]), tags=(tag_name,))

         game_added_count += 1
         average_rating += rating

         # Update highest and lowest rating
         if game_added_count == 1:
            highest_rating = rating
            lowest_rating = rating
         else:
            if rating > highest_rating:
               highest_rating = rating
            if rating < lowest_rating:
               lowest_rating = rating



   average_rating = average_rating / game_added_count if game_added_count > 0 else 0.0
   average_rating = round(average_rating, 1)  # Round to 1 decimal place
   
   game_added_value.configure(text=str(game_added_count))  # Update the games added count
   if game_added_count > 0:
      average_rating_value.configure(text=str(average_rating))  # Update the average rating
      highest_rating_value.configure(text=str(highest_rating))  # Update the highest rating
      lowest_rating_value.configure(text=str(lowest_rating))  # Update the lowest rating

   else:
      average_rating_value.configure(text="N/A")  # Update the average rating
      highest_rating_value.configure(text="N/A")  # Update the highest rating
      lowest_rating_value.configure(text="N/A")  # Update the lowest rating


   treeview.selection_remove(treeview.selection())  # <-- Clear selection after refresh
   DeleteButton.configure(state="disabled", image=grey_minus_Img)  # Disable the delete button after refresh


def on_double_click(event):

   try:
      game_id = treeview.item(treeview.selection())['values'][2]
      open_update_game(root, game_id, on_game_added=retrieve_data)

   except IndexError:
      return


#Scrollbar for treeview
leaderboard_scrollbar = ttk.Scrollbar(root)


# Create treeview to show users bookings
treeview = ttk.Treeview(root, columns=("name", "genre", "ID"), selectmode="browse", style="Treeview", yscrollcommand=leaderboard_scrollbar.set)
leaderboard_scrollbar.config(command=treeview.yview) # Link scrollbar to treeview


# Define headings
treeview.heading("#0", text="Rating", anchor="center")
treeview.heading("name", text="Game Name")
treeview.heading("genre", text="Genre")
treeview.heading("ID", text="")


# Adjust treeview columns
treeview.column("#0", width=100, anchor="center")
treeview.column("name", width=400)
treeview.column("genre", width=150, anchor="center")
treeview.column("ID", width=0, minwidth=0)


# Bindings
treeview.bind('<Motion>', 'break')
treeview.bind("<Double-1>", on_double_click)
treeview.bind("<<TreeviewSelect>>", detect_selection)

# Pre-create tags for ratings 0.0 to 10.0 in 0.1 steps
for i in range(101):
    rating = i * 0.1
    tag_name = f"rating_{i}" # Configure tag name based on its rating
    colour = get_fade_color(rating) # Retrieves correct colour based on rating
    treeview.tag_configure(tag_name, background=colour, font=("Segoe UI", 10)) # Configures the tag with the correct colour

leaderboard_scrollbar.place(x=685, y=230, height=400, width=15)
treeview.place(x=25, y=230, height = 400) 


# -- Description Entry --
description_frame = ttk.Labelframe(root, text="Description", padding=(5, 5))
description_frame.place(x=25, y=650, width=675, height=150)

descriptionEntry = tk.Text(description_frame, wrap="word", font="Verdana 14", fg="white", bg="#2C2C2C", relief="flat", highlightthickness=0)
descriptionEntry.configure(state="disabled")  # Make the text widget read-only
descriptionEntry.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


# ---- STATS ----

# ICONS

# Arrow Up Icon
arrow_up_PIL = Image.open("img/arrow_up_white.png") # Image is opened using PIL
arrow_up_PIL = arrow_up_PIL.resize((20,20)) # Image is resized
arrow_up_icon = ImageTk.PhotoImage(arrow_up_PIL) # Image is converted to a format that tkinter can use

# Arrow Down Icon
arrow_down_PIL = Image.open("img/arrow_down_white.png") # Image is opened using PIL
arrow_down_PIL = arrow_down_PIL.resize((20,20)) # Image is resized
arrow_down_icon = ImageTk.PhotoImage(arrow_down_PIL) # Image is converted to a format that tkinter can use

# Sigma Icon
sigma_PIL = Image.open("img/sigma_icon_white.png") # Image is opened using PIL
sigma_PIL = sigma_PIL.resize((20,20)) # Image is resized
sigma_icon = ImageTk.PhotoImage(sigma_PIL) # Image is converted to a format that tkinter can use

# Check Icon
check_PIL = Image.open("img/check_icon_white.png") # Image is opened using PIL
check_PIL = check_PIL.resize((20,20)) # Image is resized
check_icon = ImageTk.PhotoImage(check_PIL) # Image is converted to a format that tkinter can use




# -- Games Added --
games_added_text = ttk.Label(root, text="  Count", font=("Segoe UI", 12), foreground="white", background="#0D4551", anchor="center", image=check_icon, compound="left")
games_added_text.place(x=25, y=25, width=150, height=35)

game_added_value = ttk.Label(root, text="", font=("Segoe UI", 18, "bold"), foreground="white", background="#0D4551", anchor="center")
game_added_value.place(x=25, y=55, width=150, height=60)

# -- Average Rating --
average_rating_text = ttk.Label(root, text="  Average", font=("Segoe UI", 12), foreground="white", background="#76580d", anchor="center", image=sigma_icon, compound="left")
average_rating_text.place(x=200, y=25, width=150, height=35)

average_rating_value = ttk.Label(root, text="", font=("Segoe UI", 18, "bold"), foreground="white", background="#76580d", anchor="center")
average_rating_value.place(x=200, y=55, width=150, height=60)

# -- Highest Rating --
highest_rating_text = ttk.Label(root, text="  Highest", font=("Segoe UI", 12), foreground="white", background="#36510D", anchor="center", image=arrow_up_icon, compound="left")
highest_rating_text.place(x=375, y=25, width=150, height=35)

highest_rating_value = ttk.Label(root, text="", font=("Segoe UI", 18, "bold"), foreground="white", background="#36510D", anchor="center")
highest_rating_value.place(x=375, y=55, width=150, height=60)

# -- Lowest Rating --
lowest_rating_text = ttk.Label(root, text="  Lowest", font=("Segoe UI", 12), foreground="white", background="#760d0d", anchor="center", image=arrow_down_icon, compound="left")
lowest_rating_text.place(x=550, y=25, width=150, height=35)

lowest_rating_value = ttk.Label(root, text="", font=("Segoe UI", 18, "bold"), foreground="white", background="#760d0d", anchor="center")
lowest_rating_value.place(x=550, y=55, width=150, height=60)

# ---- END STATS ----



# -- Add Button --
AddGameImage = Image.open("img/plus_green.png") # Image is opened using PIL
AddGameImage = AddGameImage.resize((28,28)) # Image is resized
showAddGameImage = ImageTk.PhotoImage(AddGameImage) # Image is converted to a format that tkinter can use
AddGameButton = ttk.Button(root, command = Add_Game, text = "", image=showAddGameImage)
AddGameButton.place(x=25, y=165, width=50, height=50)
showAddGameImage.showAddGameImagedButton = showAddGameImage # Prevents the image from being garbage collected


# -- Delete Button --
red_minus_PIL = Image.open("img/minus_red.png") # Image is opened using PIL
red_minus_PIL = red_minus_PIL.resize((28,28)) # Image is resized
red_minus_Img = ImageTk.PhotoImage(red_minus_PIL) # Image is converted to a format that tkinter can use

grey_minus_PIL = Image.open("img/minus_grey.png") # Image is opened using PIL
grey_minus_PIL = grey_minus_PIL.resize((28,28)) # Image is resized
grey_minus_Img = ImageTk.PhotoImage(grey_minus_PIL) # Image is converted to a format that tkinter can use

DeleteButton = ttk.Button(root, command = delete_game, state="disabled", image=grey_minus_Img)
DeleteButton.place(x=90, y=165, width=50, height=50)

red_minus_PIL.showRedMinus = red_minus_PIL # Prevents the image from being garbage collected
grey_minus_Img.showGreyMinus = grey_minus_Img # Prevents the image from being garbage collected



def selection(*args):
   retrieve_data()  # Refresh the treeview with the selected genre

# -- Filter By --

genre_options = [ 
   "Filter By",  # Default text
   "All Genres",  # Option to show all genres
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
genre_selected.set("Filter By")  # Default text

genreOptionMenu = ttk.OptionMenu(root , genre_selected , *genre_options)

genre_menu = genreOptionMenu["menu"]
genre_menu.config(font=("Segoe UI", 12))

genreOptionMenu.place(x=360, y=165, width = 150, height = 50)


# -- Sort By --

sort_options = [ 
   "Sort By",  # Default text
   "Rating - Low to High", 
   "Rating - High to Low",
   "Name - A-Z",
   "Name - Z-A",
]

sort_selected = tk.StringVar()
sort_selected.set("Sort By")  # Default text

sortOptionMenu = ttk.OptionMenu(root , sort_selected , *sort_options)

sort_menu = sortOptionMenu["menu"]
sort_menu.config(font=("Segoe UI", 12))

sortOptionMenu.place(x=525, y=165, width = 175, height = 50)



# -- Dark Mode Theme --
sv_ttk.set_theme("dark")


retrieve_data()  # Populate the treeview with data from the database


genre_selected.trace_add("write", selection)
sort_selected.trace_add("write", selection)

root.mainloop()