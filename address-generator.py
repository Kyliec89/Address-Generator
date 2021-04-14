#Imports
from tkinter import *
from tkinter import ttk
import csv
import random
import pandas as pd
import sys
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy

#Global Variables

chosen_row = 0
stateChosen = None
numEntry = None
window = None

def gui():
    global stateChosen
    global numEntry
    # Set up GUI window
    window = Tk()
    window.geometry("500x500")
    window.title("Person Generator POC")

    # Greeting label
    greeting = Label(text="Welcome to People Generator")
    greeting.pack()

    # Dropdown to select state
    stateLabel = ttk.Label(window, text="Which state would you like addresses from?")
    state = StringVar()
    stateChosen = ttk.Combobox(window, width=27, textvariable=state)
    stateChosen['values'] = ("AK", "AZ", "CO", "HI", "ID", "MT", "NV", "OR", "UT", "WA", "WY")
    stateChosen.current(0)
    stateLabel.pack()
    stateChosen.pack()

    # Number of addresses entry
    inputText = Label(text="How many addresses do you need?")
    numEntry = Entry(window)
    numSaved = numEntry.get()
    inputText.pack()
    numEntry.pack()

    # submit button
    submitBtn = Button(window, text="Submit", command=stateConverter)
    submitBtn.pack()

    # Download button
    downloadBtn = Button(window, text="Download CSV", command=downloadCSV)
    downloadBtn.pack()
    window.mainloop()

#function to convert state input to file name
def stateConverter():
    stateVar = stateChosen.get()
    stateVar = stateVar.lower()
    stateFile = stateVar + '.csv'
    addressPrinter(stateFile)

#function to print random addresses
def addressPrinter(stateFile):
    global chosen_row
    lines = numEntry.get()
    lines = int(lines)

    dataRead = pd.read_csv(stateFile, usecols=[2, 3, 5, 8])
    chosen_row = dataRead.sample(n=lines)
    printRow = Label(window, justify = LEFT, text=chosen_row)
    printRow.pack()

def downloadCSV():
    chosen_row.to_csv('output.csv')


def commandLine(inputFile):
    with open(inputFile, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        state = data[1][0]
        num = data[1][1]
        numInput = int(num)
        stateVar = state.lower()
        stateFile = stateVar + '.csv'

        dataRead = pd.read_csv(stateFile, usecols=[2, 3, 5, 8])
        chosen_row = dataRead.sample(n=numInput)

        chosen_row.to_csv('output.csv')

def zipReturn(state):
    stateVar = state.lower()
    stateFile = stateVar + '.csv'
    df = pd.read_csv(stateFile, usecols=[8], low_memory=False)
    zips = df.loc[(df.POSTCODE.notnull())]
    uniqueValues = zips['POSTCODE'].unique()
    zipList = uniqueValues.tolist()
    return zipList



class RequestHandler(SimpleXMLRPCRequestHandler):
   rpc_paths = ("/RPC2",)


def microservice_server():
   host = "localhost"
   port = 7000

   with SimpleXMLRPCServer((host, port), requestHandler=RequestHandler) as server:
        server.register_introspection_functions()
        server.register_function(zipReturn)
        print('Server is running on port 7000')
        server.serve_forever()



def population(year, state):
    proxy = ServerProxy('http://localhost:9000')
    print(proxy.get_population_by_state(year, state))


def main():

    length = len(sys.argv)
    if length == 1:
        gui()

    if length == 2:
        commandLine(sys.argv[1])

    if sys.argv[1] == 'server':
        microservice_server()

    if sys.argv[1] == 'population':
        population(sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()
