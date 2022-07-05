### Things to add
### Slope of the left side of the loop, last third of the decline 
### Linear decay 
"""
Created on Fri Mar 12 13:32:09 2021

@author: Kelso
"""
#Imports
from tkinter import *
from tkinter.filedialog import askopenfilename
import numpy as np
import pandas as pd
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
from scipy.signal import find_peaks
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from skimage import io
from LineScanImportsGUI import findPeaks
from LineScanImportsGUI import averageCa
from LineScanImportsGUI import fractionalShortening
from LineScanImportsGUI import plateu
from sklearn.linear_model import LinearRegression
from tauCalc import fit_exp_nonlinear
from tauCalc import model_func


# Define tkinter function as root 
root = Tk()
global threshold
global filtering
global traces
global peaks
global traceCorrect
global pixperum
global fps
global cropfrom    
global cropto
global peakfilter

# Preset values for microscope. Change to fit your microscope
fps = 166
pixperum = 0.285


#fps = 743.97 
#pixperum = 0.0191083

threshold = 10
filtering = 11
peakfilter = 111 


traces = pd.DataFrame()
traceCorrect = 20



# Create function to choose file to load and remove the blue and red channel
def choosefile():

    global file  
    global cropfrom
    global cropto
     
    
    
    Tk().withdraw() 
    filename = askopenfilename() 
    file = io.imread(filename)
    file = file[:,:,1] # just keeping the first dimension
    cropFromentry.insert(0, 0)
    cropToentry.insert(0, len(file))
    peakIT()   
    

# Define a function to find the peaks and report their position back     
def peakIT():
     
    global peaks
    peaks = findPeaks(file[cropfrom:cropto], threshold, peakfilter)
    fig = Figure(figsize = (7, 3), dpi = 100) 
    plot1 = fig.add_subplot(111) 
    plot1.plot(peaks)
    canvas = FigureCanvasTkAgg(fig, master = root)   
    canvas.draw()   
    canvas.get_tk_widget().place(x=20, y=25) 

 
#Define a paramaters section
def parameters():
    global cropfrom
    global cropto
    global fps
    global pixelperum
    global threshold
    global peakfilter
    cropfrom = int(cropFromentry.get())
    cropto = int(cropToentry.get())
    threshold = int(Thresholdentry.get())
    peakfilter = int(peakfilterentry.get())
    fps = float(FPSentry.get())
    pixelsperum = float(pixperumentry.get())
    peakIT()
    
    
    
    

# Define a function to average the last Ca2+ transients    
def calcium():
    global traces
    global peaks
    global fps
    traces = pd.DataFrame()
    traces['Ca2+'] = averageCa(file, peaks, filtering, traceCorrect, Bckground)
    traces['Time'] = np.ones(len(traces['Ca2+']))
    column_names = ['Time', 'Ca2+']
    traces = traces.reindex(columns=column_names)
    for i in range(0,len(traces['Ca2+'])):
        traces['Time'][i] = i/fps  
    fig = Figure(figsize = (7, 3), dpi = 100) 
    plot1 = fig.add_subplot(111) 
    plot1.plot(traces['Time'], traces['Ca2+'])
    canvas = FigureCanvasTkAgg(fig, master = root)   
    canvas.draw()   
    canvas.get_tk_widget().place(x=20, y=25) 
    #traces['F/F0'] = traces['Ca2+']/np.argmax(traces['Ca2+'])
    traces['fs'] = np.ones(len(traces['Ca2+']))


# Define a function to average the last 5 contractions    
def shortening():
    global traces
    global peaks
    global pixperum
    traces['fs'] = fractionalShortening(file, peaks, filtering, traceCorrect, RightSide, LeftSide)
    traces['fs'] = traces['fs']*pixperum
    fig = Figure(figsize = (7, 3), dpi = 100) 
    plot1 = fig.add_subplot(111) 
    plot1.plot(traces['Time'], traces['fs'])
    canvas = FigureCanvasTkAgg(fig, master = root)   
    canvas.draw()   
    canvas.get_tk_widget().place(x=20, y=25) 
    traces['fs %'] = ((traces['fs']/traces['fs'][1])*100)-100
    traces['fs positive'] = (traces['fs']-traces['fs'][0])*-1
    

