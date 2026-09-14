audio to midi converter



detects transients and creates midi notes.





to run:

- install python 3.11 and ensure add to Path is checked

- install pip package manager


- place the audio track you want to analyse in the same folder

- open a command prompt window and direct it to this folder

you can do this by going to the address bar on windows and typing cmd and hitting enter



- install dependencies with pip install -r requirements.txt


- run by typing
  python main.py your\_track\_name.mp3
  and hitting enter		





You can also drag a file anywhere on your system into the command prompt after typing python main.py or selecting a file, right clicking copy as path and pasting in





press Z to toggle zooming



your midi track will be saved a .mid file


to close the app, hit ctrl-c or the x in the top right






to do:

&#x09;add FFT for frequency dependent notes



&#x09;add realtime input and output(probably an exe written in C/C++ as python is too slow)
	allow audio piping from other applications eg. reaper, logic, cubase, etc. using 



&#x09;add drum hit detector (toms, kick, cymbal, hi-hat, snare)



&#x09;add DMX output for lighting console


&#x09;add stem separator (probably some ML)

