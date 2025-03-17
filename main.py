from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from ConvertToPropertySet import convert_to_property_set
from ConvertToClassification import convert_to_classification
import ifcopenshell
import os

root = Tk()
root.title("IfcClassificationConverter")
root.geometry("395x285")
icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
root.iconbitmap(icon_path)

filename = ""
model = None


def getFile():
    global filename
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select a File",
        filetypes=(("IFC files", "*.ifc"), ("All Files", "*.*")),
    )
    filePathMess.delete(0, END)
    filePathMess.insert(0, filename)
    global model
    model = ifcopenshell.open(filename)
    values = model.by_type("IfcPropertySet")
    valNames = [v.Name for v in values]
    pSetNameListbox.delete(0, END)
    for name in valNames:
        pSetNameListbox.insert(END, name)


# General section
pSetLabel = Label(root, text="File:", font=("Calibri", 12, "bold"))
pSetLabel.grid(column=0, row=0, sticky="w", padx=10, pady=10)
filePathMess = Entry(root, width=50)
filePathMess.grid(column=0, row=1, columnspan=4, sticky="w", padx=10)

btnFile = Button(root, text="...", command=getFile, width=4)
btnFile.grid(column=4, row=1, sticky="e", padx=10)

# Create Tabs
notebook = ttk.Notebook(root)
notebook.grid(column=0, row=3, columnspan=5, rowspan=6, sticky="nsew", padx=10, pady=10)

tab1 = Frame(notebook)
tab2 = Frame(notebook)

notebook.add(tab1, text="IfcPropertySet to IfcClassification")
notebook.add(tab2, text="IfcClassification to IfcPropertySet")

# Tab IfcPropertySet to IfcClassification
pSetNameListbox = Listbox(tab1, selectmode=MULTIPLE, height=5, width=29)
pSetNameListbox.grid(column=1, row=6, columnspan=2, sticky="w", padx=(0, 8))

pSetName = Entry(tab1, width=30, state=DISABLED)
pSetName.grid(column=3, row=6, columnspan=2, sticky="nw")


# Update state of widgets
def update_input_method_tab1():
    if input_method_tab1.get() == "listbox":
        pSetNameListbox.config(state=NORMAL)
        pSetName.config(state=DISABLED)
    else:
        pSetNameListbox.config(state=DISABLED)
        pSetName.config(state=NORMAL)


input_method_tab1 = StringVar(tab1, "listbox")
rb_listbox = Radiobutton(
    tab1,
    text="Select Psets from file",
    value="listbox",
    variable=input_method_tab1,
    command=update_input_method_tab1,
)
rb_listbox.grid(column=1, row=5, columnspan=2, sticky="w", padx=(0, 10))
rb_entry = Radiobutton(
    tab1,
    text="Enter Pset name",
    value="entry",
    variable=input_method_tab1,
    command=update_input_method_tab1,
)
rb_entry.grid(column=3, row=5, columnspan=2, sticky="w")

# Tab IfcClassification to IfcPropertySet
pSetName2 = Entry(tab2, width=30, state=DISABLED)
pSetName2.grid(column=3, row=6, columnspan=2, sticky="nw")


# Update state of widgets
def update_input_method_tab2():
    if input_method_tab2.get() == "generate":
        pSetName2.config(state=DISABLED)
    else:
        pSetName2.config(state=NORMAL)


input_method_tab2 = StringVar(tab2, "generate")
pSetName.update_idletasks()
w = pSetName.winfo_width()
rb_generate = Radiobutton(
    tab2,
    text="Generate Pset names by URI \n\n(Important! bSDD URI in IfcClassificationReference Identifier must be set)",
    wraplength=165,
    value="generate",
    variable=input_method_tab2,
    command=update_input_method_tab2,
    justify=LEFT,
    anchor="w",
)
rb_generate.grid(column=1, row=5, columnspan=2, rowspan=5, sticky="nw", padx=(0, 8))
rb_entry2 = Radiobutton(
    tab2,
    text="Enter Pset name",
    value="entry",
    variable=input_method_tab2,
    command=update_input_method_tab2,
)
rb_entry2.grid(column=3, row=5, columnspan=2, sticky="nw")


# get selected pset names from tab1 or tab2
def get_selected_pset_names():
    selected_names = []
    selected_tab = notebook.index(notebook.select())
    if selected_tab == 0:
        if input_method_tab1.get() == "listbox":
            selected_indices = pSetNameListbox.curselection()
            selected_names = [pSetNameListbox.get(i) for i in selected_indices]
        else:
            selected_names = [pSetName.get()]
    else:
        if input_method_tab2.get() == "generate":
            selected_names = "GenerateNames"
        else:
            selected_names = pSetName2.get()
    return selected_names


message = Message(root, text=" ", width=380)
message.grid(column=0, row=12, columnspan=4, sticky="w")


# Start conversion process
def clicked():
    returnMessage = ""
    selected_tab = notebook.index(notebook.select())
    pset_names = get_selected_pset_names()
    if selected_tab == 0:
        returnMessage = convert_to_classification(filename, model, pset_names)
    else:
        returnMessage = convert_to_property_set(filename, model, pset_names)
    message.configure(text=returnMessage)


btnConvert = Button(root, text="Convert", command=clicked, width=10)
btnConvert.grid(column=2, row=13, padx=10)
close = Button(root, text="Close", command=root.destroy, width=10)
close.grid(column=3, row=13, padx=10)

root.mainloop()
