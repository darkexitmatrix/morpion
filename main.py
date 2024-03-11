import tkinter as tk
from tkinter import PhotoImage, Label, Button, messagebox
import requests
from morpion import start_morpion_ui

def choiceMorpion(): ###Function pour executé la function start_morpion_ui présente dans morpion.y
    messagebox.showinfo("Lancement", "Lancement du Morpion")
    start_morpion_ui()

def choicePuissance():
    messagebox.showinfo("Lancement", "Lancement du Puissance 4")


def main_menu(): ###function pour executé le menu
    root = tk.Tk()
    root.title("Choix du jeu")

    image = PhotoImage(file='bg.png')
    label = Label(root, image=image)
    label.image = image
    label.pack(fill='both', expand=True)

    button_style = {
        'fg': 'black',
        'bg': 'blue',
        'highlightbackground': 'black',
        'highlightthickness': 1,
        'borderwidth': 2,
        'relief': 'ridge'
    }

    morpionBtn = Button(root, text="Morpion", command=choiceMorpion, height=2, width=20, **button_style)
    morpionBtn.place(relx=0.5, rely=0.5, anchor='center')

    puissance4 = Button(root, text="Puissance 4", command=choicePuissance, height=2, width=20, **button_style)
    puissance4.place(relx=0.5, rely=0.6, anchor='center')




    root.mainloop()

if __name__ == "__main__":
    main_menu()