from tkinter import Scale, Tk, Frame, Label, Button
from tkinter.ttk import Notebook,Entry
from tkinter import*

from ColorCellCompression import *
from RLE import *

window=Tk()
window.title("Compressão de Imagens")
window.geometry("600x400")

frame2=Frame(window)
frame2.pack(fill="both")

tablayout=Notebook(frame2)

tipo_compre = IntVar()

tab0=Frame(tablayout)
tab0.pack(fill="both")
final = StringVar()
final.set("Tamanho do Arquivo Compresso:")

def criaTela():

    text1 = StringVar()
    text1.set("Digite o nome do arquivo:")
    label = Label( tab0, textvariable=text1, relief=RAISED, width=50)
    label.grid(row=0,column=0, padx= 10, pady=3)

    entry1 = Entry(tab0, bd = 5)
    entry1.grid(row=0,column=1, padx= 10, pady=3)

    text2 = StringVar()
    text2.set("Digite o tipo do arquivo:")
    label = Label( tab0, textvariable=text2, relief=RAISED, width=50)
    label.grid(row=1,column=0, padx= 10, pady=3)

    entry2 = Entry(tab0, bd = 5)
    entry2.grid(row=1,column=1, padx= 10, pady=3)

    R1 = Radiobutton(tab0, text="Compressão RLE \n (Sem Perdas)", variable=tipo_compre, value=1)
    R1.grid(row=2,column=0, padx= 2, pady=3)

    R2 = Radiobutton(tab0, text="Compressão Color Cell Compression \n (Com Perdas)", variable=tipo_compre, value=0)
    R2.grid(row=2,column=1, padx= 2, pady=3)

    def commandExecuta(tipo_compre):
        if tipo_compre.get() == 1:
            r = RLE(entry1.get(), entry2.get())
            s = r.comprime()
            r.mostraDescomprimido()
            final.set(s)
        else:
            ccc = ColorCellCompression(entry1.get(), entry2.get(), 4, 256)
            s = ccc.comprime()
            r = ccc.descompactada()
            
            im2 = Image.fromarray((r).astype(np.uint8))
            im2.show(title="Imagem Descompressao Algoritmo RLE")
            final.set(s)


    btnExec = Button(tab0, height=1, width=10, text="Executa", 
                            command= lambda:commandExecuta(tipo_compre))
    btnExec.grid(row=3,column=0, padx= 10, pady=3)


    label = Label( tab0, textvariable=final, relief=RAISED, width=50)
    label.grid(row=4,column=0, padx= 10, pady=3)

    explica = StringVar()

    aux = ""
    aux += "RLE: Esta algoritmo apenas substitui sequencia de pixeis com\n" 
    aux += "valores identicos por um pixel acompanhado de um flag que\n"
    aux += "representa o numero de repetições."
    explica.set(aux)

    explica2 = StringVar()

    aux = "CCC: Cria uma paleta com as 256 cores mais presentes na\n" 
    aux += "imagem original. Substitui os valores dos pixeis por indices da\n"
    aux += "tabela com a cor mais semelhante com a do grupo em que o pixel\n"
    aux += "é alocado dependendo de sua \nlumicescencia."
    explica2.set(aux)

    label2 = Label( tab0, textvariable=explica, relief=RAISED, width=50, anchor="w")
    label2.grid(row=5,column=0, padx= 10, pady=3)

    label3 = Label( tab0, textvariable=explica2, relief=RAISED, width=50, anchor="w")
    label3.grid(row=6,column=0, padx= 10, pady=3)

    tablayout.add(tab0,text="")
    tablayout.pack(fill="both")

criaTela()
window.mainloop()