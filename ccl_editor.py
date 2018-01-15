import tkinter as tk
import re
from tkinter import ttk
from tkinter import filedialog
from tkinter.font import Font
from tkinter import messagebox
from tkinter import simpledialog
import shutil
from shutil import copyfile
import math
import os

class MainApplication(tk.Frame):
    def __init__(self,master):
        self.font = Font(family="Arial", size=12)
        self.master = master
        self.master.bind('<Escape>',self.cmd_escape)
        self.master.bind('<Control-f>',self.cmd_search)
        self.object_types = []
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
                font='Consolas 11')
        self.text_xscrollbar = tk.Scrollbar(self.mainframe)
        self.text_xscrollbar.config(command=self.text_output.xview,orient='horizontal')
        self.text_output.config(xscrollcommand=self.text_xscrollbar.set)
        self.text_yscrollbar = tk.Scrollbar(self.mainframe)
        self.text_yscrollbar.config(command=self.text_output.yview)
        self.text_output.config(yscrollcommand=self.text_yscrollbar.set)
     
    def gui_set_searchbar(self):
        self.label_searchbar = tk.Label(self.frame_search,text='Search')
        self.entry_searchbar = tk.Entry(self.frame_search,width=50)
        self.entry_searchbar.bind("<KeyRelease>", self.search_text)
        self.entry_searchbar.bind("<Return>", self.search_next)
        
        self.var_replace = tk.IntVar()
        self.checkbutton_replace = tk.Checkbutton(
                self.frame_search,
                text='Replace',
                command=self.cmd_replace,
                variable=self.var_replace)
        
        self.label_replace = tk.Label(self.frame_search,text='Replace')
        self.entry_replace = tk.Entry(self.frame_search,width=50,state='disabled')
        self.entry_replace.bind("<Return>", self.replace_string)
    
    def gui_set_combobox(self):
        self.label_object_type = tk.Label(self.mainframe,text='Object type')
        self.cbox_object_type = ttk.Combobox(
                self.mainframe,
                values=self.object_types,
                state='disabled')
        self.label_object_name = tk.Label(self.mainframe,text='Object name')
        self.cbox_object_name = ttk.Combobox(
                self.mainframe,
                values=self.selected_objects,
                state='disabled')
        self.cbox_object_type.bind("<<ComboboxSelected>>", self.cmd_select_object_type)
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
        self.savemenu.add_command(label='Save .ccl',command=self.cmd_save_ccl)
        self.savemenu.add_command(label='Save .def',command=self.cmd_copy_def)
        self.savemenu.add_command(label='Replace .def',command=self.cmd_overwrite_def)
        self.filemenu.add_cascade(label='Save',menu=self.savemenu)
        
        self.editmenu = tk.Menu(self.menubar,tearoff=0)
        self.editmenu.add_command(label='Search', command=self.cmd_search,accelerator="Ctrl+F")
        self.menubar.add_cascade(label='Edit',menu=self.editmenu)
        
        self.filemenu.entryconfig('Save',state='disabled')
        self.menubar.entryconfig('Edit',state='disabled')
                    
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
            self.filemenu.entryconfig('Save',state='normal')
            self.menubar.entryconfig('Edit',state='normal')
        else:
            return
               
    def cmd_save_ccl(self):
        self.outputfile = filedialog.asksaveasfilename(parent=self.master,
                                    initialdir=self.inputfile_dir_name,
                                    title="Selet a file for export",
                                    filetypes=[('All files', '.*')]) 
    
        if self.outputfile:
            file = open(self.outputfile,'w')
            for line in self.new_setup:
                file.write('%s\n' % line)
            file.close()
        else:
            return
    
    def cmd_overwrite_def(self):
        result = tk.messagebox.askokcancel('Warning','This will overwrite the original .def file!\nMake sure your modifications are consistent!')
        
        if self.inputfile_fullpath and result == 'yes':
            file = open('temp.ccl','w')
            for line in self.new_setup:
                file.write('%s\n' % line)
            file.close()
                
            os.system('cfx5cmds -write -definition %s -text %s' % (self.inputfile_fullpath,'temp.ccl'))
            os.remove('temp.ccl')
        else:
            return
        
    def cmd_copy_def(self):
        self.outputfile = filedialog.asksaveasfilename(parent=self.master,
                                    initialdir=self.inputfile_dir_name,
                                    title="Selet a .def file to overwrite",
                                    filetypes=[('Solver input files', '*.def'),
                                               ('All files', '.*')]) 

        if self.outputfile:
            file = open('temp.ccl','w')
            for line in self.new_setup:
                file.write('%s\n' % line)
            file.close()
            
            shutil.copyfile(self.inputfile_fullpath,self.outputfile)
            os.system('cfx5cmds -write -def %s -ccl %s' % (self.outputfile,'temp.ccl'))
            os.remove('temp.ccl')
        else:
            return
    
    def get_obj_data(self):
        self.cbox_object_name.config(state='readonly')
        self.cbox_object_type.config(state='readonly')
        if os.path.exists('temp.ccl'):
            os.remove('temp.ccl')
        if self.inputfile_type == '.ccl':
            self.get_obj_names(self.inputfile_fullpath)
        else:
            os.system('cfx5dfile -read-cmds %s -output %s' % (self.inputfile_fullpath,'temp.ccl'));
            self.get_obj_names('temp.ccl')
            
    def get_obj_names(self,inputfile):
        self.objects = {}
        self.object_types = ['All']
        self.orig_setup = []
        self.expressions = {}
        with open(inputfile) as fp:
            for line in fp:
                self.orig_setup.append(line.rstrip())
        self.new_setup = self.orig_setup
        for obj in self.object_dict:
            objects_found = []
            objects_found.append('All')
            if obj == 'Boundary':
                for line in self.orig_setup:
                    if (obj.upper()+':' in line):
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
            if len(objects_found) != 1:
                self.object_types.append(obj)
        
        self.cbox_object_type.config(values=self.object_types)
        return
    
    def cmd_select_object_name(self,event):
        self.text_output.delete(1.0,'end')        
        self.cbox_object_name.config(state='readonly')
        self.selected_object = []
        self.selected_object_data = []
        obj_type = self.cbox_object_type.get()
        obj_name = self.cbox_object_name.get()
        
        self.fidx = 0
        self.lidx = 0
        temp_data = []
        if obj_type == 'Expressions':
            if obj_name == 'All':
                for idx,line in enumerate(self.orig_setup):
                    if obj_type.upper()+':' in line:
                        temp_data = self.orig_setup[idx:]
                        self.fidx = idx
                        break
                for idx,line in enumerate(temp_data):
                    if re.search(r'^\s{%s}END' % self.object_dict[obj_type],line):
                        self.selected_object_data = temp_data[:idx+1]
                        self.lidx = idx
                        break
            else:
                for idx,line in enumerate(self.orig_setup):
                    if obj_name in line and ' = ' in line:
                        temp_data = self.orig_setup[idx:]
                        self.fidx = idx
                        break
                for idx,line in enumerate(temp_data):
                    if ' = ' in line and not re.search(r'\\$',line):
                        self.selected_object_data = temp_data[:idx+1]
                        self.fidx = idx
                        self.lidx = idx
                        break
                    elif ' = ' in line and re.search(r'\\$',line):
                        self.selected_object_data.append(line)
                        temp_data = temp_data[idx+1:]
                        self.fidx = idx
                        break
                if temp_data:
                    for idx,line in enumerate(temp_data):
                        if ' = ' in line:
                            self.lidx = idx
                            break
                        else:
                            self.selected_object_data.append(line)                 
        elif obj_name == 'All':
            self.selected_object_data = self.get_selected_obj_data(obj_type)    
        else:
            for idx,line in enumerate(self.orig_setup):
                if obj_type.upper() in line and obj_name in line:
                    temp_data = self.orig_setup[idx:]
                    self.fidx = idx
                    break
            for idx,line in enumerate(temp_data):
                if re.search(r'^\s{%s}END' % self.object_dict[obj_type],line):
                    self.selected_object_data = temp_data[:idx+1]
                    self.lidx = idx
                    break
        
        self.update_text(self.selected_object_data)
        
