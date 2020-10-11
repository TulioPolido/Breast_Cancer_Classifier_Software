import tkinter as tk
from tkinter import filedialog
from tkinter import * 
from PIL import Image, ImageTk
import os
import pydicom
import cv2
import matplotlib.pyplot as plt

class App(Frame):
    filename = ''

    def convert_to_png(self, file):
        """Utiliza matplotlib e pydicom para converter .dcm para .png"""
        filename = file
        dataset = pydicom.dcmread(filename)

        if 'PixelData' in dataset:
            rows = int(dataset.Rows)
            cols = int(dataset.Columns)

        plt.imshow(dataset.pixel_array, cmap=plt.cm.bone)
        plt.show()
        print(dataset.pixel_array)
    ################### FIM convert_to_png ###################

    def chg_image(self):
        """Atualiza a imagem na tela"""
        if self.im.mode == "1": #Caso imagem for bitmap
            self.img =  ImageTk.BitmapImage(self.im, foreground="white")
        else:
            self.img =  ImageTk.PhotoImage(self.im)
        self.la.config(image=self.img, bg="#000000", width=self.img.width(), height=self.img.height())
    ################### FIM chg_image ###################

    def open(self):
        """Exibe opção para o usuário selecionar a imagem"""
        if not self.temCanvas: #Se possuir canvas não permite abrir outra imagem
            self.filename = filedialog.askopenfilename()
            self.temLabel = True
            if self.filename != "":
                if self.filename.endswith('.png') or self.filename.endswith('.tiff'): #Se a imagem for DICOM necessita de conversão
                    self.im =  Image.open(self.filename)
                    self.chg_image()
                else: 
                    self.convert_to_png(self.filename)
        else:
            self.popupmsg(title="ATENÇÃO",msg="Finalize a seleção de região antes de abrir outra imagem!", geometry="400x60")

        #self.chg_image()
    ################### FIM open ###################

    def zoom_in(self):
        """Faz zoom in na imagem exibida"""
        if self.temLabel:
            w = self.im.width
            h = self.im.height
            if w < 800 or h < 800: #Limite superior de 800px na imagem
                w = int(w * 1.1)
                h = int(h * 1.1)
            self.im = self.im.resize((w,h))
            self.chg_image()
        elif self.temCanvas:
            print('Zoom no canvas')
        else:
            self.popupmsg(title="ATENÇÃO",msg="Não é possível dar zoom", geometry="300x80")
    ################### FIM zoom_in ###################

    def zoom_out(self):
        """Faz zoom out na imagem exibida"""
        if self.temLabel:
            w = self.im.width
            h = self.im.height
            if w > 100 or h > 100: #Limite inferior de 100px na imagem
                w = int(w * 0.9090)
                h = int(h * 0.9090)
            self.im = self.im.resize((w,h))
            self.chg_image()
        elif self.temCanvas:
            print('Zoom no Canvas')
        else:
            self.popupmsg(title="ATENÇÃO",msg="Não é possível dar zoom", geometry="300x80")
    ################### FIM zoom_out ###################

    def ler_dir(self):
        """Le o diretório e 4 subdiretórios para carregas as imagens para a memória"""
        try:
            folder = filedialog.askdirectory()

            for i in range(1,5):
                subFolder = folder + '/' + str(i)
                files = os.listdir(subFolder)

                for arquivo in files:
                    img = cv2.imread(subFolder + '/' + arquivo)
                    self.imagens.append(img)
                    
            self.popupmsg(title="ATENÇÃO",msg=str(len(self.imagens)) + " imagens carregadas com sucesso!", geometry="300x80")
        except:
            self.popupmsg(title="ATENÇÃO",msg="Erro ao carregar imagens. Verifique o diretório!", geometry="300x80")
    ################### FIM ler_dir ###################

    def selec_car(self):
        self.popupmsg(title="ATENÇÃO",msg="Função não implementada!", geometry="300x80")
    ################### FIM select_car ###################

    def trein_clas(self):
        self.popupmsg(title="ATENÇÃO",msg="Função não implementada!", geometry="300x80")
    ################### FIM trein_clas ###################

    def analisar_area(self):
        self.popupmsg(title="ATENÇÃO",msg="Função não implementada!", geometry="300x80")
    ################### FIM analisar_area ###################

    def deleta_canvas(self):
        """Deleta o canvas existente"""
        if self.temCanvas:
            self.temCanvas = False
            self.canvas.destroy()
        else:
            self.popupmsg(title="Seleção de Região",msg="Nenhuma imagem selecionada para ser recortada", geometry="300x80")

    def popupmsg(self, title, msg, geometry):
        """Posta uma imagem em popup para o usuário""" 
        popup = tk.Toplevel()
        popup.wm_title(title)
        popup.geometry(geometry)
        label = tk.Label(popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = tk.Button(popup, text="OK", command = popup.destroy)
        B1.pack()
        popup.mainloop()
    ################### FIM popupmsg ###################

    def select_area(self):
        def get_mouse_posn(event):
            """Pega a posição do mouse ao clique do usuário""" 
            nonlocal topy, topx, botx, boty
            nonlocal rect_id
            topx, topy = event.x, event.y
            botx = topx + 64
            boty = topy + 64
            topx = topx - 64
            topy = topy - 64
            self.canvas.coords(rect_id, topx, topy, botx, boty) 

        def popup_request():
            """Pede ao usuário o nome do arquivo a ser salvo""" 
            cropfilename = ''

            def set_text(popup):
                nonlocal cropfilename
                cropfilename = str(text.get())
                popup.destroy()
                return

            popup = tk.Toplevel()
            popup.wm_title("Nome do arquivo")
            popup.geometry("280x80")
            text = StringVar()
            labelInst = tk.Label(popup, padx=40, text="Digite um nome para o arquivo: ").grid(row=0, column=5)
            labelText = tk.Entry(popup, textvariable=text).grid(row=1, column=5)
            B1 = tk.Button(popup, text="Salvar", command =lambda:set_text(popup)).grid(row=4, column=5)
            popup.mainloop()
            return str(cropfilename)

        def confirm_cut(event):
            """Recorta a região de interesse do usuário"""  
            nonlocal topx, topy, botx, boty
            border = (topx, topy, botx, boty)
            imgCrop = Image.open(self.filename).crop(border)
            nameFile = popup_request()
           
            if (nameFile.endswith('.png') == False):   #Verificando extensão do arquivo
                nameFile = nameFile + '.png' 
            imgCrop.save(nameFile, "PNG")
            #self.popupmsg(title="Seleção de Região",msg="Imagem " + nameFile + " salva com sucesso", geometry="300x80") #Comentado porque só aparece após a finalização do canvas

        # Alerta ao usuario caso ainda não tenha aberto uma imagem
        if self.filename == '': 
            #tk.messagebox.showwarning(title="ATENÇÃO", message="Selecione uma imagem primeiro")
            self.popupmsg(title="ATENÇÃO",msg="Selecione uma imagem primeiro", geometry="300x80")
            return
        
        if (self.img.width()<=128 and self.img.height()<=128):
            #tk.messagebox.showwarning(title="ATENÇÃO", message="A imagem selecionada é menor que 128x128")
            self.popupmsg(title="ATENÇÃO",msg="A imagem selecionada é menor que 128x128",geometry="320x80")
            return

        topx, topy, botx, boty = 0, 0, 0, 0
        rect_id = None

        if not self.temCanvas:
            img = ImageTk.PhotoImage(Image.open(self.filename))
            self.canvas = tk.Canvas(self.la, width=img.width(), height=img.height(), borderwidth=0, highlightthickness=0)
            self.canvas.pack(expand=True)
            self.canvas.img = img  
            self.canvas.create_image(0, 0, image=img, anchor=tk.NW)
            self.temCanvas = True

            rect_id = self.canvas.create_rectangle(topx, topy, botx, boty, fill='', outline='LimeGreen', width=2.0) # Desenha retangulo verde em cima da imagem
            self.la.config(image='',bg="#FFFFFF",width=5,height=5) #Remove a imagem atras do canvas
            self.temLabel = False
        else:
            self.popupmsg(title="ATENÇÃO",msg="Selecione a área a ser recortada com dois cliques",geometry="320x80")

        self.canvas.bind('<Button-1>', get_mouse_posn)
        self.canvas.bind('<Double-Button-1>', confirm_cut) # O usuario deve dar clique duplo para confirmar corte
        
    ################### FIM select_area ###################
               
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Trabalho de Processamento de Imagens')
        self.imagens = []
        self.temLabel = False
        self.temCanvas = False

        #Tela do software
        fram = Frame(self)
        Button(fram, text="Abrir imagem", command=self.open).pack(side=LEFT)
        Button(fram, text="Zoom In", command=self.zoom_in).pack(side=LEFT)
        Button(fram, text="Zoom Out", command=self.zoom_out).pack(side=LEFT)
        Button(fram, text="Ler diretório", command=self.ler_dir).pack(side=LEFT)
        Button(fram, text="Selecionar Características", command=self.selec_car).pack(side=LEFT)
        Button(fram, text="Treinar classificador", command=self.trein_clas).pack(side=LEFT)
        Button(fram, text="Selecionar Região",  command=self.select_area).pack(side=LEFT)
        Button(fram, text="Finalizar seleção",  command=self.deleta_canvas).pack(side=LEFT)
        Button(fram, text="Analisar área selecionada", command=self.analisar_area).pack(side=LEFT)
        fram.pack(side=TOP, fill=BOTH)

        #Área em que a imagem ficará presente
        self.la = Label(self)
        self.la.pack()

        self.pack()

if __name__ == "__main__":
    app = App(); app.mainloop()