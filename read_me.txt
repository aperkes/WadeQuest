To play the game, open the terminal. 
You must first set the current directory (this should change eventually, but for now this is how we're doing it...)
The easiest way to do this is to type 'cd' and then drag the game file (Ethan) into the terminal window
so your command line should look almost exactly like this: 

cd /Users/ammonperkes/Documents/WadeQuest/Ethan 

once you've done this type './myroom.py' (python myroom.py also works) 

Commands:
Commands are up to you, and can change based on the setting, but there are some that will usually work: 
explore: This will look around and see what there is to work with. 
help: This will usually give you a hint as to what do to
walk: If you can walk to get somewhere, this will often work. Sometimes there are obstacles though. 
get: If there's something to be got, this will get it. 
QUIT: This will let you quit wherever you are
SAVE: This will let you save, but you can only save in certain places. It will tell you when you can save. 
open: This open's stuff

Node Syntax (for making things)
1 (the node number)
Intro text goes here, this is read as you go in
## Commands 
word: Any one word will be found if it's an exact match. That means you can't have "door" and "open door" because it will break
*%*:Produces result if anything other than a word from the commands is given (this goes to a new node) 
*$*:Prints a phrase if anything other than a word from the commands is given. 
*?*:check1,command1;check2,command2 (This will check the STATE list, and if it's not there, it will remove the option. To be exact, it capitalizes the option so that it can't be given, because all commands are lower cased by the time they're checked.)
*!*:This happens immediately upon entering the node. It could be good for traps, items, etc. 
get an item:$ADD item text about the item (this adds an object to the state list. and then prints the item prompt)
lose an item:$REMOVE item text about the item (as above. I haven't actually added this yet) 
open a file:$OPEN filename.png text about the file (Allows it to open files in the system viewer. If it's already open it brings it to the front of the screen).
## Nodes
word:2 (What's important here is that there shouldn't be spaces. And the nodes and commands have to match) 
*%*:3
*!*:4 (I believe this is possible, I'm not actually positive. It would send you right out of a node). 

Cheat codes: 
These have to be given as you enter a node or they won't work. 
1337 quit
1337 cureent node
1337 show commands
1337 show nodes
1337 accio object
1337 destroy object
1337 skip to ## (number of a node) 

