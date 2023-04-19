from tkinter import *
import inspect
import os
import apod_desktop
import ctypes
from tkinter import ttk
import image_lib
import tkcalendar
from tkcalendar import DateEntry


# Determine the path and parent directory of this script
script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
script_dir = os.path.dirname(script_path)

# Initialize the image cache
apod_desktop.init_apod_cache(script_dir)

# Create the GUI
root = Tk()
root.title("Astronomy Picture of The Day Viewer")
root.geometry('900x700')


# Window icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('COMP593.APODViewer')
icon_path = os.path.join(script_dir, 'nasa_logo.ico')
root.iconbitmap(icon_path)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Creating the frame
frame_top = ttk.Frame(root)
frame_top.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky=NSEW)


frm_btm_left = ttk.LabelFrame(root, text='View Cached Image')
frm_btm_left.grid(row=1, column=0, pady=60, sticky=E)

frm_btm_right = ttk.LabelFrame(root, text='Get More Images')
frm_btm_right.grid(row=1, column=2, padx=(10, 10), pady=(10, 10), sticky=E)

image_path = os.path.join(script_dir,'nasa_logo_icon.png')
img_nasa = PhotoImage(file=image_path)
lbl_nasa_image = ttk.Label(frame_top, image=img_nasa)
lbl_nasa_image.grid(row=0, column=0)

lbl_sel_image = ttk.Label(frm_btm_left, text='Select Image:')
lbl_sel_image.grid(row=1, column=0, padx=5, pady=(10, 10), sticky=E)

# Adding the Select an image pull down list to the frame
apod_title_list = apod_desktop.get_all_apod_titles()
cbox_apod_title = ttk.Combobox(frm_btm_left, values=apod_title_list, state='readonly')
cbox_apod_title.set("Select an image")
cbox_apod_title.grid(row=1, column=1, pady=(10, 10), sticky=E)

# Download and save the image for the selected date
def handle_selected_apod(event):
    global image_path
    image_path = apod_desktop.determine_apod_file_path()
    if image_path is not None:
        img_nasa['file'] = image_path

cbox_apod_title.bind('<<ComboboxSelected>>', handle_selected_apod)

# Set as Desktop Button
btn_set_desktop = ttk.Button(frm_btm_left, text='Set as Desktop Image')
image_lib.set_desktop_background_image(image_path)
btn_set_desktop.grid(row=1, column=2, padx=(10, 20), pady=(10, 10), sticky=W)
if cbox_apod_title.bind('<<ComboboxSelected>>', handle_selected_apod) is True:
    btn_set_desktop.state(['!disabled'])
else:
    btn_set_desktop.state(['disabled'])



root.mainloop()