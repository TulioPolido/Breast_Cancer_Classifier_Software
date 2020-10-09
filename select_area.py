import tkinter as tk
from PIL import Image, ImageTk

WIDTH, HEIGHT = 900, 900
topx, topy, botx, boty = 0, 0, 0, 0
rect_id = None
path = "teste.png"

def get_mouse_posn(event):
    global topy, topx, botx, boty
    global rect_id
    topx, topy = event.x, event.y
    botx = topx + 64
    boty = topy + 64
    topx = topx - 64
    topy = topy - 64
    canvas.coords(rect_id, topx, topy, botx, boty) 

window = tk.Tk()
window.title("Select Area")
window.geometry('%sx%s' % (WIDTH, HEIGHT))
window.configure(background='grey')

img = ImageTk.PhotoImage(Image.open(path))
canvas = tk.Canvas(window, width=img.width(), height=img.height(),
                   borderwidth=0, highlightthickness=0)
canvas.pack(expand=True)
canvas.img = img  
canvas.create_image(0, 0, image=img, anchor=tk.NW)

# Desenha retangulo verde em cima da imagem
rect_id = canvas.create_rectangle(topx, topy, botx, boty,
                                  fill='', outline='LimeGreen', width=2.0)

def confirm_cut(event):  # Função para recortar região de interesse selecionada pelo usuário
    global topx, topy, botx, boty
    global path
    border = (topx, topy, botx, boty)
    imgCrop = Image.open(path).crop(border)
    print('Salvando imagem....')
    imgCrop.save("cropped.png", "PNG")
    

canvas.bind('<Button-1>', get_mouse_posn)
canvas.bind('<Double-Button-1>', confirm_cut) # O usuario deve dar clique duplo para confirmar corte

window.mainloop() 