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
import time
from platform import system
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
np.set_printoptions(precision=2)

class App(Frame):
    filename = ''

    def Hu(self, image):
        """Calcula os momentos de Hu para a imagem e retorna uma lista com os resultados"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #converte para cinza
        final = gray/8 #rescalona os valores para o teto de 32
        final = final.astype(int) #converte para inteiros
        _,gray = cv2.threshold(gray, 16, 32, cv2.THRESH_BINARY) #converte para binario

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
                #somar homogeneidade
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
        """Cria um popup que permite a seleção das caracteristicas de Haralick desejadas"""
        if(not self.Opened_Car_Menu):
            
            self.Opened_Car_Menu = True

            Entropia = self.Entropia                #Recuperar valores globais
            Energia = self.Energia                  #Recuperar valores globais
            Homogeneidade = self.Homogeneidade      #Recuperar valores globais
            Contraste = self.Contraste              #Recuperar valores globais

            #Criação Interface
            top = Toplevel()
            top.title("Selecionar Características")
            top.lift()      #Deixa a tela corrente no topo da pilha (gerenciador de janelas)

            CheckEntropia = IntVar()
            CheckEnergia = IntVar()
            CheckHomogeneidade = IntVar()
            CheckContraste = IntVar()

            #Checkboxes do Menu
            C1 = Checkbutton(top, text = "Entropia", variable = CheckEntropia, \
                                onvalue=1, offvalue=0, \
                                activebackground="green", height=2, \
                                width = 20)
            C2 = Checkbutton(top, text = "Energia", variable = CheckEnergia, \
                                activebackground="green", height=2, \
                                width = 20)
            C3 = Checkbutton(top, text = "Homogeneidade", variable = CheckHomogeneidade, \
                                activebackground="green", height=2, \
                                width = 20)
            C4 = Checkbutton(top, text = "Contraste", variable = CheckContraste, \
                                activebackground="green", height=2, \
                                width = 20)

            #Verifica se as características já estavam selecionadas anteriormente
            if(Entropia):
                C1.select()

            if(Energia):
                C2.select()

            if(Homogeneidade):
                C3.select()

            if(Contraste):
                C4.select()

            #Tela do Menu
            C1.pack()
            C2.pack()
            C3.pack()
            C4.pack()
            
            def on_closing():
                top.quit()
                top.destroy()

            top.protocol("WM_DELETE_WINDOW", on_closing)
            top.mainloop()

            #Setando as características selecionadas
            if(CheckEntropia.get() == 1):
                self.Entropia = True
            else:
                self.Entropia = False

            if(CheckEnergia.get() == 1):
                self.Energia = True
            else:
                self.Energia = False

            if(CheckHomogeneidade.get() == 1):
                self.Homogeneidade = True
            else:
                self.Homogeneidade = False

            if(CheckContraste.get() == 1):
                self.Contraste = True
            else:
                self.Contraste = False

            self.Opened_Car_Menu = False

            self.caracteristicas = [self.Entropia, self.Energia, self.Homogeneidade, self.Contraste]
            print(self.caracteristicas)
            msgbx.showinfo(title="Selecionar Características", message="As características marcadas foram selecionadas.")
        else:
            msgbx.showinfo(title="ATENÇÃO!", message="O Menu de características já está aberto.")
    ################### FIM selec_car ###################

    def trein_clas(self):
        """Treina uma rede neural"""
        if len(self.imagens) == 400:
            inicio = time.time()
            train_feat = []
            train_labels = []

            #seta o vetor de labels
            for i in range(0,400):
                train_labels.append(int(i/100) + 1)
        
            #Cria o vetor com os valores a serem analisados
            for imagem in self.imagens:
                val = self.Hu(imagem) + self.Haralick(imagem)
                train_feat.append(val)

            ######## Inicio rede neural #######
            # Particionamento da base
            X = train_feat
            y = train_labels
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                    test_size=0.25, random_state=0)
            
            self.mlp = MLPClassifier(solver='lbfgs', random_state=5, max_iter=400, hidden_layer_sizes=[200,300])
            self.mlp.fit(X_train, y_train)
            y_pred = self.mlp.predict(X_test)


            print("Camadas da rede: {}".format(self.mlp.n_layers_))
            print("Neurônios na camada oculta: {}".format(self.mlp.hidden_layer_sizes))
            print("Neurônios na camada de saída: {}".format(self.mlp.n_outputs_))
            print("Pesos na camada de entrada: {}".format(self.mlp.coefs_[0].shape))
            print("Pesos na camada oculta: {}".format(self.mlp.coefs_[1].shape))

            print("Acurácia da base de treinamento: {:.2f}".format(self.mlp.score(X_train, y_train)))
            print("Acurácia da base de teste: {:.2f}".format(self.mlp.score(X_test, y_test)))

            # Calcula a matriz de confusão
            cnf_matrix = confusion_matrix(y_test, y_pred)
            print(cnf_matrix)
            print(self.acuracia(cnf_matrix))
            print(self.especificidade(cnf_matrix))
            
            # Calcula tempo de execução
            self.tempo = time.time() - inicio

            print('Tempo de execução: {0}'.format(self.tempo))
        else:
            msgbx.showinfo(title="ATENÇÃO", message="Primeiro leia o diretório com as imagens de teste!")
    ################### FIM trein_clas ###################

    def analisar_area(self):
        """Analisa a area recortada pelo usuario"""

        if 'mlp' in globals():
            if self.temCrop:
                self.la2.config(image='',bg="#FFFFFF",width=0,height=0) #Remove a imagem atras do canvas
                self.temCrop = False

                cropped = cv2.imread('.crop.png')

                inicio = time.time()
                val = self.Hu(cropped) + self.Haralick(cropped)
                tempo = time.time() - inicio

                val = np.array(val)
                prediction = self.mlp.predict(val.reshape(1,-1))[0] #reshape(1,-1) pq há apenas uma instancia a ser avaliada com multiplos valores

                print(prediction)
            else:
                msgbx.showinfo(title="ATENÇÃO", message="Não há área selecionada para ser analisada!") 
        else:
            msgbx.showinfo(title="ATENÇÃO", message="O classificador não foi treinado!") 
    ################### FIM analisar_area ###################

    def acuracia(self,matriz):
        """Calcula a acuracia da rede baseado na matriz de confusao"""
        resp = 0

        for i in range(0,4):
            resp += matriz[i][i]

        return resp/100
    ################### FIM acuracia ###################

    def especificidade(self,matriz):
        """Calcula a especificidade da rede baseado na matriz de confusão"""
        resp = 0

        for i in range(0,4):
            for j in range(0,4):
                if i != j:
                    resp+= matriz[i][j]

        return resp/300

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
        if system() == 'Linux':
            self.master.attributes('-zoomed', True)
        elif system() == 'Windows':
            self.master.attributes('-fullscreen', True)
        #Variaveis da classe
        self.imagens = []
        self.temLabel = False
        self.temCanvas = False
        self.temCrop = False
        self.height = 0
        self.width = 0
        self.imgCrop = None
        self.img_atual = None
        self.tempo = 0
        self.Opened_Car_Menu = False
        self.Entropia = True
        self.Energia = True
        self.Homogeneidade = True
        self.Contraste = True
        self.caracteristicas = [self.Entropia, self.Energia, self.Homogeneidade, self.Contraste]


        #Tela do software
        fram = Frame(self)
        Button(fram, text="Abrir imagem", command=self.open).pack(side=LEFT)
        Button(fram, text="Zoom In", command=self.zoom_in).pack(side=LEFT)
        Button(fram, text="Zoom Out", command=self.zoom_out).pack(side=LEFT)
        Button(fram, text="Selecionar Região",  command=self.select_area).pack(side=LEFT)
        Button(fram, text="Finalizar seleção",  command=self.deleta_canvas).pack(side=LEFT)
        Button(fram, text="Analisar área selecionada", command=self.analisar_area,bg='gray').pack(side=LEFT)
        Button(fram, text="Selecionar Características", command=self.selec_car).pack(side=LEFT)
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
        
if __name__ == "__main__":
    app = App(); app.configure(bg='white',); app.mainloop()