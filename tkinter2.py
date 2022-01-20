#!/usr/bin/env python
# coding: utf-8

# In[34]:


from tkinter import *
from tkinter import ttk
import sys
import subprocess
from subprocess import call
#from ttkthemes import ThemedTk


# In[35]:


class Volume:
  def __init__(self,Name,Driver,Type,O,Device):
    self.name = Name+":"
    self.driver = Driver
    self.type = Type
    self.o = O
    self.device = Device

  
  def Affichage(self):
    print(" ",self.name)
    print("    driver:",self.driver)
    print("    driver_opts:")
    print("      type:",self.type)
    print("      o:",self.o)
    print("      device:", self.device,'\n')


# In[36]:


class service:
  def __init__(self,Name,Build,Image,Environment,Volumes):
    self.name = Name+":"
    self.build = Build
    self.image = Image
    self.environment = Environment
    self.restart = "restart: always"
    self.volumes = Volumes
  
  
  def Affichage(self):
    print(" ",self.name)
    print("    build:",self.build)
    print("    image:",self.image)
    if (len(self.environment)==1):
        print("    environment:\n     -",self.environment[0])
    if (len(self.environment)>1):
        print("    environment:")
        for i in range (0,len(self.environment)):
            print("     -",self.environment[i])
    print("   ", self.restart)
    if (self.volumes != "0"):
      print("    volumes:\n     -" ,self.volumes)
    print("\n")
  


# In[ ]:





# In[37]:


def goNext():
    
    print("\nNombre de Consommateur :",consoNb.get(),
          "\nNombre de Generateur :",geneNb.get())
    
    #variable
    count_conso= consoNb.get()
    count_gene= geneNb.get()
    conso = IntVar
    tabGeneratorPower= []
    tabCaptorVolumeDevice = []
    

        #scroll bar
    main_frame = Frame(window)
    #main_frame.pack(fill=BOTH, expand=1)
    my_canva = Canvas(main_frame,bg = colorBg)
    #my_canva.pack(side=LEFT, fill=BOTH, expand=1)
    scroll = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canva.yview )
    #scroll.pack(side=RIGHT, fill=Y)
    my_canva.configure(yscrollcommand=scroll.set)
    my_canva.bind('<Configure>', lambda e: my_canva.configure(scrollregion= my_canva.bbox("all")))
    frameInfo = Frame(my_canva,bg = colorBg)
    my_canva.create_window((240,0), window=frameInfo, anchor="nw")
    scroll.grid(column=1, row=0, sticky="nw")

    count=0   
    label = Label(window, text='Create Consumer', bg = colorBg, pady = 15, font = ("Verdana",14)).grid(row=0, column=2) 
    for i in range (0, consoNb.get()):
        labelNetwork = Label(window, text='Consumption'+str(i+1)+' :', bg = colorLabel, font =("Verdana",12),pady =8,padx=8).grid(row=i+1, column=1) 
        entryNetwork = Entry(window)
        entryNetwork.grid(row=i+1, column=2) 
        list_conso.append(entryNetwork)
        count+=1
    
    count=0  
    label = Label(window, text='Create Generator', bg = colorBg, pady = 15, font = ("Verdana",14)).grid(row=0, column=4)
    for i in range (0, geneNb.get()):
       labelNetwork1 = Label(window, text='Power :', bg = colorLabel, font =("Verdana",12),pady =8,padx=8).grid(row=1+count, column=3)
       entryNetwork1 = Entry(window)
       entryNetwork1.grid(row=1+count, column=4)
       list_power.append(entryNetwork1)

       labelNetwork2 = Label(window, text='Repertory to stock data :', bg = colorLabel, font =("Verdana",12),pady =8,padx=8).grid(row=2+count, column=3)
       entryNetwork2 = Entry(window)
       entryNetwork2.grid(row=2+count, column=4)
       list_stock.append(entryNetwork2)
       count+=2
       
    print(count)
    button = Button(window, text="Validate these settings", bg = colorButton, font =("Verdana",10), command=lambda:[consum(),window2()] ).grid(row=count+10, column=3)


# In[38]:


def consum():
    listC=''
    listP=''
    listS=''
    for i in list_conso:
        listC = listC + str(i.get())
    print("conso:"+listC)

    for i in list_power:
        listP = listP + str(i.get())
    print("power:"+listP)

    for i in list_stock:
        listS = listS + str(i.get())
    print("stock:"+listS)
    
    tabVolume= []
    tabService = []
    countConso,countGene,countCaptor =1,1,1
    print("taille de la liste : ", len(listS))
