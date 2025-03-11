from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from ConvertToPropertySet import convert_to_property_set
from ConvertToClassification import convert_to_classification
import ifcopenshell
import os

root = Tk()
root.title("IfcClassificationConverter")
root.geometry("425x280")
icon_path = os.path.join(os.path.dirname(__file__), 'logo.ico')
root.iconbitmap(icon_path)

filename = ""
model = None

def getFile():
    global filename
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("IFC files", "*.ifc"), ("All Files", "*.*")))
    filePathMess.insert(0, filename)
    global model
    model = ifcopenshell.open(filename)
    values = model.by_type("IfcPropertySet")
    valNames = [v.Name for v in values]
    pSetNameListbox.delete(0, END)
    for name in valNames:
        pSetNameListbox.insert(END, name)

# General section
pSetLabel = Label(root, text = "File:", font=('Calibri', 12, 'bold'))
pSetLabel.grid(column=0, row=0, sticky='w', padx=10, pady=10)
filePathMess = Entry(root, width=50)
filePathMess.grid(column=0, row=1, columnspan=4, sticky='w', padx=10)

btnFile = Button(root, text = "..." , command=getFile, width=4)
btnFile.grid(column=4, row=1, sticky='e', padx=10)

# Create Tabs
notebook = ttk.Notebook(root)
notebook.grid(column=0, row=3, columnspan=5, rowspan=6, sticky='nsew', padx=10, pady=10)

tab1 = Frame(notebook)
tab2 = Frame(notebook)

notebook.add(tab1, text="IfcPropertySet to IfcClassification")
notebook.add(tab2, text="IfcClassification to IfcPropertySet")

# Tab 1
pSetNameListbox = Listbox(tab1, selectmode=MULTIPLE, height=5, width=30)
pSetNameListbox.grid(column=1, row=6, columnspan=2, sticky='w')

pSetName = Entry(tab1, width=30, state=DISABLED)
pSetName.grid(column =3, row =6, columnspan=2 ,sticky='nw')
pSetName.insert(0, "bS_PSet_OkBKdV")

# Funktion zum Aktualisieren des Zustands der Widgets
def update_input_method():
    if input_method.get() == "listbox":
        pSetNameListbox.config(state=NORMAL)
        pSetName.config(state=DISABLED)
    else:
        pSetNameListbox.config(state=DISABLED)
        pSetName.config(state=NORMAL)

input_method = StringVar(tab1, "listbox")
rb_listbox = Radiobutton(tab1, text="Select Pset names from file", value="listbox", variable=input_method, command=update_input_method)
rb_listbox.grid(column=1, row=5, columnspan=2, sticky='w')
rb_entry = Radiobutton(tab1, text="Enter Pset name", value="entry", variable=input_method, command=update_input_method)
rb_entry.grid(column=3, row=5, columnspan=2, sticky='w')

def get_selected_pset_names():
    selected_names = []
    if input_method.get() == "listbox":
        selected_indices = pSetNameListbox.curselection()
        selected_names = [pSetNameListbox.get(i) for i in selected_indices]
    else:
        selected_names =[pSetName.get()]
    return selected_names

test = Message(root, text = " ", width=200)
test.grid(column=0, row=87, columnspan=3, rowspan=2, sticky='w')


def clicked():
    returnMessage = ""
    selected_tab = notebook.index(notebook.select())
    if selected_tab == 0:
        pset_names = get_selected_pset_names()
        returnMessage = convert_to_classification(filename, model, pset_names)
    else:
        # TODO
        returnMessage = convert_to_property_set(filename, model, pSetName.get())
    test.configure(text = returnMessage)
    

btnConvert = Button(root, text = "Convert" , command=clicked, width=10)
btnConvert.grid(column=2, row=9)
close = Button(root, text = "Close" , command=root.destroy, width=10)
close.grid(column=3, row=9)


root.mainloop()