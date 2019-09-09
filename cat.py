from koneksi import ConDB
import math
import random
import matplotlib.pyplot as plt
import datetime
import copy
import sys

class Cat :
    def __init__(self, rute, position, velocity, flag, fitness):
        self._rute = rute
        self._position = position
        self._velocity = velocity
        self._flag = flag
        self._fitness = fitness

    def set_rute(self, rute):
        self._rute = rute

    def get_rute(self):
        return self._rute

    def set_position(self, position):
        self._position = position

    def get_position(self):
        return self._position

    def set_velocity(self, velocity):
        self._velocity = velocity

    def get_velocity(self):
        return self._velocity

    def set_flag(self, flag):
        self._flag = flag

    def get_flag(self):
        return self._flag

    def set_fitness(self, fitness):
        self._fitness = fitness

    def get_fitness(self):
        return self._fitness

    def get_output(self) :
        print ("\n")
        print ("Rute : ", self._rute)
        print ("Position : ",self._position)
        print ("Velocity : ", self._velocity)
        print ("Flag : ", self._flag)
        print ("Fitness : ", self._fitness)

class Kittun :
    def __init__(self, nama, position, velocity, flag, rute, fitness):
        self._nama = nama
        self._position = position
        self._velocity = velocity
        self._flag = flag
        self._rute = rute
        self._fitness = fitness

    def set_nama(self, nama):
        self._nama = nama

    def get_nama(self):
        return self._nama

    def set_position(self, position):
        self._position = position

    def get_position(self):
        return self._position

    def set_velocity(self, velocity):
        self._velocity = velocity

    def get_velocity(self):
        return self._velocity

    def set_flag(self, flag):
        self._flag = flag

    def get_flag(self):
        return self._flag

    def set_rute(self, rute):
        self._rute = rute

    def get_rute(self):
        return self._rute

    def set_fitness(self, fitness):
        self._fitness = fitness

    def get_fitness(self):
        return self._fitness

    def get_output(self) :
        print ("\n")
        print ("Nama : ", self._nama)
        print ("Position : ",self._position)
        print ("Velocity : ", self._velocity)
        print ("Flag : ", self._flag)
        print ("Rute: ", self._rute)
        print ("Fitness : ", self._fitness)

class CatAlgorithm(object):
    def __init__(self, tour= -1, T= -1, stopping_T= -1, timematrix=-1, tmhotelfrom=-1, tmhotelto=-1, hotel=-1, drating=-1, dtarif=-1, dtime=-1):

        self.db = ConDB()
        self.tour = self.db.getWisata() if tour == -1 else tour
        self.hotel = self.db.HotelbyID(32) if hotel == -1 else hotel

        # Variabel inisialisasi awal
        self.T = 10 if T == -1 else T
        self.stopping  = 0 if stopping_T == -1 else stopping_T
        # self.T = 10000 if T == -1 else T
        # self.alpha = 0.99 if alpha == -1 else alpha
        # self.stopping_temperature = 0.00000001 if stopping_T == -1 else stopping_T

        self.minposition = -20
        self.maxposition = 20
        self.minvelocity = -3
        self.maxvelocity = 3
        self.minfit = 0.9

        self.minimalvelocity = 0
        self.maksimalvelocity = 10
        self.minimalposisi = 0
        self.maksimalposisi = ""
        self.minimalfitness = 0.9
        self.maksimalfitness = ""
        self.jumlahkucing = ""

        self.SMP = 0
        self.w = 0.729

        self.jumkucing = 10
        self.MR = 0.3
        self.c1 = 2

        self.CDC = 0

        self.currentbestposition = ""
        self.currentbestfitness = 0
        self.currentbestcat = ""

        self.bestfitness = 0
        self.bestcat = ""
        self.bestposition = 0
        self.currentsolution = ""
        self.yangbelom = ""

        self.literallyfitness = 0
        self.literallyrute = ""

        #Ga usah diubah
        self.dtime = 1 if dtime == -1 else dtime
        self.drating = 1 if drating == -1 else drating
        self.dtarif = 1 if dtarif == -1 else dtarif

        self.timematrix = self.db.getTimeMatrix() if timematrix == -1 else timematrix
        self.tmhotelfrom = self.db.TMHfrom() if tmhotelfrom == -1 else tmhotelfrom
        self.tmhotelto = self.db.TMHto() if tmhotelto == -1 else tmhotelto

        self.cur_solution= self.initialSolution()
        self.best_solution = list(self.cur_solution)

        self.hotel = self.hotels[0] if hotel == -1 else hotel
        self.hotel.dttime = datetime.time(8,0,0)
        self.endNode = copy.copy(self.hotel)

        self.cur_tsp,self.tour = self.hitungWaktu(self.cur_solution) #  Mencari fitness
        if self.cur_tsp:
            self.currentFitness = self.utility(self.cur_tsp)
            self.cur_fitness = self.utility(self.cur_solution)
            self.best_fitness = self.currentFitness
            self.best_tsp = list(self.cur_tsp)
            self.best_tour = list(self.tour)

