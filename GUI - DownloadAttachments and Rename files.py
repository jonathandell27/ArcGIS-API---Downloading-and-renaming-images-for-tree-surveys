import arcgis
import os
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from arcgis.gis import GIS
import shutil
from arcgis.features import FeatureLayerCollection

#GUI
root = Tk()

#List to display the folder location
savenamelist = []

#Defining the export folder
def savefile():
    savepath = filedialog.askdirectory()
    savename = savepath
    if len(savenamelist) < 1 :
        savenamelist.append(savename)
    path3.config(text="{}".format(savenamelist[0]))


def run ():
    print("===========================================================================================================")
    print("Starting Step 1:")
    # Computer user
    username = os.getlogin()
    print("Hello {}! How are you?".format(username))
    print("It's going to take some time. Go have a coffee in the meantime :) ")

    #File location

    currentDirectory = os.getcwd()

    # UserName,password and featureItemID. the featureItemID will be entered by the user
    PortalUrl = "https://www.arcgis.com"
    PortalUserName = "AvivGIS"
    PortalPassword = "JMTB19922019"
    featureItemID = text.get()
    PortalCertVerification = True

    # Connection to the portal and the survey layer
    gis = GIS(PortalUrl, PortalUserName, PortalPassword)

    myonline = gis.content.search(featureItemID)

    myonlinefile = myonline[0]
    attachLayer = myonlinefile.layers[0]

    print("The Layer name is {}".format(myonlinefile.name))
    print("The owner of the layer is: {}".format(myonlinefile.owner))
    print("Step 1 completed successfully - You managed to connect to the layer data")
    print("================================================================================")

    Layerfields = attachLayer.properties.fields

    for field in Layerfields:
        if field.type == 'esriFieldTypeOID':
            FID = field.name
        if field.name == text3.get():
            treenamefield = field.name
        if field.name == text2.get():
            treenumberfield = field.name


    GlobalIDexist = "No"
    for field in Layerfields:
        if field.type == 'esriFieldTypeGlobalID':
            GlobalIDfield = field.name
            GlobalIDexist = "Yes"

    FIDsurveyLayer = []  # List of survey layer ID'S from Objectid field.
    GlobalID = []  # List of GlobalID'S field. Each point has an ID value that also appears in the attachments information
    treenames = []  # List of trees names
    treenumbers = []  # list of tress numbers

    Layerquery = attachLayer.query()

    Layerfeatures = Layerquery.features

    for a in Layerfeatures:
        attributes = a.attributes
        FIDsurveyLayer.append(attributes.get('{}'.format(FID)))
        treenames.append(attributes.get('{}'.format(treenamefield)))
        treenumbers.append(attributes.get('{}'.format(treenumberfield)))
        if GlobalIDexist == "Yes":
            GlobalID.append(attributes.get('{}'.format(GlobalIDfield)))
        else:
            GlobalID = FIDsurveyLayer

    if len(FIDsurveyLayer) == len(GlobalID) == len(treenames) == len(treenumbers):
        print("Good! The number of the rows in the table is {}".format(len(FIDsurveyLayer)))
    else:
        print("Ohh no, There is a problem in the table. The process has stopped")
        exit()

    print("Step 2 completed successfully - You typed the column names correctly")

    print("================================================================================")

    print("Starting Step 3:")

    photonamelist = []  # List of the photo files name from the attachments information
    parentGlobalIdlist = []  # List of the parentGlobalId from the attachments information. All parentGlobalId values are appears in GlobalID list
    attachmentsid = []  # List of the photo ID'S. These ID's are different from the survey layer ID'S and we need them for the photos downlowd step.
    surveyLayerFID = []  # a new list of the survey layer that contains only the ID's that they have an Photos.
    phototreename = []  # from the new survey layer ID's , this list contains only the trees names
    treenumbers2 = []  # from the new survey layer ID's , this list contains only the trees numbers

    FIDwithphoto = []
    FIDwithoutphoto = []

    for i in FIDsurveyLayer:
        a = attachLayer.attachments.get_list(i)
        if not a:
            FIDwithoutphoto.append(i)
        else:
            FIDwithphoto.append(i)
            for dic in a:
                if GlobalIDexist == "Yes":
                    parentGlobalId = dic.get("parentGlobalId")
                else:
                    parentGlobalId = dic.get("parentObjectId")
                photoname = dic.get("name")
                photoid = dic.get("id")
                parentGlobalIdlist.append(parentGlobalId)
                photonamelist.append(photoname)
                attachmentsid.append(photoid)

    print("Number of points without attachment: {}".format(len(FIDwithoutphoto)))
    print("Number of points with attached image: {}".format(len(FIDwithphoto)))

    def rename(x):
        Invalidtext = [",", ")", "(", "!", "?", "%", "#", "@", "<", ">", "=", "*", "/", "'", ":", ";"]
        Invalidtextcount = []
        if x == None:
            return "None"
        for s in x:
            if s in Invalidtext:
                Invalidtextcount.append(s)

        if len(Invalidtextcount) > 0:
            return x[0:x.find(Invalidtextcount[0])]

        elif len(x) > 15:
            return "{}".format(x[0:14])
        else:
            return x

    for i in parentGlobalIdlist:
        if i in GlobalID:
            surveyLayerFID.append(FIDsurveyLayer[GlobalID.index(i)])
            phototreename.append(treenames[GlobalID.index(i)])
            treenumbers2.append(treenumbers[GlobalID.index(i)])

    print("Starting downloading the photos:")
    for i in range(0, len(surveyLayerFID)):
        OID = surveyLayerFID[i]
        ATTACHMENT_ID = attachmentsid[i]
        PHOTONAME = photonamelist[i]
        treename = phototreename[i]
        treenumber = treenumbers2[i]
        FIDfolder = r"{}\{}".format(savenamelist[0], OID)

        if not os.path.isdir(FIDfolder):
            os.mkdir(FIDfolder)

        myDownload = attachLayer.attachments.download(oid=OID, attachment_id=ATTACHMENT_ID, save_path=FIDfolder)

        print("Downloaded: {}".format(PHOTONAME))

        os.rename("{}\{}".format(FIDfolder, PHOTONAME),"{}\FID{}-photoID{}-Number{}-{}.jpg".format(FIDfolder, OID, ATTACHMENT_ID, treenumber , rename(treename)))

        print("Rename to : FID{}-photoID{}-Number{}-{}.jpg".format(OID, ATTACHMENT_ID, treenumber, rename(treename)))

        endtxt.config(text="The process was completed successfully!")

    print("Step 3 completed successfully - The images were downloaded from the web and renamed successfully")

    print("The process was completed successfully!")


