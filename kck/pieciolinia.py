import numpy as np
import cv2
import sys
import math


# wyszukuje wszystkie dlugie linie w obrazie img
def wyszukaj_pieciolinie(img, obetnij = False):
    #K = np.array([[ 1, 2, 1], [ 0, 0, 0],[ -1,-2,-1]])
    #K = K / 4
    theta = np.pi / 180
    min_szerokosc = int(img.shape[1] / 4)
    if obetnij == True:
        img = img[:, 0:int(img.shape[1] / 3)]#4
        theta = np.pi / 4 #4
        #cv2.imshow('obciete do pieciolinii', img)
        #cv2.waitKey(0)
        min_szerokosc = int(img.shape[1] / 3)
    #min_szerokosc = int(img.shape[1] / 4)
    #figure(figsize=(8,8))
    #io.imshow(res)
    ############## SZUKANIE LINII
    kernel_size = 1
    blur_gray = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    #blur_gray = abs(convolve(blur_gray, K))
    low_threshold = 50
    high_threshold = 200
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
    rho = 1  # distance resolution in pixels of the Hough grid
    #theta = np.pi / 180# angular resolution in radians of the Hough grid
    threshold = int(min_szerokosc / 4 ) #4 # minimum number of votes (intersections in Hough grid cell)
    min_line_length = min_szerokosc  # minimum number of pixels making up a line
    max_line_gap = min_szerokosc / 2  # maximum gap in pixels between connectable line segments
    line_image = np.copy(img) * 0  # creating a blank to draw lines on
    #print("shape0: {}".format(img.shape[0]))
    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                            min_line_length, max_line_gap)
    #lines2 = np.array([[[0, 0, 0, 0],],], int)
    lines2 = []
    for line in lines:
        #print(np.append(lines2, [line,]))
        for x1, y1, x2, y2 in line:
            if obetnij == True:
                if abs(y1 - y2) <= (img.shape[0] * 0.2) and y1 < 190 and y2 < 190:
                    #(y1 + 20 ) < img.shape[0] and (y2 + 20 ) < img.shape[0]:
                    lines2.append(line)
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 5)
            else:
                lines2.append(line)
                cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 5)

    lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
    #print("lines2: {} \nlines: {} type: {}".format(lines2, lines, type(lines)))
    #cv2.imshow('wyszukaj', edges)
    #cv2.imwrite("linia.jpg", lines_edges)
    #cv2.imshow('wyszukaj2', lines_edges)

    #cv2.waitKey(0)

    return lines


# zwraca kat obrotu w stopniach na podstawie zakrzywienia linii (linie powinny byc rownolegle)
def kat_obrotu(lines):
    srednia1=[]
    for line in lines:
        for x1, y1, x2, y2 in line:
            #if (x1 > x2):
               # bufx=x2
               # bufy=y2
                #x2 =x1
                #y2=y1
                #x1=bufx
                #y1=bufy
            if(x1!=x2):
                 srednia1.append(math.atan(-(y1 - y2) / (x1-x2))*180/np.pi)
            #print("{} {} {} {}".format(x1, y1, x2, y2))
            #cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 5)
    srednia= np.mean(srednia1)
    return -srednia

# zwraca wspolzedne poczatku i konca pola zawierajacego pieciolinie
def pole_pieciolinii(lines):
    x1min = min(min(lines[:, :, 0]), min(lines[:, :, 2]))
    x1min = x1min[0]
    x2max = max(max(lines[:, :, 0]), max(lines[:, :, 2]))
    x2max = x2max[0]


    y1min = min(min(lines[:, :, 1]), min(lines[:, :, 3]))
    y1min = y1min[0]
    y2max = max(max(lines[:, :, 1]), max(lines[:, :, 3]))
    y2max = y2max[0]
    #print(x1min, y2max)
    return x1min, x2max, y1min, y2max

def polozenie_poczatkowe(lines):
    x1min, x2max, y1min, y2max = pole_pieciolinii(lines)
    delta_x = x1min + x2max * 0.2
    return y1min, y2max
