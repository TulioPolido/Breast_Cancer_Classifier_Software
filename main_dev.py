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
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class App(Frame):
    filename = ''

    def Hu(self, image):
        """Calcula os momentos de Hu para a imagem e retorna uma lista com os resultados"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #converte para cinza
        final = gray/8 #rescalona os valores para o teto de 32
        final = final.astype(int) #converte para inteiros
        _,gray = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY) #converte para binario

        moments = cv2.moments(gray) #calcula os momentos da imagem
        huMoments = cv2.HuMoments(moments) #calcula os momentos de Hu

        result = []
        
        #adiciona os valores de Hu para uma lista
        result.append(huMoments[0][0])
        result.append(huMoments[1][0])
        result.append(huMoments[2][0])
        result.append(huMoments[3][0])
        result.append(huMoments[4][0])
        result.append(huMoments[5][0])
        result.append(huMoments[6][0])

        return result
    ################### FIM Hu ###################
    
    def Haralick(self, image, caracteristicas=[True,True,True,True]):
        """Calcula as propriedades de Haralick da imagem e retorna um array com os resultados"""
        resultado = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #converte para cinza
        final = gray/8
        final = final.astype(int)

        dist = 1
        while dist <= 16:
            #Calcula descritores de Haralick para cada direcao da matriz de coocorrencia 
            features = mt.features.haralick(final,distance=dist)

            #Media da coluna para a caracteristica escolhida
            if(caracteristicas[0]):
                ###somar homogeneidade
                parcial = (features[0][4] + features[1][4] + features[2][4] + features[3][4])/4
                resultado.append(parcial)
            elif(caracteristicas[1]):
                #somar entropia
                parcial = (features[0][8] + features[1][8] + features[2][8] + features[3][8])/4
                resultado.append(parcial)
            elif(caracteristicas[2]):
                #somar energia
                parcial = (features[0][0] + features[1][0] + features[2][0] + features[3][0])/4
                resultado.append(parcial)
            elif(caracteristicas[3]):
                #somar contraste
                parcial = (features[0][1] + features[1][1] + features[2][1] + features[3][1])/4
                resultado.append(parcial)
            
            dist*=2
            
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
            #folder = filedialog.askdirectory()
            folder = './imagens'

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
        train_feat = []
        train_labels = []

        #seta o vetor de labels
        for i in range(0,400):
            train_labels.append(int(i/100) + 1)
        
        #Cria o vetor com os valores a serem analisados
        for imagem in self.imagens:
            val = self.Hu(imagem) + self.Haralick(imagem)
            train_feat.append(val)

        #balanceando as imagens teste por classe
        Tclas1,Tclas2,Tclas3,Tclas4 = np.array_split(train_feat,4)
        Lclas1,Lclas2,Lclas3,Lclas4 = np.array_split(train_labels,4)

        #Dividir os dados em 75% treinamento e 25% testes
        feat_train1, feat_test1, label_train1, label_test1 = train_test_split(Tclas1, Lclas1,test_size=0.25, random_state=1)
        feat_train2, feat_test2, label_train2, label_test2 = train_test_split(Tclas2, Lclas2,test_size=0.25, random_state=1)
        feat_train3, feat_test3, label_train3, label_test3 = train_test_split(Tclas3, Lclas3,test_size=0.25, random_state=1)
        feat_train4, feat_test4, label_train4, label_test4 = train_test_split(Tclas4, Lclas4,test_size=0.25, random_state=1)

        feat_train = np.concatenate((feat_train1,feat_train2,feat_train3,feat_train4))
        feat_test = np.concatenate((feat_test1,feat_test2,feat_test3,feat_test4))
        label_train = np.concatenate((label_train1,label_train2,label_train3,label_train4))
        label_test = np.concatenate((label_test1,label_test2,label_test3,label_test4))

        #cria classificador
        self.clf_svm = LinearSVC(random_state=9)
        print('Classificador criado...')

        #Prepara o modelo de acordo com os dados a serem usados para treinamento
        self.clf_svm.fit(feat_train, label_train)
        print('Modelo criado...')

        #Testes de acertos
        resultados = self.clf_svm.predict(feat_test)
        score = accuracy_score(label_test,resultados)
        print(score)

    ################### FIM trein_clas ###################

    def analisar_area(self):
        """Analisa a area recortada pelo usuario"""
        if self.temCrop:
            self.la2.config(image='',bg="#FFFFFF",width=0,height=0) #Remove a imagem atras do canvas
            self.temCrop = False

            cropped = cv2.imread('.crop.png')

            val = self.Hu(cropped) + self.Haralick(cropped)

            val = np.array(val)
            prediction = self.clf_svm.predict(val.reshape(1,-1))[0] #reshape(1,-1) pq há apenas uma instancia a ser avaliada com multiplos valores

            print(prediction)
            #conferir se o classificador foi treinado e analisar a imagem
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
        """Permite a selecao de uma area 128x128 na imagem aberta e a salva"""
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

            #Salvando imagem no disco
            self.imgCrop.save(".crop.png")

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
        Frame.__init__(self, master)
        self.master.title('Trabalho de Processamento de Imagens')
        #Atributo zoomed inicia janela em modo tela cheia
        #self.master.attributes('-zoomed', True)
        #self.master.attributes('-fullscreen', True)

        #Variaveis da classe
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

        ###TESTES
        self.ler_dir()
        self.trein_clas()

if __name__ == "__main__":
    app = App(); app.configure(bg='white',); app.mainloop()
