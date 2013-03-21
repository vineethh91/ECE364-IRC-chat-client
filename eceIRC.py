#! /usr/bin/env python
# $Author: ee364c06 $
# $Date: 2011-11-22 17:07:23 -0500 (Tue, 22 Nov 2011) $
# $HeadURL: svn+ssh://ece364sv@ecegrid-lnx/home/ecegrid/a/ece364sv/svn/F11/students/ee364c06/Lab12/eceIRC.py $
# $Revision: 30352 $

from Tkinter import *
from tkMessageBox import askokcancel, showwarning, showinfo
import sys, irclib, threading, string
import datetime
import os

class startWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        frame = Frame(self)

        self.channelDict = {}
        self.title("Server Command window")

        frame.pack(side=LEFT, fill=BOTH, expand=1) 
        self.entry = Entry(frame)
        self.entry.pack(side=BOTTOM, fill=X)
        self.entry.config(foreground="black", background="red")

        self.slider = Scrollbar(self)
        self.slider.pack(side=RIGHT, fill=Y)

        self.textBox = Text(frame, yscrollcommand=self.slider.set)
        self.textBox.config(state=DISABLED, cursor="arrow", foreground="white",background="black")
        self.textBox.pack(side=BOTTOM, fill=BOTH, expand=1) 

        self.slider.config(command=self.textBox.yview)

        self.bind("<Return>", self.checkCommand)
        self.protocol("WM_DELETE_WINDOW", self.closeWindow)

    def checkCommand(self, a):
        cmd = self.entry.get().split()
        if self.entry.get() == "":
            self.entry.delete(0, END)
        elif cmd[0] == "/exit":
            self.closeWindow()
            self.entry.delete(0,END)
        elif cmd[0] == "/join":
            if len(cmd) == 2:
                self.channel = cmd[1]
                if self.channel[0] == "#" and self.channel not in self.channelDict:
                    channel = channelWindow()
                    server.join(cmd[1])
                    self.channelDict[self.channel] = channel
                    self.entry.delete(0,END)
            else:
                showwarning("Error!", "Provide a channel name - /join #channelName")
            self.entry.delete(0,END)
        elif cmd[0] == "/part":
            if len(cmd) == 2:
                if cmd[1] in root.channelDict:
                    channel = root.channelDict[cmd[1]]
                    channel.closeWindow()
            else:
                showwarning("Error!", "Provide a channel name - /part #channelName")
            self.entry.delete(0,END)
        else:
            self.entry.delete(0,END)

    def closeWindow(self):
        Reply = askokcancel("Verify Quit","Do you really want to quit?")
        if Reply != 0:
            self.destroy()
            die()

