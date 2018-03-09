import numpy as np
import cv2
import sys
import math
import skimage
from skimage.filters.edges import convolve
import obraz as ob
import pieciolinia as piecio

def skaner(img, x_pocz, yn):
    #print(img.shape)
    zera = np.zeros((10,), dtype=np.int)
    wsp_linii = np.zeros((10,), dtype=np.int)
    wykryte_linie = np.zeros((10,), dtype=np.int)
    wys_pola = piecio.srednia_delta_linii(yn)
    delta_linii = int(piecio.srednia_delta_linii(yn) / 4)
    rozmiar_nuty = int(wys_pola * 1.3)
    wykryte_linie_srodek = np.zeros((10,), dtype=np.int)
    #print(rozmiar_nuty, delta_linii)
    delta = 0
    #pix_zmiana = 40
    od_zmiany = 0
    reset = 0
    poczatek = 1
    jest_czarny_pz = False
    jest_czarny_akt = False
    pierwsza_zmiana = 0
    size_y = img.shape[0] - 1
    font = cv2.FONT_HERSHEY_SIMPLEX
    for x in range(x_pocz, img.shape[1] - 1, 1):
        od_zmiany += 1
        #i
        # identyfikacja koloru i faktu zmiany dla pierwszej zmiany koloru na zmiane powolna
        if od_zmiany >= int(rozmiar_nuty / 2) and pierwsza_zmiana == 1:
            pierwsza_zmiana = 2
            wykryte_linie_srodek = wykryte_linie
            #print(pierwsza_zmiana)
            for y in range(len(wsp_linii)):
                if img[min(wsp_linii[y], size_y), x] == 0:
                    jest_czarny_pz = True
                    #print("kol")
                    break
        yn = piecio.znajdz_rzeczywista_pieciolinie(img, yn, x)
        #print(yn)
        #print(wsp_linii)
        # wyznaczanie wspolrzednych linii skanujacych na podstawie wspolrzednych pieciolinii
        for i in range(len(yn)):
            wsp_linii[i * 2] = min(yn[i] - delta_linii, size_y)
            wsp_linii[(i * 2) + 1] = min(yn[i] + delta_linii, size_y)

        jest_czarny_akt = False
        #wykrywanie zmiany koloru
        for i in range(len(wsp_linii)):

            if img[min(wsp_linii[i], size_y), x] != img[min(wsp_linii[i], size_y), x + 1]:
                ##for j in range(int(delta_linii * 3)):
                  #  if (i % 2) == 0 and ob.czy_miesci(img, wsp_linii[i]+j, x+1) and img[wsp_linii[i]+j, x+1] == 0:
                if img[wsp_linii[i], x + 1] == 0:
                    jest_czarny_akt = True
                   #     break
                if pierwsza_zmiana == 0:
                    pierwsza_zmiana = 1
                    #print(pierwsza_zmiana)

                wykryte_linie[i] = 1
                od_zmiany = 0
                delta += 1
        pozycja = piecio.nazwa_dzwieku(wykryte_linie_srodek)
        if poczatek == 0:
            if od_zmiany >= int(rozmiar_nuty / 6) and sum(wykryte_linie) == 2 and delta >= 6 and delta <= 10  and not jest_czarny_pz and not jest_czarny_akt and pierwsza_zmiana == 2:
                print("cala nuta {} delta {}".format(pozycja, delta))
                cv2.putText(img, 'cala nuta {}'.format(pozycja), (x, 10), font, 0.3, (0, 0, 0), 1, cv2.LINE_AA)
                img[:, x-1] = 128
                reset = 1
            elif od_zmiany >= int(rozmiar_nuty / 6) and sum(wykryte_linie) == 2 and delta <= 6 and delta >= 4 and jest_czarny_pz and not jest_czarny_akt and pierwsza_zmiana == 2:
                print("polnuta {} delta {}".format(piecio.nazwa_dzwieku(wykryte_linie_srodek), delta))
                cv2.putText(img, 'polnuta {}'.format(pozycja), (x, 10), font, 0.3, (0, 0, 0), 1, cv2.LINE_AA)
                img[:, x - 1] = 128
                reset = 1
            elif od_zmiany >= int(rozmiar_nuty / 2) and sum(wykryte_linie) >= 4 and delta <= 10 and delta >= 8 and jest_czarny_pz and not jest_czarny_akt and pierwsza_zmiana == 2:
                print("cwiercnuta {} delta {}".format(piecio.nazwa_dzwieku(wykryte_linie_srodek), delta))
                cv2.putText(img, 'cwiercnuta {}'.format(pozycja), (x, 10), font, 0.3, (0, 0, 0), 1, cv2.LINE_AA)
                img[:, x-1] = 128
                reset = 1
            elif od_zmiany >= int(rozmiar_nuty / 2) and sum(wykryte_linie) >= 4 and delta >= 11 and delta <= 20 and jest_czarny_pz and not jest_czarny_akt and pierwsza_zmiana == 2:
                print("osemka {} delta {}".format(piecio.nazwa_dzwieku(wykryte_linie_srodek), delta))
                cv2.putText(img, 'osemka {}'.format(pozycja), (x, 10), font, 0.3, (0, 0, 0), 1, cv2.LINE_AA)
                img[:, x-1] = 128
                reset = 1
            elif od_zmiany >= int(rozmiar_nuty / 3) and sum(wykryte_linie) == 4 and delta >= 11 and delta <= 20 and not jest_czarny_akt:
                print("krzyzyk delta {}".format(delta))
                cv2.putText(img, 'krzyzyk {}'.format(pozycja), (x, 10), font, 0.3, (0, 0, 0), 1, cv2.LINE_AA)
                img[:, x-1] = 128
                reset = 1
            elif (od_zmiany >= int(rozmiar_nuty * 1.5) and delta > 0) or (od_zmiany >= int(rozmiar_nuty / 6) and delta > 60):
                print("reset awaryjny delta {}".format(delta))
                cv2.putText(img, 'reset {}'.format(pozycja), (x, 10), font, 0.3, (0, 0, 0), 1, cv2.LINE_AA)
                img[:, x-1] = 0
                reset = 1
        else:
            if od_zmiany >= int(rozmiar_nuty / 4) and sum(wykryte_linie) >= 6 and sum(wykryte_linie) <= 9 and delta >= 24 and delta <= 30 :
                print("klucz basowy delta {}".format(delta))
                cv2.putText(img, 'klucz basowy {}'.format(pozycja), (x, 10), font, 0.3, (0, 0, 0), 1, cv2.LINE_AA)
                img[:, x-1] = 128
                reset = 1
            elif od_zmiany >= int(rozmiar_nuty / 4) and sum(wykryte_linie) == 10 and delta >= 42:
                print("klucz wiolinowy delta {}".format(delta))
                cv2.putText(img, 'klucz wiolinowy {}'.format(pozycja), (x, 10), font, 0.3, (0, 0, 0), 1, cv2.LINE_AA)
                img[:, x-1] = 128
                reset = 1
        #print(wsp_linii)
        if reset > 0:
            pierwsza_zmiana = 0
            reset = 0
            jest_czarny_pz = False
            jest_czarny_akt =False
            print(wykryte_linie)
            wykryte_linie = np.zeros((10,), dtype=np.int)
            wykryte_linie_srodek = np.zeros((10,), dtype=np.int)

            delta = 0
            od_zmiany = 0
            poczatek = 0


            ### koniec glownego kodu funkcji wykrywajacej

        for y in wsp_linii:
            img[min(y, size_y), x-1] = 128
    #print(delta, wykryte_linie, sum(wykryte_linie))
    return img