#    get waktu dari db timematrix / Hitung jarak antara wisata 1 dan wisata 2
    def tmatrix(self, wisata1, wisata2):
        if wisata1.jenisWisata == 'Hotel':
            for tm in self.tmhotelfrom:
                if tm.titik_a == wisata1._id and tm.titik_b == wisata2._id :
                    time = tm.waktu
                    break
        elif wisata2.jenisWisata == 'Hotel':
            for tm in self.tmhotelto:
                if tm.titik_a == wisata2._id and tm.titik_b == wisata1._id :
                    time = tm.waktu
                    break
        else:
            for tm in self.timematrix:
                if tm.titik_a == wisata1._id and tm.titik_b == wisata2._id :
                    time = tm.waktu
                    break

        return time

    def getNodeMatrix(self, wisata, waktu, tour):
        for tm in self.timematrix:
            if wisata._id == tm.titik_a and waktu == tm.waktu:
                node = self.getNodebyId(tm.titik_b)
                if node in tour:
                    wisata = node
                    break
        return wisata

    def getNodebyId(self, idnode):
        wisata = None
        for node in self.tour:
            if node._id == idnode and node.jenisWisata != 'Hotel' :
                wisata = node
                break
        return wisata

#   random tour untuk solusi awal /
#   MELETAKKAN KUCING SECARA ACAK DALAM DIMENSI D
    def initialSolution(self):
        solution = list(self.tour)
        random.shuffle(solution)
        return solution

    # def initialSolution1(self):
    #     for i in range(len.tour) :
    #         solution = tour[i], tour[i+1]
    #         # solution = list(self.tour)
    #         random.shuffle(solution)
    #         return solution

#   fungsi normalisasi
    def normalisasi(self, x, ub,lb):
       normalisasi = (x - lb) / (ub - lb)
       return normalisasi

#   Menghitung waktu berdasarkan durasi
    def distanceTwoPlace(self, sol1, sol2):
        ''' Objective value of a solution '''
        ubf = 596
        lbf = 5814
        ubt = 597
        lbt = 6093
        ub = 77
        lb = 9432
        x = self.normalisasi(self.tmatrix(sol2, sol1), ub, lb)
        return x

    def fitness(self, sol):
        ''' Objective value of a solution '''
        ubf = 596
        lbf = 5814
        ubt = 597
        lbt = 6093
        ub = 77
        lb = 9432
        z = 0
        x = sum([self.normalisasi(self.tmatrix(sol[i - 1], sol[i]), ub, lb) for i in range(1, len(sol))])
        y = len(sol) - 1
        try:
            z = x / y
        except ZeroDivisionError:
            z = 0
        return ((self.normalisasi(self.tmatrix(self.hotel, sol[0]), ubf, lbf) + z + self.normalisasi(self.tmatrix(sol[len(sol) - 1], self.hotel), ubt, lbt))) / 3

    def carikecepatan(self, sol):
        lb = 0
        ub = 43200
        x = sum([self.tmatrix(sol[i - 1], sol[i]) for i in range(1, len(sol))])
        return (self.tmatrix(self.hotel, sol[0]) + x + self.tmatrix(sol[len(sol) - 1], self.hotel))

    #   Fitness berdasarkan rating
    def fitnessRating(self, sol):
        ub = 4.7
        lb = 0
        return self.normalisasi(sum([sol[i-1].rating for i in range(0,len(sol))])/len(sol), ub, lb)