class connectWindow(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title("Connection")

        photo = PhotoImage(file="irc.gif")
        self.w = Label(self, image=photo)
        self.w.photo = photo
        self.w.pack(side=TOP)

        self.serverLabel = Label(self, text = "Server Name", font=("Helvetica", 14, "bold"), justify=CENTER, bg="black", fg="red").pack(side=TOP, fill=X)
        
        self.serverNameText = Entry(self, width=30)
        self.serverNameText.config(bg="red",fg="black")
        self.serverNameText.insert(0,"ecegrid-lnx.ecn.purdue.edu")
        self.serverNameText.pack(side=TOP, fill=X)

        self.userNameLabel = Label(self, text = "User Name", font=("Helvetica", 14, "bold"), justify=CENTER, bg="black", fg="red").pack(side=TOP, fill=X)
        
        self.userNameText = Entry(self)
        self.userNameText.config(bg="red",fg="black")
        self.userNameText.insert(0,"ee364c06")
        self.userNameText.pack(side=TOP, fill=X)
    
        frame = Frame(self)
        self.connect = Button(frame, text="Connect!", command=self.connect)
        self.connect.pack(side=LEFT, fill=X)
        self.connect.config(cursor='circle', fg="#00FF00", bg="#000080")
        self.info = Button(frame, text ="info", relief=RAISED, bitmap="info", command=self.info)
        self.info.pack(side=RIGHT)
        self.info.config(fg="red", bg="black")
        frame.pack(side=TOP, fill=BOTH, expand=1)

        self.protocol("WM_DELETE_WINDOW", self.closeWindow)
        
    def connect(self):
        try:
            server.connect(self.serverNameText.get(), 6667, self.userNameText.get())
        except irclib.ServerConnectionError:
            showwarning("Connection Error!", "Can't connect to the specified IRC server!")
        else:
            #print "Successful connection"
            self.destroy()
            root.deiconify()

    def info(self):
        showinfo(title="About", message="Vinny's IRC client v0.1", type="ok")

    def closeWindow(self):
        Reply = askokcancel("Verify Quit","Do you really want to quit?")
        if Reply != 0:
            self.destroy()
            die()

class channelWindow(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        
        frame = Frame(self)
        frame.pack(side=TOP, fill=BOTH, expand=1)
        
        self.userList = []
        self.channelName = root.channel
        self.title(self.channelName)

        self.slider1 = Scrollbar(frame)
        self.outputBox = Text(frame, yscrollcommand=self.slider1.set)
        self.outputBox.tag_config("others", foreground="red")
        self.outputBox.tag_config("me", foreground="#000080")
        self.outputBox.config(state=DISABLED, bg="white", fg="red", \
                                font=("Helvetica", 12, "bold"))
        self.outputBox.pack(side=LEFT, fill=BOTH, expand=1)
        self.slider1.pack(side=LEFT, fill=Y, expand=1)
        self.slider1.config(command=self.outputBox.yview)

        self.slider2 = Scrollbar(frame)
        self.usersBox = Listbox(frame, yscrollcommand=self.slider2.set)
        self.usersBox.config(state=DISABLED, bg="black", fg="red", \
                                font=("Times", 14, "bold"))
        self.usersBox.pack(side=LEFT, fill=BOTH, expand=1)
        self.slider2.config(command=self.usersBox.yview)
        self.slider2.pack(side=LEFT, fill=Y, expand=1)
        
        self.entry = Entry(self)
        self.entry.pack(side=TOP, fill=X)
        self.entry.config(bg="#00FF00", fg="black")

        self.entry.bind("<Return>", self.message)

	self.log = 0
	self.logFileName = self.channelName
        self.protocol("WM_DELETE_WINDOW", self.closeWindow)

    def message(self, a):
        if self.checkCommand(self) == 0 and self.entry.get()[0] != "/":
            now = datetime.datetime.now()
            #print "no match"
            server.privmsg(self.channelName, self.entry.get())
            self.outputBox.config(state=NORMAL)
            msg = now.strftime("(%H:%M:%S) ") + " " + server.get_nickname() + ": " + self.entry.get() + "\n"
	    self.outputBox.insert(END, msg, "me")
	    if self.log == 1:
		self.fi.write(msg)
            self.outputBox.yview(END)
            self.outputBox.config(state=DISABLED)
            self.entry.delete(0, END)
	elif self.channelName in root.channelDict:
	    self.entry.delete(0, END)
		
    def checkCommand(self, a): 
        str = self.entry.get()
        cmd = str.split()
        found = 0
        if self.entry.get() == "":
            found = 1
        elif cmd[0] == "/exit":
	    if self.log == 1:
	    	self.fi.write("\n******* End of Chat log **********\n")
		self.fi.close()
		self.log = 0
            self.closeWindow()
            found = 1
        elif cmd[0] == "/join":
            if len(cmd) == 2:
                channel = cmd[1]
                if channel[0] == "#" and channel not in root.channelDict:
                    channelObject = channelWindow()
                    channelObject.channelName = channel
		    channelObject.logFileName = channel
                    channelObject.title(channel)
                    server.join(cmd[1])
                    root.channelDict[channel] = channelObject
                    self.entry.delete(0,END)
            else:
                showwarning("Error!", "Provide a channel name - /join #channelName")
            self.entry.delete(0,END)
            found = 1
        elif cmd[0] == "/part": 
            if len(cmd) == 2:
                self.entry.delete(0, END)
                if cmd[1] in root.channelDict:
                    channel = root.channelDict[cmd[1]]
                    channel.closeWindow()
            else:
                showwarning("Error!", "Provide a channel name - /part #channelName")
            found = 1
	elif str == "/log on" and self.log == 0:
	    self.log = 1
	    time = datetime.datetime.now()
	    date = time.strftime("%Y-%m-%d") 
	    name =  self.logFileName.split('#')[1] + "-Log-" + date + ".txt"
            #print self.channelName + " - log file = " + name
	    if os.path.exists(name):
	    	self.fi = open(name, "a")
	    else:
	    	self.fi = open(name, "w")
	    self.fi.write("\n******** Chat log from " + self.logFileName + " on " + time.strftime("%Y/%m/%d @ %H:%M:%S") + " ********\n\n")
            self.outputBox.config(state=NORMAL)
	    msg = "\n********* Chat logging is now enabled. Type /log off to turn it off *********\n" 
	    self.outputBox.insert(END, msg, "me")
            self.outputBox.config(state=DISABLED)
	    found = 1
	elif str == "/log off" and self.log == 1:
	    self.log = 0
            self.outputBox.config(state=NORMAL)
	    msg = "\n********* Chat logging is now disabled. *********\n" 
	    self.outputBox.insert(END, msg, "me")
            self.outputBox.config(state=DISABLED)
	    self.fi.write("\n******* End of Chat log **********\n")
	    self.fi.close() 
	    found = 1 
        return found

    def closeWindow(self):
	    if self.log == 1:
	    	self.fi.write("\n******* End of Chat log **********\n")
		self.fi.close()
		self.log = 0
            server.part(self.channelName)
            del root.channelDict[self.channelName]
            self.destroy()


def shandler(conn, event):
    msg = "*** " + string.join(event.arguments(), ' ') + "\n"
    global root
    #print root
    root.textBox.config(state=NORMAL)
    root.textBox.insert(END,msg)
    root.textBox.config(state=DISABLED)


def on_join(conn, event): 
    if event.target() in root.channelDict:
        channel = root.channelDict[event.target()]
        channel.outputBox.config(state=NORMAL)
        channel.outputBox.insert(END, "*** " + event.source() + " joined " + event.target() + "\n")
        channel.outputBox.config(state=DISABLED)
        nick =  event.source().split('!')
        if nick[0] not in channel.userList and "@" + nick[0] not in channel.userList:
            channel.userList.append(nick[0])
        channel.userList = sortNameList(channel.userList)
        channel.usersBox.delete(0, END)
        for I in channel.userList:
            channel.usersBox.insert(END, I)

def on_part(conn, event): 
    #print "part - " + string.join(event.arguments(), ' ')
    #print event.target()
    #print event.source()
    if event.target() in root.channelDict:
        #print "parting channel"
        channel = root.channelDict[event.target()]
        channel.outputBox.config(state=NORMAL)
        channel.outputBox.insert(END, "*** " + event.source() + " left " + event.target() + "\n")
        channel.outputBox.config(state=DISABLED)
        nick =  event.source().split('!')
        if nick[0] in channel.userList or "@" + nick[0] in channel.userList:
            channel.userList.remove(nick[0])
        channel.usersBox.delete(0, END)
        for I in channel.userList:
            channel.usersBox.insert(END, I)

def on_quit(conn, event): 
    nick =  event.source().split('!')
    for key in root.channelDict:
        channel = root.channelDict[key]
        for I in channel.userList:
            if nick[0] in channel.userList or "@" + nick[0] in channel.userList:
                channel.outputBox.config(state=NORMAL)
                channel.outputBox.insert(END, "*** " + event.source() + " quit IRC" + "\n")
                channel.outputBox.config(state=DISABLED)
                channel.userList.remove(nick[0])
                channel.usersBox.delete(0, END)
                for I in channel.userList:
                    channel.usersBox.insert(END, I)

def publicmsg(conn, event): 
    nick = event.source().split('!')[0]
    if event.target() in root.channelDict:
        now = datetime.datetime.now()
        channel = root.channelDict[event.target()]
        channel.outputBox.config(state=NORMAL)
        msg = now.strftime("(%H:%M:%S)") + " " + nick + ": " + string.join(event.arguments(), ' ') + "\n"
	channel.outputBox.insert(END, msg) 
	if channel.log == 1:
	    channel.fi.write(msg)
        channel.outputBox.yview(END)
        channel.outputBox.config(state=DISABLED)

def namereply(conn, event): 
    #print event.arguments()
    if event.arguments()[1] in root.channelDict:
        channel = root.channelDict[event.arguments()[1]]
        channel.usersBox.config(state=NORMAL)
        names = event.arguments()[2].split()
        channel.userList = []
        channel.usersBox.delete(0, END)
        for I in names:
            if I not in channel.userList and "@" + I not in channel.userList:
                channel.userList.append(I)
        channel.userList = sortNameList(channel.userList)
        for I in channel.userList:
            channel.usersBox.insert(END, I)

def currenttopic(conn, event):  
    if event.arguments()[0] in root.channelDict:
        channel = root.channelDict[event.arguments()[0]]
        newtitle = event.arguments()[0] + " - " + event.arguments()[1]
        channel.title(newtitle)

def spin():
    global done, irc
    while done == 0:
        irc.process_once(0.2)
    sys.exit(0)

def die():
    global done
    done = 1
    sys.exit(0)

def sortNameList(names):
    newAtList = []
    newNotAtList = []
    for I in names:
        if I[0] == "@":
            newAtList.append(I)
        else:
            newNotAtList.append(I)
    newAtList.sort(key=str.lower)
    newNotAtList.sort(key=str.lower)
    newAtList += newNotAtList
    return newAtList


done = 0

irc = irclib.IRC()
server = irc.server()

#server.add_global_handler("join", on_join)
server.add_global_handler("yourhost", shandler )
server.add_global_handler("created", shandler)
server.add_global_handler("myinfo", shandler )
server.add_global_handler("featurelist", shandler )
server.add_global_handler("luserclient", shandler )
server.add_global_handler("luserop", shandler )
server.add_global_handler("luserchannels", shandler )
server.add_global_handler("luserme", shandler )
server.add_global_handler("n_local", shandler )
server.add_global_handler("n_global", shandler )
server.add_global_handler("luserconns", shandler )
server.add_global_handler("welcome", shandler )
server.add_global_handler("motd", shandler)
server.add_global_handler("join", on_join) 
server.add_global_handler("part", on_part)
server.add_global_handler("quit", on_quit)
server.add_global_handler("pubmsg", publicmsg)
server.add_global_handler("namreply", namereply)
server.add_global_handler("currenttopic", currenttopic)

root = startWindow()
root.withdraw()
connect = connectWindow()

thread1 = threading.Thread(target=spin)
thread1.start()

#channel = channelWindow()
root.mainloop()
#die()
