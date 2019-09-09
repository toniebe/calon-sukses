from cat import CatAlgorithm
from koneksi import ConDB
from tourmanager import TourManager
import matplotlib.pyplot as plt
import random
import math
import copy
import time

def main(tourid,idhotel,dwaktu,drating,dtarif):

    bestFitness = 0
    nodeLen = 0
    for iteration in range(0,10):
        start_time = time.time()
        db = ConDB()
        tspperday = []
        tps_allDay = []
        waktuDatang = []
        for i in range(3):
            tspperday.append([])
            tps_allDay.append([])
            waktuDatang.append([])
        hotel = db.HotelbyID(idhotel)
        tur = db.WisatabyID(tourid)
        timematrix = db.TimeMatrixbyID(tourid)
        tmhotelfrom = db.TMHfrombyID(idhotel,tourid)
        tmhotelto = db.TMHtobyID(idhotel,tourid)
        i = 0
        avgFitness = 0
        while i < 3 and tur:
            cso = CatAlgorithm(tour=tur, T=100, stopping_T=0, timematrix=timematrix, tmhotelfrom=tmhotelfrom,
                               tmhotelto=tmhotelto, hotel=hotel, drating=drating, dtarif=dtarif, dtime=dwaktu)
            tsp,rest= cso.tsp()
            tur = rest
            for node in tsp:
                tspperday[i].append(node._id)
                tps_allDay[i].append(node)
                waktuDatang[i].append(str(node.timedatang))
            waktuDatang[i].insert(0,str(hotel.dttime))
            waktuDatang[i].append(str(cso.endNode.dttime))
            hotel = copy.copy(cso.hotel)
            # print("fitness akhir: ",fitness)
            i += 1
        #     avgFitness += fitness
        # if bestFitness < avgFitness:
        #     bestFitness = avgFitness
        #     bestTime = "%s seconds" % (time.time() - start_time)                # Testing Line
        #     nodeLen = len(tspperday[0])+len(tspperday[1])+len(tspperday[2])             # Testing line
        #     bestRute = tps_allDay

    # print("===========================")
    # print("Fitness total : ", avgFitness/3)                                           # Testing Line
    # print("Time    : ", bestTime)                                               # Testing Line
    # print("inp Len : ", len(tourid))
    # print("out Len : ", nodeLen)                                                # Testing Line
    # print("rute H1 : ", bestRute[0])
    # print("rute H2 : ", bestRute[1])
    # print("rute H3 : ", bestRute[2])
    # print("--- %s seconds ---" % (time.time() - start_time))
    return tspperday,waktuDatang


if __name__ == '__main__':
    # node = [2,3,5,6,7,14,15,16,17,18,19,20,21,22,23,25,26,27,28]
    # nodeUsed = [1]                                                              # Testing line
    # for i in range(0,len(node)):                                                       # Testing line
    #     nodeUsed.append(node[i])                                                # Testing line
    #     tsp,waktudatang, fitness = main(nodeUsed,33,1,0,0)
    tsp, waktudatang = main([1, 2, 3, 5, 6, 7, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28], 33, 1, 0, 0)
    print(tsp)
    print(waktudatang)
    # print(fitness)
