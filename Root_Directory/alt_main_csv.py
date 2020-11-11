import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
# NOTE: ExifTags from Image.open at bottom
from PIL import Image, ImageTk, ImageDraw, ExifTags
import csv 
from Cleanup import cleanup


class MainApplication():
    """
    This applications opens a canvas with image which allow the user to visually select 
    Regions of Interest (ROIs).
    Once the user has selected all useful ROIs the user should be given the following:
    """
    def __init__(self, image):
        # For more than one window, you CANNOT create multiple instances of tk.Tk()
        # this will be done in the 1st method, the following will use tk.Toplevel method
        # seen here:
        self.root = tk.Toplevel()
        self.master = self.root
        self.master.title("PCB Analysis")
        
        cleanup()
        
        # TODO make one palette (with more colours)
        # NOTE: All colours MUST have a 4 variant for shading
        self.colour_palette = [
            "deep pink", 
            "yellow",
            "red", 
            "dark orange",  
            "green",
            "blue"
            ]
        self.hex_palette={"deep pink":"#f91692",
                          "yellow": "#fefd1f",
                          "red":"#f91101",
                          "dark orange":"#fa8b0d",
                          "green":"#7afb1e", #lawn green
                          "blue":"#120ffc"
                         }
        # NOTE: Updated from an array of tuples to a dictionary, currently not useful
        # TODO: look into making this an array of tuples 
        COMPONENTS = {
            "Non-polarised":0,
            "Polarised":1,
            "IC/uC/multipin":2,
            "At angle":3,
            "At angle (square uC)":4
            }
        # Set window size, prevents unpredicable behaviour (when using scrollbars)
        # such as slow startup animations (actual performance doesn't affected) 
        self.master.geometry("900x500")
        self.image = image
        self.sidebar = self.init_sidebar()
        self.sidebar_elements(self.colour_palette, COMPONENTS)
        self.sidebar_actions()
        self.mainwindow = self.init_mainwindow(self.master)
        # TODO: see if colour_palette can be used without passing through all the function (avoid GLOBAL)
        self.canvas = self.init_canvas(self.image, self.colour_palette)
        self.canvas_resize()
        # Moved to inside init_canvas, such that srollbars are added ("packed") before canvas
        # self.init_scrollbars()
        self.root.mainloop()

    def init_sidebar(self):
        self.sidebar = tk.Frame(
            master=self.master, 
            width=150, 
            bg='gray10', 
            # height=500, 
            relief='sunken', 
            # borderwidth=2
            )
        self.sidebar.pack(
            # expand=False, 
            fill='both', 
            side='left', 
            # anchor='nw'
            )

        # Frame is designed to shrink to contents, this links exaplains how to stop this using the command below
        # https://stackoverflow.com/questions/563827/how-to-stop-tkinter-frame-from-shrinking-to-fit-its-contents 
        # so instead of using this, consider a padx on the buttons instead
        self.sidebar.pack_propagate(0)

        return self.sidebar

    def init_mainwindow(self, master):
        self.mainwindow = tk.Frame(master, bg='#CCC')
        self.mainwindow.pack(
            # NOTE: Commenting expand and fill out causes a scaling animation not prev. there but look neat now
            # BUT! resizing draws on canvas and is note desirable
            expand=True,             
            fill='both', 
            side='left'
            )
        return self.mainwindow

    def init_canvas(self, image, colour_palette):
        self.canvas = tk.Canvas(self.mainwindow, highlightthickness=0)
        self.init_scrollbars()
        self.image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(
            image.size[0]//2, image.size[1]//2, image=self.image_tk)
        self.canvas.pack(side="top", fill="both")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Display coords of mousepointer as mouse moves
        # while leaving a final rectangle when lmb is released
        # Initialisation
        self.start = []
        self.end = []
        # TODO(jarrod): change to a dictionary
        # NOTE: re-evaluating this point
        self.drawn_elements = []  # used to store all drawn elements to allow undo
        self.tmp_elements = [] # Elements created while dragging mouse (designed to be removed. i.e. do not rely on the contents of this array)
        # Callback Functions
        def lmb_clicked(event, start):
            """
            Actions followed as a result of lmb being clicked
            """
            # Get coords on canvas, even after scrolling/ moving window
            self.canvas = event.widget
            self.x = self.canvas.canvasx(event.x)
            self.y = self.canvas.canvasy(event.y)
            # start coord array
            start.append(self.x)
            start.append(self.y)
            # print("clicked at: ", self.x, self.y)

        def lmb_released(
            event, 
            end, 
            start, 
            drawn_elements, 
            tmp_elements
            ):
            """
            Actions followed once the left mouse button is released
            """
            # Get coords on canvas, even after scrolling/ moving window
            self.canvas = event.widget
            self.x = self.canvas.canvasx(event.x)
            self.y = self.canvas.canvasy(event.y)
            # end coord array
            end.append(self.x)
            end.append(self.y)

            print("pressed at: ", start[0], start[1])
            print("released at: ", self.x, self.y)

            self.min_draw_distance = 10
            if ((abs(self.start[0]-self.end[0]) > self.min_draw_distance) or (abs(self.start[1]-self.end[1]) > self.min_draw_distance)):
                draw_on_canvas(self, start, end, drawn_elements, colour_palette)
            else:
                print("Min draw distance")

            draw_on_canvas_tmp_delete_element(self,tmp_elements,0)
            print(len(drawn_elements))
            print("Elements: {}".format(drawn_elements))
            print("Radio Button Value: {}".format(self.component_selection.get()))
            # https://stackoverflow.com/questions/2679418/how-to-get-the-coordinates-of-an-object-in-a-tkinter-canvas
            # https://stackoverflow.com/questions/58680194/how-to-get-the-id-of-canvas-item
            print("***END OF STATEMENTS***\n")
            self.start = []
            self.end = []

        def undo_drawn_element(event, drawn_elements):
            if (len(self.drawn_elements) > 0):
                # NOTE: As drawn_elements are a tuple storing the rect and radio button value, you need to
                # pop out the rect element to remove the rect from canvas, the tuple is removed as well
                self.canvas.delete(self.drawn_elements.pop()[0])
                #print("Removed element")
            else:
                #print("No Elements to remove")
                pass
        
        def lmb_dragged(event, start, tmp_elements):
            """ 
            Actions as a result of mouse being dragged
            FIXED: This appears to be called on mouse presses too causing an index out of range error
            """
            # Get coords on canvas, even after scrolling/ moving window
            self.canvas = event.widget
            self.x = self.canvas.canvasx(event.x)
            self.y = self.canvas.canvasy(event.y)
            
            # Draw an updating elements which follows the mouse pointer
            self.rectangle = draw_on_canvas_tmp(self,start,[self.x,self.y])
            self.tmp_elements.append(self.rectangle)
            
            # Delete the last element left as result of dragging the mouse
            draw_on_canvas_tmp_delete_element(self,tmp_elements,1)

        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # End callback functions

        # Canvas Bindings
        self.canvas.bind(
            "<Button-1>", 
            lambda event: lmb_clicked(event, self.start)
        )
        self.canvas.bind(
            "<ButtonRelease-1>", 
            lambda event: lmb_released(event, self.end, self.start, self.drawn_elements, self.tmp_elements)
        )
        self.canvas.bind(
            "<Button-3>",
            lambda event: undo_drawn_element(event, self.drawn_elements)
        )
        self.canvas.bind(
            "<B1-Motion>", lambda event: lmb_dragged(event,self.start, self.tmp_elements)
        )

        self.canvas.bind(
            "<MouseWheel>", lambda event: on_mousewheel(event)
        )
        # End Canvas Bindings

        # Supplementary Canvas Functions
        def draw_on_canvas(self, start, end, drawn_elements, colour_palette):
            """
            Element drawn on canvas given the position the mouse is clicked and
            where the mouse is released. 
            Element remains after mouse button is released.
            """
            self.rectangle = self.canvas.create_rectangle(
                start[0], start[1], end[0], end[1],
                outline=self.colour_palette[self.component_selection.get()],
                width=3)
            self.drawn_elements.append((self.rectangle,self.component_selection.get()))

        def draw_on_canvas_tmp(self,start,end):
            """
            Draw elements as mouse is dragged to give feedback to the user
            """
            self.rectangle = self.canvas.create_rectangle(
                start[0], 
                start[1], 
                end[0], 
                end[1])
            return self.rectangle

        def draw_on_canvas_tmp_delete_element(self, tmp_elements,state):
            """
            Delete all elements created as a result of of dragging the mouse
            """
            if (state == 0 and len(tmp_elements)>0): #Active on Button B1-release
                self.canvas.delete(tmp_elements[-1])
            else:
                for i in range(len(tmp_elements)-1):
                    self.canvas.delete(tmp_elements[i])
            # return tmp_elements
        # End Supplementary Canvas Functions
        return self.canvas

    def canvas_resize(self):
        """
        Resize Canvas Window Automatically
        """
        def resize(event):
            self.w, self.h = self.mainwindow.winfo_width(), self.mainwindow.winfo_height()
            self.canvas.configure(width=self.w, height=self.h)

        self.mainwindow.bind("<Configure>", resize)

    def init_scrollbars(self):
        """ 
        To move contents in canvas in mainwindow, note: scrollbars are parented to mainwindow
        """
        self.hbar = tk.Scrollbar(self.mainwindow, orient="horizontal")
        self.hbar.config(command=self.canvas.xview)
        self.hbar.pack(side="bottom", fill="x")

        self.vbar = tk.Scrollbar(self.mainwindow, orient="vertical")
        self.vbar.config(command=self.canvas.yview)
        self.vbar.pack(side="right", fill="y")

    def sidebar_elements(self, colour_palette, COMPONENTS):
        # root.update used to get winfo (from here: https://stackoverflow.com/questions/3950687/how-to-find-out-the-current-widget-size-in-tkinter)
        # self.root.update()
        self.component_frame = tk.Frame(self.sidebar,
            # width=self.sidebar.winfo_width(), 
            bg='gray10', 
            # height= int(self.sidebar.winfo_height()*0.9),  
            borderwidth=2)
        self.component_frame.pack(side="top", fill=tk.X)

        # Reference: http://effbot.org/tkinterbook/radiobutton.htm
        self.component_selection = tk.IntVar()
        self.component_selection.set(0)

        # TODO: check where else root.update is located or sidebar sizing option and optimised so that we keep doing it for each item
        # self.root.update()
        i = 0
        for text in COMPONENTS:
            mode = COMPONENTS[text]
            self.selection = tk.Radiobutton(
                master=self.component_frame, 
                text=text, 
                variable=self.component_selection,
                value=mode,
                indicatoron=False,
                # width=int(self.sidebar.winfo_width()*0.1),
                pady=10,
                bg=str(self.colour_palette[i]+"4"),
                selectcolor = self.colour_palette[i]
                )
            self.selection.pack(anchor="w", fill=tk.X)
            i += 1
    
    def sidebar_actions(self):
        """
        All buttons on the sidebar that operate outside of the scope of the canvas or do not relate to electronic components
        """
        self.actions_frame = tk.Frame(self.sidebar
            # width=self.sidebar.winfo_width(), 
            # bg='gray10', 
            # height= int(self.sidebar.winfo_height()*0.9),  
            # borderwidth=2
            )
        self.actions_frame.pack(side="bottom", fill=tk.X)

        complete_button = tk.Button(
            master=self.actions_frame,
            pady=10,
            text="Finished",
            command=self.messagebox_prompt
        )
        complete_button.pack(side="top", fill=tk.X)

    def messagebox_prompt(self):
        # NOTE: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/tkMessageBox.html
        self.messagebox_prompt_answer = messagebox.askyesno(
            title="Confirm Action",
            message="Are you sure you're finshed as this operation cannot be undone.",
            default="no"
        )

        if (self.messagebox_prompt_answer):
            # TODO: make one for loop from the two below
            # NOTE: Testing to PIL draw on image used for saving image for testing results in report
            # https://stackoverflow.com/questions/9886274/how-can-i-convert-canvas-content-to-an-image
            # https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
            # with Image.open(self.image) as self.drawn_image:
            self.drawn_image= self.image
            self.draw= ImageDraw.Draw(self.drawn_image)
            for i in range(len(self.drawn_elements)):
                self.draw.rectangle(
                    xy=[int(self.canvas.coords(self.drawn_elements[i][0])[0]), 
                        int(self.canvas.coords(self.drawn_elements[i][0])[1]), 
                        int(self.canvas.coords(self.drawn_elements[i][0])[2]),
                        int(self.canvas.coords(self.drawn_elements[i][0])[3])], 
                    outline=self.hex_palette[str(self.colour_palette[self.component_selection.get()])],
                    width=5)
            self.drawn_image.save("poi_out_img.jpg")
            
            # TODO: Make sure this directory exits before (running `Cleanup.py` does this)
            with open("Files/poi.csv","w",newline="") as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(["type"]+["x0"]+["y0"]+["x1"]+["y1"])  
                for i in range(len(self.drawn_elements)):
                    # f.write(str(self.drawn_elements[i][1]) + ", " + str(self.canvas.coords(self.drawn_elements[i][0]))+ "\n")
                    spamwriter.writerow([int(self.drawn_elements[i][1])] \
                                +[int(self.canvas.coords(self.drawn_elements[i][0])[0])] \
                                +[int(self.canvas.coords(self.drawn_elements[i][0])[1])] \
                                +[int(self.canvas.coords(self.drawn_elements[i][0])[2])] \
                                +[int(self.canvas.coords(self.drawn_elements[i][0])[3])])
            
            self.root.quit()

if __name__ == "__main__":
    # image = Image.open("D:\Python\opencv_defect_detection\Week 5\IS5/scnM.jpg")
    # image = Image.open("D:\Python\opencv_defect_detection\Week 5\IS5/tmp.jpg")
    image = Image.open("D:\Python\opencv_defect_detection\Week 11\IS1/defects.jpg")

    # https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image
    
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
    print("Warning: bypassing file directory, blank window is required.")
    MainApplication(image)