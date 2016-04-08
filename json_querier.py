#!/usr/bin/python3
# coding: utf-8

import os, sys, json, argparse

def input_from_list(question, choices):
    '''
    Asks the user to choose among a list (choices) given a question
    '''
    action = 0

    question += '\n'
    for i in range(len(choices)):
        question += '\t('+str(i)+') ' + choices[i] + '\n'
    print(question)

    validated = False
    while( validated == False ):
        try:
            action = int(input('? [0-{:d}] '.format(len(choices)-1)))
            while( action < 0 or action >= len(choices)):
                action = int(input('? [0-{:d}] '.format(len(choices)-1)))
        except ValueError:
            continue

        validated = True
        answer = input('You chose \'{:s}\', sure about that? (Y/n) '.format(
                choices[action]))
        if( answer == 'n' or answer =='N' ):
            validated = False

    return action

def input_string(question):
    '''
    Asks the user to type some input given a question
    '''
    user_input = ''
    answer = 'n'
    while (answer == 'n' or answer == 'N'):
        user_input = input(question + " (Leave blank to abort) ")
        if(user_input == ''):
            answer = input("You didn't type anything, abort? (Y/n)")
            if(answer != 'n' and answer != 'N'):
                print('You\'re loosing my time, you know?')
                break
        else:
            answer = input("You typed '{}', is that right? (Y/n)".format(user_input))

    return user_input

def extract_characters(script):
    '''
    Extracts the (unique) characters list from the script
    '''
    characters=[]
    for block in script['movie_script']:
        if(block['type'] == BLOCK_TYPES[SPEECH]):
            character = block['character']
            if not character in characters:
                characters.append(character)

    return characters

def extract_locations(script):
    '''
    Extracts the (unique) locations list from the script
    '''
    locations=[]
    for block in script['movie_script']:
        if(block['type'] == BLOCK_TYPES[LOCATION]):
            location = block['text']
            if not location in locations:
                locations.append(location)

    return locations

def extract_directions(script):
    '''
    Extracts the stage directions list from the script
    '''
    directions=[]
    for block in script['movie_script']:
        if(block['type'] == BLOCK_TYPES[DIRECTIONS]):
            directions.append(block['text'])

    return directions

def extract_speech_given_character(script, character, strict_match=False):
    '''
    Extracts the given character's utterances from the script

    If strict_match is True, we will only extract utterances that perfectly match (==) the parameter;
    otherwise, we will extract utterances whose character partly matches (in) the parameter.
    In both cases, the match is case-insensitive.

    Also asks the user wether one wants to keep the character's name before each utterance.
    '''

    keep_character_name = False
    answer = input('Do you want to keep the character\'s names? (y/N) ')
    if( answer == 'y' or answer =='Y' ):
        keep_character_name = True

    speeches=[]
    for block in script['movie_script']:
        if( block['type'] == BLOCK_TYPES[SPEECH] and
            (strict_match and (character.lower() == block['character'].lower()) or
             not strict_match and (character.lower() in block['character'].lower())) ):
            if( keep_character_name ):
                speeches.append(block['character'])
            speeches.append(block['text'])

    return speeches

def extract_all_characters_speech(script):
    '''
    Extracts all speeches from the script
    '''
    return extract_speech_given_character(script, '')

def extract_speech_asking_user(script):
    '''
    Extracts utterances by asking the user which character one wants to get

    Also asks wether the user wants a perfect (==) or partial (in) match.
    '''
    character = input_string('Please provide the name of the character: ')

    strict_match = False
    answer = input('Do you want utterances of this exact character (or any character that matches \'{}\')? (y/N) '.format(character))
    if( answer == 'y' or answer =='Y' ):
        strict_match = True

    return extract_speech_given_character(script, character, strict_match)

def extract_speech_using_characters_list(script):
    '''
    Extracts utterances by providing the user with the characters list

    Also asks wether the user wants a perfect (==) or partial (in) match.
    '''
    characters = sorted(extract_characters(script))
    character = characters[input_from_list('Please choose a character:', characters)]

    strict_match = False
    answer = input('Do you want utterances of this exact character (or any character that matches \'{}\')? (y/N) '.format(character))
    if( answer == 'y' or answer =='Y' ):
        strict_match = True

    return extract_speech_given_character(script, character, strict_match)

def extract_speech(script):
    '''
    Asks the user which speeches one wants to extract, and calls the appropriate function
    '''
    speech=[]

    choices = ['all characters',
               'give the character\'s name',
               'choose from the characters list']

    action = input_from_list("Which character speeches do you want to extract?", choices)

    if( action == 0 ):
        return extract_all_characters_speech(script)
    elif( action == 1 ):
        return extract_speech_asking_user(script)
    elif( action == 2 ):
        return extract_speech_using_characters_list(script)




helptext="""Welcome to the JSON Movie Script Querier!

With it, you can query a JSON file created with movie_script_parse.py to extract only the information you need.

It was written by Adrien Luxey for Pierre Peigné-Leroy in 2016."""

BLOCK_TYPES=['character', 'speech', 'stage direction', 'location']
CHARACTER=0
SPEECH=1
DIRECTIONS=2
LOCATION=3

ACTIONS=['extract all character names', 'extract some speech',
         'extract all stage directions', 'extract all locations']
EXTRACT_CHARACTERS=0
EXTRACT_SPEECH=1
EXTRACT_DIRECTIONS=2
EXTRACT_LOCATIONS=3


argparser= argparse.ArgumentParser(description=helptext)
argparser.add_argument('json_filename', metavar='json_filename', type=str, nargs='?',
        help='Location of the JSON file on your machine')
argparser.add_argument('out_filename', metavar='out_filename', type=str, nargs='?',
                       help='Location of the output file you want to make')

args=argparser.parse_args()

# loop until we get a valid json_filename

#json_filename="home/adrien/Programmation/Pierre/da-funky-movie-script-parser/outputs/the_fifth_element.json"
json_filename = ''
if( args.json_filename != None ):
    json_filename = args.json_filename
else:
    json_filename = input_string('Please provide the movie\'s JSON file path: ')

with open(json_filename) as fd:
    script = json.load(fd)

    print()
    print('You opened the movie \'{}\'.'.format(script['movie_title']))
    print()


    action = input_from_list("What do you want to do with it?", ACTIONS)

    if( action == EXTRACT_CHARACTERS ):
        result_list = extract_characters(script)
    elif( action == EXTRACT_SPEECH ):
        result_list = extract_speech(script)
    elif( action == EXTRACT_DIRECTIONS ):
        result_list = extract_directions(script)
    else: # EXTRACT_LOCATIONS
        result_list = extract_locations(script)

    result_string = '\n\n'.join(result_list)

    print(result_string)

    print()
    print()
    print()
    input('Happy? (Y/I don\'t really care) ')
    print()


    if( args.out_filename != None ):
        out_filename = args.out_filename
    else:
        print('(We\'re in {})'.format(os.getcwd()))
        out_filename = input_string('Where do you want to save that?')

    try:
        fd = open(out_filename, 'w')
        fd.write(result_string)
        print('We just successfully wrote what you asked to {} .'.format(script['movie_title'], fd.name))
        print('Bravo!')
    except:
        print("Shit happened: ", sys.exc_info()[0])
    finally:
        fd.close()
        print()
        print('This script was made by Adrien Luxey for Pierre Peigné-Leroy in 2016.')
        print('It\'s free to use and all, go check our licence.')
