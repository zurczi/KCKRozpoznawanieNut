import numpy as np
import cv2
import pieciolinia as piecio
from skimage.morphology import square
from skimage import morphology

def inwersja(img):
    return (255 - img)
# korekcja gamma
def gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

# skaluje zdjecie na podatawie podanej wysokosci
def skaluj_wysokosc(img, height):
    percent = height / float(img.shape[0])
    return cv2.resize(img, (int(img.shape[1] * percent), height))

# skaluje zdjecie na podstawie podanej szerokosci
def skaluj_szerokosc(img, width):
    percent = width / float(img.shape[1])
    return cv2.resize(img, (width, int(img.shape[0] * percent)))

# rozmazuje zdjecie o okreslony wspolczeynnik, nastepnie proguje obraz
def rozmaz_proguj(img, poziom_rozmazania, prog):
    img = cv2.GaussianBlur(img, (poziom_rozmazania, poziom_rozmazania), 0)
    img = progowanie(img, prog)
    return img


# zamienia piksele obrazu img na wartosci 0 i 255 porownujac piksel do prog
def progowanie(img, prog):
    # Load an color image in grayscale
    thresh = prog
    binary = (img > thresh) * 255
    binary = np.uint8(binary)  # unit64 => unit8
    return binary


# wczytuje obrazy o nazwach okreslonych w tablicy nazwy
def wczytaj(nazwy):
    wzorce = []
    for plik in nazwy:
        img = cv2.imread(plik, 0)
        wzorce.append(progowanie(img, 100))
    return wzorce

# wczytuje obraz i zamienia go na odcien szarosci
def laduj_szary_obraz(sciezka):
    img = cv2.imread(sciezka)
    #cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    #print(img.shape[0])
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# obraca obraz o dany kat
def obroc(obraz,kat):
    rows, cols = obraz.shape
    #print(kat)
    #kati = int(kat)
    #if kati in range(-5, 5):
    #    return obraz
    #print(obraz.shape):

    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), kat, 1)
    dst = cv2.warpAffine(obraz, M, (cols, rows), cv2.INTER_LINEAR, cv2.BORDER_CONSTANT, 1)
    return dst

# obcia obraz, tak aby zawieral pieciolinie
def przytnij(lines, img):
    x1min, x2max, y1min, y2max = piecio.pole_pieciolinii(lines)
    #print(x1min, x2max, y1min, y2max)
    dy = y2max - y1min
    dx = x2max - x1min
    #print(x1min, x2max, y1min, y2max)
   # lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
    img = img[max(0, y1min - (int)(dy*0.2)) : y2max + (int)(dy * 0.2), max(0, x1min  - (int)(dx*0.0)) : x2max + (int)(dx*0.0)]
   # img = img[y1min:y2max,x1min:x2max]
    return img

# rysuje poziome linie na obrazie o wskazanych wspolrzednych i kolorze
def rysuj_poziome(img, y_table, kolor):
    for y in y_table:
        img[y, :] = kolor
    return img

# sprawdza czy systepuje czasny kolor na danej poziomej linii
def czy_czarny_poziomo(img, y, x, delta_x):
    for i in range(delta_x):
        if img[y, x + i] == 0:
            return True
    return False

def czy_miesci(img, y, x):
    if img.shape[0] <= y:
        return False
    if img.shape[1] <= x:
        return False
    return True

def filtruj(img):
    #img = cv2.medianBlur(img, 5)
    #th3 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 5)
    kernel_size = 1
    #img = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    low_threshold = 50
    high_threshold = 200
    edges = cv2.Canny(img, low_threshold, high_threshold)

    count = 3
    dilated = edges
    for i in range(count):
        dilated = morphology.dilation(dilated, square(3))

    eroded = dilated
    for i in range(count):
        eroded = morphology.erosion(eroded, square(3))
    out = inwersja(eroded)
    #kernel_size *= 3
    #img = cv2.GaussianBlur(eroded, (kernel_size, kernel_size), 0)
    #img = progowanie(img, 15)
    #cv2.imshow('testy filtru', out)
    #cv2.imwrite("maska.jpg", out)
    #cv2.waitKey(0)
    return out