root.title("סקר עצים - הורדת תמונות")
root.geometry('600x600')
button3 = Button(root, text="Output Folder Location",bg='#0052cc', fg='#ffffff',height = 2, width = 20,font = ('Sans','10','bold'),padx = 80, command  =savefile)
path3 = Label(root, text="")
button4 = Button(root, text="Run",bg='#0052cc', fg='#ffffff',height = 2, width = 20,padx = 80,font = ('Sans','10','bold'), command  =run)
filename = StringVar()
text = Entry(root, textvariable = filename)
textlable = Label(root,text="Input the ID of the layer",height = 2, width = 20,padx = 80,font = ('Sans','10','bold'))
filename2 = StringVar()
text2 = Entry(root, textvariable = filename2)
textlable2 = Label(root,text="Input the field name of the Tree numbers",height = 2, width = 20,padx = 80,font = ('Sans','10','bold'))
filename3 = StringVar()
text3 = Entry(root, textvariable = filename3)
textlable3= Label(root,text="Input the field name of the Tree names",height = 2, width = 20,padx = 80,font = ('Sans','10','bold'))

button3.place(x=150, y=50)
path3.place(x=50, y=100,height = 20, width = 500)
textlable.place(x=150, y=150)
text.place(x=230, y=200, height = 20, width = 150)
textlable2.place(x=150, y=250)
text2.place(x=230, y=300, height = 20, width = 150)
textlable3.place(x=150, y=350)
text3.place(x=230, y=400, height = 20, width = 150)
button4.place(x=150, y=450)
endtxt = Label(root, text="",height = 2, width = 20,padx = 80,font = ('Sans','10','bold'))
endtxt.place(x=100, y=500)

root.mainloop()




#======================================================================================================
