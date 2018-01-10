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
        
        self.gui_set_frames()
        self.gui_set_text()
        self.gui_set_grid()
        
    def gui_set_frames(self):
        self.mainframe = tk.Frame(self.master)
        
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
        
    def gui_set_grid(self):
        self.mainframe.pack(fill='both',expand=1,padx=5,pady=5)
        self.text_output.grid(row=1,column=1,sticky='NSEW')
        self.text_xscrollbar.grid(row=2,column=1,sticky='NSEW')
        self.text_yscrollbar.grid(row=1,column=2,sticky='NSEW')
        


def main():
    root = tk.Tk()
    root.title('CCL editor')
    MainApplication(root)
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()
   
if __name__ == '__main__':
    main()