# Define two functions to allow for correction of the start of the averaged traces
def movetraceminus():
    global traceCorrect
    traceCorrect = traceCorrect-10
    calcium()
def movetraceplus():
    global traceCorrect
    traceCorrect = traceCorrect+10
    calcium()
    

# Define a function plot Ca2+ transients against contraction (raw values)
def plotloop():
    global traces
    fig = Figure(figsize = (7, 3), dpi = 100) 
    plot1 = fig.add_subplot(111) 
    plot1.plot(traces['Ca2+'], traces['fs positive'])
    canvas = FigureCanvasTkAgg(fig, master = root)   
    canvas.draw()   
    canvas.get_tk_widget().place(x=20, y=25) 

# Define a function to create an excel sheet with all different traces
# and copy data values to the clipboard for pasting into any sheet
def saveData():
    global traces
    global fps
    global tfifty
    
    # Defin 10 and 90% of the trace
    tenperc = int(len(traces['Ca2+'])*0.1)
    nintyperc = int(len(traces['Ca2+'])*0.9)             
    
    # Create variable for different Ca measurements
    systolicCa = np.max(traces['Ca2+']) #Systolic Ca
    diastolicCa = np.mean(traces['Ca2+'][(len(traces['Ca2+'])-tenperc):(len(traces['Ca2+']))]) #Diastolic Ca
 
    # If noise is high and background is subtracted CaD can go below zero, set CaD to 0.1  
    if diastolicCa < 0: 
       diastolicCa = 0.1
       
    amplitudeCa = systolicCa - diastolicCa # Ca amplitude
    FoverF0Ca = systolicCa/diastolicCa #Ca F over F0 max
    timetopeakCa = (np.argmax(traces['Ca2+']))/fps #Ca Time to peak
    traces['F/F0'] = traces['Ca2+']/diastolicCa #Ca F over F0 full trace
     
    traces.to_excel('Traces.xls') #Save full traces to Excel file
    
    fiftydecayCa = ((amplitudeCa*0.5)+diastolicCa) # Calculate Ca 50% decay value 
    # Define a function to find nearest recorded value
    def find_nearest(array, fiftydecayCa):
        array = np.asarray(array)
        idx = (np.abs(array - fiftydecayCa)).argmin()
        print('IDX  ', idx)
        return array[idx]
    # Use the previously defined function to create a variable 
    # that denotes the nearest measured value to the calculated value
    nearest = find_nearest(traces['Ca2+'], fiftydecayCa)
    tfifty = traces['Ca2+'].where(traces['Ca2+'] == nearest)
    # Sort out non matching values
    for i in range(len(tfifty)):
        if tfifty[i] > 0:
            decayfifty = i
        else: 
            i = i+1
    decayfiftyy = traces['Time'][decayfifty] #Final variable containin time at 50% decay

    # Create variable for different contraction measurements
    systolicfs = np.min(traces['fs']) #Systolic cell lenght
    diastolicfs = np.mean(traces['fs'][(len(traces['fs'])-tenperc):(len(traces['fs']))]) #Diastolic cell lenght
    amplitudefs = systolicfs - diastolicfs #Contraction 
    FractionalShort = (systolicfs/diastolicfs) # Fractional shortening in % 
    timetopeakfs = (np.argmin(traces['fs']))/fps # Time to maximum contraction

    # Calculate Tau decay for Ca
    plateuCa = plateu(traces['Ca2+'])
    CaTau = fit_exp_nonlinear(traces['Time'][plateuCa:len(traces)], traces['Ca2+'][plateuCa:len(traces)])
    # Calculate Tau decay for FS
    plateufs = plateu(traces['fs positive'])
    FsTau = fit_exp_nonlinear(traces['Time'][plateufs:len(traces)], traces['fs positive'][plateufs:len(traces)])
    
    
    #Chose if the graph should display Ca tau or FS tau. 
    #Both are calculated regardless
    if TauGraph.get() > 0:
        fig = Figure(figsize = (7, 3), dpi = 100) 
        plot1 = fig.add_subplot(111) 
        plot1.plot(traces['Time'], traces['fs positive'])
        plot1.plot(traces['Time'][plateufs:len(traces)], model_func(traces['Time'][plateufs:len(traces)], FsTau[0], FsTau[1], FsTau[2]))
        canvas = FigureCanvasTkAgg(fig, master = root)   
        canvas.draw()   
        canvas.get_tk_widget().place(x=20, y=25) 
    else:
        fig = Figure(figsize = (7, 3), dpi = 100) 
        plot1 = fig.add_subplot(111) 
        plot1.plot(traces['Time'], traces['Ca2+'])
        plot1.plot(traces['Time'][plateuCa:len(traces)], model_func(traces['Time'][plateuCa:len(traces)], CaTau[0], CaTau[1], CaTau[2]))
        canvas = FigureCanvasTkAgg(fig, master = root)   
        canvas.draw()   
        canvas.get_tk_widget().place(x=20, y=25) 
        

    CaTau = CaTau + traces['Time'][plateuCa]
    FsTau = FsTau + traces['Time'][plateufs]
    #print('plateu', plateu(traces['Ca2+']))
    print(diastolicCa, diastolicfs)
    print(systolicCa, systolicfs)
    print(amplitudeCa, amplitudefs)
    print(FoverF0Ca, FractionalShort)
    print(CaTau[1], FsTau[1])
    print('decay fifty', decayfiftyy)
    
    
    root.clipboard_clear()
    root.clipboard_append('Parameter')
    root.clipboard_append('\t')
    root.clipboard_append('Ca2+')
    root.clipboard_append('\t')
    root.clipboard_append('FS')
    root.clipboard_append('\n')
    root.clipboard_append('Diastolic')
    root.clipboard_append('\t')
    root.clipboard_append(diastolicCa) #Systolic
    root.clipboard_append('\t')
    root.clipboard_append(diastolicfs) #Tau decay Ca2+
    root.clipboard_append('\n')
    root.clipboard_append('Systolic') #Diastolic
    root.clipboard_append('\t')
    root.clipboard_append(systolicCa) #Diastolic
    root.clipboard_append('\t')
    root.clipboard_append(systolicfs)
    root.clipboard_append('\n')
    root.clipboard_append('Raw amplitude')
    root.clipboard_append('\t')
    root.clipboard_append(amplitudeCa) #Amplitude
    root.clipboard_append('\t')
    root.clipboard_append(amplitudefs)
    root.clipboard_append('\n')
    root.clipboard_append('Relative change')
    root.clipboard_append('\t')
    root.clipboard_append(FoverF0Ca) #Tau decay Ca2+
    root.clipboard_append('\t')
    root.clipboard_append(FractionalShort)
    root.clipboard_append('\n')
    root.clipboard_append('tau') #Tau decay Ca2+
    root.clipboard_append('\t')
    root.clipboard_append(CaTau[1]) #Tau decay Ca2+
    root.clipboard_append('\t')
    root.clipboard_append(FsTau[1])
    root.clipboard_append('\n')
    root.clipboard_append('Time to peak') #Tau decay Ca2+
    root.clipboard_append('\t')
    root.clipboard_append(timetopeakCa) #Tau decay Ca2+
    root.clipboard_append('\t')
    root.clipboard_append(timetopeakfs)
    root.clipboard_append('\n')
    root.clipboard_append('Time to 50% decay') #50% decay Ca2+
    root.clipboard_append('\t')
    root.clipboard_append(decayfiftyy) #50% decay Ca2+

    
    
