import numpy as np
import cv2
import time 
import copy
import os
from pygame import mixer
mixer.init() # initiate the mixer instance

path = os.path.join(os.path.dirname(__file__))
path_images = path + "\imagenes"
path_sounds = path + "\sounds"

class ficha:
    def __init__(self, color, row=0, col=0, posx=0, posy=0):
        self.color = color
        if not posx:
            self.row = row
            self.col = col
            self.posy = 85+52+104*row
            self.posx = 85+52+104*col
        else:
            self.posx = posx
            self.posy = posy
            self.row = int((self.posy-85-52)/104)
            self.col = int((self.posx-85-52)/104)
        
    def act_pos(self, posy, posx):
        self.posx = posx
        self.posy = posy
        
    def act_cell(self, row, col):
        self.row = row
        self.col = col
        self.posy = 85+52+104*row
        self.posx = 85+52+104*col
    
    def centrar(self):
        self.posy = 85+52+104*self.row
        self.posx = 85+52+104*self.col
    
    def center_cell(self):
        return 85+52+104*self.col, 85+52+104*self.fil
    
class peon(ficha):
    def __init__(self, color, row=0, col=0, posx=0, posy=0):
       super().__init__(color, row, col, posx, posy)
       self.id = self.color + 'P'
       self.img = cv2.resize(cv2.imread(path_images + "\\" + self.id + ".png", cv2.IMREAD_UNCHANGED),(100,100))
       self.movido = False
       
    def valid_mov(self, row, col, ficha_atacada):
        if(ficha_atacada == None and self.col!=col):
            return False
        elif self.movido and abs(self.row-row) > 1:  
            return False
        elif not self.movido and abs(self.row-row) > 2:  
            return False
        elif (ficha_atacada != None and self.color == ficha_atacada.color):  
            return False
        elif ((ficha_atacada != None) and (abs(self.row-row)!=1 or abs(self.col-col)!=1)):
            return False
        elif(self.color=='w' and self.row<row):
            return False
        elif(self.color=='b' and self.row>row):
            return False
        return True
    
class tower(ficha):
    def __init__(self, color, row=0, col=0, posx=0, posy=0):
       super().__init__(color, row, col, posx, posy)
       self.id = self.color + 'T'
       self.img = cv2.resize(cv2.imread(path_images + "\\" + self.id + ".png", cv2.IMREAD_UNCHANGED),(100,100))
       self.movido = False
       
    def valid_mov(self, row, col, ficha_atacada):
        if (abs(self.row-row)!=0 and abs(self.col-col)!=0):
            return False
        elif (ficha_atacada != None and self.color == ficha_atacada.color):  
            return False
        return True
       
class horse(ficha):
    def __init__(self, color, row=0, col=0, posx=0, posy=0):
         super().__init__(color, row, col, posx, posy)
         self.id = self.color + 'H'
         self.img = cv2.resize(cv2.imread(path_images + "\\" + self.id + ".png", cv2.IMREAD_UNCHANGED),(100,100))
    
    def valid_mov(self, row, col, ficha_atacada):
        if ((abs(self.row-row) + abs(self.col-col))!=3) or not (abs(self.row-row)==1)^(abs(self.col-col)==1):
            return False
        elif (ficha_atacada != None and self.color == ficha_atacada.color):  
            return False
        return True
    
class alfil(ficha):
    def __init__(self, color, row=0, col=0, posx=0, posy=0):
        super().__init__(color, row, col, posx, posy)
        self.id = self.color + 'A'
        self.img = cv2.resize(cv2.imread(path_images + "\\" + self.id + ".png", cv2.IMREAD_UNCHANGED),(100,100))
    
    def valid_mov(self, row, col, ficha_atacada):
        if abs(self.row-row)!=abs(self.col-col):
            return False
        elif (ficha_atacada != None and self.color == ficha_atacada.color):  
            return False
        return True
    
class queen(ficha):
    def __init__(self, color, row=0, col=0, posx=0, posy=0):
         super().__init__(color, row, col, posx, posy)
         self.id = self.color + 'Q'
         self.img = cv2.resize(cv2.imread(path_images + "\\" + self.id + ".png", cv2.IMREAD_UNCHANGED),(100,100))
    
    def valid_mov(self, row, col, ficha_atacada):
        if not ((abs(self.row-row)!=0 and abs(self.col-col)!=0)^(abs(self.row-row)!=abs(self.col-col))):
            return False
        elif (ficha_atacada != None and self.color == ficha_atacada.color):  
            return False
        return True

