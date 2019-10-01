from koneksi import ConDB
import math
import random
import matplotlib.pyplot as plt
import datetime
import copy
class SimAnneal(object):
    def __init__(self, tour= -1, T = -1, alpha = -1, stopping_T = -1, timematrix=-1, tmhotelfrom=-1, tmhotelto=-1, hotel=-1, drating=-1, dtarif=-1, dtime=-1):
        self.db = ConDB()
        self.tour = self.db.getWisata() if tour == -1 else tour
#        self.hotel = hotel
        self.hotels = self.db.HotelbyID(32)

        self.T = 10000 if T == -1 else T
        self.alpha = 0.99 if alpha == -1 else alpha
        self.stopping_temperature = 0.00000001 if stopping_T == -1 else stopping_T

        self.dtime = 1 if dtime == -1 else dtime
        self.drating = 1 if drating == -1 else drating
        self.dtarif = 1 if dtarif == -1 else dtarif

        self.timematrix = self.db.getTimeMatrix() if timematrix == -1 else timematrix
        self.tmhotelfrom = self.db.TMHfrom() if tmhotelfrom == -1 else tmhotelfrom
        self.tmhotelto = self.db.TMHto() if tmhotelto == -1 else tmhotelto

        self.cur_solution,startnode = self.initialSolution()
        self.best_solution = list(self.cur_solution)

        self.hotel = self.hotels[0] if hotel == -1 else hotel
        self.hotel.dttime = datetime.time(8,0,0)
        self.endNode = copy.copy(self.hotel)

        self.cur_tsp,self.tour = self.hitungWaktu(self.cur_solution)
        if self.cur_tsp:
            self.currentFitness = self.utility(self.cur_tsp)
            self.cur_fitness = self.utility(self.cur_solution)
            self.best_fitness = self.currentFitness
            self.best_tsp = list(self.cur_tsp)
            self.best_tour = list(self.tour)

#    get waktu dari db timematrix
    def tmatrix(self,wisata1,wisata2):
        if wisata1.jenisWisata == 'Hotel':
            for tm in self.tmhotelfrom:
                if(tm.titik_a == wisata1._id and tm.titik_b == wisata2._id):
                    time = tm.waktu
                    break
        elif wisata2.jenisWisata == 'Hotel':
            for tm in self.tmhotelto:
                if(tm.titik_a == wisata2._id and tm.titik_b == wisata1._id):
                    time = tm.waktu
                    break
        else:
            for tm in self.timematrix:
                if(tm.titik_a == wisata1._id and tm.titik_b == wisata2._id):
                    time = tm.waktu
                    break

        return time

    def getNodeMatrix(self,wisata,waktu,tour):
        for tm in self.timematrix:
            if(wisata._id == tm.titik_a and waktu == tm.waktu):
                node = self.getNodebyId(tm.titik_b)
                if node in tour:
                    wisata = node
                    break
        return wisata

    def getNodebyId(self,idnode):
        wisata = None
        for node in self.tour:
            if(node._id == idnode and node.jenisWisata != 'Hotel'):
                wisata = node
                break
        return wisata

#   random tour untuk solusi awal
    def initialSolution(self):
        solution = list(self.tour)
        random.shuffle(solution)
        start = solution[0]
        return solution,start
#   fungsi normalisasi
    def normalisasi(self,x,ub,lb):
       normalisasi = (x-lb)/(ub-lb)
       return normalisasi

#   Menghitung waktu berdasarkan durasi
    def fitness(self, sol):
        ''' Objective value of a solution '''
        ubf = 596
        lbf = 5814
        ubt = 597
        lbt = 6093
        ub = 77
        lb = 9432
        x = sum( [ self.normalisasi(self.tmatrix(sol[i-1],sol[i]),ub,lb) for i in range(1,len(sol)) ] )
        y = len(sol)-1
        try:
            z = x / y
        except ZeroDivisionError:
            z = 0
        return ((self.normalisasi(self.tmatrix(self.hotel,sol[0]),ubf,lbf)+z+self.normalisasi(self.tmatrix(sol[len(sol)-1],self.hotel),ubt,lbt)))/3

#   Fitness berdasarkan rating
    def fitnessRating(self, sol):
        ub = 4.7
        lb = 0
        return self.normalisasi(sum([sol[i-1].rating for i in range(1,len(sol))])/len(sol),ub,lb)

#   Fitness berdasarkan tarif
    def fitnessTarif(self, sol):
        lb = 50000
        ub = 0
        return self.normalisasi(sum([sol[i-1].tarif for i in range(1,len(sol))])/len(sol),ub,lb)

