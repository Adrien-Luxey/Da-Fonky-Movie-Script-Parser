#!/usr/bin/python3
# coding: utf-8

# https://docs.python.org/3.0/library/urllib.request.html
# webpage type : https://docs.python.org/3.4/library/http.client.html
import os, sys, json, re, argparse, urllib.request, html5lib
from bs4 import BeautifulSoup, Tag, UnicodeDammit


aliens_url = 'http://www.imsdb.com/scripts/Aliens.html'
matrix_url = 'http://www.imsdb.com/scripts/Matrix,-The.html'
wrong_url = 'http://www.imqsdsdb.com/scriptljhs/Maqsdtrix,-The.html'


helptext="""Welcome to the Movie Script Parser!

It aims at creating a well formatted JSON file from the URL of a movie script online.

The parser was written using only scripts from http://www.imsdb.com, so it might fail on other sites (and also fail on IMSDB, who knows?).

It was written by Adrien Luxey for Pierre Peigné-Leroy in 2016."""

argparser= argparse.ArgumentParser(description=helptext)
argparser.add_argument('script_url', metavar='script_url', type=str, nargs='?',
        help='URL of the webpage containing the movie script')

args=argparser.parse_args()


# loop until we get a valid script_url

script_url = ''
is_webpage_fetched = False
while not is_webpage_fetched:
    # get the script's URL from the parameters if it was passed
    if( script_url == '' and args.script_url != None ):
        script_url = args.script_url
    else:
        print('Please provide the URL of a movie script you want to see parsed as JSON.')
        print('The parser was intended to work with imsdb.com, and you must provide a full URL (with http[s]://)')

        script_url = input('--> ')

    try:
        request = urllib.request.Request(script_url)
        webpage_bytes = urllib.request.urlopen(request)
        soup = BeautifulSoup(webpage_bytes, 'lxml')
        print('Detected encoding is ', soup.original_encoding)
        is_webpage_fetched = True
    except urllib.error.URLError as err:
        print('Catched an URLError while fetching the URL:', err)
        print()
        pass
    except ValueError as err:
        print('Catched a ValueError while fetching the URL:', err)
        print()
        pass
    except:
        print('Catched an unrecognized error')
        raise
    else:
        #script_text = soup.find("td", class_="scrtext").find("pre")
        script_text = soup.find("pre")

        if( script_text.find("pre") ):
            print('Found a <pre> inside the <pre>')
            script_text = script_text.find("pre")

        print('Parsing {} and extracting the first <pre> resulted in the following text:'.format(request.full_url))
        print(str(script_text)[:256])
        answer = input('Is that the script you expected? (Y/n) ')

        if( answer == 'N' or answer == 'n' ):
            answer = input('Shall we try with another URL? (Y/n) ')
            if( answer == 'N' or answer == 'n' ):
                raise ValueError('The result was not what we expected.')

        is_webpage_fetched = True



print()
print()
print('OK, we have the text. A few questions before we get parsing:')

# script dict to be serialized as JSON
script=dict()


# Let's fill what we can here
script['movie_url'] = request.full_url

# movie's name
answer = 'n'
while (answer == 'n' or answer == 'N'):
    script['movie_title'] = input("What's the name of this movie? ")
    answer = input("You typed '{}', is that right? (Y/n)".format(script['movie_title']))

# movie's year
answer = 'n'
while (answer == 'n' or answer == 'N'):
    script['movie_year'] = input("When was this movie released? (Leave blank to skip) ")
    if(script['movie_year'] == ''):
        answer = input("You didn't type anything, skip? (Y/n)")
        if(answer != 'n' and answer != 'N'):
            del script['movie_year']
    else:
        answer = input("You typed '{}', is that right? (Y/n)".format(script['movie_year']))




BLOCK_TYPES=['character', 'speech', 'stage direction', 'location']
CHARACTER=0
SPEECH=1
DIRECTIONS=2
LOCATION=3


# COMPILE ALL THE REGULAR EXPRESSIONS!
spaces_regex = re.compile("^(\s*).*")
location_regex = re.compile("^\s*(INT\.|EXT\.)")

