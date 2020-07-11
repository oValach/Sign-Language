from lib import bvh2glo_simple
import numpy as np
from lib import SL_dict
import matplotlib.pyplot as plt
from lib import data_comp
import operator
import math
import glob

if __name__ == "__main__":
    done_files = 0
    distancesJointsAll = [[None]]*61
    fileRangesAll = []
    for filepath in glob.iglob('C:/Users/User/PRJ4/data_bvh/*.bvh'): #iterating over files
        #try:
            BVH_file = filepath
            dictionary_file = 'C:/Users/User/PRJ4/data/ultimate_dictionary2.txt'

            #načtení BVH souboru a přepočítání angulárních dat na trajektorii v globáních souřadnicích
            joints, trajectory = bvh2glo_simple.calculate(BVH_file)
            frames, joint_id, channels = np.shape(trajectory)

            ranges = [] #pole délek jednotlivých transition [snímků/tra.]
            DISTS = [] #pole vzdáleností, které ucestovaly jednotlivé části těla během transitions
            number = 0

            dictionary = SL_dict.search_take_file(dictionary_file, BVH_file)
            
            frameCounter = 0
            maxprevSpeed = [0]*len(joints)
            sumprevSpeed = [0]*len(joints)
            maxtraSpeed = [0]*len(joints)
            sumtraSpeed = [0]*len(joints)
            maxnextSpeed = [0]*len(joints)
            sumnextSpeed = [0]*len(joints)

            for i,val in enumerate(dictionary):
                number += 1
                for tmp_key in val.keys():
                    if tmp_key == 'sign_name' and val[tmp_key] == 'tra.':

                        start = val['annotation_Filip_bvh_frame'][0]
                        end = val['annotation_Filip_bvh_frame'][1]

                        DIST = data_comp.comp_dist(trajectory,start,end) #implementovaná fn na výpočet abs. vzdálenosti
                        DISTS.append(DIST)
                        ranges.append(end-start)

                        nextLine = dictionary[i+1]
                        speedVals = data_comp.comp_speed(trajectory,dictionary,previousLine,val,nextLine) #fce - získání rychlostí
                        if speedVals[3] == 1:
                            for jointIdx in range(len(joints)): #kontrola maxim rychlostí pro jednotlive klouby
                                if speedVals[0][jointIdx] > maxprevSpeed[jointIdx]:
                                    maxprevSpeed[jointIdx] = speedVals[0][jointIdx]
                                if speedVals[1][jointIdx] > maxtraSpeed[jointIdx]:
                                    maxtraSpeed[jointIdx] = speedVals[1][jointIdx]
                                if speedVals[2][jointIdx] > maxnextSpeed[jointIdx]:
                                    maxnextSpeed[jointIdx] = speedVals[2][jointIdx]

                                sumprevSpeed[jointIdx] = sumprevSpeed[jointIdx] + speedVals[0][jointIdx]
                                sumtraSpeed[jointIdx] = sumtraSpeed[jointIdx] + speedVals[1][jointIdx]
                                sumnextSpeed[jointIdx] = sumnextSpeed[jointIdx] + speedVals[2][jointIdx]
                            frameCounter += 1
                            break
                previousLine = val

            Dist_sorted = [] #přeuspořádání DISTS, index řádku = část těla, obsahuje všechny polohy dané části těla ve snímcích
            numberof = 0
            while numberof < len(DISTS[1]):
                Dist_sorted.append([])
                for i in range(len(DISTS)):
                    Dist_sorted[numberof].append(DISTS[i][numberof])
                numberof +=1

            avg_dist_singly = [] #průměrná uražená vzdálenost pro každou část těla (mometálně nepoužito)
            for i in range(len(Dist_sorted)):
                avg_dist_singly.append(np.mean(Dist_sorted[i]))
            avg_dist_all = np.mean(avg_dist_singly) #celková průměrná uražená vzdálenost (-||-)

            done_files +=1
            print(done_files)
            #plt.scatter(Dist_sorted[indexes[0]], ranges.values())
            #plt.show()
            for k in range(len(Dist_sorted)): #akumulace hodnot do společného pole
                distancesJointsAll[k] = distancesJointsAll[k] + Dist_sorted[k]
                if distancesJointsAll[k][0] == None:
                    distancesJointsAll[k].pop(0)
            fileRangesAll = fileRangesAll+ranges

            if done_files == 33:
                avgprevSpeed = [summary1 / frameCounter for summary1 in sumprevSpeed]
                avgtraSpeed = [summary2 / frameCounter for summary2 in sumtraSpeed]
                avgnextSpeed = [summary3 / frameCounter for summary3 in sumnextSpeed]

                corr_coefs = [] #pole korelací částí těla s délkou transitiony přes všechny soubory
                for j in range(len(distancesJointsAll)):
                    corr_matrix = np.corrcoef(distancesJointsAll[j], fileRangesAll)
                    corr_coefs.append(corr_matrix[0][1])
                m = 0
                maxes = {}
                corr_coefsCopy = corr_coefs.copy()
                while m < 3: #3 maxima
                    idx = corr_coefsCopy.index(max(corr_coefsCopy)) 
                    maxes[joints[idx]] = corr_coefsCopy[idx]
                    corr_coefsCopy[idx] = 0
                    m += 1
                file = open("results_duration.txt","a") #uložení výsledků
                file.write("BIGGEST correlations:" +str(maxes)+'\n')
                file.write("ALL correlations:\n")
                for p in range(len(joints)):
                    file.write(str(joints[p]) + " - " + str(corr_coefs[p])+'\n')

                file = open("results_speed.txt","a")
                file.write('Joint           , Maximals [pre,tra,next],  Average [pre,tra,next]\n\n')
                for idx in range(len(joints)):
                    file.write(str(joints[idx])+'    '+str(round(maxprevSpeed[idx],3))+','+str(round(maxtraSpeed[idx],3))+','+str(round(maxnextSpeed[idx],3))+'    |    '+str(round(avgprevSpeed[idx],3))+','+str(round(avgtraSpeed[idx],3))+','+str(round(avgnextSpeed[idx],3))+'\n')

                ''' Výstup v konzoli
                print("BIGGEST correlations:" +str(maxes)+'\n')
                print("ALL correlations:\n")
                for p in range(len(joints)):
                    print(str(joints[p]) + " - " + str(corr_coefs[p])+'\n')
                '''
