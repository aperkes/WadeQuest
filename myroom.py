#! /usr/bin/env python

""" This is a new game for Ethan. Instead of focussing on the fighting and maze generation dynamic (which was fun, and might come back) this will center on problem solving, multiple possible paths, to give a feeling of progress and choice without the existential boredom of eternal randomized mazes. 

One of the first things I need to do, is build a simple object to keep track of location, possibilities, and progress. """

import sys
import time
import os
import ast
import shutil
import random
import string
import math
import thread
import threading

global HOME
global USER_FILES
global CHAPTERS
global CURRENT_USER
global CURRENT_CHAPTER
global STATE


##For Windows: (Figure out what else this needs) 
# This might be bad form, but I think it should work
if os.name == 'nt':
    #HOME = 'C:\Users\Ethan\Documents\WadeQuest-master'  ### <--- Change this to the file path if it doesn't work
    HOME = sys.path[0]  ## <-- Add a hash here (#) at the start of line if you change the directory.
    def clear_screen():
        os.system('cls')
    def system_open(file_name):
        os.system('start ' + file_name)
else:
    HOME = sys.path[0]
    #HOME = os.getcwd()
    def clear_screen():
        os.system('clear')
    def system_open(file_name):
        os.system('open ' + file_name)

print 'Home = ' + HOME
USER_FILES = HOME + '/user_files'
CHAPTERS = HOME + '/chapters'
CURRENT_USER = 0 #dynamic global variable that allows for removal of os.getcwd()
CURRENT_CHAPTER = 0
STATE = []  # dynamic global variable that allows for changed state. 
""" Figure out how to make that work... """

class Node(object): ## Object for nodes. Input possible commands and their messages, as well as exits.
    def __init__(self, loc, intro, commands, paths):
        self.loc = loc ## This is just a number. It's not really a room. One location might correspond to "in a room, but with no key." and the next might be, "in a room, found a key" 
        self.intro = intro ##This is what is explained when you enter a room
        self.commands = commands ## Commands are dictionaries, where "use the key" gives "door now unlocked" 
        self.paths = paths ## Exits are also dictionaries, where "open the door" gives "loc 5" 

"""
def timed_input(prompt,timeout):
    slowprint(prompt)
    timer = threading.Timer(timeout,thread.interrupt_main)
    answer = None
    try:
        timer.start()
        astring = raw_input('')
    except KeyboardInterrupt:
        pass
    timer.cancel()
    return answer
"""
# Function to print slowly, adjust the time to slow it down...
def slowprint(s):
    if '*name*' in s:
        s = s.replace('*name*',CURRENT_USER.split('/')[-1].capitalize())
    try:
        if r'\n' in s:
            strings = s.split(r'\n')
            for line in strings:
                slowprint(line)
        else:
            count = 0
            for c in s + '\n':
                sys.stdout.write(c)
                count += 1
                sys.stdout.flush()
                time.sleep(1./70)  ## Adjust this line.
    except:
        print s[count:] 

#program to create a file which saves your progress at a particular node. 
def save_state(node):
    choice = raw_input('Are you sure you want to save? Doing so will erase previous save files. ').strip()
    if choice[0].lower() == 'y':    
        state = node.loc
        save_file = open(CURRENT_CHAPTER + '/save_data.txt','w')
        save_file.write(str(state))
        save_file.close()
        return True 
    elif choice[0].lower() == 'n':
        return 0
    else: 
        print "that didn't make sense. Use yes or no"
        return 0

def load_state():
    save_file = open(CURRENT_CHAPTER + '/save_data.txt','r')
    state = save_file.readline().strip()
    state = int(state)
    return state

