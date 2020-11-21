import tkinter as tk
from tkinter import filedialog
from tkinter import * 
from PIL import Image, ImageTk
from platform import system
import time
import os
import pydicom
import cv2
import mahotas as mt
import matplotlib.pyplot as plt
import tkinter.messagebox as msgbx
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.neural_network import MLPClassifier

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
            ################### FIM on_closing ###################   

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
            msgbx.showinfo(title="Selecionar Características", message="As características marcadas foram selecionadas.")
        else:
            msgbx.showinfo(title="ATENÇÃO!", message="O Menu de características já está aberto.")
    ################### FIM selec_car ###################
    '''
    def selec_gray_scale():
        
        top = Toplevel
        top.title("Selecionar Escala de Cinza")
        top.lift()

        scale = IntVar()

        R1 = Radiobutton(text='8',value=8,variable=scale).pack(anchor=W)
        
        R2 = Radiobutton(text='16',value=16,variable=scale).pack(anchor=W)

        R3 = Radiobutton(text='32',value=32,variable=scale).pack(anchor=W)
        
        def on_closing():
            top.quit()
            top.destroy()
        ################### FIM on_closing ###################   

        top.protocol("WM_DELETE_WINDOW", on_closing)
        mainloop()

        if (scale.get() == 8):
            self.scale_gray = 8
            
        if (scale.get() == 16):
            self.scale_gray = 32

        if (scale.get() == 32):
            self.scale_gray = 32
    ################### FIM selec_gray_scale ###################  
    '''
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

            #Dividir os dados nas 4 classes
            Tclas1,Tclas2,Tclas3,Tclas4 = np.array_split(train_feat,4)
            Lclas1,Lclas2,Lclas3,Lclas4 = np.array_split(train_labels,4)

            #Balancea os dados em 75% treinamento e 25% testes
            feat_train1, feat_test1, label_train1, label_test1 = train_test_split(Tclas1, Lclas1,test_size=0.25, random_state=1)
            feat_train2, feat_test2, label_train2, label_test2 = train_test_split(Tclas2, Lclas2,test_size=0.25, random_state=1)
            feat_train3, feat_test3, label_train3, label_test3 = train_test_split(Tclas3, Lclas3,test_size=0.25, random_state=1)
            feat_train4, feat_test4, label_train4, label_test4 = train_test_split(Tclas4, Lclas4,test_size=0.25, random_state=1)

            #Reunir os dados
            feat_train = np.concatenate((feat_train1,feat_train2,feat_train3,feat_train4))
            feat_test = np.concatenate((feat_test1,feat_test2,feat_test3,feat_test4))
            label_train = np.concatenate((label_train1,label_train2,label_train3,label_train4))
            label_test = np.concatenate((label_test1,label_test2,label_test3,label_test4))

            ######## Inicio rede neural #######
            
            self.mlp = MLPClassifier(solver='lbfgs', random_state=5, max_iter=400, hidden_layer_sizes=[200,300])
            self.mlp.fit(feat_train, label_train)
            y_pred = self.mlp.predict(feat_test)


            print("Camadas da rede: {}".format(self.mlp.n_layers_))
            print("Neurônios na camada oculta: {}".format(self.mlp.hidden_layer_sizes))
            print("Neurônios na camada de saída: {}".format(self.mlp.n_outputs_))
            print("Pesos na camada de entrada: {}".format(self.mlp.coefs_[0].shape))
            print("Pesos na camada oculta: {}".format(self.mlp.coefs_[1].shape))

            print("Acurácia da base de treinamento: {:.2f}".format(self.mlp.score(feat_train, label_train)))
            print("Acurácia da base de teste: {:.2f}".format(self.mlp.score(feat_test, label_test)))

            # Calcula a matriz de confusão
            cnf_matrix = confusion_matrix(label_test, y_pred)
            acuracia = self.acuracia(cnf_matrix)
            especificidade = self.especificidade(cnf_matrix)
            
            # Calcula tempo de execução
            self.tempo = time.time() - inicio

            #Exibindo informações
            self.printaValores(tempo=self.tempo,matriz=cnf_matrix,espec=especificidade,acc=acuracia)

            print('Tempo de execução: {0}'.format(self.tempo))
        else:
            msgbx.showinfo(title="ATENÇÃO", message="Primeiro leia o diretório com as imagens de teste!")
    ################### FIM trein_clas ###################

    def analisar_area(self):
        """Analisa a area recortada pelo usuario"""

        if self.mlp != None:
            if self.temCrop:
                self.la2.config(image='',bg="#D8D8D8",width=0,height=0) #Remove a imagem atras do canvas
                self.temCrop = False

                cropped = cv2.imread('.crop.png')

                inicio = time.time()
                val = self.Hu(cropped) + self.Haralick(cropped)
                t = time.time() - inicio

                val = np.array(val)
                prediction = self.mlp.predict(val.reshape(1,-1))[0] #reshape(1,-1) pq há apenas uma instancia a ser avaliada com multiplos valores

                print(prediction)
                self.printaValores(tempo=t,carac=val)
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
    ################### FIM especificidade ###################

    def deleta_canvas(self):
        """Deleta o canvas existente"""
        if self.temCanvas:
            self.temCanvas = False
            self.canvas.delete("all")
            self.canvas.destroy()
            self.la.config(width=1,height=1,bg='#D8D8D8')
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
            self.canvas = tk.Canvas(self.la,bg='#D8D8D8', width=img.width(), height=img.height(), borderwidth=0, highlightthickness=0)
            self.canvas.pack(expand=True)
            self.canvas.img = img  
            self.canvas.create_image(0, 0, image=img, anchor=tk.NW)
            self.temCanvas = True

            rect_id = self.canvas.create_rectangle(topx, topy, botx, boty, fill='', outline='LimeGreen', width=2) # Desenha retangulo verde em cima da imagem
            self.la.config(image='',bg="#D8D8D8",width=0,height=0) #Remove a imagem atras do canvas
            self.temLabel = False
        elif not self.temLabel:
            msgbx.showinfo(title="ATENÇÃO", message="Selecione uma imagem antes!")
        else:
            msgbx.showinfo(title="ATENÇÃO", message="Selecione a área a ser recortada com dois cliques")
            
        self.canvas.bind('<Button-1>', get_mouse_posn)
        self.canvas.bind('<Double-Button-1>', confirm_cut) # O usuario deve dar clique duplo para confirmar corte   
    ################### FIM select_area ###################

    def printaValores(self,tempo=None,espec=None,acc=None,matriz=None,carac=None):
        #Criação Interface
        top = Toplevel()
        top.title("Informações")
        top.geometry('400x400')
        top.lift()      #Deixa a tela corrente no topo da pilha (gerenciador de janelas)

        string = ''
        if tempo is not None:
            string += ('\nTempo: \t\t%.3fs\n'%(tempo))
        if carac is not None:
            string += ('\nH1:\t\t%.6f\nH2:\t\t%.6f\nH3:\t\t%.6f\nH4:\t\t%.6f\nH5:\t\t%.6f\nH6:\t\t%.6f\nH7:\t\t%.6f\n'%(carac[0],carac[1],carac[2],carac[3],carac[4],carac[5],carac[6]))
            i = 7
            if self.caracteristicas[0]:
                string += ('\nEntropia:\t\t%.6f\n'%(carac[i]))
                i+=1
            if self.caracteristicas[1]:
                string += ('\nEnergia:\t\t%.6f\n'%(carac[i]))
                i+=1
            if self.caracteristicas[2]:
                string += ('\nHomogeneidade:\t%.6f\n'%(carac[i]))
                i+=1
            if self.caracteristicas[3]:
                string += ('\nContraste:\t\t%.6f\n'%(carac[i]))
        if espec is not None:
            string += ('\nEspecificidade:\t%.6f\n'%(espec))
        if acc is not None:
            string += ('\nPrecisão:\t\t%.1f%%\n'%(acc*100))
        if matriz is not None:
            string += ('\nMatriz de confusão:\n\n\t1\t2\t3\t4\n___________________________________________________\n1|\t%d\t%d\t%d\t%d\n2|\t%d\t%d\t%d\t%d\n3|\t%d\t%d\t%d\t%d\n 4|\t%d\t%d\t%d\t%d\n'\
                        %(matriz[0][0],matriz[0][1],matriz[0][2],matriz[0][3],\
                        matriz[1][0],matriz[1][1],matriz[1][2],matriz[1][3],\
                        matriz[2][0],matriz[2][1],matriz[2][2],matriz[2][3],\
                        matriz[3][0],matriz[3][1],matriz[3][2],matriz[3][3],))

        
        texto = Label(top, text=string)
        texto.pack()
    ################### FIM printaValores ###################
               
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
        self.mlp = None
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
        Button(fram, text="Analisar área selecionada", command=self.analisar_area).pack(side=LEFT)
        Button(fram, text="Selecionar Características", command=self.selec_car).pack(side=LEFT)
        Button(fram, text="Ler diretório", command=self.ler_dir).pack(side=LEFT)
        Button(fram, text="Treinar classificador", command=self.trein_clas).pack(side=LEFT)
        fram.pack(side=TOP, fill=BOTH)

        #Área em que a imagem ficará presente
        self.la = Label(self)
        self.la.config(bg='#D8D8D8')
        self.la.pack()

        #Área que o recorte ficará presente
        self.la2 = Label(self)
        self.la2.config(bg='#D8D8D8')
        self.la2.pack(side=BOTTOM)

        self.pack()
        
if __name__ == "__main__":
    app = App(); app.configure(bg='#D8D8D8',); app.mainloop()