#        self.highlight_block(obj_type,
#                             obj_type.upper()+':',
#                             self.object_dict[obj_type],
#                             'red')

#        self.highlight_block('dom','DOMAIN:',2,'red')
#        self.highlight_block('bnd','BOUNDARY:',4,'blue')   
#        self.highlight_block('if','DOMAIN INTERFACE:',2,'green')
        blk_indices = self.get_indices('Domain')
        self.highlight_names_2('Domain',blk_indices,'red')
        blk_indices = self.get_indices('Boundary')
        self.highlight_names_2('Boundary',blk_indices,'blue')

        
    def get_selected_obj_data(self,obj_type):
        selected = []
        temp_data = []
        fidx = []
        lidx = []
        for idx,line in enumerate(self.orig_setup):
            if obj_type == 'Boundary':
                if re.search(r'(%s:)' % obj_type.upper(),line) and 'Side' not in line:
                    fidx.append(idx)
            else:
                if re.search(r'(%s:)' % obj_type.upper(),line):
                    fidx.append(idx)
        
        self.fidx = fidx[0]         
        for findex in fidx:
            temp_data = self.orig_setup[findex:]
            for idx,line in enumerate(temp_data): 
                if re.search(r'^\s{%s}END' % self.object_dict[obj_type],line):
                    selected = selected + temp_data[:idx+1]
                    lidx.append(idx)
                    break
        self.lidx = lidx[-1]
        return selected
            
            
    def update_text(self,obj_data):
        self.text_output.delete(1.0,'end')
        for line in obj_data:
            self.text_output.insert('end',line+'\n')
        self.selected_object_data = obj_data
    
    def cmd_select_object_type(self,event):
        self.text_output.delete(1.0,'end')
        obj_type = self.cbox_object_type.get()
        if obj_type == 'All':
            self.cbox_object_name.config(state='disabled')
            self.update_text(self.new_setup)
