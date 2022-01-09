# Usado para ler imagens
from PIL import Image
# Usado para armazenar imagem
import numpy as np
import os

class RLE:
    def __init__(self, nomeArq, tipoArq) -> None:
        self.nome_arq = nomeArq
        self.tipo_arq = tipoArq

        self.im = Image.open(self.nome_arq + self.tipo_arq)
        self.im = self.im.convert('RGB')
        pass

    def tamanhoArquivo(self, nome):
        f_size = os.path.getsize(nome)
        f_size_kb = f_size/1024
        # print(f_size_kb, "kB")
        return f_size_kb

    def comprime(self):
        # Converte imagem em matriz
        data = np.array(self.im)   # "data" is a height x width x 4 numpy array
        red, green, blue = data.T # Temporarily unpack the bands for readability

        # dimensoes da imagem
        img_width = len(red)
        img_heigth = len(red[0])

        size = [str(img_width), str(img_heigth)]

        # vetor com as cores salvas
        cores = [[red[0][0], green[0][0], blue[0][0]]]
        # vetor com as flags
        flags = [0]

        # loop que percorre as listas
        for i in range(img_heigth):
            for j in range(img_width):
                cor_atual = [red[i][j], green[i][j], blue[i][j]]

                # caso a cor seja igual anterior
                # aumenta o valor da flag
                if cor_atual == cores[len(cores)-1]:
                    flags[len(flags)-1] += 1
                # caso contrario adiciona nova cor
                else:
                    cores.append(cor_atual)
                    flags.append(1)

        saida = open(self.nome_arq + "_rle_compress.txt", "w")
        saida.write(size[0] + " ")
        saida.write(size[1] + " ")

        for i in range(len(cores)):
            saida.write(str(flags[i]) + " " + str(cores[i][0]) + " " + str(cores[i][1]) + " " + str(cores[i][2]) + " ")

        # fecha arquivo texto
        saida.close()
        # print(self.tamanhoArquivo(self.nome_arq + "_rle_compress.txt"), "kB")
        return "Tamanho do Arquivo Compresso: " + str(self.tamanhoArquivo(self.nome_arq + "_rle_compress.txt")).replace(".",",") + "kB"

    def descomprime(self):
        comprimido = open(self.nome_arq + "_rle_compress.txt", "r")

        tokens = []

        for l in comprimido:
            tokens = l.split()

        width = int(tokens[0])
        height = int(tokens[1])

        # remove token tamanho
        tokens = tokens[2:]

        img_descom = np.zeros(shape=(height, width, 3))

        cores = []

        for i in range(0, len(tokens), 4):
            repeticoes = int(tokens[i])

            for p in range(repeticoes):
                cores.append([int(tokens[i+1]), int(tokens[i+2]), int(tokens[i+3])])
        
        pos = 0
        for i in range(height):
            for j in range(width):
                img_descom[j][i][0] = cores[pos][0]
                img_descom[j][i][1] = cores[pos][1]
                img_descom[j][i][2] = cores[pos][2]
                pos += 1

        return img_descom

    def mostraDescomprimido(self):
        img_descom = self.descomprime()
        im2 = Image.fromarray((img_descom).astype(np.uint8))
        im2.show(title="Imagem Descompressao Algoritmo RLE")

# rle = RLE("cor", ".png")
# rle.comprime()
# rle.mostraDescomprimido()