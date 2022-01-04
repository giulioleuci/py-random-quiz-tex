import jinja2
from jinja2 import Template
import os
import pandas as pd
import itertools
import random
from random import shuffle
import numpy as np
import matplotlib.pyplot as plt
import pprint
import sys
import argparse

pp = pprint.PrettyPrinter(indent=4)

latex_jinja_env = jinja2.Environment(
    block_start_string = '\BLOCK{',
    block_end_string = '}',
    variable_start_string = '\VAR{',
    variable_end_string = '}',
    comment_start_string = '\#{',
    comment_end_string = '}',
    line_statement_prefix = '%%',
    line_comment_prefix = '%#',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.'))
    )

# DEFINE FUNCTIONS

def preamble(name,
             title,
             classes,
             date,
             time):
    d = """
\\documentclass[a4paper,11pt]{exam}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage{lmodern}
\\usepackage[italian]{babel}
\\usepackage{amsfonts}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{fullpage}
\\usepackage{graphicx}
\\usepackage{wrapfig}
\\usepackage{siunitx}
\\usepackage{physics}
\\usepackage{multicol}
\\usepackage{geometry}
\\usepackage{microtype}
\\usepackage{siunitx}
\\usepackage{physics}
\\usepackage{multicol}

\\newcommand{\\um}[2]{\\SI[output-decimal-marker={,}]{#1}{#2}}\\usepackage{wrapfig}

\\geometry{top=2cm, bottom=2cm, left=2cm, right=1.5cm}

\\pagestyle{headandfoot}
\\firstpageheadrule
\\runningheadrule
\\firstpageheader{\\VAR{name}}{\\VAR{title}}{\\VAR{classes}}
\\firstpagefooter{\\VAR{date}}{\\VAR{time}}{}
\\runningfooter{\\VAR{date}}{\\VAR{time}}{}
\\runningheader{\\VAR{name}}{\\VAR{title}}{\\VAR{classes}}

\\begin{document}

    """
    return latex_jinja_env.from_string(d).render(name=name,
                                                 title=title,
                                                 classes=classes,
                                                 date=date,
                                                 time=time)

def start_model(text_before_questions=''):
    d = '''
\\VAR{text_before_questions}
\\begin{questions}

    '''
    return latex_jinja_env.from_string(d).render(text_before_questions=text_before_questions)

def end_model():
    d = '''
\\end{questions}

    '''
    return d

def new_model():
    return '''
    \\newpage
    
    '''

def question(question='question',
             choise1='choise1',
             choise2='choise2',
             choise3='choise3',
             choise4='choise4'):
    d = '''
\\question \\VAR{question}
\\begin{oneparchoices}
  \\choice \\VAR{choise1}
  \\choice \\VAR{choise2}
  \\choice \\VAR{choise3}
  \\choice \\VAR{choise4}
\\end{oneparchoices}

    '''
    return latex_jinja_env.from_string(d).render(question=question,
                                                 choise1=choise1,
                                                 choise2=choise2,
                                                 choise3=choise3,
                                                 choise4=choise4)

def end_doc():
    d = '''
\\end{document}
    '''
    return d

 
##############################################################################################
############# CREATE DOC #####################################################################
##############################################################################################

