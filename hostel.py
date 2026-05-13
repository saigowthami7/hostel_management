import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql
import mysql.connector

class hostel():
    def __init__(self,root):
        self.root = root
        self.root.title("Hostel Accommodation")

        self.width = self.root.winfo_screenwidth()
        self.height =self.root.winfo_screenheight()
        self.root.geometry(f"{self.width}x{self.height}+0+0")

        titleLbl= tk.Label(self.root, text="Hostel Accommodation System",bg="brown",fg="white",bd=4,relief="groove",font=("Arial",50,"bold"))
        titleLbl.pack(side="top",fill="x")

        # global variables
        self.room = 4
        self.bed = 4

        # input frame
        inFrame = tk.Frame(self.root, bg="light blue", bd=4, relief="ridge")
        inFrame.place(width=self.width/3,height=self.height-180, x=100,y=100)

        rnLbl = tk.Label(inFrame, bg="light blue", font=("Arial",15), text="RollNo:")
        rnLbl.grid(row=0, column=0, padx=20, pady=40)
        self.rnIn = tk.Entry(inFrame,bd=2,width=20, font=("Arial",15,"bold"))
        self.rnIn.grid(row=0,column=1, padx=20, pady=40)

        nameLbl = tk.Label(inFrame, bg="light blue", font=("Arial",15), text="Name:")
        nameLbl.grid(row=1, column=0, padx=20, pady=30)
        self.nameIn = tk.Entry(inFrame,bd=2,width=20, font=("Arial",15,"bold"))
        self.nameIn.grid(row=1, column=1, padx=20, pady=30)

        classLbl = tk.Label(inFrame, bg="light blue", font=("Arial",15), text="Class:")
        classLbl.grid(row=2,column=0, padx=20, pady=30)
        self.classIn = tk.Entry(inFrame,bd=2,width=20, font=("Arial",15,"bold"))
        self.classIn.grid(row=2,column=1, padx=20, pady=30)

        fnameLbl = tk.Label(inFrame, bg="light blue", font=("Arial",15), text="Father:")
        fnameLbl.grid(row=3, column=0, padx=20 , pady=30)
        self.fnameIn = tk.Entry(inFrame,bd=2,width=20, font=("Arial",15,"bold"))
        self.fnameIn.grid(row=3, column=1, padx=20, pady=30)

        okBtn = tk.Button(inFrame, bd=3,command=self.reserveFun, relief="raised",text="OK", font=("Arial",20,"bold"), width=20)
        okBtn.grid(row=4,column=0, padx=40, pady=30,columnspan=2)

        # output frame

        self.outFrame = tk.Frame(self.root, bg="light yellow", bd=4, relief="ridge")
        self.outFrame.place(width=self.width/2,height=self.height-180, x=self.width/3+150, y=100)
        self.tabFun()

    def tabFun(self):
        tabFrame = tk.Frame(self.outFrame, bg="brown", bd=4, relief="sunken")
        tabFrame.place(x=40, y=40, width=self.width/2-80,height=self.height-260)

        x_scrol = tk.Scrollbar(tabFrame, orient="horizontal")
        x_scrol.pack(side="bottom", fill="x")

        y_scrol = tk.Scrollbar(tabFrame, orient="vertical")
        y_scrol.pack(side="right", fill="y")

        self.table = ttk.Treeview(tabFrame, columns=("rollNo","name","class","fname"),xscrollcommand=x_scrol.set, yscrollcommand=y_scrol.set)

        x_scrol.config(command=self.table.xview)
        y_scrol.config(command=self.table.yview)

        self.table.heading("rollNo", text="Roll_No")
        self.table.heading("name",text= "Name")
        self.table.heading("class", text="Class")
        self.table.heading("fname",text="Father_Name")
        self.table["show"]= "headings"

        self.table.column("rollNo", width=150)
        self.table.column("name", width=150)
        self.table.column("class", width=150)
        self.table.column("fname",width=150)


        self.table.pack(fill="both", expand=1)

    def reserveFun(self):  
        rn = int(self.rnIn.get())
        name = self.nameIn.get()
        cls = self.classIn.get()
        fname = self.fnameIn.get() 

        con = pymysql.connect(host="localhost", user="root", passwd="#$aigow12345", database="hostel_management")
        cur = con.cursor()

        if rn and name and cls and fname:
            try:
                if self.room > 0:
                    if self.bed >0:
                        self.bed -= 1

                        cur.execute("insert into hostel(rollNo,name,class,fname) values(%s,%s,%s,%s)",(rn,name,cls,fname))
                        con.commit()
                        tk.messagebox.showinfo("Success",f"bed No.{4-self.bed} reserved in room No.{5-self.room}")
                    
                        cur.execute("select * from hostel")
                        data = cur.fetchall()

                        self.tabFun()
                        self.table.delete(*self.table.get_children())
                        for i in data:
                            self.table.insert('',tk.END, values=i)

                    else:
                        self.bed = 4
                        self.room -=1

                else:
                    tk.messagebox.showerror("Error","All Rooms Reserved")
            except Exception as e:
                tk.messagebox.showerror("Error",f"Error: {e}")            
        else:
            tk.messagebox.showerror("Error","Please Fill All Input Fields")

         
         


root = tk.Tk()
obj = hostel(root)
root.mainloop()