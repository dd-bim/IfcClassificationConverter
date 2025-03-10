from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from ConvertToPropertySet import convert_to_property_set
from ConvertToClassification import convert_to_classification
import ifcopenshell

root = Tk()
root.title("IfcClassificationConverter")
root.geometry("365x220")
root.iconbitmap('logo.ico')

filename = ""
model = None

def getFile():
    global filename
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("IFC files", "*.ifc"), ("All Files", "*.*")))
    filePathMess.insert(0, filename)
    

def truncate_text(text, length):
    if len(text) > length:
        return text[:length-3] + "..."
    return text


filler = Label(root, text = " ", font=('Calibri', 12, 'bold'), width=4)
filler.grid(column=0, row=0)

methodLabel = Label(root, text = "Direction:", font=('Calibri', 12, 'bold'))
methodLabel.grid(column=1, row=1, sticky='w')

method = StringVar(root, "1")
r1 = Radiobutton(root, text = "IfcPropertySet to IfcClassification", value = 1, variable = method)
r1.grid(column = 1, row = 2, columnspan=2, sticky='w')
r2 = Radiobutton(root, text = "IfcClassification to IfcPropertySet", value = 2, variable = method)
r2.grid(column = 1, row = 3, columnspan=2, sticky='w')

filler2 = Label(root, text = " ", font=('Calibri', 12, 'bold'), width=3)
filler2.grid(column=0, row=4)


pSetLabel = Label(root, text = "File:", font=('Calibri', 12, 'bold'))
pSetLabel.grid(column=1, row=4, sticky='w')
filePathMess = Entry(root, width=22)
filePathMess.grid(column=2, row=4, columnspan=2, sticky='w')

btnFile = Button(root, text = "..." , command=getFile, width=4)
btnFile.grid(column=3, row=4, sticky='e')

pSetLabel = Label(root, text = "Pset Name:", font=('Calibri', 12, 'bold'))
pSetLabel.grid(column=1, row=5, sticky='w')

pSetName = Entry(root, width=22)
pSetName.grid(column =2, row =5, columnspan=2 ,sticky='w')
pSetName.insert(0, "bS_PSet_OkBKdV")

# values = []
# def loadFile():
#     global model
#     model = ifcopenshell.open(filename)
#     print(model.schema)
#     global values
#     values = model.by_type("IfcPropertySet")
#     print(values)

# btnLoad = Button(root, text = "Load" , command=loadFile, width=4)
# btnLoad.grid(column=3, row=5, sticky='e')

# pSetName = ttk.Combobox(root, width=18, values=values)
# pSetName.grid(column =2, row =5, columnspan=2 ,sticky='w')
# pSetName.insert(0, "bS_PSet_OkBKdV")

test = Message(root, text = " ", width=200)
test.grid(column=1, row=7, columnspan=3, rowspan=2, sticky='w')


def clicked():
    returnMessage = ""
    if method.get() == "1":
        returnMessage = convert_to_classification(filename, pSetName.get())
    else:
        returnMessage = convert_to_property_set(filename, pSetName.get())
    test.configure(text = returnMessage)
    
    
btnConvert = Button(root, text = "Convert" , command=clicked, width=10)
btnConvert.grid(column=2, row=9)
close = Button(root, text = "Close" , command=root.destroy, width=10)
close.grid(column=3, row=9)


root.mainloop()