class king(ficha):
    def __init__(self, color, row=0, col=0, posx=0, posy=0):
        super().__init__(color, row, col, posx, posy)
        self.id = self.color + 'K'
        self.img = cv2.resize(cv2.imread(path_images + "\\" + self.id + ".png", cv2.IMREAD_UNCHANGED),(100,100))
        self.movido = False
        
    def valid_mov(self, row, col, ficha_atacada):
        if (abs(self.row-row)> 1 or abs(self.col-col) > 1):
            return False
        elif (ficha_atacada != None and self.color == ficha_atacada.color):  
            return False
        return True
    
# Los margenes el tablero son 84px, y cada cuadrado son 104px
class Tablero:
    clear_tablero_img = cv2.imread(path_images + "\\tablero.jpg")
    ficha_mano = None
    tablero_aux_img = np.zeros((1000,1000,4))  
    tablero_aux = np.full((8,8),None)
    
    def __init__(self):
        # Se define el tablero
        self.tablero = np.full((8,8),None)
        self.tablero[0] = [tower('b',0,0),horse('b',0,1),alfil('b',0,2),queen('b',0,3),king('b',0,4),alfil('b',0,5),horse('b',0,6),tower('b',0,7)]
        for col in range(8): self.tablero[1][col] = peon('b',1,col)
        for col in range(8): self.tablero[6][col] = peon('w',6,col)
        self.tablero[7] = [tower('w',7,0),horse('w',7,1),alfil('w',7,2),queen('w',7,3),king('w',7,4),alfil('w',7,5),horse('w',7,6),tower('w',7,7)]

        # Se crea la imagen 
        self.tablero_img = cv2.imread(path_images + "\\tablero.jpg")
        for fil in range(8):
            for col in range(8):
                if(self.tablero[fil][col] != None): self.draw_ficha(self.tablero[fil][col])
        
        # El turno empieza en las blancas
        self.turno = 'w'
        
        # Varible que guarda si hay jaque
        self.HayJaque = False
        
        # Se muestra el tablero
        self.show() 
    
        
    def coord_to_cell(self, pos):
        return int((pos-85)/104)
    
    def draw_ficha(self, ficha):
        if(ficha != None and (ficha.posy+52<1000 and ficha.posx+52 < 1000)):
            img_ficha = ficha.img
            indices = np.where(img_ficha[:,:,3] !=0)
            self.tablero_img[indices[0]+ficha.posy-52, indices[1]+ficha.posx-52] = img_ficha[indices][:,0:3]
                
    def clean_ficha(self, ficha):
        if ficha != None:
            if(ficha.posy+52 < 1000 and ficha.posx+52 < 1000):
                self.tablero_img[ficha.posy-52:ficha.posy+52,ficha.posx-52:ficha.posx+52] = self.clear_tablero_img[ficha.posy-52:ficha.posy+52,ficha.posx-52:ficha.posx+52]
        
    def change_turno(self):
        if(self.turno == 'w'): self.turno = 'b'
        else: self.turno = 'w'
        
    def corona(self, ficha):  
        corona = False
        if(ficha.id[1] != 'P'): 
            corona = False
        elif(ficha.color == 'w' and ficha.row == 0):
            corona = True
        elif(ficha.color == 'b' and ficha.row == 7):
            corona = True
        return corona
    
    def is_block(self, ficha, row_fin, col_fin):
        if(ficha == None): return True
        if(ficha.id[1] == 'H'): return False 
        #if(ficha == horse()): return True
        
        if(ficha.id[1] == 'T' or (ficha.id[1] == 'Q' and (ficha.col==col_fin or ficha.row==row_fin))):
            #Bloqueo en columna?
            lenght_row = ficha.row - row_fin
            for i in range(abs(lenght_row) - 1):
                if(lenght_row<0):
                    if(self.tablero[ficha.row - lenght_row - i - 1][ficha.col] != None):
                        return True
                else:
                    if(self.tablero[ficha.row - lenght_row + i + 1][ficha.col] != None):
                        return True
        
            #Bloqueo en fila?
            lenght_col = ficha.col - col_fin
            for i in range(abs(lenght_col) - 1):
                if(lenght_col<0):
                    if(self.tablero[ficha.row][ficha.col - lenght_col - i - 1] != None):
                        return True
                else:
                    if(self.tablero[ficha.row][ficha.col - lenght_col + i + 1] != None):
                        return True        
         
        
        if(ficha.id[1] == 'A' or (ficha.id[1] == 'Q' and (abs(ficha.row-row_fin)==abs(ficha.col-col_fin)))):
            lenght= ficha.row - row_fin
            #Bloqueo diagonal /
            if(((ficha.col - col_fin) > 0)^((ficha.row - row_fin) > 0)):
                for i in range(abs(lenght) - 1):
                    
                    if(lenght<0):
                        if(self.tablero[ficha.row - lenght - i - 1][ficha.col + lenght + i + 1] != None):
                            return True
                    else:
                        if(self.tablero[ficha.row - lenght + i + 1][ficha.col + lenght - i - 1] != None):
                            return True  
            else:
                for i in range(abs(lenght) - 1):
                    if(lenght<0):
                        if(self.tablero[ficha.row - lenght - i - 1][ficha.col - lenght - i - 1] != None):
                            return True
                    else:
                        if(self.tablero[ficha.row - lenght + i + 1][ficha.col - lenght + i + 1] != None):
                            return True  
        return False
    
    def movimiento_valido(self, ficha, row_fin, col_fin, ficha_atacada):
        valid = True
        if(not ficha.valid_mov(row_fin, col_fin, ficha_atacada) or self.is_block(ficha, row_fin, col_fin)): 
            valid = False
        
        ficha_mano_aux = copy.copy(ficha)
        self.tablero_aux = self.tablero.copy();
        
        # #Simulación movimiento para ver si habrá un jaque
        self.tablero[ficha.row][ficha.col]  = None # Actualizo el tablero
        ficha_mano_aux.act_cell(row_fin,col_fin)
        self.tablero[row_fin][col_fin]  =  ficha_mano_aux  # Actualizo el tablero

        if(self.jaque()): valid = False
        self.tablero = self.tablero_aux.copy()
        return valid

    def jaque(self):
        aux = np.where(self.tablero != None)
        
        #Busco donde esta el rey del que le toca
        pos_rey = (0,0)
        for pieza in self.tablero[aux]:
            if(pieza.id[1] == 'K' and pieza.color == self.turno): 
                pos_rey = (pieza.row,pieza.col)
        
        hayJaque = False
        #Busco todos los atacantes y miro a ver si hay un jaque
        for pieza in self.tablero[aux]:
            if(hayJaque): break
            if(pieza.color != self.turno):
                if(pieza.id[1] != 'P'):
                    for i_pieza in range(8):
                        for j_pieza in range(8):
                            if(pieza.valid_mov(i_pieza, j_pieza, self.tablero[i_pieza][j_pieza]) and not self.is_block(pieza, i_pieza, j_pieza)):
                                if(pos_rey == (i_pieza,j_pieza)):
                                    hayJaque = True
                else:   
                    if(pieza.color == 'w'):
                        if(pos_rey == (pieza.row - 1,pieza.col - 1) or pos_rey == (pieza.row - 1,pieza.col + 1)):
                            hayJaque = True
                    else:
                        if(pos_rey == (pieza.row + 1,pieza.col - 1) or pos_rey == (pieza.row + 1,pieza.col + 1)):
                            hayJaque = True
        
        return hayJaque
    
    def SinMovimientos(self):
        SinMovimientos = True
        aux = np.where(self.tablero != None)
        
        for pieza in self.tablero[aux]:
            if not SinMovimientos: break
            if(pieza.color == self.turno):
               for i_pieza in range(8):
                    for j_pieza in range(8):
                        if(self.movimiento_valido(pieza, i_pieza, j_pieza, self.tablero[i_pieza][j_pieza])):
                            SinMovimientos = False
                
        return SinMovimientos
            
    def enrroque(self, row_fin, col_fin):
        if(self.ficha_mano.id[1] != 'K'): return False
        if(self.ficha_mano.movido == True): return False
        enrroque = False
        row = self.ficha_mano.row
        if(col_fin == 6): 
            #Si no es una torre y no se movido enrroque es false
            if(self.tablero[row][7].id[1] == 'T' and self.tablero[row][7].movido==False):
                self.tablero[row][self.ficha_mano.col]  = None
                self.tablero[row][6] = self.ficha_mano
                self.ficha_mano.act_cell(row, 6)
                self.clean_ficha(self.ficha_mano)
                self.draw_ficha(self.ficha_mano)
                
                self.tablero[self.ficha_mano.row][5] = self.tablero[self.ficha_mano.row][7]
                self.clean_ficha(self.tablero[self.ficha_mano.row][7])
                self.tablero[self.ficha_mano.row][5].act_cell(row, 5)
                self.draw_ficha(self.tablero[self.ficha_mano.row][7])
                self.tablero[self.ficha_mano.row][7] = None
                mixer.music.load(path_sounds + '\enroque.mp3')
                enrroque = True
                
        if(col_fin == 1 or col_fin == 2):
            if(self.tablero[self.ficha_mano.row][0].id[1] == 'T' and self.tablero[self.ficha_mano.row][0].movido==False):
                self.tablero[row][self.ficha_mano.col]  = None
                self.tablero[row][2] = self.ficha_mano
                self.ficha_mano.act_cell(row, 2)
                self.clean_ficha(self.ficha_mano)
                self.draw_ficha(self.ficha_mano)
                
                self.tablero[self.ficha_mano.row][3] = self.tablero[self.ficha_mano.row][0]
                self.clean_ficha(self.tablero[self.ficha_mano.row][0])
                self.tablero[self.ficha_mano.row][3].act_cell(row, 3)
                self.draw_ficha(self.tablero[self.ficha_mano.row][0])
                self.tablero[self.ficha_mano.row][0] = None
                mixer.music.load(path_sounds + '\enroque.mp3')
                enrroque = True
                
        return enrroque
        
        
    def mouse_click(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.ficha_mano = self.tablero[self.coord_to_cell(y)][self.coord_to_cell(x)]
            if(self.ficha_mano != None):
                if(self.ficha_mano.color != self.turno): 
                    self.ficha_mano = None
                else:
                    self.tablero_aux = self.tablero.copy() #Guardo copias de como estaba el tablero antes de mover nada
                    self.tablero[self.coord_to_cell(y)][self.coord_to_cell(x)]  = self.ficha_mano
                    self.clean_ficha(self.ficha_mano)
                    self.tablero_aux_img = self.tablero_img.copy() #Guardo copias de como estaba el tablero antes de mover nada
                    self.ficha_mano.act_pos(posy=y,posx=x)
                    self.draw_ficha(self.ficha_mano)
                    self.show()
                
        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            if(self.ficha_mano != None):
                self.tablero_img = self.tablero_aux_img.copy()
                self.ficha_mano.act_pos(posy=y,posx=x)
                self.draw_ficha(self.ficha_mano)
                self.show()
            
        elif event == cv2.EVENT_LBUTTONUP:
            error = False
            if(self.ficha_mano != None):
                self.tablero_img = self.tablero_aux_img.copy()
                row_fin = self.coord_to_cell(y)
                col_fin = self.coord_to_cell(x)
                
                
                #Si se sale de los límites del tablero, cargatelo
                if(not(row_fin > 7 or col_fin > 7)):
                    ficha_atacada = self.tablero[row_fin][col_fin];
                    if(ficha_atacada != None): mixer.music.load(path_sounds + '\capture.mp3')
                    else: mixer.music.load(path_sounds + '\move.mp3')
                else:
                    error = True
            
                if not error:
                    enrrocado = False
                    if((enrrocado := self.enrroque(row_fin, col_fin) ) or (self.movimiento_valido(self.ficha_mano, row_fin, col_fin, ficha_atacada) and (ficha_atacada == None or ficha_atacada.id[1]!='K'))):
                        if not enrrocado:
                            self.tablero[self.ficha_mano.row][self.ficha_mano.col]  = None # Actualizo el tablero
                            self.ficha_mano.act_cell(row_fin, col_fin)
                            self.clean_ficha(self.ficha_mano)
                            if(self.corona(self.ficha_mano)): self.ficha_mano = queen(self.ficha_mano.color, self.ficha_mano.row, self.ficha_mano.col) #Si corona lo cambio por una reina
                            self.tablero[row_fin][col_fin]  =  self.ficha_mano # Actualizo el tablero
                            self.draw_ficha(self.ficha_mano)
                            if(self.ficha_mano.id[1] == 'P' or self.ficha_mano.id[1] == 'T' or self.ficha_mano.id[1] == 'K'): self.ficha_mano.movido = True;
                          
                       
                        self.show()
                        mixer.music.play()
                        # Si ha llegado hasta aqui es que ya se ha movido, así que se cambia de turno
                        self.change_turno()
                        
                        
                        #Tengo jaque?
                        self.HayJaque = self.jaque()
                        sinMov = self.SinMovimientos()
                        if self.HayJaque and sinMov:
                            cv2.imshow('Ajedrez',cv2.imread(path_images + "\\fin.jpg"))
                            cv2.waitKey(0)
                            self.__init__()
                        elif(sinMov):
                            cv2.imshow('Ajedrez',cv2.imread(path_images + "\\ahogado.jpg"))
                            cv2.waitKey(0)
                            self.__init__()
                            
                    else:
                        self.ficha_mano.centrar() # Centramos las posx y las posy, según la celda en la que está (sigue siendo la primera ya que no se ha movido)
                        self.tablero[self.ficha_mano.row][self.ficha_mano.col]  = self.ficha_mano
                        self.draw_ficha(self.ficha_mano)
                        self.show()    
                
    def show(self):
        cv2.imshow('Ajedrez',self.tablero_img)
        cv2.setMouseCallback("Ajedrez", self.mouse_click)
        

class Ajedrez:
    def __init__(self):
        self.Tablero = Tablero()
        self.turno = 'w'
    
if __name__ == '__main__':    
    tablero = Tablero()
    tablero.show()
    k = 100
    # 'e' to EXIT
    while k != 101:
        k = cv2.waitKey(0)

    