#consommateur
    nbConso = len(listC)
    for i in range (0, len(listC)):
        name = "server-conso"+str(countConso)
        build = "docker-server-minimal_consommateur/."
        image = "server-conso"+str(countConso)
        env = ["CONSO= "+listC[i]]
        env.append("COUNT= "+str(countConso))
        vol = "0"
        conso= service(name, build,image,env,vol)
        tabService.append(conso)
        countConso += 1
#generateur
    nbGene = len(listP)
    for i in range (0, len(listP)):
        name = "server-gene"+str(countGene)
        build = "docker-server-minimal_generateur/v0.1.0/."
        image = "server-gene"+str(countGene)
        env = ["GENE= "+ listP[i]]
        env.append("COUNT= "+str(countGene))
        vol = "0"
        gene= service(name, build,image,env,vol)
        tabService.append(gene)
        countGene +=1

#captor    
    nbCaptor = len(listP)
    for i in range (0, len(listP)):
        name = "client_captor"+str(countCaptor)
        build = "docker-client-minimal_captor/v0.0.1/."
        image = "client-captor"+str(countCaptor)
        env = ["COUNT= "+ str(countCaptor)]
        vol = "volume"+str(countCaptor)
        nameVol = "volume"+str(countCaptor)
        driver = "local"
        typeNet = "none"
        o = "bind"
        device = '"C:/Users/gesli/OneDrive/Documents/ing5/pfe/data "'
        captor= service(name,build,image,env,vol)
        tabService.append(captor)
        vol = Volume(nameVol,driver,typeNet,o,device)
        tabVolume.append(vol)
        countCaptor +=1

#scada 
    nbScada = 1
    for i in range (1, int(nbScada)+1):
        name = "client_scada"+str(i)
        build = "docker-client-minimal_scada/v0.0.1/."
        image = "client-scada"+str(i)
        env = ["COUNT= "+str(i)]
        vol = "0"
        captor= service(name, build,image,env,vol)
        tabService.append(captor)  
    AffichageGlobale(tabService,tabVolume)


# In[39]:


def window2():
    close_window()
    subprocess.call("docker-compose up -d", shell= True)
    window2 = Tk()
    window2.geometry("720x480")
    window2.title("Docker-Compose Generator2")
    label = Label(window2, text='Docker-Compose Generator', bg = colorBg, foreground='#777', pady = 15, font = ("Verdana",14)).grid(row=0, column=1)
    window2['bg']= colorBg
    window2.mainloop()


# In[40]:


def AffichageGlobale(tabService,tabVolume):
    stdoutOrigin=sys.stdout 
    sys.stdout = open("docker-compose.yml", "w")
    print("version: '3'\n\nservices:")
    for i in range (0, len(tabService)):
        tabService[i].Affichage()
    print("volumes:")
    for i in range (0, len(tabVolume)):
        tabVolume[i].Affichage()
    sys.stdout.close()
    sys.stdout=stdoutOrigin
    
    
def print_docker(tabConsumption):    
    for i in range (0, len(tabConsumption)):
        print(tabConsumption)
        
def close_window():
    window.destroy()  

def clear():
    list = window.grid_slaves()
    for l in list:
        l.destroy()
   


# In[42]:



#color
colorBg='#F4FEFE'
colorLabel ="#F4FEFE"
colorButton = "#F4FEFE"



#init
window = Tk()
#window = ThemedTk(theme='adapta')
#print(root.get_themes())

window.geometry("720x480")
#window.resizable(height=True,width=True)
window.title("Docker-Compose Generator")
label = Label(window, text='Docker-Compose Generator', bg = colorBg, foreground='#777', pady = 15, font = ("Verdana",14)).grid(row=0, column=1)
window['bg']= colorBg

#Variable
consoNb = IntVar()
geneNb = IntVar()
list_conso = []
list_power = []
list_stock = []

#Frame
#frame = Frame(window, bg = colorBg)
labelConso = Label(window, text='Number of Consumers :', bg = colorLabel, foreground='#777', font =("Verdana",12),pady =8,padx=8).grid(row=1, column=0)
entryConso = Entry(window, textvariable= consoNb).grid(row=1, column=1 ,pady =8,padx=8)
labelGene = Label(window, text='Number of Generators :', bg = colorLabel, foreground='#777', font =("Verdana",12),pady =8,padx=8).grid(row=2, column=0)
entryGene = Entry(window, textvariable= geneNb).grid(row=2, column=1,pady =8,padx=8)
button = Button(window, text="Validate these settings", bg = colorButton, foreground='#777', font =("Verdana",10), padx =7, command=lambda:[clear(),goNext()]).grid(row=3, column=1)
#frame.pack()
#lambda:[window.pack_forget(),


#window.mainloop()
window.mainloop()


# In[ ]:




