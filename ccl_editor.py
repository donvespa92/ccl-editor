import tkinter as tk
import re
from tkinter import ttk
from tkinter import filedialog
from tkinter.font import Font
from tkinter import messagebox
from shutil import copyfile
import pandas as pd
import math
import os

class MainApplication(tk.Frame):
    def __init__(self,master):
        self.font = Font(family="Arial", size=12)
        self.master = master
        self.master.bind('<Escape>',self.cmd_escape)
        self.master.bind('<Control-f>',self.cmd_search)
        self.object_types = ['Domain',
                             'Boundary',
                             'Domain Interface',
                             'Material',
                             'Expressions',
                             'Monitor Point',
                             ]
        self.object_dict = {'Domain':2,
                            'Material':2,
                            'Boundary':4,
                            'Expressions':4,
                            'Domain Interface':2,
                            'Monitor Point':6,
                            }
        self.selected_objects = []
        
        self.gui_set_frames()
        self.gui_set_text()
        self.gui_set_combobox()
        self.gui_set_searchbar()
        self.gui_set_menu()
        self.gui_set_grid()
        
        self.master.config(menu=self.menubar)
        
    def gui_set_frames(self):
        self.mainframe = tk.Frame(self.master)
        self.frame_search = tk.Frame(self.master)
        
    def gui_set_text(self):
        self.text_output = tk.Text(
                self.mainframe,
                height=20,
                width=80,
                wrap='none',
                font='Consolas 11',
                state='disabled')
        self.text_xscrollbar = tk.Scrollbar(self.mainframe)
        self.text_xscrollbar.config(command=self.text_output.xview,orient='horizontal')
        self.text_output.config(xscrollcommand=self.text_xscrollbar.set)
        self.text_yscrollbar = tk.Scrollbar(self.mainframe)
        self.text_yscrollbar.config(command=self.text_output.yview)
        self.text_output.config(yscrollcommand=self.text_yscrollbar.set)
     
    def gui_set_searchbar(self):
        self.entry_searchbar = tk.Entry(self.frame_search,font=self.font,width=50)
     
    def gui_set_combobox(self):
        self.label_object_type = tk.Label(self.mainframe,text='Object type')
        self.cbox_object_type = ttk.Combobox(
                self.mainframe,
                values=self.object_types,
                state='readonly')
        self.label_object_name = tk.Label(self.mainframe,text='Object name')
        self.cbox_object_name = ttk.Combobox(
                self.mainframe,
                values=self.selected_objects,
                state='readonly')
        self.cbox_object_type.bind("<<ComboboxSelected>>", self.cmd_select_object_type)
        self.cbox_object_type.set(self.object_types[0])
        self.cbox_object_name.bind("<<ComboboxSelected>>", self.cmd_select_object_name)
   
    def gui_set_grid(self):
        self.mainframe.pack(fill='both',expand=1,padx=5,pady=5)
        self.mainframe.columnconfigure(1,weight=1)
        self.mainframe.columnconfigure(2,weight=1)
        self.mainframe.rowconfigure(2,weight=1)
        
        self.label_object_type.grid(row=0,column=1,sticky='W')
        self.label_object_name.grid(row=0,column=2,sticky='W')
        self.cbox_object_type.grid(row=1,column=1,sticky='NSEW')
        self.cbox_object_name.grid(row=1,column=2,sticky='NSEW')
        
        self.text_output.grid(row=2,columnspan=2,column=1,sticky='NSEW')
        self.text_xscrollbar.grid(row=3,columnspan=2,column=1,sticky='NSEW')
        self.text_yscrollbar.grid(row=2,column=3,sticky='NSEW')
    
    def gui_set_menu(self):
        self.menubar = tk.Menu(self.master)
        
        self.filemenu = tk.Menu(self.menubar,tearoff=0)
        self.filemenu.add_command(label='Open', command=self.cmd_open_file)
        self.menubar.add_cascade(label='File',menu=self.filemenu)
        
        self.savemenu = tk.Menu(self.filemenu,tearoff=0)
        self.savemenu.add_command(label='Save .ccl')
        self.savemenu.add_command(label='Save .def')
        self.savemenu.add_command(label='Replace .def')
        self.filemenu.add_cascade(label='Save',menu=self.savemenu)
        
        self.editmenu = tk.Menu(self.menubar,tearoff=0)
        self.editmenu.add_command(label='Search', command=self.cmd_search,accelerator="Ctrl+F")
        self.editmenu.add_command(label='Search and Replace', command=self.cmd_open_file)
        self.menubar.add_cascade(label='Edit',menu=self.editmenu)
                    
    def cmd_open_file(self):
        temp = tk.filedialog.askopenfilename(
                title='Choose a .def file',
                filetypes=(              
                        ("CFX Command file", "*.ccl"),
                        ("Solver input file", "*.def"),
                        ("Result file", "*.res"),
                        ("All files", "*.*") ) )
        
        if temp:
            self.inputfile_fullpath = temp
            self.inputfile_name = os.path.basename(self.inputfile_fullpath)
            self.inputfile_dir_name = os.path.dirname(self.inputfile_fullpath)
            self.inputfile_type = os.path.splitext(self.inputfile_fullpath)[1]
            
            self.get_obj_data()
        else:
            return
               
    def get_obj_data(self):
        if os.path.exists('temp.ccl'):
            os.remove('temp.ccl')
        if self.inputfile_type == '.ccl':
            self.get_obj_names(self.inputfile_fullpath)
        else:
            os.system('cfx5dfile -read-cmds %s -output %s' % (self.inputfile_fullpath,'temp.ccl'));
            self.get_obj_names('temp.ccl')
            
    def get_obj_names(self,inputfile):
        self.objects = {}
        self.orig_setup = []
        self.expressions = {}
        with open(inputfile) as fp:
            for line in fp:
                self.orig_setup.append(line.rstrip())
        
        for obj in self.object_dict:
            objects_found = []
            objects_found.append('All')
            if obj == 'Boundary':
                for line in self.orig_setup:
                    if (obj.upper()+':' in line and ' Side ' not in line):
                        objects_found.append(line.split(':')[1].lstrip(' ').rstrip(' '))
            elif obj == 'Expressions':
                temp_data = []
                for idx,line in enumerate(self.orig_setup):
                    if obj.upper()+':' in line:
                        temp_data = self.orig_setup[idx:]
                        break
                for idx,line in enumerate(temp_data):
                    if re.search(r'^\s{%s}END' % self.object_dict[obj],line):
                        temp_data = temp_data[:idx]
                        break
                for line in temp_data:
                    if ' = ' in line:
                        objects_found.append(line.split(' = ')[0].lstrip(' ').rstrip(' '))
            else:
                for line in self.orig_setup:
                    if obj.upper()+':' in line:
                        objects_found.append(line.split(':')[1].lstrip(' ').rstrip(' '))
            self.objects[obj] = objects_found
        return
    
    def cmd_select_object_name(self,event):
        self.selected_object = []
        self.selected_object_data = []
        obj_type = self.cbox_object_type.get()
        obj_name = self.cbox_object_name.get()
        
        temp_data = []
        
        if obj_type == 'Expressions':
            for idx,line in enumerate(self.orig_setup):
                if obj_name in line and ' = ' in line:
                    temp_data = self.orig_setup[idx:]
                    break
            for idx,line in enumerate(temp_data):
                if ' = ' in line and not re.search(r'\\$',line):
                    self.selected_object_data = temp_data[:idx+1]
                    break
                elif ' = ' in line and re.search(r'\\$',line):
                    self.selected_object_data.append(line)
                    temp_data = temp_data[idx+1:]
                    break
            for line in temp_data:
                if ' = ' in line:
                    break
                else:
                    self.selected_object_data.append(line)                 
        elif obj_name == 'All':
            self.selected_object_data = self.get_selected_obj_data(obj_type)
        else:
            for idx,line in enumerate(self.orig_setup):
                if obj_type.upper() in line and obj_name in line:
                    temp_data = self.orig_setup[idx:]
                    break
            for idx,line in enumerate(temp_data):
                if re.search(r'^\s{%s}END' % self.object_dict[obj_type],line):
                    self.selected_object_data = temp_data[:idx+1]
                    break
        
        self.update_text(self.selected_object_data)
    
    def get_selected_obj_data(self,obj_type):
        selected = []
        temp_data = []
        fidx = []
        for idx,line in enumerate(self.orig_setup):
            if obj_type == 'Boundary':
                if re.search(r'(%s:)' % obj_type.upper(),line) and 'Side' not in line:
                    fidx.append(idx)
            else:
                if re.search(r'(%s:)' % obj_type.upper(),line):
                    fidx.append(idx)
                    
        for findex in fidx:
            temp_data = self.orig_setup[findex:]
            for idx,line in enumerate(temp_data): 
                if re.search(r'^\s{%s}END' % self.object_dict[obj_type],line):
                    selected = selected + temp_data[:idx+1]
                    break
        return selected
            
            
    def update_text(self,obj_data):
        self.text_output.config(state='normal')
        self.text_output.delete(1.0,'end')
        for line in obj_data:
            self.text_output.insert('end',line+'\n')
        self.text_output.config(state='disabled')    
    
    def cmd_select_object_type(self,event):
        obj_type = self.cbox_object_type.get()
        self.cbox_object_name.config(values=self.objects[obj_type])
        self.cbox_object_name.set(self.objects[obj_type][0])
        
    
    def cmd_escape(self,event):
        self.frame_search.pack_forget()
        return

    def cmd_search(self,*arg):
        self.frame_search.pack(fill='both',expand=1,padx=5,pady=5)
        self.entry_searchbar.pack(fill='both',expand=1,padx=5,pady=5)
        self.entry_searchbar.focus_set()
        return
    


def main():
    root = tk.Tk()
    root.title('CCL editor')
    MainApplication(root)
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()
   
if __name__ == '__main__':
    main()