### Function for loading a directory of nodes. 
### This will read in each node
### Node files need to be formatted as follows:
###
### 1
### ## Commands
### You find yourself in a dark room...
### look: You don't see anything
### feel: You find a light switch
### door: The door is locked
### key: You go through the door
### ## Paths 
### key: 2
### This is a text file, commands should not be capitalized (although I'll correct for it)
def load_nodes(directory):
    your_adventure = {}
    for node_file in os.listdir(directory): 
        if 'node' in node_file:
            node = open(directory + '/' + node_file,'r')
            node_loc = int(node.readline().strip())
            node_intro = node.readline().strip()
            header = node.readline() ## Reads off command header
            line = node.readline().strip()
            node_commands = {}
            #print node_loc
            while line[0] != '#':
                command = line.split(':')
                node_commands[command[0]] = command[1]
                line = node.readline().strip()
            line = node.readline().strip()
            node_paths = {}
            while line != '':
                path = line.split(':')
                node_paths[path[0]] = int(path[1])
                line = node.readline().strip()
            new_node = Node(node_loc, node_intro, node_commands, node_paths)
            your_adventure[node_loc] = new_node
            node.close()
        else:
            pass
    return your_adventure

### Function to check if a given choice corresponds with a command and/or exit
def find_phrases(choice): ## Finds every possible segment of an input (basically a suffix array)
    phrases = []
    words = choice.split()
    L = len(words)
    for n in range(L): 
        for m in range(n+1,L+1):
            phrases.append(' '.join(words[n:m]))
#   print phrases
    return phrases

def remove_punctuation(text):
    return text.translate(string.maketrans("",""), string.punctuation)

def is_square(square): 
    root = math.sqrt(square)
    if int(root + 0.5) ** 2 == square: 
        return True
    else: 
        return False

def smart_match(choice,node):
    choice = remove_punctuation(choice)
    """
    if 'SAVE' in choice: ## Allows for saving, but only at specified nodes
        if save_state:
            outcome = ['Progress Saved, returning to the game...']
        else: 
            outcome = ['Returning to the game...']
    if 'SAVE' in choice and not 'save' in node.commands: 
        outcome = ["You can't save here"]
    """
## This should all go into a function...
# Check for conditional, determine result....
   # print node.commands
    if '*?*' in node.commands:
       # print 'current commands'
       # print node.commands
       # print node.paths
       # print 'found ??'
        #checks = node.commands['*?*'].split(',')
        check_dict = dict(check.split(',') for check in node.commands['*?*'].split(';'))
        #for check in checks:
        for check in check_dict:
#if the check is in your state, do nothing
           # print 'checking each check'
## Revamp this, set condition based on upper/lower, since it always lower cases, this should work. 
            if check.strip() in STATE:
               # print 'found ' + check.strip()
               # print STATE
                try: #Fix upper case if it's there. 
                    node.commands[check_dict[check].lower()] = node.commands[check_dict[check].upper()]
                    del node.commands[check_dict[check].upper()]
                except: #Otherwise, it's already there, so just leave it. 
                    pass
                try:
                    node.paths[check_dict[check].lower()] = node.paths[check_dict[check]]
                    del node.paths[check_dict[check].upper()]
                except:
                    pass
# If the check isn't in your state, it deletes the option from commands
            if check.strip() not in STATE:
               # print 'cannot find ' + check.strip()
               # print 'deleting option'
               # print STATE
## Check if there's a lowercase command to delete, if so, delete it. 
                try:
                    node.commands[check_dict[check].upper()] = node.commands[check_dict[check]]
                    del node.commands[check_dict[check]]
                except: #Exceptions should only come if it's already been removed, in which case you can do nothing
                    pass
                #del node.commands[check_dict[check]]
## Check if there's a paths, and if so delete it. 
                try:
                    node.paths[check_dict[check].upper()] = node.paths[check_dict[check]]
                    del node.paths[check_dict[check]]

                    #del node.paths[check_dict[check]]
                except:
                    pass
               # print node.commands
               # print node.paths
# Del the conditional commands (otherwise that will cause all sorts of problems)
## It turns out I have to leave this otherwise it can only check once, which is sub optimal
    if '*X*' in node.commands:
        check_dict = dict(check.split(',') for check in node.commands['*X*'].split(';'))
        #for check in checks:
        for check in check_dict:
#if the check isn't in your state, do nothing
            if check.strip() not in STATE:
               # print 'found ' + check.strip()
               # print STATE
                try: #Fix upper case if it's there. 
                    node.commands[check_dict[check].lower()] = node.commands[check_dict[check].upper()]
                    del node.commands[check_dict[check].upper()]
                    #print 'deleting upper case'
                except: #Otherwise, it's already there, so just leave it. 
                    #print 'no uppder case found'
                    pass
                try:
                    node.paths[check_dict[check].lower()] = node.paths[check_dict[check]]
                    del node.paths[check_dict[check].upper()]
                except:
                    pass
