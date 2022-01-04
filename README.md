# py-random-quiz-tex

## INTRODUZIONE ##################################################

PyQuiz è un generatore di test in LaTeX a risposta multipla randomizzati, con correzione e reporting automatici.

NB: lo script è stato testato UNICAMENTE su Ubuntu 20.04 munito della distribuzione Python Anaconda.

Per poter essere utilizzato il quiz da somministrare deve essere contenuto in un file in formato Excel (.xlsx) così strutturato:
- Primo foglio.
	- prima riga: nome del test (verrà stampato in alto a sinistra su ogni pagina dei pdf)
	- seconda riga: argomento del test (verrà stampato in alto al centro su ogni pagina dei pdf)
	- terza riga: classi coinvolte (verrà stampato in alto a destra su ogni pagina dei pdf)
	- quarta riga: data di svolgimento (verrà stampato in basso a sinistra su ogni pagina dei pdf)
	- quinta riga: tempo concesso (verrà stampato in basso al centro su ogni pagina dei pdf)
	- sesta riga: intestazione del test (verrà stampato all'inizio di ogni test, insieme al numero del modello del test)

- Ulteriori fogli (uno per domanda del quiz).
	- prima riga: testo della domanda in formato LaTeX
	- seconda riga: opzione di risposta corretta
	- terza riga: distrattore
	- quarta riga: distrattore
	- quinta riga: distrattore

Attenzione! A volte nella sintassi LaTeX è necessario aggiungere un'ulteriore \, controllare manualmente i file .tex qualora il risultato non fosse corretto o si generassero errori durante la compilazione dei file .tex.

I parametri che lo scrip accetta in ingresso si ottengono col comando "pyquiz.py -h":

```
pyquiz.py -h
usage: pyquiz.py [-h] -a {c,v} [-q QUESTIONNAIRE] [-n NUMBER] [-c CORRECT]
                 [-m MISSING] [-i INCORRECT] [-g GRADE] [-r REPORT] [-s SAVE]
                 [-e SEED]

optional arguments:
  -h, --help            show this help message and exit
  -a {c,v}, --action {c,v}
                        [c]rea o [v]aluta un test
  -q QUESTIONNAIRE, --questionnaire QUESTIONNAIRE
                        Nome del file contenente il test
  -n NUMBER, --number NUMBER
                        Numero di test da creare
  -c CORRECT, --correct CORRECT
                        Punti per risposta corretta
  -m MISSING, --missing MISSING
                        Punti per risposta non data
  -i INCORRECT, --incorrect INCORRECT
                        Punti per risposta errata
  -g GRADE, --grade GRADE
                        Nome del file contenente i test da valutare
  -r REPORT, --report REPORT
                        Stampa a video i report della valutazione
  -s SAVE, --save SAVE  Salva il report della valutazione
  -e SEED, --seed SEED  Seme per la randomizzazione
```

## GENERARE I FILE PDF ##################################################

Utilizzare le opzioni -a, -q, -n, -c, -m, -i, -e.

`-a`: l'azione da scegliere è "c", creare

`-q`: nome (o percorso) del file .xlsx contenente il test (default: test.xlsx)

`-n`: numero di test da generare (default: 30), ne viene generato uno aggiuntivo da usare come correttore da mettere agli atti della scuola

`-c`: punti da assegnare per ogni risposta esatta (default: 4)

`-m:` punti da assegnare per ogni risposta non data (default: 1)

`-i`: punti da assegnare per ogni risposta errata (default: 0)

`-e`: ignorare questa opzione nella maggioranza dei casi

Ad esempio, se voglio generare 60 test a partire dal file quizzone.xlsx, assegnando 1 punto per ogni risposta esatta, 0 per ogni risposta non data e -0,25 per ogni risposta errata, il comando da utilizzare è `pyquiz.py -a c -q quizzone.xlsx -c 1 -m 0 -i -0.25`.

Verrà generato il file .pdf "quizzone.pdf".

## INSERIRE LE RISPOSTE DEGLI STUDENTI ##################################################

Le risposte degli studenti vanno inseriti nel file .xlsx generato dal programma che termina per "correctors.xlsx". Il file "correctors_for_students.xlsx" contiene l'associazione quiz-risposta esatta che è possibile condividere con gli studenti immediatamente dopo l'erogazione del test.

Per inserire le risposte degli studenti usare tassativamente la struttura del file generato: inserire, in corrispondenza del numero del test desiderato, il nome dello studente in "student_name" e le sue risposte in "student_answers", in maiuscolo e separate da un trattino; inserire "M" per le risposte non date.

## CORREGGERE I QUIZ ##################################################

Utilizzare le opzioni -a, -g, -r, -s.

`-a`: l'azione da scegliere è "v", valutare

`-g`: nome (o percorso) del file contenente le risposte degli studenti (default: test_correctors.xlsx)

`-r`: permette di sopprimere la stampa a terminale degli esiti della correzione se impostato su False (default: True)

`-s`: permette di sopprimere il salvataggio su file degli esiti della correzione se impostato su False (default: True)

Una volta effettuata la correzione, verrà generato un file .xlsx terminante in correct_and_mark.xlsx, contenente per ogni modello di test (e quindi alunno!) il numero di risposte corrette, il numero di risposte non date, il numero di risposte errate, il punteggio grezzo totale e il punteggio espresso in decimi.

Vengono poi generati un file di testo contenente la media delle valutazioni e il numero di risposte corrette/non date/errata per ogni domanda del quiz (ordinante come nel foglio .xlsx iniziale: la domanda 1 è contenuta nel secondo foglio, la domanda 2 nel terzo, e così via), un grafico contenente uno stacked bar plot delle risposte per ogni domanda (ordinate come descritto prima), e un istogramma dei voti conseguiti dagli alunni.

