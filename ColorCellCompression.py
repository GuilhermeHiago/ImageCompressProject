# Usado para ler imagens
from PIL import Image
# Usado para armazenar imagem
import numpy as np
# Usado para ordenar o historiograma
from operator import itemgetter

class ColorCellCompression:
    def __init__(self, nomeArquivo, tipoArq, tamCel, maxCores) -> None:
        #######################################
        #### VARIAVEIS DO ALGORITMO
        #######################################

        self.tam_celula = tamCel
        self.max_cores = maxCores

        # variaveis do histograma
        self.cores = []
        self.freq = {}
        self.texto = ""
        # Carrega imagem
        self.im = Image.open(nomeArquivo + tipoArq)
        self.im = self.im.convert('RGBA')
        self.nomeArq = nomeArquivo
        self.tipoArq = tipoArq

    # Calcula luminescencia de pixel com equação 
    # do algoritmo Color Cell Compression
    def calcula_luminescencia(self, r, g, b):
        return 0.30 * r + 0.59 * g + 0.11 * b

    # Metodo necessario para calcular a distancia entre cores
    def distancia_cor(self, r1, g1, b1, r2, g2, b2):
        r = (r1-r2)**2
        g = (g1-g2)**2
        b = (b1-b2)**2

        return (r + g + b)**(1/2)

    # Metodo que recebe uma cor e uma lista de cores
    # retorna a cor mais semelhante encontrada
    def encontra_cor_prox(self, r, g, b, list_cores):
        pos_prox = 0
        dist_anterior = self.distancia_cor(r, g, b, list_cores[0][0], list_cores[0][1], list_cores[0][2])

        for i in range(len(list_cores)):
            dist = self.distancia_cor(r, g, b, list_cores[i][0], list_cores[i][1], list_cores[i][2])
            
            if dist < dist_anterior:
                dist_anterior = dist
                pos_prox = i

        return pos_prox

    def cria_tabela_cores(self):
        # Converte imagem em matriz
        data = np.array(self.im)   # "data" is a height x width x 4 numpy array
        red, green, blue, alpha = data.T # Temporarily unpack the bands for readability

        img_size = len(red)

        #######################################
        #### CRIA TABELA DE FREQ CORES
        #######################################

        for i in range(len(red)):
            for j in range(len(red[0])):
                cor = [red[i][j], green[i][j], blue[i][j]]

                # Se cor ja presente incrementa frequencia
                if str(cor) in self.freq.keys():
                    self.freq[str(cor)] = self.freq[str(cor)] + 1
                # Caso contrario adiciona
                else:
                    self.cores.append(cor)
                    self.freq[str(cor)] = 1

        # Ordena a tabele em ordem decrescente
        decrescente = sorted(self.freq.items(), key=itemgetter(1), reverse=True)

        #######################################
        #### SELECIONA 256 CORES MAIS USADAS 
        #### E COM DISTANCIA MINIMA
        #######################################
        cores_uso = []
        distancia_min_cor = 10

        for i in range(len(decrescente)):
            ult_pos = 0

            insere = True

            # trata string
            lista = []
            s = decrescente[i][0]
            lista.append(int(s[1: s.find(',')]))
            s = s[s.find(',')+1:]
            lista.append(int(s[0: s.find(','):]))
            s = s[s.find(',')+1:]
            lista.append(int(s[0: s.find(']'):]))

            # se a cor nova for proxima da ja adicionadas
            for d in cores_uso:
                if self.distancia_cor(d[0], d[1], d[2], lista[0], lista[1], lista[2]) < distancia_min_cor:
                    insere = False
            
            if insere:
                cores_uso.append(lista)
                self.texto += " " + str(lista[0]) + " " + str(lista[1]) + " " + str(lista[2])

            if len(cores_uso) == 256:
                break
            
        self.texto = str(len(red)) + " " + str(len(red[0])) + " " + str(len(cores_uso)) + " " + str(self.tam_celula) + self.texto
        return cores_uso

    def comprime(self):
        cores_uso = self.cria_tabela_cores()

        data = np.array(self.im)   # "data" is a height x width x 4 numpy array
        red, green, blue, alpha = data.T # Temporarily unpack the bands for readability

        img_size = len(red)

        #######################################
        #### COMPRIME IMAGEM
        #######################################

        # posição na largura
        pos = 0
        # posição na altura
        pos2 = 0

        while pos < img_size and pos2 < img_size:
            lumi, bitmap = [], []

            for i in range(self.tam_celula):
                lumi.append([])

            for i in range(self.tam_celula):
                bitmap.append([])

            cor1, cor2 = [0, 0, 0], [0, 0, 0]

            # Calcula luminescencia de todos na celula
            for i in range(pos, pos+self.tam_celula):
                for j in range(pos2, pos2+self.tam_celula):
                    lumi[i-pos].append(self.calcula_luminescencia(red[i][j], green[i][j], blue[i][j]))

            # soma todos elementos de lumi e faz a media
            lumi_media = sum([sum(x) for x in lumi]) / (len(lumi) * len(lumi[0]))

            # nas posiçoes que lumi[i][j] > lumi_media, bitmap[i][j] = 1, se nao, bitmap[i][j] = 0
            bitmap = [[ 1 if lumi[i][j] > lumi_media else 0 for j in range(len(lumi[0]))] for i in range(len(lumi))]

            # INICIO calculo da media para cor 1 e cor 2
            soma1 = [0, 0, 0]
            soma2 = [0, 0, 0]

            n_soma1, n_soma2 = 0, 0

            # Soma cores da celula nos grupos 0 ou 1 do Bitmap
            for i in range(pos, pos+self.tam_celula):
                for j in range(pos2, pos2+self.tam_celula):
                    if(bitmap[i-pos][j-pos2] == 1):
                        soma1[0] += red[i][j]
                        soma1[1] += green[i][j]
                        soma1[2] += blue[i][j]
                        n_soma1 += 1
                    else:
                        soma2[0] += red[i][j]
                        soma2[1] += green[i][j]
                        soma2[2] += blue[i][j]
                        n_soma2 += 1

            if n_soma1 == 0:
                cor1 = [red[pos][pos2], green[pos][pos2], blue[pos][pos2]]
            else:    
                cor1 = [x/n_soma1 for x in soma1]

            if n_soma2 == 0:
                cor2 = [red[pos][pos2], green[pos][pos2], blue[pos][pos2]]
            else:    
                cor2 = [x/n_soma2 for x in soma2]
            # FIM calculo da media para cor 1 e cor 2

            # troca cor 1 por uma das 256, a mais proxima
            indice1 = self.encontra_cor_prox(cor1[0], cor1[1], cor1[2], cores_uso)
            cor1 = cores_uso[indice1]
            # troca cor 1 por uma das 256, a mais proxima
            indice2 = self.encontra_cor_prox(cor2[0], cor2[1], cor2[2], cores_uso)
            cor2 = cores_uso[indice2]

            self.texto += " " + str(indice1) + " " + str(indice2)
            
            # Para cada pixel da celula define RGB
            for i in range(pos, pos+self.tam_celula):
                for j in range(pos2, pos2+self.tam_celula):
                    if(bitmap[i-pos][j-pos2] == 1):
                        self.texto += " 1"
                    else:
                        self.texto += " 0"

            # Avança pos na largura
            pos += 4
            # Avança pos na altura
            if pos >= img_size:
                pos = 0
                pos2 += 4

        arq = open(self.nomeArq + "_ccc_compress.txt", "w")
        arq.write(self.texto)
        arq.close()

        tam_kb = (len(red)*len(red[0]))*2*0.000125
        # tam = 32 bits por celula vezes o numero de celulas (comprimento/self.tam_celula)
        tam = 32 * (len(red)/4)*(len(red[0])/4)
        # n cores * 24 bits (n de bits por cor)
        tam_palete = len(cores_uso) * 24

        tam_kb = (tam + tam_palete) * 0.000125

        s = "Tamanho do Arquivo Compresso: " + str(tam_kb) + "kB" + "\n"
        s = s.replace(".", ",")
        s += "Numero de cores: " + str(len(cores_uso)) + "\n"
        s = s.replace(".", ",")
        s += "Tamanho Pallet de Cores: " + str(tam_palete*0.000125) + " kB"
        s = s.replace(".", ",")
        return s

    def descompactada(self):
        arq = open(self.nomeArq + "_ccc_compress.txt", "r")

        tokens = []

        for l in arq:
            tokens = l.split(" ")

        width = int(tokens[0])
        height = int(tokens[1])

        img_descom = np.zeros(shape=(height, width, 3))

        n_cores = int(tokens[2])
        cell_size = int(tokens[3])
        # remove token tamanho
        tokens = tokens[4:]

        # Carrega as cores salvas no arquivo
        cores = []
        token_pos = 0
        for i in range(n_cores):
            cores.append([tokens[token_pos], tokens[token_pos+1], tokens[token_pos+2]])
            # token_pos += 3
            tokens = tokens[3:]

        n = (width * height) // cell_size
        img_x, img_y = 0, 0

        for iteracao in range(n):
            if len(tokens) < 1:
                 break 
            
            indice1 = int(tokens[0])
            indice2 = int(tokens[1])

            tokens = tokens[2:]
            bitmap = np.zeros(shape=(cell_size, cell_size))
            # print(cell_size)
            # print(bitmap)

            for i in range(cell_size):
                for j in range(cell_size):
                    bitmap[i][j] = tokens[0]
                    tokens = tokens[1:]

            for j in range(cell_size):
                for i in range(cell_size):
                    if bitmap[i][j] == 1:
                        img_descom[j+img_y][i+img_x][0] = cores[indice1][0]
                        img_descom[j+img_y][i+img_x][1] = cores[indice1][1]
                        img_descom[j+img_y][i+img_x][2] = cores[indice1][2]
                    elif bitmap[i][j] == 0:
                        img_descom[j+img_y][i+img_x][0] = cores[indice2][0]
                        img_descom[j+img_y][i+img_x][1] = cores[indice2][1]
                        img_descom[j+img_y][i+img_x][2] = cores[indice2][2]
            # Avança pos na largura
            img_x += 4
            # Avança pos na altura
            if img_x >= width:
                img_x = 0
                img_y += 4

        return img_descom

        