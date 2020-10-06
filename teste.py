import PIL.Image

try:
    from Tkinter import *
    import tkFileDialog as filedialog
except ImportError:
    from tkinter import *
    from tkinter import filedialog
import PIL.ImageTk


class App(Frame):
    def chg_image(self):
        
        if self.im.mode == "1": # bitmap image
            self.img = PIL.ImageTk.BitmapImage(self.im, foreground="white")
        else:              # photo image
            self.img = PIL.ImageTk.PhotoImage(self.im)
        self.la.config(image=self.img, bg="#000000",
            width=self.img.width(), height=self.img.height())


    def open(self):
        filename = filedialog.askopenfilename()
        if filename != "":
            if filename.endswith('.png'):
                self.im = PIL.Image.open(filename)
            else: 
                print('Nao eh PNG')

        self.chg_image()
        self.num_page=0
        self.num_page_tv.set(str(self.num_page+1))

    def zoom_in(self):
        w = self.im.width
        h = self.im.height
        if w < 800 or h < 800:
            w = int(w * 1.1)
            h = int(h * 1.1)
        self.im = self.im.resize((w,h))
        self.chg_image()

    def zoom_out(self):
        w = self.im.width
        h = self.im.height
        if w > 100 or h > 100:
            w = int(w * 0.9)
            h = int(h * 0.9)
        self.im = self.im.resize((w,h))
        self.chg_image()
    '''
    def ant(self):
        self.num_page=self.num_page-1
        if self.num_page < 0:
            self.num_page = 0
        self.im.seek(self.num_page)
        self.chg_image()
        self.num_page_tv.set(str(self.num_page+1))

    def prox(self):
        self.num_page=self.num_page+1
        try:
            self.im.seek(self.num_page)
        except:
            self.num_page=self.num_page-1
        self.chg_image()
        self.num_page_tv.set(str(self.num_page+1)) '''

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Trab de PI')

        self.num_page=0
        self.num_page_tv = StringVar()

        fram = Frame(self)
        Button(fram, text="Abrir imagem", command=self.open).pack(side=LEFT)
        Button(fram, text="Zoom In", command=self.zoom_in).pack(side=LEFT)
        Button(fram, text="Zoom Out", command=self.zoom_out).pack(side=LEFT)
        #Button(fram, text="Próx.", command=self.prox).pack(side=LEFT)
        #Button(fram, text="Ant.", command=self.ant).pack(side=LEFT)
        Label(fram, textvariable=self.num_page_tv).pack(side=LEFT)
        fram.pack(side=TOP, fill=BOTH)

        self.la = Label(self)
        self.la.pack()

        self.pack()

if __name__ == "__main__":
    app = App(); app.mainloop()