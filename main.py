import PySimpleGUI as sg
import os
from PIL import Image, ImageTk
import io

def get_img_data(f, zoom, maxsize=(650, 650), first=False):
    """Gera as imagens utilizando Pillow"""

    img = Image.open(f)
    w = img.width
    h = img.height
    w = int(w * zoom)
    h = int(h * zoom)
    img = img.resize((w,h))
    img.thumbnail(maxsize)
    if first:
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


#Driver
zoom = float(1)
folder = sg.popup_get_folder('Escolha a pasta de imagens:', default_path='')
if not folder:
    sg.popup_cancel('Cancelando.')
    raise SystemExit()

img_types = (".png", ".dcm", ".tiff") #Tipos de imagens suportados
flist0 = os.listdir(folder) #Listagem de arquivos no diretorio
fnames = [f for f in flist0 if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(img_types)] #Nomes das imagens a serem listadas

num_files = len(fnames) #qtd de imagens
if num_files == 0:
    sg.popup('A pasta escolhida está vazia.')
    raise SystemExit()

filename = os.path.join(folder, fnames[0])  #Pega a primeira imagem como arquivo inicial a ser exibido
image_elem = sg.Image(data=get_img_data(filename, zoom, first=True)) #Estabelece como o elemento imagem deve ser exibido
filename_display_elem = sg.Text(filename, size=(80, 3)) #Estabelece como o nome da imagem deve ser exibido

#Coluna que exibe a imagem a seu nome
col = [[filename_display_elem],
       [image_elem],
       [sg.Button('Zoom In', size=(8, 2)), sg.Button('Zoom Out', size=(8, 2))]]

#Coluna que lista os elementos da pasta
col_files = [[sg.Listbox(values=fnames, change_submits=True, size=(60, 30), key='listbox')]]

#Layout completo
layout = [[sg.Column(col_files), sg.Column(col)]]

window = sg.Window('Trabalho de PI', layout, return_keyboard_events=True,
                   location=(0, 0), use_default_focus=False)

# loop do programa
i = 0
while True:
    event, values = window.read()
    print(event, values) #Para debugar
   
    if event == sg.WIN_CLOSED: #Se janela for fechada, sair finalizar o loop
        break

    elif event == 'listbox': 
        f = values["listbox"][0]            
        filename = os.path.join(folder, f)  
        i = fnames.index(f)  

    elif event in ('Zoom Out', 'MouseWheel:Down'):  
        if zoom > 0.5: 
            zoom -= 0.1
        print(zoom)
        image_elem.update(data=get_img_data(filename, zoom, first=True)) #Atualiza imagem

    elif event in ('Zoom In', 'MouseWheel:Up'):     
        if zoom < 2.0:
            zoom += 0.1  
        print(zoom)
        image_elem.update(data=get_img_data(filename, zoom, first=True)) #Atualiza imagem

    else:
        filename = os.path.join(folder, fnames[i])

    if filename.endswith(".dcm"): #Se for DICOM necessitará de conversão
        print("Arquivo dcm")
    else:
        image_elem.update(data=get_img_data(filename, zoom, first=True)) #Atualiza imagem
        filename_display_elem.update(filename) #Atualiza nome da imagem

window.close()