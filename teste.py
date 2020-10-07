import PIL.Image
import pydicom
import cv2
import matplotlib.pyplot as plt
try:
    from Tkinter import *
    import tkFileDialog as filedialog
except ImportError:
    from tkinter import *
    from tkinter import filedialog
import PIL.ImageTk

class App(Frame):
    def convert_to_png(self, file):
        filename = file
        dataset = pydicom.dcmread(filename)

        # Normal mode:
        print()
        print("Filename.........:", filename)
        print("Storage type.....:", dataset.SOPClassUID)
        print()

        pat_name = dataset.PatientName
        display_name = pat_name.family_name + ", " + pat_name.given_name
        print("Patient's name...:", display_name)
        print("Patient id.......:", dataset.PatientID)
        print("Modality.........:", dataset.Modality)
        print("Study Date.......:", dataset.StudyDate)

        if 'PixelData' in dataset:
            rows = int(dataset.Rows)
            cols = int(dataset.Columns)
            print("Image size.......: {rows:d} x {cols:d}, {size:d} bytes".format(
                rows=rows, cols=cols, size=len(dataset.PixelData)))
            if 'PixelSpacing' in dataset:
                print("Pixel spacing....:", dataset.PixelSpacing)

        # use .get() if not sure the item exists, and want a default value if missing
        print("Slice location...:", dataset.get('SliceLocation', "(missing)"))
        # plot the image using matplotlib
        #plt.imshow(dataset.pixel_array, cmap=plt.cm.bone)
        #plt.show()
        print(dataset.pixel_array)

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
                self.chg_image()
            else: 
                print('Eh DICOM')
                self.convert_to_png(filename)

        #self.chg_image()

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

    def ler_dir(self):
        print("Ler diretório")

    def selec_car(self):
        print("Selecionar Características")

    def trein_clas(self):
        print("Treinar classificador")

    def anal_area(self):
        print("Analisar área selecionada")
     
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Trab de PI')

        #Tela do software
        fram = Frame(self)
        Button(fram, text="Abrir imagem", command=self.open).pack(side=LEFT)
        Button(fram, text="Zoom In", command=self.zoom_in).pack(side=LEFT)
        Button(fram, text="Zoom Out", command=self.zoom_out).pack(side=LEFT)
        Button(fram, text="Ler diretório", command=self.ler_dir).pack(side=LEFT)
        Button(fram, text="Selecionar Características", command=self.selec_car).pack(side=LEFT)
        Button(fram, text="Treinar classificador", command=self.trein_clas).pack(side=LEFT)
        Button(fram, text="Analisar área selecionada", command=self.anal_area).pack(side=LEFT)
        fram.pack(side=TOP, fill=BOTH)

        #Área em que a imagem ficará presente
        self.la = Label(self)
        self.la.pack()

        self.pack()

if __name__ == "__main__":
    app = App(); app.mainloop()