#Define a function to search for peaks and split them into frequencie dependent columns
                 


# Function to call for splitting and graphing the traces

# Create and draw top button
filebutton = Button (root, text = 'Choose file', command = choosefile, padx=317)
filebutton.place(x=20, y=0)

#Create and draw bottom buttons
peaksButton = Button (root, text = 'Find peaks', command = peakIT, state = NORMAL)
peaksButton.place(x=20, y=355)
'''
threshupbutton = Button(root, text = '+', command = thresholdup, padx = 5)
threshupbutton.place(x=90, y=355)

threshdownbutton = Button(root, text = '-', command = thresholddown, padx = 6)
threshdownbutton.place(x=120, y=355)
'''
calciumbutton = Button (root, text = 'Plot Ca2+', command = calcium, padx = 10)
calciumbutton.place(x=150, y=355)


moveminusbutton = Button(root, text = '<-', command = movetraceminus, padx = 6)
moveminusbutton.place(x=235, y=355)

moveplusbutton = Button(root, text = '->', command = movetraceplus, padx = 5)
moveplusbutton.place(x=270, y=355)

shortening = Button (root, text = 'Plot Shortening', command = shortening, padx = 5)
shortening.place(x=305, y=355)

LeftSide = IntVar()
LeftSideCheck = Checkbutton(root, text="Left", variable=LeftSide).place(x=410, y=355)

