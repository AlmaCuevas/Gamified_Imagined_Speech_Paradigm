# Gamified version for an Imagined Speech research protocol
 
Brain Computer Interfaces are a fast-growing technology that transform human thoughts into real-world actions. With this **gamified acquisition paradigm**, you will be able to register imagined speech of four different command words. Use these commands to guide the character out of the maze!

![ExperimentalParadigm](https://github.com/AlmaCuevas/Gamified_Imagined_Speech_Paradigm/assets/134006734/67995ca5-4294-4055-869e-54960e4ea529)

Suspecting that your acquisition paradimg may affect the user's concentration or alertness? Try this paradigm! Our results have showned an overall significant improvement of user experience compared to traditional paradigms

## Traditional = Reading words in a screen with a tempo
![UEQ_Traditional](https://github.com/AlmaCuevas/Gamified_Imagined_Speech_Paradigm/assets/134006734/61b429f2-26ed-45cb-ac0a-19fcc4043cf1)

## Experimental = Gamified Version
![UEQ_Experimental](https://github.com/AlmaCuevas/Gamified_Imagined_Speech_Paradigm/assets/134006734/1de05371-e23f-429f-8e36-369a1c7e3408)

**Results Based on User Experience Questionnaire*

## Description of files:
* board.py = boards for each level, start positions and sequence order
* requirements.txt = the packages required
* tutorial.py = dynamic of the experiment in the form of a tutorial
* paradigm_si.py = dynamic of the experiment

In assets/extras_images you'll find the visual resources.

This code was inspired from https://github.com/plemaster01/PythonPacman, for a tutorial you can check: https://www.youtube.com/watch?v=9H27CimgPsQ&t=684s

## How to run
1. Make sure to install all the files on *requirements.txt*
2. Run the file *paradigm_si.py*. An LSL outlet will be created with the name "PyGame - Experimental Paradigm". The game will start 20 seconds later.
3. Start your EEG recording using your preferred equipment. Make sure to link it to the generated LSL outlet.
4. Run the whole videogame (approx. 12min). We recommend you write down every vocalized word by the user to identify errors.

*Extra Points*
- We suggest running *tutorial.py* before anything else, so you get accostumed to the game and specially the use of the commands. No connection is needed for performing the tutorial.
- If you do not have an EEG, you can still run the program and examine the game.


# Resources
[Database](https://data.mendeley.com/datasets/57g8z63tmy/1)
[Traditional Imagined Speech Paradigm](https://github.com/EdgarAgRod/Traditional_Imagined_Speech_Paradigm)
[Imagined Speech Preprocessing](https://github.com/EdgarAgRod/Imagined_Speech_Preprocessing)
