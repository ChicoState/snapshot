from pynput import keyboard
from screenshot import take_screenshot, process_ocr
import UI


# Takes and saves a screenshot
# Currently has weird bug where after pressing the snapshot hotkeys, subsequent double presses of ctrl will trigger the snapshot function again even if q hasnt been pressed
# Bug only occurs with the snapshot function, other hotkeys work as expected and trigger only when appropriate
# My guess is that the bug probably has something to do with the interaction between pynput keyboard listener and the screenshot functionality waiting for screenshot to be taken by user
def snapshot():
    print('Taking snapshot')
    cropped_image = take_screenshot()
    process_ocr(cropped_image = cropped_image)

# Quits the program
def quit():
    print('Quitting')
    exit()
    
def test1():
    print('1')
    
def test2():
    print('2')	

# List of hotkeys and their associated functions
with keyboard.GlobalHotKeys({
        '<ctrl>+q': snapshot,
        '<ctrl>+p': quit,
        '<ctrl>+9': test1,
        '<ctrl>+0': test2,}) as h:
    h.join()