#!/usr/bin/env python

##   ircClient.py
##   Avi Kak (kak@purdue.edu)
##   April 9, 2017

##   This is the Python version of the command-line IRC client.
##
##   To make a connection, your command line should look like
##
##      ircClient.py  irc.freenode.net  6667  botrow  ##PurdueCompsec
##
##   where 'botrow' is your nick and '##PurdueCompsec' the name of the channel.
##   Obviously, 'irc.freenode.net' is the hostname of the server and 6667 the port
##   number.
##
##   After you are connected, to send a text string to the server, enter
##   
##      PRIVMSG  ##PurdueCompsec  :your actual text message goes here
##
##   where 'PRIVMSG' is the command name for sending a text message and
##   '##PurdueCompsec' the name of the channel.  What comes after the colon is the
##   text you want to send to to the channel.  Similarly, if you want to announce to
##   to the ##PurdueCompsec channel that you will be away for 10 minutes, you can
##   enter
##
##      AWAY ##PurdueCompsec :Back in 10 mins
##
##   If you want yourself to be unmarked as being away, all you need to enter is
##
##       AWAY
##
##   without any arguments to the command.  To quit a chat session, all you have to
##   say is
##
##       QUIT
##
##   It is normal for the server to return an ERROR message when you quit.
##
##   If you don't know where the command names PRIVMSG, AWAY, QUIT, etc., come from,
##   read the RFC1459 IRC standard.  That standard defines a total of 40 such
##   commands.
##
##   Also try PING, WHO, WHOIS, USERS, PART, QUIT, NAMES, LIST, VERSION,
##   STATS c, STATS l, STATS k, ADMIN, etc., with this command-line client.

import sys, socket, signal, os, re                                                       #(1)

if len(sys.argv) != 5:                                                                   #(2)
    sys.exit(''' Usage:  Requires 4 arguments as in\n\n\n'''
             '''     ircClient.py  host  port  nick  channel  \n\n'''
             ''' Example: ircClient.py irc.freenode.net 6667 botrow \##PurdueCompsec\n\n''') 

def sock_close( signum, frame ):                                                         #(3)
    global sock
    sock.close
    sys.exit(0)

signal.signal( signal.SIGINT, sock_close )                                               #(4)

server  = sys.argv[1]                                                                    #(5)
port    = int(sys.argv[2])                                                               #(6)
nick    = sys.argv[3]                                                                    #(7)
login   = nick                                                                           #(8)
channel = sys.argv[4]                                                                    #(9)

try:                                                                                    #(10)
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )                          #(11)
    sock.connect((server, port))                                                        #(12)
except socket.error, (value, message):                                                  #(13)
    if sock:                                                                            #(14)
        sock.close()                                                                    #(15)
    else:                                                                               #(16)
        print("Could not establish a client socket: " + message)                        #(17)
        sys.exit(1)                                                                     #(18)

IRC_cmds =  '''ADMIN AWAY CONNECT ERROR INFO INVITE                                      
               ISON JOIN KICK KILL LINKS LIST MODE 
               NAMES NICK NOTICE OPER PART PASS PING 
               PONG PRIVMSG QUIT REHASH RESTART SERVER 
               SQUIT STATS SUMMON TIME TOPIC TRACE 
               USER USERHOST USERS VERSION WALLOPS 
               WHO WHOIS WHOWAS'''                                                      #(19)
IRC_cmds = IRC_cmds.split()                                                             #(20)

sys.stderr.write("[Connected to " + server + " : " + str(port) + "]\n")                 #(21)

#  Spawn a child process. The variable pid is set to the PID of the child process in
#  the main parent process.  However, in the child process, the value of PID is set to 0.
pid = os.fork()                                                                         #(22)
if pid == 0:                                                                            #(23)
    # WE ARE IN THE CHILD PROCESS HERE:
    # The job of the child process is to upload the locally generate messages to the
    # Freenode server --- from where they get broadcast to all other channel members.
    while True:                                                                         #(24)
        msg = sys.stdin.readline()                                                      #(25)
        if msg is not None:                                                             #(26)
            split_msg = filter(None, msg.split())                                       #(27)
        if split_msg[0] in IRC_cmds:                                                    #(28)
            sock.send(msg)                                                              #(29)
            if split_msg[0] == 'QUIT': break                                            #(30)
        else:                                                                           #(31)
            sys.stderr("Syntax error. Try again\n")                                     #(31)
else:
    # WE ARE IN THE PARENT PROCESS HERE.
    # Use blocking read to receive messages incoming from the server and to respond to 
    # those messages appropriately.  If there is a need to send a message to the server, 
    # a message that is not a reply to something received from the server, the child 
    # process will take care of that.
    # But first you must log into the server.  To log into a server that does not need 
    # a password, you need to send the NICK and USER messages to the server as shown 
    # below. See Section 3.1.3 of RFC 2812 for the syntax used for the USER message.
    sock.send("NICK " + nick + "\r\n")                                                  #(32)
    sock.send("USER " + login + " 0 * :A Handcrafted IRC Client\r\n")                   #(33)
    while True:                                                                         #(34)
        input = ''                                                                      #(35)
        while True:                                                                     #(36)
            byte = sock.recv(1)                                                         #(37)
            if byte == "\n": break                                                      #(38)
            input += byte                                                               #(39)
        # Check the numerical responses from the server.
        if '004' in input:               # connection established                       #(40)
            # If connection established successfully, we terminate this `while' loop
            # and switch to the `while' loop in line (i) for downloading chat from
            # the server on a continuous basis:
            break                                                                       #(41)
        elif 'PING' in input:
            # Some servers require sending back PONG with the same characters as
            # received from the server:
            print( "Found ping: " + input)                                              #(42)
            if ':' in input:                                                            #(43)
                digits = input[input.find(':') + 1 : ]                                  #(44)
                sock.send( 'PONG ' + digits + "\r\n")                                   #(45)
        elif '433' in input:                                                            #(46)
             sys.exit("Nickname is already in use.")                                    #(47)
    print("Joining the channel\n")                                                      #(48)
    sock.send('JOIN ' + channel + "\r\n")                                               #(49)
    print("Waiting for a reply\n")                                                      #(50)
    while True:                                                                         #(51)
        input = ''                                                                      #(52)
        while True:                                                                     #(53)
            byte = sock.recv(1)                                                         #(54)
            if byte == "\n": break                                                      #(55)
            input += byte                                                               #(56)
        regex = re.compile( r'^PING(.*)$', re.IGNORECASE )                              #(57)
        m = re.search( regex, input )                                                   #(58)
        if m is not None:                                                               #(59)
            sock.send("PONG " + m.group(1) + "\r\n")                                    #(60)
        else:                                                                           #(61)
            # It is this part of the parent process that displays the incoming chat:
            # In the incoming chat, a remote user is identified with a string like
            # "nick!login_name@host".  We want to abbreviate that to just the nick:
            regex = r'(^[^!]*)![^ ]*'                                                   #(62)
            m = re.search( regex, input )                                               #(63)
            if m is not None:                                                           #(64)
                input = re.sub(regex, m.group(1), input)                                #(65)
            print(input)                                                                #(66)
