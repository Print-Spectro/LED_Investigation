import serial
import serial.tools.list_ports
import time
import datetime
import os
from numpy import average
from numpy import std
from numpy import linspace

class semiconductor_investigation:
    """Class containing all the methods information required for practical 
    """
    def __init__(self, **kwargs):
        self.folder = "" #one can define the directory in which the files are saved. use \\ at the end of the folder name.
        self.repeats = 10 #number of repeats performed for each component
        self.samples = 101 #number of points sampled for each voltage range
        self.delay = 0.05 #delay for each reading in s
        self.component = "red_LED" #single component for the collect method running a single time, default value changeable
        self.components = ["test_0", "test_1"] #component list for the run method, default value changeable
        self.ser = None #store serial object
        self.s_v = 0
        self.e_v = 1

    def serial_on(self, **kwargs):
        """
        Method for starting serial connection
        Input
        --------
        ser : Serial Object
        Commence serial connection beforehand and set the self.ser before running code kind of redundant ngl.

        Output
        --------
        successful connection readout
        """
        self.ser = kwargs.get("serial", self.ser)
        for i in range(3):
            b = self.ser.readline()
            readstring = b.decode("utf-8")
            print(readstring)
    
    def collect(self, **kwargs):
        """
        This function collects the current against a given voltage for a given component and sample frequency and saves a columnated text
        file containing current against voltage.

        kwargs
        ---------- 
        component : string
        Component used, default behaviour is to save a file in a filder both named after the component, unless a filename is given.
        filename: string
        file location to save the data. 
        ser: Serial object
        The serial connection should be set up beforehand. One can use a dummy serial for testing. 
        s_v : int
        Start voltage for the test
        e_v : int
        End voltage for the test
        no_ : int
        Number of samples within defined voltage range

        Output
        ------------------
        Text file containing column separated data with headings for voltage across LED and current through LED
        """
 
        s_v, e_v = kwargs.get("start", self.s_v), kwargs.get("end", self.e_v)
        no_ = kwargs.get("samples", 101)
        component = kwargs.get("component", self.component)
        filename = kwargs.get("filename", self.folder + component + "\\" + component + ".txt")
        try:
            os.mkdir(component)
        except FileExistsError:
            print("Directory already exists")
        with open(filename, "w") as text_file:
            text_file.write("comp: "+component + " V_range: " +str(s_v)+"-"+str(e_v) +" "+", V_Step: "+ str((e_v-s_v)/(no_-1))+"V, Delay: "+str(self.delay) +" ms\n"+ "Date :" +str(datetime.datetime.now())[:10]+ "\n"+'voltage'+' '+'current'+'\n')
            for i in list(linspace(s_v,e_v,no_)):
                self.ser.write('{0}{1}{2}'.format("<S",str(i),">").encode())
                self.ser.write('<I1>'.encode())
                self.ser.write("<V2>".encode())
                z = self.ser.readline().decode("utf-8").split()[1] #readline to skip the output set voltage sent
                x = self.ser.readline().decode("utf-8").split()[1]
                y = self.ser.readline().decode("utf-8").split()[1]
                text_file.write(x+' '+y+'\n')
                time.sleep(self.delay)

    def run(self, **kwargs):
        """
        Method for automating experiment; it can collect data for a list of different components and calculate the averages and standard deviations
        kwargs
        ---------- 
        components : list of strings
        The list of components being investigated
        rep: number of repeats to be carried out for each component

        Output
        ------------------
        Text files containing raw data from the collect function and text files containing averages and std 
        from the average function
        """    
        components = kwargs.get("components" , self.components)
        rep = kwargs.get("repeats" , self.repeats)
        for comp in components:
            input("Press Enter when " + comp + " is ready") 
#This experiment is not automated. If it were, this input statement could be replaced with a line of code to swap the components before measurements are taken.
            for j in range(rep):
                self.collect(filename = self.folder + comp + "\\" + comp + str(j) + ".txt", component = comp)
            self.analysis(component = comp)
    
    def analysis(self, **kwargs):
        """
        Calculates averages and standard deviation for a set of data files in a folder.
        kwargs
        ---------- 
        component : string
        Name of component being investigated. It is default behaviour for this function to attempt calculations in 
        rep: number of repeats to be carried out for each component

        Output
        ------------------
        Text file at chosen location containing columnated data with headings. Data will be means and standard deviations
        for the recorded voltage and 
        
        """           
        component = kwargs.get("component", self.component)
        filename = kwargs.get("filename", self.folder + component + "\\" + component.upper() + "averages.txt")
        data_loc = kwargs.get("filename", self.folder + component)
        with open(filename, "w") as output:
            text_file.write("comp: "+component + " V_range: " +str(s_v)+"-"+str(e_v) +" "+", V_Step: "+ str((e_v-s_v)/(no_-1))+"V, Delay: "+str(self.delay) +" ms\n"+ "Date :" +str(datetime.datetime.now())[:10]+ "\n"+'voltage'+' '+'current'+'\n')
            output.write("avg_voltages"+" "+"std_voltages"+" "+"avg_current"+" "+"std_current\n")
            files = []
            for i in os.listdir(data_loc):
                if component in i:
                    with open(data_loc + "\\" + i) as file:
                        file = file.readlines()
                        for line in range(len(file)):
                            #print("a")
                            if file[line].split()[0] == "Date":
                                file = file[line+2:]
                                #print(file[line+2])
                                files.append(file)
                                break                   
            for i in range(len(files[0])):
                currents = []
                voltages = []
                for j in range(len(files)):
                    currents.append(float(files[j][i].split()[1]))
                    voltages.append(float(files[j][i].split()[0]))
                output.write(str(average(voltages))+" "+str(std(voltages))+" "+str(average(currents)) + " " + str(std(currents))+ "\n")

