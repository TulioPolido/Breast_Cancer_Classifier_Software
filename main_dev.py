import tkinter as tk
from tkinter import filedialog
from tkinter import * 
from PIL import Image, ImageTk
import os
import pydicom
import math
import cv2
import mahotas as mt
import matplotlib.pyplot as plt
import tkinter.messagebox as msgbx
import numpy as np

class App(Frame):
    filename = ''

    def reamostragemCinza(self):
        #dividir todos pontos por 8 e transormar em escala de cinza
        image = cv2.imread("./teste/file_example_TIFF_1MB.tiff")
        print(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print(gray)
        final = gray/8
        print(final)
        '''
        image = cv2.imread(self.imgCrop)
        print(self.imgCrop)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        print(image)
        '''
        return final
    ################### FIM reamostragemCinza ###################

    def Haralick(self, image, caracteristicas):

        ##LEMBRAR remover teste da main ao finalizar
        resultado = 0
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        final = gray/8
        final = final.astype(int)
        
        #Calcula descritores de Haralick para cada direcao da matriz de coocorrencia 
        features = mt.features.haralick(final)
        print(features)
        
        #Somar a coluna para a caracteristica escolhida
        if(caracteristicas[0]):
            ###somar homogeneidade
            resultado = (features[0][1] + features[1][1] + features[2][1] + features[3][1])/4
            
        elif(caracteristicas[1]):
            #somar entropia
            resultado = (features[0][8] + features[1][8] + features[2][8] + features[3][8])/4
            
        elif(caracteristicas[2]):
            #somar energia
            resultado = (features[0][0] + features[1][0] + features[2][0] + features[3][0])/4
            
        elif(caracteristicas[3]):
            #somar contraste
            resultado = (features[0][1] + features[1][1] + features[2][1] + features[3][1])/4
            
        return resultado
    ################### FIM Haralick ###################


    def convert_to_png(self, file):
        """Utiliza matplotlib e pydicom para converter .dcm para .png"""
        filename = file
        dataset = pydicom.dcmread(filename)

        if 'PixelData' in dataset:
            rows = int(dataset.Rows)
            cols = int(dataset.Columns)

        plt.imshow(dataset.pixel_array, cmap=plt.cm.bone)
        
        plt.axis('off')
        plt.savefig('./dicom.png', format='png', dpi=200, transparent=True, pad_inches=0, bbox_inches='tight')   
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
                    self.img_atual =  Image.open(self.filename)
                    self.width = self.im.width
                    self.height = self.im.height
                    self.chg_image()
                else: 
                    self.convert_to_png(self.filename)
                    self.filename = './dicom.png'
                    self.im =  Image.open(self.filename)
                    self.img_atual =  Image.open(self.filename)
                    self.width = self.im.width
                    self.height = self.im.height
                    self.chg_image()

        else:
            msgbx.showinfo(title="ATENÇÃO", message="Finalize a seleção de região antes de abrir outra imagem!")
            
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
            self.width = w
            self.height = h
            self.im = self.img_atual.resize((w,h))
            self.chg_image()
        elif self.temCanvas:
            msgbx.showinfo(title="ATENÇÃO", message="Não é possível dar zoom durante a seleção de área!")
        else:
            msgbx.showinfo(title="ATENÇÃO", message="Não é possível dar zoom")
    ################### FIM zoom_in ###################

    def zoom_out(self):
        """Faz zoom out na imagem exibida"""
        if self.temLabel:
            w = self.im.width
            h = self.im.height
            if w > 100 or h > 100: #Limite inferior de 100px na imagem
                w = int(w * 0.9090)
                h = int(h * 0.9090)
            self.width = w
            self.height = h
            self.im = self.img_atual.resize((w,h))
            self.chg_image()
        elif self.temCanvas:
            msgbx.showinfo(title="ATENÇÃO", message="Não é possível dar zoom durante a seleção de área!")
        else:
            msgbx.showinfo(title="ATENÇÃO", message="Não é possível dar zoom")
    ################### FIM zoom_out ###################

    def ler_dir(self):
        """Le o diretório e 4 subdiretórios para carregar as imagens para a memória"""
        try:
            folder = filedialog.askdirectory()

            for i in range(1,5):
                subFolder = folder + '/' + str(i)
                files = os.listdir(subFolder)

                for arquivo in files:
                    img = cv2.imread(subFolder + '/' + arquivo)
                    self.imagens.append(img)
                    
            msgbx.showinfo(title="ATENÇÃO", message=str(len(self.imagens)) + " imagens carregadas com sucesso!")
        except:
            msgbx.showinfo(title="ATENÇÃO", message="Erro ao carregar imagens. Verifique o diretório!")
    ################### FIM ler_dir ###################

    def selec_car(self):
        msgbx.showinfo(title="ATENÇÃO", message="Função não implementada!")
    ################### FIM select_car ###################

    def trein_clas(self):
        msgbx.showinfo(title="ATENÇÃO", message="Função não implementada!")
    ################### FIM trein_clas ###################

    def analisar_area(self):
        if self.temCrop:
            self.la2.config(image='',bg="#FFFFFF",width=0,height=0) #Remove a imagem atras do canvas
            self.temCrop = False

        else:
            msgbx.showinfo(title="ATENÇÃO", message="Não há área selecionada para ser analisada!")    
    ################### FIM analisar_area ###################

    def deleta_canvas(self):
        """Deleta o canvas existente"""
        if self.temCanvas:
            self.temCanvas = False
            self.canvas.delete("all")
            self.canvas.destroy()
        else:
            msgbx.showinfo(title="Seleção de Região", message="Nenhuma imagem selecionada para ser recortada")
    ################### FIM deleta_canvas ###################

    def popupmsg(self, title, msg, geometry):
        """Posta uma imagem em popup para o usuário""" 
        #msgbx.showinfo(title=title, message=msg)
        popup = tk.Toplevel()
        popup.wm_title(title)
        popup.geometry(geometry)
        label = tk.Label(popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = tk.Button(popup, text="OK", command = popup.destroy)
        B1.pack()
        popup.mainloop()
        return
    ################### FIM popupmsg ###################

    def select_area(self):
        # Alerta ao usuario caso ainda não tenha aberto uma imagem
        if self.filename == '': 
            msgbx.showinfo(title="ATENÇÃO", message="Selecione uma imagem primeiro")
            return
        
        if (self.img.width()<=128 and self.img.height()<=128):
            msgbx.showinfo(title="ATENÇÃO", message="A imagem selecionada é menor que 128x128")
            return

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
            return 

        def confirm_cut(event):
            """Recorta a região de interesse do usuário"""  
            nonlocal topx, topy, botx, boty
            border = (topx, topy, botx, boty)
            aux_img = Image.open(self.filename)
            aux_img = aux_img.resize((self.width,self.height))

            self.imgCrop = aux_img.crop(border)

            aux_crop = ImageTk.PhotoImage(self.imgCrop)
            self.la2.config(image=aux_crop, bg='#000000', width=aux_crop.width(), height=aux_crop.height())
            self.temCrop = True
            self.popupmsg(title="Seleção de Região",msg="Imagem selecionada com sucesso", geometry="300x80")
            return 

        topx, topy, botx, boty = 0, 0, 0, 0
        rect_id = None

        if not self.temCanvas and self.temLabel:
            aux_img = Image.open(self.filename)
            aux_img = aux_img.resize((self.width, self.height))
            img = ImageTk.PhotoImage(aux_img)
            self.canvas = tk.Canvas(self.la, width=img.width(), height=img.height(), borderwidth=0, highlightthickness=0)
            self.canvas.pack(expand=True)
            self.canvas.img = img  
            self.canvas.create_image(0, 0, image=img, anchor=tk.NW)
            self.temCanvas = True

            rect_id = self.canvas.create_rectangle(topx, topy, botx, boty, fill='', outline='LimeGreen', width=2) # Desenha retangulo verde em cima da imagem
            self.la.config(image='',bg="#FFFFFF",width=0,height=0) #Remove a imagem atras do canvas
            self.temLabel = False
        elif not self.temLabel:
            msgbx.showinfo(title="ATENÇÃO", message="Selecione uma imagem antes!")
        else:
            msgbx.showinfo(title="ATENÇÃO", message="Selecione a área a ser recortada com dois cliques")
            
        self.canvas.bind('<Button-1>', get_mouse_posn)
        self.canvas.bind('<Double-Button-1>', confirm_cut) # O usuario deve dar clique duplo para confirmar corte   
    ################### FIM select_area ###################
               
    def __init__(self, master=None):
        #variaveis globais
        Frame.__init__(self, master)
        self.master.title('Trabalho de Processamento de Imagens')
        self.imagens = []
        self.temLabel = False
        self.temCanvas = False
        self.temCrop = False
        self.height = 0
        self.width = 0
        self.imgCrop = None
        self.img_atual = None


        #Tela do software
        fram = Frame(self)
        Button(fram, text="Abrir imagem", command=self.open).pack(side=LEFT)
        Button(fram, text="Zoom In", command=self.zoom_in).pack(side=LEFT)
        Button(fram, text="Zoom Out", command=self.zoom_out).pack(side=LEFT)
        Button(fram, text="Selecionar Região",  command=self.select_area).pack(side=LEFT)
        Button(fram, text="Finalizar seleção",  command=self.deleta_canvas).pack(side=LEFT)
        Button(fram, text="Analisar área selecionada", command=self.analisar_area,bg='gray').pack(side=LEFT)
        Button(fram, text="Selecionar Características", command=self.selec_car,bg='gray').pack(side=LEFT)
        Button(fram, text="Ler diretório", command=self.ler_dir).pack(side=LEFT)
        Button(fram, text="Treinar classificador", command=self.trein_clas,bg='gray').pack(side=LEFT)
        
        fram.pack(side=TOP, fill=BOTH)

        #Área em que a imagem ficará presente
        self.la = Label(self)
        self.la.pack()

        #Área que o recorte ficará presente
        self.la2 = Label(self)
        self.la2.pack(side=BOTTOM)

        self.pack()

        image = cv2.imread("./teste/file_example_TIFF_1MB.tiff")
        caracteristicas = [True,False,False,False]
        self.Haralick(image,caracteristicas)

if __name__ == "__main__":
    app = App(); app.configure(bg='white'); app.mainloop()