#   Fitness dengan DOI
    def utility(self,sol):
        return ((self.dtime*self.fitness(sol)) + (self.drating*self.fitnessRating(sol)) + (self.dtarif*self.fitnessTarif(sol)))/3

#   cek konstrain jam buka dan tutup
    def checkjam(self,node):
        accept = False
        if node.buka == node.tutup:
            accept = True
        elif node.timedatang > node.buka and node.dttime < node.tutup:
            accept = True
        return accept

#   Menghitung rentang waktu tiap destinasi wisata
    def jammenit(self,node1,node2):
        datang = self.tmatrix(node1,node2)
        jamd = (node1.dttime.hour) + int(datang // 3600)
        menitd = (node1.dttime.minute) + int((datang // 60) % 60 )
        detikd = (node1.dttime.second) + int(datang % 60)
        if detikd > 59:
            menitd += int(detikd / 60)
            detikd = int(detikd % 60)
        if menitd > 59:
            jamd += int(menitd / 60)
            menitd = int(menitd % 60)
        waktu = datang + node2.time
        jam = (node1.dttime.hour) + int(waktu // 3600)
        menit = (node1.dttime.minute) + int((waktu // 60) % 60 )
        detik = (node1.dttime.second) + int(waktu % 60)
        if detik > 59:
            menit += int(detik / 60)
            detik = int(detik % 60)
        if menit > 59:
            jam += int(menit / 60)
            menit = int(menit % 60)
        jdatang = [jamd,menitd,detikd]
        jselesai = [jam,menit,detik]
        return jdatang,jselesai

#   Menghitung waktu perjalanan dalam 1 hari
    def hitungWaktu(self,tour):
        sol = list(tour)
        tsp = []
        cur_node = self.hotel
        for i in range(0,len(sol)):
            jamd,jams = self.jammenit(cur_node,sol[i])
            if jams[0] < 20 :
                node = copy.copy(sol[i])
                node.timedatang = datetime.time(jamd[0],jamd[1],jamd[2])
                node.dttime = datetime.time(jams[0],jams[1],jams[2])
                accept = self.checkjam(node)
                if accept == True:
                    cur_node = node
                    tsp.append(cur_node)
            else :
                break
        return tsp,sol

#   Menghitung Acceptance Probability
    def P_accept(self, candidate_fitness):
        accepted = math.exp( -abs(candidate_fitness-self.currentFitness) / self.T  )
        return accepted

#   Menentukan solusi terbaik dari kandidat yang ada
    def accept(self, candidate):
        candidate_tsp,candidate_tour = self.hitungWaktu(candidate)
        candidate_fitness = self.utility(candidate_tsp)
        if candidate_fitness > self.currentFitness:
            self.currentFitness = candidate_fitness
            self.cur_solution = candidate
            self.cur_tsp = list(candidate_tsp)
            self.tour = candidate_tour

        else:
            if random.random() < self.P_accept(candidate_fitness):
                self.currentFitness = candidate_fitness
                self.cur_solution = candidate
                self.cur_tsp = list(candidate_tsp)
                self.tour = candidate_tour


    def Anneal(self):
        '''
        Execute simulated annealing algorithm
        '''
        if self.cur_tsp:
            while self.T >= self.stopping_temperature:
                m = 0
                while (m<10):
                    candidate = list(self.cur_solution)
                    l = random.randint(0, len(candidate)-1)
                    i = random.randint(0, len(candidate)-1)
                    if l < i:
                       l,i = i,l
                    candidate[i:(i+l)] = reversed(candidate[i:(i+l)])
                    self.accept(candidate) # fungsi accepted probabilitas
                    self.T *= self.alpha
                    m += 1
            # print(self.tour)
            return self.tour,self.cur_tsp,self.currentFitness

#   Fungsi TSP untuk mereturn hasil tsp dalam 1 hari dan sisa tour untuk TSP hari selanjutnya
    def tsp(self):
        tsp = []
        rest = []
        if self.cur_tsp:
            tour,tsp,fitness = self.Anneal()
            nama_tsp = [x.name for x in tsp ]
            rest = [x for x in tour if x.name not in nama_tsp]
            waktu = self.tmatrix(tsp[len(tsp)-1],self.endNode)
            jam = (tsp[len(tsp)-1].dttime.hour) + int(waktu // 3600)
            menit = (tsp[len(tsp)-1].dttime.minute) + int((waktu // 60) % 60 )
            detik = (tsp[len(tsp)-1].dttime.second) + int(waktu % 60)
            if detik > 59:
                menit += int(detik / 60)
                detik = int(detik % 60)
            if menit > 59:
                jam += int(menit / 60)
                menit = int(menit % 60)
            if jam > 23:
                jam -= 24
            self.endNode.dttime = datetime.time(jam,menit,detik)
        return tsp,rest,fitness