# zwraca wspolrzedne x 5 linii w pieciolinii na podstawie linii
def wspolrzedne_pieciolinii(lines):
    x1, x2, y1, y5 = pole_pieciolinii(lines)
    y3 = (y1 + y5) / 2
    y2 = (y1 + y3) / 2
    y4 = (y3 + y5) / 2
    return int(y1), int(y2), int(y3), int(y4), int(y5)

# srednia roznica pomiedzy 5 liniami w px
def srednia_delta_linii(yn):
    return int((yn[4] - yn[0]) / 4)

# ustala rzeczywiste linie pieciolinii na podstawie wyznaczonych wspolrzednych i pikseli w obrazie
def znajdz_rzeczywista_pieciolinie(img, wspolrzedne, x):
    out_y = [0, 0, 0, 0, 0]
    delta_y_skan = int(srednia_delta_linii(wspolrzedne) / 4)
    min_y = 0
    max_y  = 0
    size_y = img.shape[0] - 1
    for i, y_center in enumerate(wspolrzedne):
        out_y[i] = wspolrzedne[i]
        if img[y_center, x] == 0:
            continue
        for j in range(delta_y_skan):

            if img[min(y_center + j, size_y), x] == 0:
                min_y = y_center + j
                max_y = min_y

                for k in range(int(delta_y_skan / 2)):
                    if img[min(min_y + k, size_y), x] == 255:
                        max_y = min_y + k
                        break
                out_y[i] = int((min_y + max_y) / 2)
                break
            if img[min(y_center - j, size_y), x] == 0:
                max_y = y_center - j
                min_y = max_y

                for k in range(int(delta_y_skan / 2)):
                    if img[min(max_y - k, size_y), x] == 255:
                        min_y = max_y - k
                        break
                out_y[i] = int((min_y + max_y) / 2)
                break

            img[min(y_center - j,size_y), x] = 128
            img[min(y_center + j,size_y), x] = 128
    #cv2.imshow('po progowaniu', img)
    #cv2.waitKey(0)
    return out_y

# po wykrytych liniach pionowych identyfikuje dzwiek
def nazwa_dzwieku(wykryte_linie):
    wysokosc = ['na 1', 'pomiedzy 1 i 2', 'na 2', 'pomiedzy 2 i 3', 'na 3', 'pomiedzy 3 i 4', ' na 4', 'pomiedzy 4 i 5', 'na 5']
    ostatni = len(wykryte_linie) - 1
    for i in range(len(wykryte_linie)):
        if wykryte_linie[ostatni - i] == 1:
            return wysokosc[ostatni - i - 1]
    return ''

# generuje tablice obrazow z piecioliniami na podstawie obrazu zrodlowego
def wydziel_pieciolinie(img, maska):
    x_center = int(img.shape[1] / 2)
    x_min = 100
    delta = []
    delta_x_pos = []
    #wyszukiwanie ilosci czarnych pikseli dla pionowych linii
    for i, x in enumerate(range(x_center - x_min, x_center + x_min, 20)):
        delta.append(0)
        delta_x_pos.append(x)
        for y in range(img.shape[0]):
            if img[y, x] == 0:
                delta[i] += 1

    #print(delta, delta_x_pos)

    min_delta = min(delta)
    for i in range(len(delta)):
        if delta[i] == min_delta:
            min_delta_x_pos = delta_x_pos[i]
            break;
   # print(min_delta_x_pos)

    yn = []
    # budowanielisty linii
    for y in range(img.shape[0] - 1):
        if img[y, min_delta_x_pos] > 150 and img[y + 1, min_delta_x_pos] < 100:
            yn.append(y)
            #img[y-2:y+2, min_delta_x_pos-2:min_delta_x_pos+2] = 128

    #print(yn)
    y_pieciolinii = []
    img_out = []
    maska_out = []
    for i in range(int(len(yn) / 5)):
        y_pieciolinii.append(yn[i*5:(i*5) + 5])
        img_out.append(img[max(int(y_pieciolinii[i][0]- 50), 0):int(y_pieciolinii[i][4]+50), :])
        maska_out.append(maska[max(int(y_pieciolinii[i][0] - 50), 0):int(y_pieciolinii[i][4] + 50), :])
        #cv2.imshow('image', img_out[i])
        #cv2.waitKey(0)
    #cv2.imshow('image', img)
    #cv2.waitKey(0)
    return img_out, maska_out