# If the check is in your state, it deletes the option from commands
            if check.strip() in STATE:
## Check if there's a lowercase command to delete, if so, delete it. 
                try:
                    node.commands[check_dict[check].upper()] = node.commands[check_dict[check]]
                    del node.commands[check_dict[check]]
                except: #Exceptions should only come if it's already been removed, in which case you can do nothing
                    pass
## Check if there's a paths, and if so delete it. 
                try:
                    node.paths[check_dict[check].upper()] = node.paths[check_dict[check]]
                    del node.paths[check_dict[check]]

                except:
                    pass
    if '*!*' in node.commands:
        outcome[0] = node.commands['*!*']
        if '*!*' in node.paths:
            outcome[1] = node.paths['*!*']
    else:
        outcome = []
        for phrase in find_phrases(choice):
            phrase = phrase.lower()
            if phrase in node.commands:
    #           print 'phrase added: ' + phrase
                outcome.append(node.commands[phrase])
            if phrase in node.paths:
    #           print 'exit added: ' + phrase
                outcome.append(int(node.paths[phrase]))
        if r'*$*' in node.commands and len(outcome) == 0:
            outcome.append(node.commands[r'*$*'])
        if r'*%*' in node.commands and len(outcome) == 0: ## Allows for specific result when choice isn't in commands. *%* represents anything not specified.
            outcome.append(node.commands[r'*%*'])
            outcome.append(node.paths[r'*%*'])
        if len(outcome) == 0:
            print_fail()
            choice = raw_input(" ")
            if choice == 'QUIT':
                outcome = ['',776]
            else:
                outcome = smart_match(choice,node)
### More functions: This one opens a file. it's rather clever.
        if '$OPEN' in outcome[0]:
           # print outcome
           # raw_input('continue debug:')
            prompt_list = outcome[0].split()
            open_file = CURRENT_CHAPTER + '/' + prompt_list[1]
            space = ' '
            dialog = space.join(prompt_list[2:])
           # raw_input("Current Chapter: " + CURRENT_CHAPTER)
            system_open(open_file)
            #os.system('open ' + open_file)
            outcome[0] = dialog
## This allows you to add a state if the right command is given.
        if '$ADD' in outcome[0]:
            prompt_list = outcome[0].split()
            space = ' '
            dialog = space.join(prompt_list[2:])
            add_object = prompt_list[1]
            STATE.append(add_object)
            outcome[0] = dialog
           # print outcome
           # raw_input("continue?")
    #print 'returning outcome: '
#   print outcome
    return outcome

def print_fail():
    possible_fails = ["You can't",
            "That won't work here",
            "That won't work here",
            "That won't work here",
            "That won't work here",
            "No",
            "That doesn't make sense...",
            "Were those even words?",
            "Maybe you should call Ammon, he could help"
            ]
    print random.choice(possible_fails)

def run_node(node):
    """
    print "***node stuff:"
    print 'Node number:'
    print node.loc
    print 'node intro'
    print node.intro
    print 'Node commands:'
    print node.commands
    print 'Node paths'
    print node.paths
    print '**** end node stuff ****'
    """
    slowprint(node.intro)
    choice = raw_input(" ")
    if choice == "QUIT": ## THis allows for excape from loops, eventually it will be more elegant
        return 776
    if "SAVE" in choice and 'SAVE' in node.commands: 
        save_state(node)
