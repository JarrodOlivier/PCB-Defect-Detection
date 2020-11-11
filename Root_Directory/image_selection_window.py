import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ExifTags

from alt_main_csv import MainApplication

class Image_Selection_Window():
    """
    This application opens a file browser window before proceeding to the main 
    functionality
    """
    def __init__(self):
        self.root = tk.Tk()
        self.master = self.root
        self.master.title("PCB Analysis")
        # Set window size, prevents unpredicable behaviour (when using scrollbars)
        # such as slow startup animations (actual performance doesn't affected) 
        self.master.geometry("500x200")
        self.master.resizable(width=False, height=False)

        self.window = tk.Frame(self.master)
        self.window.pack(fill="both", padx=10, pady=10)
        
        self.heading = tk.Label(self.window,text="Find File (Image)")
        self.heading.pack(side="top")

        self.searchFrame = tk.Frame(self.window)
        self.searchFrame.pack(fill="both")

        # create functions for the following
        self.proceed_btn_init()

        self.location_text_field = self.location_text_field_init()
        self.browse_file_btn_init()


        # self.directory_view_init()

        self.root.mainloop()

    def browse_file_btn_init(self):
        self.browse_file_btn = tk.Button(master=self.searchFrame, text="Browse", command = self.open_file_dialog)
        self.browse_file_btn.pack(side="left", padx=10, expand=True)
        return self.browse_file_btn

    def location_text_field_init(self):
        self.location = tk.Text(master=self.searchFrame,height=1, width=50)
        self.location.pack(side="left")
        return self.location
        

    def open_file_dialog(self):
        self.filename = filedialog.askopenfilename(#initialdir = "/",
                                                    title = "Select a File", 
                                                    filetypes = (("Image files", ".png .jpg .jpeg .tiff .gif"), ("all files", "*.*")))
        self.location.delete("1.0","end")
        self.location.insert("1.0",self.filename)
    
    def proceed_btn_init(self):
        self.proceed_btn = tk.Button(text="Proceed to Analysis Tool", command=self.proceed) 
        self.proceed_btn.pack(side="bottom", pady=10)

    def proceed(self):
        # newWindow = tk.Tk()
        image_location = self.location_text_field.get("1.0","end")
        image_location =str(image_location)
        image_location = image_location[0:len(image_location)-1]
        image = Image.open(image_location)

        # attempting to get exif data of the image to see if image is rotated.
        try:
            exif = dict((ExifTags.TAGS[k], v) for k, v in image._getexif().items() if k in ExifTags.TAGS)
            if exif['Orientation'] == 6:
                image = image.rotate(-90, expand=True)
            elif exif['Orientation'] == 5:
                image = image.rotate(90, expand=True)
            print(exif['Orientation'])
        except Exception as e:
            print(e)
        finally:
            print("EXIF data not available. proceeding...")
        MainApplication(image)
    
    # Functions not implemented
    def directory_view_init(self):
        """
        [NOT YET IMPLEMENTED]
        """
        self.listbox = tk.Listbox(self.root)
        self.listbox.insert(1,"D:\Python\Screenshot2Text")
        self.listbox.pack(side="bottom")
    
    def image_preview_canvas_init(self):
        """ 
        Once the user selected an image through the browse button a preview should be 
        shown before proceeding, giving visual feedback to the user
        [NOT YET IMPLEMENTED]
        """
        image_location = self.location_text_field.get("1.0","end")
        image_location =str(image_location)
        image_location = image_location[0:len(image_location)-1]
        image = Image.open(image_location)
        
        self.image_preview = tk.Canvas(root)
        self.image_tk = ImageTk.PhotoImage(image)

my_gui = Image_Selection_Window()