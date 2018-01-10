import tkinter as tk
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
        
        self.gui_set_frames()
        self.gui_set_text()
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
                width=60,
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
        
    def gui_set_grid(self):
        self.mainframe.pack(fill='both',expand=1,padx=5,pady=5)
        self.text_output.grid(row=1,column=1,sticky='NSEW')
        self.text_xscrollbar.grid(row=2,column=1,sticky='NSEW')
        self.text_yscrollbar.grid(row=1,column=2,sticky='NSEW')
    
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
        return
    
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