#   Fitness berdasarkan tarif
    def fitnessTarif(self, sol):
        ub = 50000
        lb = 0
        return self.normalisasi(sum([sol[i-1].tarif for i in range(0, len(sol))])/len(sol), ub, lb)

#   Fitness dengan DOI / MAUT
    def utility(self, sol):
        return ((self.dtime*self.fitness(sol)) + (self.drating*self.fitnessRating(sol)) + (self.dtarif*self.fitnessTarif(sol)))/3

#   cek konstrain jam buka dan tutup
    def checkjam(self, node):
        accept = False
        if node.buka == node.tutup:
            accept = True
        elif node.timedatang > node.buka and node.dttime < node.tutup:
            accept = True
        return accept

#   Menghitung rentang waktu tiap destinasi wisata
    def jammenit(self, node1, node2):
        datang = self.tmatrix(node1, node2)
        jamd = node1.dttime.hour + int(datang // 3600)
        menitd = node1.dttime.minute + int((datang // 60) % 60 )
        detikd = node1.dttime.second + int(datang % 60)
        if detikd > 59:
            menitd += int(detikd / 60)
            detikd = int(detikd % 60)
        if menitd > 59:
            jamd += int(menitd / 60)
            menitd = int(menitd % 60)
        waktu = datang + node2.time
        jam = node1.dttime.hour + int(waktu // 3600)
        menit = node1.dttime.minute + int((waktu // 60) % 60 )
        detik = node1.dttime.second + int(waktu % 60)
        if detik > 59 :
            menit += int(detik / 60)
            detik = int(detik % 60)
        if menit > 59 :
            jam += int(menit / 60)
            menit = int(menit % 60)
        jdatang = [jamd, menitd, detikd]
        jselesai = [jam, menit, detik]
        return jdatang, jselesai

#   Menghitung waktu perjalanan dalam 1 hari
#   Mengurutkan tempat wisata berdasarkan jam buka
    def hitungWaktu(self, tour):
        sol = list(tour)
        tsp = []
        cur_node = self.hotel
        for i in range(0, len(sol)):
            jamd, jams = self.jammenit(cur_node, sol[i])
            if jams[0] < 20 :
                node = copy.copy(sol[i])
                node.timedatang = datetime.time(jamd[0], jamd[1], jamd[2])
                node.dttime = datetime.time(jams[0], jams[1], jams[2])
                accept = self.checkjam(node)
                if accept == True:
                    cur_node = node
                    tsp.append(cur_node)
            else :
                break
        return tsp, sol


# INI SA
#   Menghitung Acceptance Probability
#     def P_accept(self, candidate_fitness):
#         accepted = math.exp( -abs(candidate_fitness-self.currentFitness) / self.T  )
#         return accepted

#   Menentukan solusi terbaik dari kandidat yang ada
#     def accept(self, candidate):
#         candidate_tsp, candidate_tour = self.hitungWaktu(candidate)
#         candidate_fitness = self.utility(candidate_tsp)
#         if candidate_fitness > self.currentFitness:
#             self.currentFitness = candidate_fitness
#             self.cur_solution = candidate
#             self.cur_tsp = list(candidate_tsp)
#             self.tour = candidate_tour

        # else:
        #     if random.random() < self.P_accept(candidate_fitness):
        #         self.currentFitness = candidate_fitness
        #         self.cur_solution = candidate
        #         self.cur_tsp = list(candidate_tsp)
        #         self.tour = candidate_tour

    # def Anneal(self):
    #     '''
    #     Execute simulated annealing algorithm
    #     '''
    #     if self.cur_tsp:
    #         while self.T >= self.stopping_temperature: # Pengecekan kondisi berhenti
    #             m = 0
    #             while m < 10:
    #                 candidate = list(self.cur_solution)
    #                 l = random.randint(0, len(candidate)-1)
    #                 i = random.randint(0, len(candidate)-1)
    #                 if l < i:
    #                    l, i = i, l
    #                 candidate[i:(i+l)] = reversed(candidate[i:(i+l)])
    #
    #                 self.accept(candidate) # fungsi accepted probabilitas
    #                 self.T *= self.alpha
    #                 m += 1
    #         return self.tour, self.cur_tsp


# I N I  A L G O R I T M A  K U C I N G

    def tracking(self, kuc, bestposition):
        r1 = random.random()
        v = kuc.get_velocity()
        catposition = kuc.get_position()
        batasrute = len(kuc.get_rute()) - 1
        rutesaatini = kuc.get_rute()
        ruteacak = kuc.get_rute()
        fitnesssaatini = kuc.get_fitness()

        tukar = random.randint(0, batasrute)
        dengan = random.randint(0, batasrute)
        pindahke = rutesaatini[tukar]
        ruteacak[tukar] = rutesaatini[dengan]
        ruteacak[dengan] = pindahke
        rutenya, b = self.hitungWaktu(ruteacak)
        fitnessnya = self.utility(rutenya)
        if fitnessnya > fitnesssaatini :
            vbaru =  (r1 * self.c1) + (self.w * v) * (bestposition - catposition)

            if vbaru < self.minvelocity :
                kuc.set_velocity(self.minvelocity)
            elif vbaru > self.maxvelocity :
                kuc.set_velocity(self.maxvelocity)
            else :
                kuc.set_velocity(vbaru)

            pbaru = catposition + vbaru
            if pbaru < self.minposition :
                kuc.set_position(self.minposition)
            elif pbaru > self.maxposition :
                kuc.set_position(self.maxposition)
            else :
                kuc.set_position(pbaru)

            kuc.set_fitness(fitnessnya)
            kuc.set_rute(rutenya)

    def seeking(self, kuc):
        jcopy = []
        fitnesssaatini = kuc.get_fitness()
        rutesaatini = kuc.get_rute()
        ruteacak = kuc.get_rute()
        batasrute = len(kuc.get_rute()) - 1
        SPC = False

        # B A N G K I T K A N  J  C O P Y
        for j in range (0, self.SMP) :
            tukar = random.randint(0, batasrute)
            dengan = random.randint(0, batasrute)
            SRD = random.uniform(self.minposition, self.maxposition)
            pindahke = rutesaatini[tukar]
            ruteacak[tukar] = rutesaatini[dengan]
            ruteacak[dengan] = pindahke
            rutenya, b = self.hitungWaktu(ruteacak)
            fitnessnya = self.utility(rutenya)
            if fitnesssaatini != self.minfit :
                jcopy.append([rutenya, fitnessnya, SRD])

        hitung = 0
        for sij in range(0, len(jcopy)):
            if jcopy[sij][2] != fitnesssaatini:
                proba = abs(jcopy[sij][2] - self.minfit)
                bilitas = fitnesssaatini - self.minfit
                probabilitas = proba / bilitas
                if probabilitas > hitung :
                    hitung = probabilitas
                    SPC = True
                    self.SMP = self.SMP - 1
                elif probabilitas < 0 :
                    hitung = 0
                    SPC = False
            else:
                probabilitas = 0
                SPC = False

        # for j in range (0, self.SMP) :
        #     SRD = random.uniform(self.minposition, bestposition)
        #     candidate = copy.copy(kuc.get_rute())
        #     for k in range(0, self.CDC) :
        #         l = random.randint(0, len(candidate)-1)
        #         i = random.randint(0, len(candidate)-1)
        #         if l < i:
        #            l, i = i, l
        #         candidate[i:(i+l)] = reversed(candidate[i:(i+l)])
        #     self.cur_tsp, self.tour = self.hitungWaktu(candidate)  # Mencari fitness
        #     fit = self.utility(self.cur_tsp)
            if SPC == True :
                kecepatanbaru = jcopy[sij][2] - kuc.get_position()
                kuc.set_rute(jcopy[sij][0])
                kuc.set_fitness(jcopy[sij][1])
                kuc.set_position(jcopy[sij][2])
                kuc.set_velocity(kecepatanbaru)

    def cat(self) :
        if self.cur_tsp :
            # while self.T >= self.stopping :  # Pengecekan kondisi berhenti
            self.bestfitness = 0
            hitungMR = self.jumkucing - (math.floor(self.jumkucing * self.MR))
            listKucing = []
            self.currentbestfitness = 0
            acakbendera = []

            berhenti = False
            sama = False

            for ab in range(0, self.jumkucing) :
                acakbendera.append(ab)

            # I N I S I A L I S A S I
            for ia in range(0, self.jumkucing) :
                tempatwisata = self.initialSolution()
                self.cur_tsp, self.tour = self.hitungWaktu(tempatwisata) #  Mencari fitness

                f = self.utility(self.cur_tsp)
                position = random.uniform(self.minposition, self.maxposition)
                self.SMP = len(self.cur_tsp)

                if ia + 1 <= hitungMR:
                    flag = "Seeking"
                else :
                    flag = "Tracking"

                listKucing.append(Cat(self.cur_tsp, position, 0, flag, f))

            # I T E R A S I  M U L A I  D A R I  S I N I
            while berhenti == False or sama == False :

                print("berhenti : ", berhenti)
                print("sama : ", sama)
                self.minfit = 0.9

                # C A R I  M I N  F I T N E S S
                for cing in range(0, len(listKucing)):
                    if listKucing[cing].get_fitness() < self.minfit:
                        self.minfit = listKucing[cing].get_fitness()

                # C A R I  B E S T  F I T N E S S
                for cing in range(0, len(listKucing)) :
                    if listKucing[cing].get_fitness() > self.currentbestfitness :
                        self.currentbestfitness = listKucing[cing].get_fitness()
                        self.currentbestcat = listKucing[cing].get_rute()
                        self.currentbestposition = listKucing[cing].get_position()
                        b, c = self.hitungWaktu(self.tour)
                        self.currentsolution = list(c)

                print("fitness : ", self.currentbestfitness)
                print("position: ", self.currentbestposition)
                # print("kucing 0 : ", listKucing[0].get_output())
                # print("kucing 1 : ", listKucing[1].get_output())

                # M U L A I  P R O S E S  A L G O R I T M A
                for kuc in listKucing :
                    if kuc.get_flag() == "Tracking":
                        self.tracking(kuc, self.currentbestposition)

                    elif kuc.get_flag() == "Seeking":
                        self.seeking(kuc)

                # print("kucing 0 : ", listKucing[0].get_output())
                # print("kucing 1 : ", listKucing[1].get_output())

                random.shuffle(acakbendera)
                hitunglagi = 0
                for ac in range(1, len(listKucing)+1) :
                    if ac == acakbendera[ac - 1] and hitunglagi < hitungMR:
                        listKucing[ac - 1].set_flag("Tracking")
                        hitunglagi = hitunglagi + 1
                    else:
                        listKucing[ac - 1].set_flag("Seeking")

                hitungtrue = 0


                if self.currentbestfitness == self.bestfitness and self.currentbestposition == self.bestposition :
                    berhenti = True
                    for kocheng in listKucing :
                        if kocheng.get_position() == self.currentbestposition :
                            hitungtrue = hitungtrue + 1
                        else :
                            hitungtrue = hitungtrue + 0
                    if hitungtrue == self.jumkucing + 1 :
                            sama = True
                else :
                    # if self.currentbestfitness != self.bestfitness and self.currentbestposition != self.bestposition:
                    self.bestfitness = self.currentbestfitness
                    self.bestcat = self.currentbestcat
                    self.bestposition = self.currentbestposition
                    self.yangbelom = self.currentsolution
            sys.exit()
                # Pengecekan apakah best fitness pertama tetap yg tertinggi
                # dari best fitness setelah algoritma selesai
                # for kuch in range (0, len(listKucing)) :
                #     if listKucing[kuch].get_fitness() > self.bestfitness :
                #         self.cur_tsp, self.tour = self.hitungWaktu(self.cur_solution)
                #         self.bestfitness = listKucing[kuch].get_fitness()
                #         self.bestindex = kuch
                # self.T = self.T - 1

            # if self.currentbestfitness > self.bestfitness :
            #     self.bestfitness = self.currentbestfitness
            #     self.bestcat = self.currentbestcat
            #     self.yangbelom = self.currentsolution

            return self.yangbelom, self.bestcat.get_rute(), self.bestfitness

    def cobaseeking(self, kucingnih):
        jcopy = []
        SPC = False
        posisisaatini = (kucingnih.get_position() - 1)
        rutesaatini = kucingnih.get_rute()
        fitnesssaatini = kucingnih.get_fitness()
        minfit = 0.9

        j = 1
        while j < self.SMP :
            SRD = random.randint(self.minimalposisi, len(rutesaatini) - 1)
            if SRD != posisisaatini :
                pindahke = rutesaatini[posisisaatini]
                rutesaatini[posisisaatini] = rutesaatini[SRD]
                rutesaatini[SRD] = pindahke
                rutenya, b = self.hitungWaktu(rutesaatini)
                fitnessnya = self.utility(rutenya)
                if fitnessnya < minfit :
                    minfit = fitnessnya
                if fitnessnya != fitnesssaatini :
                    jcopy.append([SRD, rutenya, fitnessnya])
                j = j + 1

        for sij in range(0, len(jcopy)) :
            proba = jcopy[sij][2] - self.minfit
            bilitas = self.currentbestfitness - self.minfit
            probabilitas = round(proba / bilitas)
            if probabilitas == 1:
                if jcopy[sij][2] > fitnesssaatini:
                    posisisaatini = jcopy[sij][0] + 1
                    rutesaatini = jcopy[sij][1]
                    fitnesssaatini = jcopy[sij][2]

                else :
                    SPC = True
                    kucingnih.set_position(jcopy[sij][0] + 1)
                    kucingnih.set_rute(jcopy[sij][1])
                    kucingnih.set_fitness(jcopy[sij][2])

        if SPC == False :
            # print("False")
            kucingnih.set_position(posisisaatini + 1)
            kucingnih.set_rute(rutesaatini)
            kucingnih.set_fitness(fitnesssaatini)

    def cobatracking(self, kucingnih) :

        xk = kucingnih.get_position()
        rutesaatini = kucingnih.get_rute()
        vk = kucingnih.get_velocity()
        r1 = random.random()
        xbest = kucingnih.get_position()

        for x in range(0, len(rutesaatini)):
            if rutesaatini[x] == kucingnih.get_nama() :
                xbest = x + 1

        # for j in range(0, jumrute) :
        #     acakrute = rutesaatini
        #     pindahke = acakrute[j]
        #     acakrute[j] = acakrute[xk]
        #     acakrute[xk] = pindahke
        #     rutenya, b = self.hitungWaktu(acakrute)
        #     fitnessnya = self.utility(rutenya)
        #
        # for disimpan in simpan :
        #     if disimpan[2] > fitnesssaatini :
        #         xbest = disimpan[0]
        #         rutesaatini = disimpan[1]
        #         fitnesssaatini = disimpan[2]

        vbaru = self.w * vk + r1 * self.c1 * (xbest - xk)
        xbaru = xk + vbaru

        xnya = xk-1
        acakrute = rutesaatini

        if xbaru > len(kucingnih.get_rute()) :
            kucingnih.set_position(self.maksimalposisi)
            pindahinx = len(kucingnih.get_rute()) - 1
            pindahke = acakrute[pindahinx]
            acakrute[pindahinx] = acakrute[xnya]
            acakrute[xnya] = pindahke

        elif xbaru < len(kucingnih.get_rute()) :
            kucingnih.set_position(self.minimalposisi + 1)
            pindahinx = self.minimalposisi
            pindahke = acakrute[xnya]
            acakrute[xnya] = acakrute[pindahinx]
            acakrute[pindahinx] = pindahke

        else :
            kucingnih.set_position(xbaru)
            pindahinx = xbaru - 1
            pindahke = acakrute[xnya]
            acakrute[xnya] = rutesaatini[pindahinx]
            acakrute[pindahinx] = pindahke

        rut, b = self.hitungWaktu(acakrute)
        fitnessnya = self.utility(rut)
        kucingnih.set_rute(rutesaatini)
        kucingnih.set_fitness(fitnessnya)

        if vbaru > self.maksimalvelocity :
            kucingnih.set_velocity(self.maksimalvelocity)
        elif vbaru < self.minimalvelocity :
            kucingnih.set_velocity(self.minimalvelocity)
        else :
            kucingnih.set_velocity(vbaru)

    def seekingmode(self, kucingnih):
        jcopy = []
        self.SMP = len(kucingnih.get_rute()) + 1
        SPC = False
        posisisaatini = kucingnih.get_position()
        rutesaatini = kucingnih.get_rute()
        fitnesssaatini = kucingnih.get_fitness()
        kecepatansaatini = kucingnih.get_velocity()
        minfit = 0.9
        for j in range(1, self.SMP) :
            SRD = random.randint(self.minimalposisi, self.maksimalposisi - 1)
            if SRD != posisisaatini :
                pindahke = rutesaatini[SRD]
                rutesaatini[SRD] = rutesaatini[posisisaatini]
                rutesaatini[posisisaatini] = pindahke
                rutenya, b = self.hitungWaktu(rutesaatini)
                fitnessnya = self.utility(rutenya)
                if fitnessnya < minfit :
                    minfit = fitnessnya
                if fitnessnya != fitnesssaatini :
                    jcopy.append([SRD, rutenya, fitnessnya])
        jumSPC = 0
        for sij in range(0, len(jcopy)) :
            if jcopy[sij][2] != minfit :
                proba = jcopy[sij][2] - self.minfit
                bilitas = self.currentbestfitness - self.minfit
                probabilitas = proba / bilitas
                SPC = True

                self.SMP = self.SMP - 1

            else :
                probabilitas = 0
                SPC = False

            if SPC == True :
                jumSPC += 1
                rute = jcopy[sij][1]
                r, s = self.hitungWaktu(rute)
                posisisaatini = (jcopy[sij][0]) + 1
                rutesaatini = r
                fitnesssaatini = jcopy[sij][2]
                kecepatansaatini = (jcopy[sij][0] - posisisaatini)


        kucingnih.set_position(posisisaatini)
        r, s = self.hitungWaktu(rutesaatini)
        kucingnih.set_rute(r)
        kucingnih.set_fitness(fitnesssaatini)
        kucingnih.set_velocity(kecepatansaatini)

    def trackingmode(self, kucingnih) :
        xk = kucingnih.get_position()
        fitnesssaatini = kucingnih.get_fitness()
        rutesaatini = kucingnih.get_rute()
        acakrute = rutesaatini
        vk = kucingnih.get_velocity()
        jumrute = len(kucingnih.get_rute())

        r1 = random.random()
        xbest = 0
        simpan = []

        # Cari X Best
        for j in range(0, jumrute) :
            acakrute = rutesaatini
            pindahke = acakrute[j]
            acakrute[j] = acakrute[xk]
            acakrute[xk] = pindahke
            rutenya, b = self.hitungWaktu(acakrute)
            fitnessnya = self.utility(rutenya)
            simpan.append([j, rutenya, fitnessnya])

        for disimpan in simpan :
            if disimpan[2] > fitnesssaatini :
                xbest = disimpan[0]
                rutesaatini = disimpan[1]
                fitnesssaatini = disimpan[2]

        vbaru = self.w * vk + r1 * self.c1 * (xbest - xk)

        xbaru = xk + vk
        kucingnih.set_position(xbaru)
        r, s = self.hitungWaktu(rutesaatini)
        kucingnih.set_fitness(fitnesssaatini)
        kucingnih.set_rute(r)
        if vbaru > self.maksimalvelocity :
            kucingnih.set_velocity(self.maksimalvelocity)
        elif vbaru < self.minimalvelocity :
            kucingnih.set_velocity(self.minimalvelocity)
        else :
            kucingnih.set_velocity(vbaru)

    def kucingguys(self) :
        if self.cur_tsp :
            literally = []
            bismillahbest = 0
            while self.T >= self.stopping:  # Pengecekan kondisi berhenti
                listKittun = []
                self.currentbestfitness = 0

                tempatwisata = self.initialSolution()
                self.cur_tsp, self.tour = self.hitungWaktu(tempatwisata)  # Mencari fitness

                self.currentbestfitness = self.utility(self.cur_tsp)
                self.currentbestposition = self.cur_tsp
                self.jumlahkucing = len(self.cur_tsp) + 1
                MRnya = math.floor(self.jumlahkucing * self.MR)
                self.maksimalposisi = len(self.cur_tsp)
                self.maksimalfitness = self.currentbestfitness

                # I N I S I A L I S A S I
                for index in range(0, len(self.cur_tsp)):
                    nama = self.cur_tsp[index]
                    if index + 1 <= MRnya:
                        flag = "Tracking"
                    else :
                        flag = "Seeking"
                    listKittun.append(Kittun(nama, index, 0, flag, self.currentbestposition, self.currentbestfitness))

                for k in listKittun :
                    if k.get_flag() == "Seeking" :
                        self.seekingmode(k)
                    elif k.get_flag() == "Tracking" :
                        self.trackingmode(k)

                # # C A R I  M I N  F I T N E S S
                # for cing in range(0, len(listKittun)):
                #     if listKittun[cing].get_fitness() < self.minfit:
                #         self.minfit = listKittun[cing].get_fitness()

                # C A R I  B E S T  F I T N E S S
                for u in listKittun :
                    if u.get_fitness() > self.currentbestfitness :
                        self.currentbestfitness = u.get_fitness()
                        self.currentbestposition = u.get_rute()
                    literally.append([self.tour, self.currentbestposition, self.currentbestfitness])

                # BANDINGKAN DENGAN ITERASI BERIKUTNYA
                # if self.currentbestfitness > self.literallyfitness :
                #     self.literallyfitness = self.currentbestfitness
                #     self.literallyrute = self.bestcat
                #     self.yangbelom = self.tour

                self.T = self.T - 1

            for c in literally :
                if c[2] > bismillahbest :
                    self.yangbelom = c[0]
                    self.literallyrute = c[1]
                    self.literallyfitness = c[2]

        #     print("Bismillah")
        #     print("tour : ", self.yangbelom)
        #     print("tsp : ", self.literallyrute)
        # sys.exit()
        return self.yangbelom, self.literallyrute, self.literallyfitness

    def kucingnya(self) :
        if self.cur_tsp :
            listKittun = []
            self.currentbestfitness = 0

            tempatwisata = self.initialSolution()
            self.cur_tsp, self.tour = self.hitungWaktu(tempatwisata)  # Mencari fitness

            self.currentbestfitness = self.utility(self.cur_tsp)
            self.currentbestposition = self.cur_tsp
            self.jumlahkucing = len(self.cur_tsp) + 1
            MRnya = math.floor(self.jumlahkucing * self.MR)
            self.maksimalposisi = len(self.cur_tsp)
            self.maksimalfitness = self.currentbestfitness

            # I N I S I A L I S A S I
            for index in range(0, len(self.cur_tsp)):
                nama = self.cur_tsp[index]
                if index + 1 <= MRnya:
                    flag = "Tracking"
                else :
                    flag = "Seeking"
                listKittun.append(Kittun(nama, index, 0, flag, self.currentbestposition, self.currentbestfitness))

            for k in listKittun :
                if k.get_flag() == "Seeking" :
                    self.seekingmode(k)
                elif k.get_flag() == "Tracking" :
                    self.trackingmode(k)

            # C A R I  B E S T  F I T N E S S
            for u in listKittun :
                print(u.get_output())
                if u.get_fitness() > self.currentbestfitness :
                    self.currentbestfitness = u.get_fitness()
                    self.currentbestposition = u.get_rute()

        # print(self.tour)
        # print(self.currentbestposition)
        # print(self.currentbestfitness)

        return self.tour, self.currentbestposition

#   Fungsi TSP untuk mereturn hasil tsp dalam 1 hari dan sisa tour untuk TSP hari selanjutnya
    def tsp(self):
        tsp = []
        rest = []
        if self.cur_tsp:
            tour, tsp = self.kucingnya()
            nama_tsp = [x.name for x in tsp ]
            rest = [x for x in tour if x.name not in nama_tsp]
            waktu = self.tmatrix(tsp[len(tsp)-1], self.endNode)
            jam = tsp[len(tsp)-1].dttime.hour + int(waktu // 3600)
            menit = tsp[len(tsp)-1].dttime.minute + int((waktu // 60) % 60 )
            detik = tsp[len(tsp)-1].dttime.second + int(waktu % 60)
            if detik > 59 :
                menit += int(detik / 60)
                detik = int(detik % 60)
            if menit > 59 :
                jam += int(menit / 60)
                menit = int(menit % 60)
            if jam > 23 :
                jam -= 24
            self.endNode.dttime = datetime.time(jam, menit, detik)
        return tsp, rest