#            self.highlight_block('dom','DOMAIN:',2,'red')
#            self.highlight_block('bnd','BOUNDARY:',4,'blue')   
#            self.highlight_block('if','DOMAIN INTERFACE:',2,'green')
#            self.highlight_names_2()
        else:
            self.cbox_object_name.config(state='readonly')
            self.cbox_object_name.config(values=self.objects[obj_type])
            self.cbox_object_name.set(self.objects[obj_type][0])
    
    def cmd_escape(self,event):
        self.checkbutton_replace.deselect()
        self.entry_replace.delete(0,'end')
        self.entry_replace.config(state='disabled')
        self.entry_searchbar.delete(0,'end')
        self.frame_search.pack_forget()
        self.text_output.tag_remove('found', '1.0', 'end')
        return

    def cmd_search(self,*arg):
        self.frame_search.pack(fill='both',expand=1,padx=5,pady=5)
        self.label_searchbar.grid(row=1,column=1,sticky='E')
        self.entry_searchbar.grid(row=1,column=2)
        self.checkbutton_replace.grid(row=2,column=1,sticky='EW')
        self.entry_replace.grid(row=2,column=2)
        self.entry_searchbar.focus_set()
        return
    
    def cmd_replace(self):
        self.entry_replace.config(state='normal')
    
    def replace_string(self,event):
        str_old = self.entry_searchbar.get()
        str_new = self.entry_replace.get()
        
        data_new = self.selected_object_data
        for idx,line in enumerate(data_new):
            if str_old in line:
                data_new[idx] = line.replace(str_old,str_new)
        
        self.new_setup = self.orig_setup
        self.new_setup[self.fidx:self.lidx] = data_new
        
        self.update_text(data_new)
        return
 
    def highlight_block(self,tagname,string,spaces,color):
        objects_found = False
        
        idx = '1.0'
        self.text_output.tag_remove(tagname, '1.0', 'end')
        self.text_output.tag_remove('obj_name', '1.0', 'end')
        
        block_fidx = []
        block_lidx = []
        
        while 1: 
            idx = self.text_output.search(string, idx, nocase=1, stopindex='end')
            if not idx: break
            block_fidx.append(idx)    
            lidx = '%s+%dc' % (idx, len(string))
            self.text_output.tag_add(
                    'obj_name',
                    lidx,
                    self.text_output.index('%d.end' % float(idx)))
            idx = lidx
            objects_found = True

        if objects_found == True:
            idx = '1.0'
            self.text_output.tag_remove('end', '1.0', 'end')
            while 1: 
                idx = self.text_output.search(r'^\s{%s}END' % spaces, idx, nocase=1, stopindex='end',regexp=True)
                if not idx: break
                block_lidx.append(idx)    
                lidx = '%s+%dc' % (idx, len('END')+spaces)
                idx = lidx
            
        block_idx = {}
        for fidx in block_fidx:
            for lidx in block_lidx:
                if float(lidx) > float(fidx):
                    block_idx[fidx] = lidx
                    break
        
        self.text_output.tag_remove(tagname, '1.0', 'end')
        for fidx in block_idx:
            self.text_output.tag_add(tagname, fidx, '%s+%dc' % (fidx,len(string)))
            self.text_output.tag_add(tagname, 
                                     block_idx[fidx],
                                     '%s+%dc' % (block_idx[fidx],len('END')+spaces))
            
        self.text_output.tag_config(
                    tagname,
                    foreground=color,
                    font='Consolas 11 bold')
        
        self.text_output.tag_config(
                    'obj_name',
                    foreground = 'yellow',
                    font='Consolas 11 bold')
    
    def highlight_names(self):
        self.text_output.tag_remove('objname', '1.0', 'end')
        for obj_type in self.object_types:
            if obj_type != 'All':
                for name in self.objects[obj_type]:
                    idx = '1.0'
                    while 1: 
                        idx = self.text_output.search(': '+name, idx, nocase=1, stopindex='end')
                        if not idx: break
                        lidx = '%s+%dc' % (idx, len(name)+2)
                        self.text_output.tag_add('objname', idx, lidx)
                        idx = lidx
            
        self.text_output.tag_config(
                'objname',
                foreground='black',
                font='Consolas 11 bold')
     
    def highlight_names_2(self,tag,blk_idx,color):
        self.text_output.tag_remove(tag+'type', '1.0', 'end')
        self.text_output.tag_remove(tag+'name', '1.0', 'end')
        self.text_output.tag_remove(tag+'end', '1.0', 'end')
        
        for fx in blk_idx:
            fidx_type = '%d.0' % (fx+1) 
            lidx_type = self.text_output.search(':', fidx_type)
            fidx_name = self.text_output.search(':', fidx_type)
            fidx_name = fidx_name+'+1c'
            lidx_name = '%d.end' % (fx+1)
            self.text_output.tag_add(tag+'type', fidx_type, lidx_type)
            self.text_output.tag_add(tag+'name', fidx_name, lidx_name)
            
            fidx_end = '%d.0' % (blk_idx[fx]+1)
            lidx_end = '%d.end' % (blk_idx[fx]+1)
            self.text_output.tag_add(tag+'end', fidx_end, lidx_end)
               
        self.text_output.tag_config(
                        tag+'type',
                        foreground=color,
                        font='Consolas 11 bold')
        self.text_output.tag_config(
                        tag+'name',
                        foreground='black',
                        font='Consolas 11 bold')
        self.text_output.tag_config(
                        tag+'end',
                        foreground=color,
                        font='Consolas 11 bold')
        
        
    def get_indices(self,obj_type):
        blk_idx = {}
        fidx = []
        lidx = []
        for idx,line in enumerate(self.selected_object_data):
            space = len(line) - len(line.lstrip())
            if obj_type.upper()+':' in line: 
                fidx.append(idx)
            if 'END' in line and space == self.object_dict[obj_type]:
                lidx.append(idx)
                
        for fx in fidx:
            for lx in lidx:
                if lx > fx:
                    blk_idx[fx] = lx
                    break
        return blk_idx
    
    def search_text(self,event):
        if event.keysym != 'Return':
            self.counter = 1
            self.text_output.tag_remove('found', '1.0', 'end')
            tag = self.entry_searchbar.get()
            self.fidx_search = []
            if tag:
                idx = '1.0'
                while 1:
                    idx = self.text_output.search(r'(%s)' % tag, idx, nocase=0, stopindex='end',regexp=True)
                    if not idx: break
                    self.fidx_search.append(math.floor(float(idx)))
                    lastidx = '%s+%dc' % (idx, len(tag))
                    self.text_output.tag_add('found', idx, lastidx)
                    idx = lastidx
                self.text_output.tag_config(
                        'found',
                        foreground='red',
                        background='yellow',
                        font='Consolas 11 bold')
            else:
                self.text_output.yview_moveto(0)
            
            if self.fidx_search:
                self.text_output.yview_moveto(0)
                self.text_output.yview_scroll(self.fidx_search[0]-1,'units')
        else:
            return
        
    def search_next(self,event):
        if self.fidx_search:
            self.text_output.yview_moveto(0)
            self.text_output.yview_scroll(self.fidx_search[self.counter]-1,'units')
        if self.counter == len(self.fidx_search)-1:
            self.counter = 1
        else:
            self.counter += 1
    


def main():
    root = tk.Tk()
    root.title('CCL editor')
    MainApplication(root)
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()
   
if __name__ == '__main__':
    main()