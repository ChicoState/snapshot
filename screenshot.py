import pyautogui
import tkinter as tk
from PIL import Image, ImageTk

class SnippingTool:
    def __init__(self):
        self.screenshot = pyautogui.screenshot()
        #self.screenshot.save("full_screenshot.png")  #save inital image (usefull for testing)

        self.root = tk.Tk() # Initialize Tkinter window, refrence as self.root
        self.root.attributes("-fullscreen", True) # make window fullscreen (not sure if we should use this, ive had some issues)

        self.canvas = tk.Canvas(self.root, cursor="cross") # create widget, cursor similar to snipping tool
        self.tk_image = ImageTk.PhotoImage(self.screenshot) # convert image format for Tkinter
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image) # load screenshot into Tkinter window
        self.canvas.pack(fill=tk.BOTH, expand=True) # resize image to window

        # cropped image coordinate variables
        self.start_x = None
        self.start_y = None
        self.rect = None

        # set mouse binds / movements 
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.root.mainloop() # keep window open untill program finishes 

    # start rectangle selection 
    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle( self.start_x, self.start_y, event.x, event.y, outline="red", width=2 )

    # update rectangle selection
    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        end_x, end_y = event.x, event.y # set final values
        self.root.destroy() # close Tkinter window

        # check if user went backwards for some reason
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        right = max(self.start_x, end_x)
        bottom = max(self.start_y, end_y)

        cropped_image = self.screenshot.crop((left, top, right, bottom)) # crop image
        cropped_image.save("screenshot.png") # save image
        print("saved image as 'screenshot.png'")

SnippingTool() #run function