## Some cheats to see what's going on for debug (or for laziness)
## Because of the way this works, all cheating has to be done when you first arrive at a node
    while '1337' in choice:
        if choice == '1337 quit':
            choice = raw_input("Are you sure you want to quit? ")
            if choice.lower()[1] == 'y':
                outcome = ['',776]
            else: 
                'Returning to game...'
                choice = raw_input("What do you want to do? ")
        elif choice == '1337 current node':
            print node.loc
            choice = raw_input("What do you want to do? ")
        elif choice == '1337 show commands':
            print node.commands
            choice = raw_input("What do you want to do? ")
        elif choice == '1337 show paths':
            print node.paths
            choice = raw_input("What do you want to do? ")
        elif choice == '1337 show state':
            print STATE
            choice = raw_input("What do you want to do? ")
        elif 'accio' in choice: 
            state = choice.split()[-1]
            STATE.append(state)
            choice = raw_input("What do you want to do? ")
        elif 'destroy' in choice: 
            state = choice.split()[-1]
            STATE.remove(state)
            choice = raw_input("What do you want to do? ")
        elif 'skip to' in choice:
            print choice
            number = int(choice.split()[-1])
            print number
            nextnode = number
            print 'skipping to ' + str(nextnode)
            return nextnode
        else: 
            print "That wasn't actually a thing"
            choice = raw_input("What do you want to do? ")
    outcome = smart_match(choice,node)
    while outcome == []:
        print_fail()
        choice = raw_input("What now? ")
        if choice == "QUIT":
            return 776
        else:
            outcome = smart_match(choice,node)
    while choice != "QUIT":
        slowprint(outcome[0])
        try: 
            nextnode = outcome[1]
            return nextnode
        except:
            pass
        choice = raw_input(' ')
        outcome = smart_match(choice,node)
    return 776

def add_chapter(chapter): ##Takes a directory of a new chapter, adds to current user's chapters
    shutil.copytree(chapter,CURRENT_USER + '/chapters/' + chapter.split('/')[-1])

def add_next_adventure(CURRENT_CHAPTER): ## Add's next chapter, if it exists
    current_number = int(CURRENT_CHAPTER[-1])
    next_chapter = CHAPTERS + '/chapter' + str(current_number + 1)
    
    if next_chapter.split('/')[-1] in os.listdir(CHAPTERS):
        if next_chapter.split('/')[-1] not in os.listdir(CURRENT_USER + '/chapters'):
            add_chapter(next_chapter)
            print '***New Chapter Opened!***'
            slowprint('........ . . . .')
            return 1 
        else:
            return 0
    else: 
        print 'That\'s the end for now. Go outside and have your own adventures'
        slowprint('........ . . . .')
        return 0

def add_all_chapters(): ## Cheat to unloack all chapters
    count = 0
    for chapter in os.listdir(CHAPTERS):
        if chapter in os.listdir(CURRENT_USER + '/chapters'):
            pass
        elif os.path.isdir(CHAPTERS + '/' + chapter):
            add_chapter(CHAPTERS + '/' + chapter)
            count += 1
    print str(count) + ' Chapters added'
    time.sleep(0.5)
    return 1

def have_an_adventure(adventure):
    if 'save_data.txt' in os.listdir(CURRENT_CHAPTER):
        print 'Save file exists. Would you like to load previous game?'
        choice = raw_input('type yes to load game ')
        if choice[0].lower() == 'y': 
            current_node = load_state()
        else: 
            current_node = 1
    else:
        print 'No save state found, starting chapter'
        current_node = 1
    while current_node != 777 and current_node != 776: ### 777 is designated the final node, whether through victory. 776 is Quitting 
        current_node = run_node(adventure[current_node])
    if current_node == 777:
        add_next_adventure(CURRENT_CHAPTER)
    raw_input('press enter to continue')
    slowprint('returning to menu...')

def select_chapter():
    for chapter in os.listdir(CURRENT_USER + '/chapters'):
        if chapter[0] != '.':
            print chapter
    print 'Which chapter?'
    choice = raw_input().strip()
    if choice == 'QUIT':
        sys.exit()
    try:
        if int(choice[-1]) - 1 in range(len(os.listdir('./chapters'))):
            return CURRENT_USER + '/chapters/chapter' + str(choice[-1])
        else:
            print "That's not an option..."
            return select_chapter()
    except:
        print "That's not a chapter, how about a number.  Like 1"
        return select_chapter()

