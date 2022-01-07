# Import
from tkinter import Tk, Label, Button, Menu, Toplevel, Entry, Checkbutton, BooleanVar
from pyglet import font as pygletFont
import json, time, datetime, winsound

# create root
root = Tk()

# Load fonts
try:
    pygletFont.add_file('fonts/digital-7.ttf')    
except:
    print('Error loading fonts')

# tkinter window class
class MyTimer:

    def __init__(self, master):
        # master
        self.master = master
        
        # variables
        # counter used in timer
        self.tiks = 0 
        # check if start has been pressed 
        self.pressed = False
        # Init runonce variable
        self.runonce = False
        # timeout entry
        self.var = BooleanVar()
        # init var
        self.var.set(False)
        # Init after
        self.AFTER = None

        # width & height 
        w = 330 
        h = 200
        # center screen
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws/2 - w/2)
        y = (hs/3 - h/2)
        # screen size
        self.master.geometry('%dx%d+%d+%d' % (w,h,x,y))
        # fixed size screen
        self.master.resizable(0,0)
        # screen title
        self.master.title('Drink water bitch')
        # screen color
        self.master['bg'] = 'black'

        # Create menu bar
        menu_bar = Menu(self.master)
        # Add menu to master
        self.master.config(menu=menu_bar)
        # Add command to menu bar
        menu_bar.add_command(label='Configuration', command=self.TimerConfig)

        # Timer Label
        self.timer_label = Label(self.master, text='00:00', font=('digital-7',60),
                            fg='lawn green', bg='black')
        # Pack Timer Label
        self.timer_label.pack(pady=5)
        # Clock Label
        self.clock_label = Label(self.master, text='00:00:00', font=('digital-7',20),
                            fg='lawn green', bg='black')
        # Pack Clock Label
        self.clock_label.pack(pady=1)
        # Start Button
        self.btn_start =  Button(self.master, text='Start', command=self.StartTimer,
                            height=2, width=10, fg='white', bg='black',
                            activeforeground='black', activebackgroun='black')
        # Pack Start Button
        self.btn_start.pack(side='left',padx=60)
        # Stop Button
        self.btn_stop =  Button(self.master, text='Stop', command=self.StopTimer,
                            height=2, width=10, fg='red', bg='black',
                            activeforeground='black', activebackgroun='black')
        # Pack Stop Button
        self.btn_stop.pack(side='left')
        # load settings
        with open('conf/conf.json') as f:
            self.conf_file =  json.load(f)
            self.timeout =  self.conf_file['timer']
            self.autostart = self.conf_file['autostart']
        
        # start clock
        self.clock()
        # check if autostart is true
        if self.autostart:
            # start timer
            self.StartTimer()
    
    # functions

    def TimerConfig(self):
        '''timer configuration window'''
        # create settings window
        self.settingsWindow = self.CreateWindow(self.master,'black',(220,180),'Settings')
        # Current time setting label
        currTime_label = Label(self.settingsWindow, text=f'Current time settings {self.timeout}',
                            font=('digital-7',15), fg='lawn green', bg='black').pack(pady=5)
        # Input label
        timeout_label = Label(self.settingsWindow, text='Set timeout',
                            font=('digital-7',15), fg='lawn green', bg='black').pack(pady=1)                            
        # Input for new time
        setTime = Entry(self.settingsWindow, font=('digital-7',15), fg='red',
                        bg='black', insertbackground='white')
        # pack setTime Entry
        setTime.pack()
        # auto start checkbox
        btn_auto = Checkbutton(self.settingsWindow, text='Auto-Start', fg='white', bg='black',
                                activeforeground='black', variable=self.var, onvalue=True,
                                offvalue=False, activebackground='black', selectcolor='black')
        # if autostart is true or false, mark or unmark checkbutton
        if self.autostart:
            btn_auto.select()
        else:
            btn_auto.deselect()
        # pack btn_auto
        btn_auto.pack()
        # save settings button
        btn_save =  Button(self.settingsWindow, text='Save', font=('',10), fg='white', bg='black',
                           activeforeground='black', activebackground='black',
                           command=lambda:[self.save(setTime.get(),self.var.get()), self.closewindow(self.settingsWindow)])
        # pack save button
        btn_save.pack(pady=15)

    def is_not_blank(self, s):
        return bool(s and s.strip())
    
    def save(self, t, auto):
        try:
            # check if time is not a blank space
            if self.is_not_blank(t):
                # if is not a blank space, convert to int and store time
                self.int_t = int(t)
            else:
                # if blank space, use time in configuration file
                self.int_t = self.timeout
        except ValueError:
            '''If input is not an integer, show error message'''
            # create error message window
            error_window = self.CreateWindow(self.settingsWindow, 'black',(200,50),'Error')
            # add error label
            error_lable = Label(error_window, text='Time must be an Integer', font=('digital-7',15),
                                fg='red', bg='black').pack(pady=5)
        # save timer setting
        self.conf_file['timer'] = self.int_t
        # save autostart setting
        self.conf_file['autostart'] = auto
        # set new timeout
        self.timeout = self.int_t
        # save new settings in conf.json
        with open('conf/conf.json','w') as json_conf_file:
            json.dump(self.conf_file, json_conf_file)
        

    def closewindow(self, window):
        window.destroy()

    def btnPressed(self):
        '''change status that start btn has been pressed'''
        self.pressed = True

    def StopTimer(self):
        '''Stops timer and reset variables'''
        # stop alarm
        self.stopAlarm()
        # reset runonce variable
        self.runonce =  False
        # reset tiks counter
        self.tiks = 0
        # reset timer label
        self.timer_label['font'] = ('digital-7', 60)
        self.timer_label['text'] = '00:00'
        self.timer_label['fg'] = 'lawn green'
        # reset pressed 
        self.pressed =  False
        # reset start button
        self.btn_start['command'] = self.StartTimer
        # stop after loop
        if self.AFTER is not None:
            # check if after has been called once
            self.timer_label.after_cancel(self.AFTER)

    def clock(self):
        '''Gets current time and display it every second
        in clock_label'''
        # get current time
        current_time = datetime.datetime.now()
        now = current_time.strftime("%I:%M:%S")
        # set time in label
        self.clock_label['text'] = now
        # # call clock function every 1 second
        self.clock_label.after(1,self.clock)

    def StartTimer(self):
        ''' Start timer and start alarm'''
        # check if start button has already been pressed
        if not self.pressed:
            #if pressed, change command of button
            self.btn_start['command'] = self.btnPressed 
        # increment counter 
        self.tiks += 1
        # get minutes and seconds
        minutes, seconds = divmod(self.tiks, 60)
        time = '{:02d}:{:02d}'.format(minutes, seconds)
        if minutes >= self.timeout:
            '''check if timer is equal to timeout setting'''
            if not self.runonce:
                # Play Alarm once
                self.playAlarm()
                # change status of runonce
                self.runonce = True
            # change text in timer_label
            self.timer_label['font'] = ('digital-7', 30)
            self.timer_label['text'] =  'DRINK WATER, GET UP!!'
            self.timer_label['fg'] = 'red'
        else:
            # set time in timer_label   
            self.timer_label['text'] = time
        # create instance of after to stop it later and to loop function
        self.AFTER = self.timer_label.after(1000, self.StartTimer)

    def playAlarm(self):
        '''play alarm'''
        # Creo que no funciona con .mp3 y solo con .wav
        winsound.PlaySound('audio/AlarmaDespiertaBasuraHumana.mp3', winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)   

    def stopAlarm(self):
        '''stop alarm'''
        winsound.PlaySound(None, winsound.SND_PURGE)    

    def CreateWindow(self, ParentW, color, size, title):
        '''Create a Toplevel object in case a new window is needed'''
        new_window =  Toplevel(ParentW)
        # new window size
        w,h = size
        # center new window
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws/2 - w/2)
        y = (hs/3 - h/2)
        # new window size
        new_window.geometry('%dx%d+%d+%d' % (w,h,x,y))
        # new window fixed screen
        new_window.resizable(0,0)
        # new window title
        new_window.title(title)
        # new window color
        new_window['bg'] = color
        return new_window

# Timer Object
Gui = MyTimer(root)
# Run loop
root.mainloop()