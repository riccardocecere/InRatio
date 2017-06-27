from math import *
import numpy as np
import sys
import Image2Array
import matplotlib.pyplot as plt

def DTW(A, B,d = lambda x,y: abs(x-y)):
    """
        algoritmo che dati due array in entrata si trova le coppie da paragonare (path) e successivamente
        ritorna la somma di tutte le distanze tra i valori delle coppie trovate tra i due array  (cost[-1,-1])
    """
    # create the cost matrix
    A, B = np.array(A), np.array(B)
    M, N = len(A), len(B)
    cost = sys.maxint * np.ones((M, N))

    # initialize the first row and column
    cost[0, 0] = d(A[0], B[0])
    for i in range(1, M):
        cost[i, 0] = cost[i-1, 0] + d(A[i], B[0])

    for j in range(1, N):
        cost[0, j] = cost[0, j-1] + d(A[0], B[j])
    # fill in the rest of the matrix
    for i in range(1, M):
        for j in range(1,N):
            choices = cost[i - 1, j - 1], cost[i, j-1], cost[i-1, j]
            cost[i, j] = min(choices) + d(A[i], B[j])

    # find the optimal path
    n, m = N - 1, M - 1
    path = []

    while (m, n) != (0, 0):
        path.append((m, n))
        m, n = min((m - 1, n), (m, n - 1), (m - 1, n - 1), key = lambda x: cost[x[0], x[1]])
    
    path.append((0,0))
    return cost[-1, -1], path

def compare(image1, image2):
    """
        metodo che, date in ingresso due immagini, riporta in uscita i quattro valori di comparazione tra esse
        applicando l'algoritmo di Dinamic Time Warping 
    """
    #prendo i quattro array conteneti le caratteristiche dell'immagini
    vertDensity1, top1, bottom1, horizDensity1 = Image2Array.image2Array(image1)
    vertDensity2, top2, bottom2, horizDensity2 = Image2Array.image2Array(image2)
    #comparo i quattro array tra le due immagini per avere i costi e le coppie di comparazione negli array
    costVertDensity, pathVertDensity = DTW(vertDensity1,vertDensity2)
    costTop, pathTop = DTW(top1, top2)
    costBottom, pathBottom = DTW(bottom1, bottom2)
    costHorizDensity, pathHorizDensity = DTW(horizDensity1, horizDensity2)
    return [costVertDensity , costTop , costBottom , costHorizDensity]
"""
def compareListOfImages(imageList):
    costVertDensity , costTop , costBottom , costHorizDensity = numpy.zeros(shape=(len(imageList)))
    for image,i in zip(imageList, range(0,len(imageList))):
        costVertDensity[i] , costTop[i] , costBottom[i] , costHorizDensity[i]= compare2Images 
"""

def main():
    vertDensity1, top1, bottom1, horizDensity1 = Image2Array.image2Array("istanze\dominuf(1).bin.png")
    vertDensity2, top2, bottom2, horizDensity2 = Image2Array.image2Array("istanze\dominuf(2).bin.png")
    costVertDensity, pathVertDensity = DTW(vertDensity1,vertDensity2)
    costTop, pathTop = DTW(top1, top2)
    costBottom, pathBottom = DTW(bottom1, bottom2)
    costHorizDensity, pathHorizDensity = DTW(horizDensity1, horizDensity2)
    #c1=cost1/min(len(A1),len(B1))
    #c2=cost2/min(len(A2),len(B2))
    #c3=cost3/min(len(A3),len(B3))
    print 'Total Distance is ', costVertDensity , costTop , costBottom , costHorizDensity 
    offset = 0
    #plt.xlim([-1, max(len(A3), len(B3)) + 1])
    #plt.plot(vertDensity1)
    #plt.plot(vertDensity2 + offset)
    #for (x1, x2) in pathVertDensity:
    #    plt.plot([x1, x2], [vertDensity1[x1], vertDensity2[x2] + offset])
    #plt.show()
    #plt.plot(top1)
    #plt.plot(top2 + offset)
    #for (x1, x2) in pathTop:
    #    plt.plot([x1, x2], [top1[x1], top2[x2] + offset])
    #plt.show()
    #plt.plot(bottom1)
    #plt.plot(bottom2 + offset)
    #for (x1, x2) in pathBottom:
    #    plt.plot([x1, x2], [bottom1[x1], bottom2[x2] + offset])
    #plt.show()
    #plt.plot(horizDensity1)
    #plt.plot(horizDensity2 + offset)
    #for (x1, x2) in pathHorizDensity:
    #    plt.plot([x1, x2], [horizDensity1[x1], horizDensity2[x2] + offset])
    #plt.show()
    

if __name__ == '__main__':
    main()