def make_profile(): ## Creates a new profile. Must be in user_files when it runs
    name = raw_input('What is your name?\n').strip()
    if name in os.listdir(USER_FILES):
        print 'Profile already exists...'
        print 'Please choose a new name (or type QUIT to return)'
        return make_profile()
    if name == 'QUIT':
        print 'returning to welcome...'
        return 0
    print "So your name is " + name + " ?"
    choice = raw_input( "Are you sure?\n")
    if choice[0].lower() == 'y':
        slowprint('Adding adventurer...')
        os.mkdir(USER_FILES + '/' + name.lower())
        global CURRENT_USER
        CURRENT_USER =  USER_FILES + '/' + name.lower()
        slowprint('...creating world...')
        add_chapter(CHAPTERS + '/chapter1')
        print 'all done! Happy adventures!'
        return 1
    elif choice == 'QUIT':
        sys.exit()
    else:
        make_profile()
        return 1

def remove_profile():
    print "Be very very careful here, you could destroy everything"
    names = os.listdir(USER_FILES)
    for name in names:
        if name[0] != '.':
            print name
    name = raw_input('Which file do you want to remove?\n')
    if name in names:
        choice = raw_input( 'Are you completely sure you want to delete ' + name + '?\n')
        if choice[0].lower() == 'y':
            shutil.rmtree(USER_FILES +'/'+ name.lower())
            slowprint('. . . file removed')
            if name.lower() not in os.listdir(USER_FILES):
                print 'You deleted yourself, so please select a new user'
                user = select_user()
                return 1
            return 1
        else:
            print 'Probably for the best'
            return 0
    else: 
        print "that's not a user name, probably for the best anyway"
        return 0
        

def select_user():
    names = os.listdir(USER_FILES)
    count = 0
    for name in names: 
        if os.path.isdir(USER_FILES + '/' + name):
            print name
            count += 1
    if count == 0:
        print 'No user found'
        return 0
    choice = raw_input('Which one are you? Type your name exactly as written\n')
    if choice.lower() in names:
        print 'Welcome ' + choice + '. Loading profile'
        slowprint('...')
        global CURRENT_USER
        CURRENT_USER = USER_FILES + '/' + choice.lower().strip()
        return choice
    elif choice == "QUIT":
        sys.exit()
        return 'QUIT'
    else: 
        print "I couldn't find you"
        choice = raw_input('Try again? ')
        if choice[0].lower() == 'y':
            choice = select_user()
        choice = raw_input('Would you like to add a new user? ')
        if choice[0].lower() == 'y':
            choice = make_profile()
            return select_user()
        else:
            print 'returning to menu...'
            return 0
        return choice
    
def welcome():
    clear_screen()
    #os.system('clear')
    slowprint('Welcome adventurer. Have you been here before?')
    choice = raw_input('')
    if choice[0].lower() == 'y':
        choice = select_user()
        if choice == 0:
            make_profile()
        if choice == 'QUIT':
            welcome()
            return 0
    elif choice[0].lower() == 'n':
        make_profile()
    elif choice == 'QUIT':
        sys.exit()
    else:
        print "That doesn't actually make sense, let's try again..."
        welcome()
        return 0 


def menu():
    # Initialize/reset global variables
    STATE = []
    user_home = CURRENT_USER
    name = CURRENT_USER.split('/')[-1].capitalize()
    clear_screen()
    #os.system('clear')
    print "Hi " + name + ", what would you like to do?"
    print "Go on an Adventure?" 
    print 'Change User?'
    ###print "Change your name?" 
    print "Quit?" 
    choice = raw_input(" ")
    if 'go' in choice.lower():
        global CURRENT_CHAPTER
        CURRENT_CHAPTER = select_chapter()
        adventure = load_nodes(CURRENT_CHAPTER)
        clear_screen()
        #os.system('clear')

        have_an_adventure(adventure)
        clear_screen()
        #os.system('clear')
    elif 'change' in choice.lower():
        user = select_user()
        return 'U'
    elif 'quit' in choice.lower():
        #os.system('clear')
        clear_screen()
        slowprint('farewell adventurer.')
        return 'Q'
    elif choice == 'DELETE':
        remove_profile()
        return 'D'
    elif choice == 'ADD_ALL':
        add_all_chapters()
    else:
        print "I'm not sure I'm familiar with that one."
        return 0


### Initialize program, change to correct directory

### Load user profile ###
welcome()
choice = menu()
while menu() != 'Q':
    pass    