# funkcja glowna
if __name__ == '__main__':
    nazwa = 'test9.jpg'
    obraz = ob.laduj_szary_obraz('./wzorce/'+nazwa)
    print('nazwa:   {3}\nrozmiar: {0}\nsrednia: {1}\nmediana: {2}'.format(obraz.shape, np.mean(obraz), np.median(obraz), nazwa))
    srednia = int(np.mean(obraz))

    obraz = ob.skaluj_szerokosc(obraz, 2000)
    obraz = cv2.medianBlur(obraz, 3)
    #dst = cv2.fastNlMeansDenoisingMulti(obraz, 2, 5, None, 4, 7, 35)

    #cv2.imshow('po medianie', obraz)
    #cv2.waitKey(0)
    maska = ob.filtruj(obraz)
    #cv2.imshow('zaladowany obraz', obraz)
    #cv2.imshow('zaladowana maska', maska)
    #cv2.waitKey(0)

    pieciolinia=piecio.wyszukaj_pieciolinie(maska)

    kat=piecio.kat_obrotu(pieciolinia)
    obrocone=ob.obroc(obraz,kat)
    obrocona_maska = ob.obroc(maska, kat)
    #obrocone = rozmarz_proguj(obrocone, 5, 150)
    #edycja, kod testowy
    #cv2.imshow('obrocone zdjecie', obrocone)
    #cv2.imshow('obrocona maska', obrocona_maska)
    #cv2.waitKey(0)

    pieciolinia = piecio.wyszukaj_pieciolinie(obrocona_maska)

    final = ob.przytnij(pieciolinia, obrocone)
    final_maska = ob.przytnij(pieciolinia, obrocona_maska)
    #cv2.imshow('przyciete', final)
    #cv2.imshow('przyciete maska', final_maska)
    #cv2.waitKey(0)
    #final = skaluj_szerokosc(final, 1000)
    """
            PROGOWANIE
    """
    final = ob.progowanie(final, srednia - 30)
    final = ob.rozmaz_proguj(final, 5, srednia + 10)

    test = ob.skaluj_szerokosc(final, 1000)
    #cv2.imshow('po progowaniu', test)
    #cv2.waitKey(0)

    img_table, mask_table = piecio.wydziel_pieciolinie(final, final_maska)
    #cv2.imshow('gg', img_table[0])
    #cv2.waitKey(0)
    #print(len(img_table))
    for i, img in enumerate(img_table):
        nazwa = 'img{}'.format(i)
        print(nazwa,img.shape)
        przyciete = ob.skaluj_wysokosc(img, 200)
        przyciete_maska = ob.skaluj_wysokosc(mask_table[i], 200)

        pieciolinia = piecio.wyszukaj_pieciolinie(przyciete_maska)
        przyciete = ob.przytnij(pieciolinia, przyciete)

        """
                PROGOWANIE
        """
        przyciete = ob.progowanie(przyciete, srednia + 10)
        #cv2.imshow('po progowaniu2', przyciete)
        #cv2.waitKey(0)

        #skanowanie
        pieciolinia = piecio.wyszukaj_pieciolinie(przyciete, True)
        yn = piecio.wspolrzedne_pieciolinii(pieciolinia)
        x_pocz = 8
        #print(yn)
        yn = piecio.znajdz_rzeczywista_pieciolinie(przyciete, yn, x_pocz)
        final = skaner(przyciete, x_pocz, yn)


        cv2.imshow(nazwa, final)
        cv2.waitKey(0)

