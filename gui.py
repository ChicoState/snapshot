import tkinter as tk

def button1_clicked():
    print("pretend we did something meaningful here")
def button2_clicked():
    print("a second button")

root = tk.Tk() 
button = tk.Button(root, 
    text="Button", 
    command=button1_clicked)

button.pack(padx=20, pady=20)

button2 = tk.Button(root, 
    text="Button 2", 
    command=button2_clicked)

button2.pack(padx=20, pady=20)

root.mainloop() 