def create_random_tests(questionnaire,
                        n_test,
                        point_correct,
                        point_missing,
                        point_incorrect,
                        name='',
                        title='',
                        classes='',
                        date='',
                        time='',
                        seed=0):

    filename = questionnaire.split('.')[0]
    
    random.seed(seed)   
    
    df = pd.ExcelFile(questionnaire)
    
    print('Creating... Please wait...')

    sheets = df.sheet_names

    n_questions = len(sheets)-1

    # variables for preamble and introduction
    parsed = df.parse(sheets[0], header=None).values
    name = parsed[0][0]
    title = parsed[1][0]
    classes = parsed[2][0]
    date = parsed[3][0]
    time = parsed[4][0]
    intro = parsed[5][0]

    questions_index = [x+1 for x in range(len(sheets[1:]))]

    # permutations of questions
    
    all_quest = [list(np.random.permutation(questions_index)) for x in range(n_test*1000)] # 1000 for SAFE
    all_quest = list(k for k,_ in itertools.groupby(all_quest))
   
    all_perm = [x for x in list(itertools.permutations([0,1,2,3]))]
    
    randomy = []
    
    for q in all_quest:
        randomy.append([q,random.choices(all_perm,k=n_questions)])
        
    randomy = list(k for k,_ in itertools.groupby(randomy))
    randomy = random.choices(randomy,k=n_test+1)
    
    if len(randomy)<n_test:
        print('ERROR. Safe not enough safe :) on 169')
        return
    
    ### CREATE DOC

    # initialize document for print
    doc = preamble(name,
                   title,
                   classes,
                   date,
                   time)
    
    # cycle over models
    i = 0
    for random_q,random_a in randomy:
        # print introduction of test and the model number
        text_before_questions = '''
        \\begin{center} 
        \\fbox{\\fbox{\\parbox{17cm}{\\centering '''+intro+"\\\\\\ Modello n. "+str(i)+'''                       
        }}}
        \\end{center}'''
        doc+=start_model(text_before_questions)

        # cycle over questions (sheets from second to end)
        for sheet,ans in zip(random_q,random_a):
            q = df.parse(sheet).columns[0]+"\\\\\\"
            a = [x[0] for x in df.parse(sheet).values]
            doc+=question(q,a[ans[0]],a[ans[1]],a[ans[2]],a[ans[3]])

        # end model
        doc+=end_model()
        if i != len(randomy):
            doc+=new_model()
        i+=1
        
            
    # end document
    doc+=end_doc()

    # save tex
    with open(os.path.join(filename+'.tex'),'w') as file:
        file.write(doc)
        file.close()
        print(os.path.join(filename+'.tex')+'file was created.')

    # create pdfs
    if True: # da cambiare
        pdflatex = 'pdflatex '+filename+'.tex'+' > /dev/null'
        os.system(pdflatex)
        print(os.path.join(filename+'.pdf')+' was created compiling .tex file.')

    ### CREATE CORRECTORS
    
    i = 0

    label = {0:'A', 1:'B', 2:'C', 3:'D'}


    correctors = []

    questions = [x for x,_ in randomy]
    answers = [y for _,y in randomy]
    for random_q,random_a in randomy:
        random_q = [str(x) for x in random_q] # string of question order
        answers = []
        for ans in random_a:
            answers.append(label[ans.index(0)])
        #random_a = [label[x.index(0)] for x in random_a] # string of LETTERS of correct answers
        #number = str(i) # string o
        questions = '-'.join(random_q)
        answers = '-'.join(answers)
        correctors.append([i,questions,answers,point_correct,point_missing,point_incorrect,'','','','','','',''])
        i+=1

    #saving excel with correctors
    dfans = pd.DataFrame(correctors,columns=['number',
                                            'questions_order',
                                            'correct_answers',
                                            'point_correct', #default 4
                                            'point_missing', #default 1
                                            'point_incorrect', # default 0
                                            'student_name', #placehoder
                                            'student_answers', #placeholder
                                            'student_correct', #placeholder
                                            'student_missing', #placeholder
                                            'student_incorrect', #placeholder
                                            'student_score', #placeholder
                                            'student_mark' #placeholder
                                            ],index=None)

    col_to_students = ['number','correct_answers','point_correct','point_incorrect','point_missing']
    dfans[col_to_students].to_excel(filename+'_correctors_for_students.xlsx', index=False)
    dfans.to_excel(filename+'_correctors.xlsx', index=False)
    print(filename+'_correctors_for_students.xlsx'+' was created.')
    print(filename+'_correctors.xlsx'+' was created.')
    print('Please use '+filename+'_correctors.xlsx'+' for grading tests.')
    
    return


##############################################################################################
############# GRADING ########################################################################
##############################################################################################

