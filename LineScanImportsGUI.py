#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 14:22:11 2021

@author: Kelso
"""

import numpy as np
#import skimage
from skimage import io
from matplotlib import pyplot as plt
import pandas as pd
#from scipy.misc import electrocardiogram
from scipy.signal import find_peaks
from scipy.signal import convolve as convolve
from scipy.signal import medfilt
#from helperFunctions import getMaxima  
#from scipy.signal import medfilt


#file = file[:,:,1] # just keeping the first dimension        


def findPeaks(trace, threshold, pfilter):
    CaStrip = pd.DataFrame()
    CaStrip[0] = np.zeros(len(trace))
   
    for i in range(len(trace)):
        CaStrip[0][i] = np.mean(trace[i])
     
    filtereddata=medfilt(CaStrip[0][0:len(CaStrip)], pfilter)###<------------------------------- VARIABLE
    #threshold = np.argmax(filtereddata)/20
    #print(threshold)
    #filtereddata=medfilt(trace[0:len(trace), 256], 111)###<------------------------------- VARIABLE
    tracer = filtereddata
    peaks, _ = find_peaks(tracer, height=threshold) ### <------------------------------- VARIABLE
    plt.plot(filtereddata)
    plt.plot(peaks, tracer[peaks], "X")
    plt.plot(np.zeros_like(tracer), "--", color="gray")
    plt.title('Pay attention to this one!')
    plt.show()
    
    return(peaks)
    

def averageCa(trace, peaks, filtercoeff, scoot, Bckground):
    ### Find stim freq based on time between the peaks 
    
    ### TEST AREA 
    CaStrip = pd.DataFrame()
    CaStrip[0] = np.zeros(len(trace))
    for i in range(len(trace)):
        #CaStrip[0][i] = np.mean(trace[i,:])
        CaStrip[0][i] = np.median(trace[i,:])
    ####
    
    filtereddata=medfilt(CaStrip[0][0:len(trace)], filtercoeff)###<------------------------------- VARIABLE
    #filtereddata=medfilt(trace[0:len(trace), 256], filtercoeff)###<------------------------------- VARIABLE
    period = int((peaks[2]-peaks[1]))
    ### Start the graph X timeunits before the peak
    shift = peaks[1]-scoot
    ### Split Traces
    periodic={}
    for i in range (5):
        periodic[i] = filtereddata[shift+(i+(len(peaks)-6))*period:shift+(i+(len(peaks)-5))*period]

    #allTraces = pd.DataFrame(periodic) #Save full traces to Excel file
    #allTraces.to_excel('All.xls')
    #for i in range (5):
    #    plt.plot(periodic[i])
    ### Create an average trace from the last 5 transients 
    ### Plot it and report Systolic, Diastolic, Amplitude and F/F0
    avgTrace=np.array(pd.DataFrame(periodic).mean(axis=1))
    #plt.plot(avgTrace/np.mean(avgTrace[250:300]))
    #plt.title('Average Ca2+ transient')
    #plt.show()
### NEW
    if Bckground.get() > 0:
        Background = np.median(trace[1:5][0:len(trace)])
        avgTrace=avgTrace-Background
          
        
    return(avgTrace)
def fractionalShortening(trace, peaks, filtercoeff, scoot, LeftSide, RightSide):
    #Do some crazy Jakub magic
    ### Create filters as np arrays instead
    leftfilter = np.ones((60))
    leftfilter[0:30] = -1

    leftBoundary = np.zeros((len(trace)))
    rightBoundary = np.zeros((len(trace)))
    ### Run filter on left sige of the trace and then right 
    for i in range(len(trace)):
        leftconv = convolve(trace[i, 0:512], leftfilter , mode='same')
        leftBoundary[i] = np.argmin(leftconv)
        rightconv = convolve(trace[i, 0:512], leftfilter , mode='same')
        rightBoundary[i] = np.argmax(rightconv)
    filterleft=medfilt(leftBoundary, filtercoeff)
    filterright=medfilt(rightBoundary, filtercoeff)
    
    print(LeftSide)
    if LeftSide.get() == RightSide.get():
        shortening = filterright-filterleft
    elif LeftSide.get() > RightSide.get():
        shortening = 512-(filterleft*2)
    elif LeftSide.get() < RightSide.get():
        shortening = (filterright*2)-512
    
    #plt.plot(shortening)
    #plt.show()
    ### Create a new variable for the Shortening, split them like the Ca transients and plot the average. 
    #x = 20 ### <------------------------------------------------------------------ VARAIBLE
    period = int((peaks[2]-peaks[1]))
    shift = peaks[1]-scoot
    periodica={}
    for i in range (5):
        periodica[i] = shortening[shift+(i+(len(peaks)-6))*period:shift+(i+(len(peaks)-5))*period]
    avgTrace=np.array(pd.DataFrame(periodica).mean(axis=1))
    
    #allTraces = pd.DataFrame(periodica) #Save full traces to Excel file
    #allTraces.to_excel('AllFS.xls')
    
    #plt.plot(avgTrace)
    #plt.title('Average Fractional Shortening')
    #plt.show()
    return(avgTrace)
    
    
def variability(trace, peaks, filtercoeff, scoot):
    ### Find stim freq based on time between the peaks 
    
    ### TEST AREA 
    CaStrip = pd.DataFrame()
    CaStrip[0] = np.zeros(len(trace))
    for i in range(len(trace)):
        CaStrip[0][i] = np.mean(trace[i,:])
    ####
    
    filtereddata=medfilt(CaStrip[0][0:len(trace)], filtercoeff)###<------------------------------- VARIABLE
    #filtereddata=medfilt(trace[0:len(trace), 256], filtercoeff)###<------------------------------- VARIABLE
    period = int((peaks[2]-peaks[1]))
    ### Start the graph X timeunits before the peak
    shift = peaks[1]-scoot
    ### Split Traces
    periodic={}
    for i in range (5):
        periodic[i] = filtereddata[shift+(i+(len(peaks)-5))*period:shift+(i+(len(peaks)-4))*period]

    #for i in range (5):
    #    plt.plot(periodic[i])
    ### Create an average trace from the last 5 transients 
    ### Plot it and report Systolic, Diastolic, Amplitude and F/F0
    avgTrace=np.array(pd.DataFrame(periodic).std)
    #plt.plot(avgTrace/np.mean(avgTrace[250:300]))
    #plt.title('Average Ca2+ transient')
    #plt.show()
    plt.plot(avgTrace)
    plt.show()
    return(avgTrace)


def plateu(trace):
    peak = np.argmax(trace)
    length = len(trace)-peak
    cutoff = trace[peak]-(trace[peak]*0.1)
    i = peak
    while trace[i] > cutoff:
        i=i+1
    return(i)

        
    
    