RightSide = IntVar()
RightSideCheck = Checkbutton(root, text="Right", variable=RightSide).place(x=460, y=355)

loopbutton = Button (root, text = 'Plot loop', command = plotloop, padx = 10)
loopbutton.place(x=520, y=355)

savebutton = Button (root, text = 'Export data', command = saveData, padx = 10)
savebutton.place(x=625, y=355)

# Create GUI for parameter customization
parametersButtom = Button (root, text = 'Update parameters', command = parameters, padx = 10)
parametersButtom.place(x=750, y=200)

cropFromlabel = Label(root, text='Crop from: ')
cropFromlabel.place(x=740, y=43)

cropFromentry = Entry(root, width=15)

cropFromentry.place(x=830, y=40)

cropTolabel = Label(root, text='Crop to: ')
cropTolabel.place(x=740, y=63)

cropToentry = Entry(root, width=15)
#cropToentry.insert(0, len(file))
cropToentry.place(x=830, y=60)

thresholdlabel = Label(root, text='Threshold: ')
thresholdlabel.place(x=740, y=83)

Thresholdentry = Entry(root, width=15)
Thresholdentry.insert(0, threshold)
Thresholdentry.place(x=830, y=80)

peakfilterlabel = Label(root, text='Filter: ')
peakfilterlabel.place(x=740, y=103)

peakfilterentry = Entry(root, width=15)
peakfilterentry.insert(0, peakfilter)
peakfilterentry.place(x=830, y=100)

FPSlabel = Label(root, text='FPS: ')
FPSlabel.place(x=740, y=143)

FPSentry = Entry(root, width=15)
FPSentry.insert(0, fps)
FPSentry.place(x=830, y=140)

pixperumlabel = Label(root, text='pix/um: ')
pixperumlabel.place(x=740, y=123)

pixperumentry = Entry(root, width=15)
pixperumentry.insert(0, pixperum)
pixperumentry.place(x=830, y=120)

TauGraph = IntVar()
TauGraphCheck = Checkbutton(root, text="Show FS tau not Ca2+ tau", variable=TauGraph).place(x=735, y=180)

Bckground = IntVar()
BckgroundCheck = Checkbutton(root, text="Sutract background", variable=Bckground).place(x=735, y=165)

# Create the damn window and start analyzing! Whoop! 
icon = PhotoImage(file = 'icon.png')

root.title("LineMaster")
root.geometry("940x390")
root.iconphoto(False, icon)

#This stuff only works in Spyder for some reason. Good to have but... 
# Deine a function to kill the kernel when quitting the GUI
"""
    def on_closing():
    if messagebox.askokcancel("Quit", "You done!?"):
        root.destroy()
        quit()

root.protocol("WM_DELETE_WINDOW", quit())
"""
root.mainloop()