def grading_test(grade,
                 report,
                 save):
    
    filename = grade.split('.')[0]
    
    df = pd.read_excel(grade)

    students_correct = []
    students_missing = []
    students_incorrect = []
    students_point = []
    students_mark = []

    report = {}
    flag = True

    for row in df.iterrows():
        c = 0
        m = 0
        i = 0
        
        row = row[1]
        
        correct = row['correct_answers'].split('-')
        student = row['student_answers'].split('-')
        order = row['questions_order'].split('-')
        
        p_correct = row['point_correct']
        p_missing = row['point_missing']
        p_incorrect = row['point_incorrect']
        
        # create reporting only once
        if flag:
            for e in order:
                if e not in report:
                    report[e] = {'correct':0,'missing':0,'incorrect':0}
        
        p_max = p_correct*len(correct)
        
        for ans,cor,q in zip(student,correct,order):
            if ans=='M':
                m+=1
                report[q]['missing']+=1
                continue
            if ans==cor:
                c+=1
                report[q]['correct']+=1
            else:
                i+=1
                report[q]['incorrect']+=1
        
        points = c*p_correct + m*p_missing + i*p_incorrect
        mark = 10*points/p_max # punteggio in decimi
        
        students_correct.append(c)
        students_missing.append(m)
        students_incorrect.append(i)
        students_point.append(points)
        students_mark.append(round(mark,2)) 
    
    n_students = len(students_correct)

    df['student_correct'] = students_correct
    df['student_missing'] = students_missing
    df['student_incorrect'] = students_incorrect
    df['student_score'] = students_point
    df['student_mark'] = students_mark
    
    df.to_excel(filename+'_correct_and_mark.xlsx', index=False)
    print(filename+'_correct_and_mark.xlsx'+' was created.')
    
    avg_mark = round(np.average(students_mark),2)

    # print report
    if report:
        print('********************')
        print('****** REPORT ******')
        print('Students analyzed: ',n_students)
        print('Students mark avg: ', avg_mark)
        print('Questions report')
        pp.pprint(report)
        
    # save report
    if save:
        with open(filename+'_report.txt','w') as text:
            original_stdout = sys.stdout
            sys.stdout = text
            print('********************')
            print('****** REPORT ******')
            print('Students analyzed: ',n_students)
            print('Students mark avg: ', avg_mark)
            print('Questions report')
            print(report)
            sys.stdout = original_stdout
    
        ### graphicx
        # marks
        plt.hist(students_mark)
        plt.xlim([1,10])
        plt.savefig(filename+'_report_marks.png')
        
        # questions
        quest = list(report.keys())
        quest.sort()
        correct = []
        missing = []
        incorrect = []
        correctmiss = [c+m for c,m in zip(correct,missing)]

        for q in quest:
            correct.append(report[q]['correct'])
            missing.append(report[q]['missing'])
            incorrect.append(report[q]['incorrect'])
            
        correctmiss = [c+m for c,m in zip(correct,missing)]
        
        fig, ax = plt.subplots()

        fig.set_figheight(10)
        fig.set_figwidth(15)

        ax.bar(quest, correct, 0.2,  label='corr', color='tab:blue')
        ax.bar(quest, missing, 0.2, bottom=correct,  label='miss', color='tab:gray')
        ax.bar(quest, incorrect, 0.2, bottom=correctmiss,  label='inc', color='tab:olive')

        ax.set_ylabel('Number')
        ax.set_xlabel('Question number in original order')
        ax.set_title('Report by question')
        ax.legend()

        plt.savefig(filename+'_report_question.png')
    
    return


##############################################################################################
############# MAIN ###########################################################################
##############################################################################################

if __name__ == "__main__":
    # sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

    parser = argparse.ArgumentParser(description='')
    
    parser.add_argument('-a', '--action', help='[c]rea o [v]aluta un test', required=True, default='c', choices = ['c', 'v'])
    parser.add_argument('-q', '--questionnaire', help='Nome del file contenente il test', required=False, default='test.xlsx')
    parser.add_argument('-n', '--number', help='Numero di test da creare', required=False, default=30)
    parser.add_argument('-c', '--correct', help='Punti per risposta corretta', required=False, default=4)
    parser.add_argument('-m', '--missing', help='Punti per risposta non data', required=False, default=1)
    parser.add_argument('-i', '--incorrect', help='Punti per risposta errata', required=False, default=0)  
    parser.add_argument('-g', '--grade', help='Nome del file contenente i test da valutare', required=False, default='test_correctors.xlsx')
    parser.add_argument('-r', '--report', help='Stampa a video i report della valutazione', required=False, type=bool, default=True)
    parser.add_argument('-s', '--save', help='Salva il report della valutazione', required=False, type=bool, default=True)
    parser.add_argument('-e', '--seed', help='Seme per la randomizzazione', required=False, default=47)  

    args = parser.parse_args()
    
    
    # crea
    if args.action=='c':
        create_random_tests(questionnaire=args.questionnaire,
                            n_test=args.number,
                            point_correct=args.correct,
                            point_missing=args.missing,
                            point_incorrect=args.incorrect,
                            seed=args.seed
                            )
        
        
    if args.action=='v':
        grading_test(grade=args.grade,
                     report=args.report,
                     save=args.save)
