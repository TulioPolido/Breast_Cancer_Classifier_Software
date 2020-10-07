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
        """Atualiza a imagem"""
        if self.im.mode == "1": #Caso imagem for bitmap
            self.img = PIL.ImageTk.BitmapImage(self.im, foreground="white")
        else:
            self.img = PIL.ImageTk.PhotoImage(self.im)
        self.la.config(image=self.img, bg="#000000", width=self.img.width(), height=self.img.height())

    def open(self):
        """Exibe opção para o usuário selecionar a imagem"""
        filename = filedialog.askopenfilename()
        if filename != "":
            if filename.endswith('.png') or filename.endswith('.tiff'): #Se a imagem for DICOM necessita de conversão
                self.im = PIL.Image.open(filename)
            else: 
                print('Eh DICOM')

        self.chg_image()

    def zoom_in(self):
        """Faz zoom in na imagem exibida"""
        w = self.im.width
        h = self.im.height
        if w < 800 or h < 800: #Limite superior de 800px na imagem
            w = int(w * 1.1)
            h = int(h * 1.1)
        self.im = self.im.resize((w,h))
        self.chg_image()

    def zoom_out(self):
        """Faz zoom out na imagem exibida"""
        w = self.im.width
        h = self.im.height
        if w > 100 or h > 100: #Limite inferior de 100px na imagem
            w = int(w * 0.9)
            h = int(h * 0.9)
        self.im = self.im.resize((w,h))
        self.chg_image()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Trab de PI')
        fram = Frame(self)

        #Botões a serem exibidos
        Button(fram, text="Abrir imagem", command=self.open).pack(side=LEFT)
        Button(fram, text="Zoom In", command=self.zoom_in).pack(side=LEFT)
        Button(fram, text="Zoom Out", command=self.zoom_out).pack(side=LEFT)
        fram.pack(side=TOP, fill=BOTH)

        #Área em que a imagem ficará presente
        self.la = Label(self)
        self.la.pack()

        self.pack()

if __name__ == "__main__":
    app = App(); app.mainloop()