def get_line_type(line, stripped_line, usual_spaces, characters):
    # Counting the number of spaces at the beginning of the line
    spmatch = spaces_regex.search(line)
    spaces_number = len(spmatch.group(1))
    block_type = 0

    if( location_regex.search(line) != None ):
        return LOCATION

    if stripped_line in characters:
        return CHARACTER

    # Look for space
    for block_type_usual_spaces in usual_spaces:
        if spaces_number in block_type_usual_spaces:
            block_type = usual_spaces.index(block_type_usual_spaces)
            #print('We consider {:d} leading spaces as a \'{:s}\' block.'.format(
            #      spaces_number, BLOCK_TYPES[block_type]))
            return usual_spaces.index(block_type_usual_spaces)

    print('There are {:d} space(s) at the beginning of this line'.format(spaces_number))
    question = "What kind of block is that?\n"
    for i in range(len(BLOCK_TYPES)):
        question += '\t('+str(i)+') ' + BLOCK_TYPES[i] + '\n'
    print(question)

    validated = False
    while( validated == False):
        try:
            block_type = int(input('? [0-{:d}] '.format(len(BLOCK_TYPES)-1)))
            while( block_type < 0 or block_type >= len(BLOCK_TYPES)):
                block_type = int(input('? [0-{:d}] '.format(len(BLOCK_TYPES)-1)))
        except ValueError:
            continue

        validated = True
        answer = input('You said the last block type was \'{:s}\', sure about that? (Y/n) '.format(
                BLOCK_TYPES[block_type]))
        if( answer == 'n' or answer =='N' ):
            validated = False

    remember_spaces = False
    validated = False
    while( validated == False):
        answer_spaces = input('Are all  lines with {:d} leading spaces \'{:s}\' blocks ? (Y/n) '.format(
                spaces_number, BLOCK_TYPES[block_type]))

        if( answer_spaces == 'n' or answer_spaces =='N' ):
            print('You said no: we will ask you again next time.')
            remember_spaces = False
        else:
            print('You said yes: ' +
                  'every new block with {:d} leading spaces '.format(spaces_number) +
                  'will now be considered a \'{:s}\'.'.format(BLOCK_TYPES[block_type]) )
            remember_spaces = True

        validated = True
        answer = input('Are you sure? (Y/n) ')
        if( answer == 'n' or answer =='N' ):
            validated = False

    if( remember_spaces ):
        usual_spaces[block_type].append(spaces_number)

    return block_type



# In[53]:

# DA big loop

usual_spaces=[[] for i in range(len(BLOCK_TYPES))]

# Ici on définit les variables qu'on remplira de texte
is_intro = True
movie_script = []
intro = []
last_line_type = -1
last_character = ''
text = []
characters=[]


print()
print()
print("Here we go for some kickass movie script parsing!")
print()
print()
print("Start by telling me when the introduction will end.")

for block in script_text.descendants:
    # Si block est une instance de bs4.Tag, il est entouré de balises HTML
    # Le prochain block contiendra le même texte sans les balises
    # Donc on continue sans parser ce bloc
    if(isinstance(block, Tag)):
        continue

    # UnicodeDammit converts any string to UTF-8
    # does not work so well
    block = UnicodeDammit(block, soup.original_encoding).unicode_markup
    # remove leading and ending end of lines
    block = block.strip('\n')

    # if the block doesn't have any text, skip it
    if( re.search('\w', block) == None ):
        continue

    # bs4 ne coupe pas toujours bien les différents blocs
    # Mieux vaut donc redécouper par paragraphe et les traiter un à un
    for line in block.split('\n'):
        stripped_line = line.strip(' \n\t\r')
        if( re.search('\w', line) == None ):
            continue

        print('------------------------------ Begin line ------------------------------')
        print(line)
        print('                        ------- End line -------')

        if( is_intro ):
            print()
            answer = input("Is that still part of the intro? (Y/n) ")

            if(answer == 'n' or answer == 'N'):
                is_intro = False
                movie_script.append({
                    'type': 'introduction',
                    'text': '\n'.join(intro)})

                print(movie_script[-1])
            else:
                print("OK")
                print()
                intro.append(stripped_line)
                continue


        line_type = get_line_type(line, stripped_line, usual_spaces, characters)
        print("The last line was interpreted as '{}'".format(BLOCK_TYPES[line_type]))
        print()

        if(last_line_type == -1 # -1 = not initialized
           or last_line_type == line_type):
            text.append(stripped_line)
        else:
            if(last_line_type == CHARACTER):
                last_character='\n'.join(text)
                if not last_character in characters:
                    characters.append(last_character)
            elif(last_line_type == SPEECH):
                movie_script.append({
                    'type': BLOCK_TYPES[last_line_type],
                    BLOCK_TYPES[CHARACTER]: last_character,
                    'text': '\n'.join(text)})
                print('We just parsed this JSON block:')
                print(movie_script[-1])
            else:
                movie_script.append({
                    'type': BLOCK_TYPES[last_line_type],
                    'text': '\n'.join(text)})
                print('We just parsed this JSON block:')
                print(movie_script[-1])
            text=[stripped_line]

        last_line_type = line_type

        #print('block_type={:d}'.format(line_type))
        #print('usual spaces:')
        #print(usual_spaces)
        #print('This line is a \'{:s}\'.'.format(BLOCK_TYPES[line_type]))

        print()

    print()
    print()

movie_script.append({
    'type': BLOCK_TYPES[line_type],
    'text': '\n'.join(text)})

print('We just parsed this JSON block:')
print(movie_script[-1])
print()
print()

script['movie_script'] = movie_script

print('All done, biiiiitch!')


# In[64]:

print(flush=True)
print(flush=True)
print('(Our current directory is: {})'.format(os.getcwd()), flush=True)
out_filename = input('Now, gimme an output filename: ')

try:
    fd = open(out_filename, 'w')
    json.dump(script, fd, indent=True)
    print('We just successfully wrote {}\'s script as JSON to {} .'.format(script['movie_title'], fd.name))
    print('Bravo!')
except:
    print("Shit happened: ", sys.exc_info()[0])
finally:
    fd.close()
    print()
    print('This script was made by Adrien Luxey for Pierre Peigné-Leroy in 2016.')
    print('It\'s free to use and all, go check our licence.')

