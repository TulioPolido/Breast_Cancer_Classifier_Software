import PIL.Image
import os
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
import tkinter as tk

class App(Frame):
    filename = None
    def convert_to_png(self, file):
        """Utiliza matplotlib e pydicom para converter .dcm para .png"""
        filename = file
        dataset = pydicom.dcmread(filename)

        if 'PixelData' in dataset:
            rows = int(dataset.Rows)
            cols = int(dataset.Columns)
            print("Image size.......: {rows:d} x {cols:d}, {size:d} bytes".format(
                rows=rows, cols=cols, size=len(dataset.PixelData)))

        plt.imshow(dataset.pixel_array, cmap=plt.cm.bone)
        plt.show()
        print(dataset.pixel_array)

    def chg_image(self):
        """Atualiza a imagem na tela"""
        if self.im.mode == "1": #Caso imagem for bitmap
            self.img = PIL.ImageTk.BitmapImage(self.im, foreground="white")
        else:
            self.img = PIL.ImageTk.PhotoImage(self.im)
        self.la.config(image=self.img, bg="#000000", width=self.img.width(), height=self.img.height())

    def open(self):
        """Exibe opção para o usuário selecionar a imagem"""
        self.filename = filedialog.askopenfilename()
        if self.filename != "":
            if self.filename.endswith('.png') or self.filename.endswith('.tiff'): #Se a imagem for DICOM necessita de conversão
                self.im = PIL.Image.open(self.filename)
                self.chg_image()
            else: 
                print('Eh DICOM')
                self.convert_to_png(self.filename)

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
        """Le o diretório e 4 subdiretórios para carregas as imagens para a memória"""
        folder = filedialog.askdirectory()

        for i in range(1,5):
            subFolder = folder + '/' + str(i)
            files = os.listdir(subFolder)

            for arquivo in files:
                img = cv2.imread(subFolder + '/' + arquivo)
                self.imagens.append(img)
                
        cv2.imshow('image',self.imagens[0])


    def selec_car(self):
        print("Selecionar Características")

    def trein_clas(self):
        print("Treinar classificador")

    def anal_area(self):
        print("Analisar área selecionada")

    def select_area(self):
        if self.filename == None: #Criar popup avisando
            print("Selecione uma imagem primeiro")
            return
        print("Seleciona região de interesse para analise")
        
        #WIDTH, HEIGHT = 900, 900
        topx, topy, botx, boty = 0, 0, 0, 0
        rect_id = None
        #path = "teste.png"
        
        #self.im = PIL.Image.open(self.filename)
        '''window = Tk.Tk()
        window.title("Select Area")
        window.geometry('%sx%s' % (WIDTH, HEIGHT))
        window.configure(background='grey')
        '''
        
        #img = PIL.ImageTk.PhotoImage(PIL.Image.open(path))
        canvas = tkinter.Canvas(self.la, width=self.img.width(), height=self.img.height(),
                        borderwidth=0, highlightthickness=0)
        canvas.pack(expand=True)
        canvas.img = self.img  
        canvas.create_image(0, 0, image=self.img, anchor=tk.NW)

        '''
        def get_mouse_posn(event, self):
            self.topy, self.topx, self.botx, self.boty
            self.rect_id
            self.topx, self.topy = event.x, event.y
            self.botx = self.topx + 64
            self.boty = self.topy + 64
            self.topx = self.topx - 64
            self.topy = self.topy - 64
            canvas.coords(self.rect_id, self.topx, self.topy, self.botx, self.boty) 
        '''
        
        '''
        # Desenha retangulo verde em cima da imagem
        rect_id = canvas.create_rectangle(topx, topy, botx, boty,
                                        fill='', outline='LimeGreen', width=2.0)
        '''
        '''def confirm_cut(event, self):  # Função para recortar região de interesse selecionada pelo usuário
            global topx, topy, botx, boty
            global path
            border = (topx, topy, botx, boty)
            imgCrop = PIL.Image.open(path).crop(border)
            print('Salvando imagem....')
            imgCrop.save("cropped.png", "PNG")'''
            
        '''
        canvas.bind('<Button-1>', get_mouse_posn)
        #canvas.bind('<Double-Button-1>', confirm_cut) # O usuario deve dar clique duplo para confirmar corte

        #window.mainloop() 
        '''

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Trab de PI')
        self.imagens = []

        #Tela do software
        fram = Frame(self)
        Button(fram, text="Abrir imagem", command=self.open).pack(side=LEFT)
        Button(fram, text="Zoom In", command=self.zoom_in).pack(side=LEFT)
        Button(fram, text="Zoom Out", command=self.zoom_out).pack(side=LEFT)
        Button(fram, text="Ler diretório", command=self.ler_dir).pack(side=LEFT)
        Button(fram, text="Selecionar Características", command=self.selec_car).pack(side=LEFT)
        Button(fram, text="Treinar classificador", command=self.trein_clas).pack(side=LEFT)
        Button(fram, text="Selecionar Região", command=self.select_area).pack(side=LEFT)
        Button(fram, text="Analisar área selecionada", command=self.anal_area).pack(side=LEFT)
        fram.pack(side=TOP, fill=BOTH)

        #Área em que a imagem ficará presente
        self.la = Label(self)
        self.la.pack()

        self.pack()

if __name__ == "__main__":
    app = App(); app.mainloop()