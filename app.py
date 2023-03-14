import json

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bs4 import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, RadioField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
date = datetime.now()
app.config['SECRET_KEY'] = 'dfghj765$%^Kjhgd'

class LoginForm(FlaskForm):
    userLogin = StringField('Nazwa użytkownika: ', validators=[DataRequired()])
    userPass = PasswordField('Hasło: ', validators=[DataRequired()])
    submit = SubmitField('Zaloguj')

class AddSubject(FlaskForm):
    subject = StringField("Nazwa przedmiotu", validators=[DataRequired()])
    submit = SubmitField('Dodaj')

class AddGrade(FlaskForm):
    subject = SelectField('Wybierz przedmiot', choices=str)
    term = RadioField('Wybierz semestr:', choices=[('term1', 'Semestr 1'), ('term2', 'Semestr 2')])
    category = SelectField('Wybierz kategorię:', choices=[('answer', 'Odpowiedź'), ('quiz', 'Kartkówka'), ('test', 'Sprawdzian')])
    grade = SelectField('Wybierz ocenę', choices=[
        (6, 'Celujący'),
        (5, 'Bardzo dobry'),
        (4, 'Dobry'),
        (3, 'Dostateczny'),
        (2, 'Dopuszczający'),
        (1, 'Niedostateczny')
    ])
    submit = SubmitField('Dodaj')

users = {1: {'userLogin': 'bwalczyk', 'userPass': 'Qwerty123!', 'fname': 'Bartosz', 'lname': 'Walczyk'}}

def countAverage(subjectValue, termValue):
    with open('data/grades.json') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
    sumGrades = 0
    length = 0
    if subjectValue == "" and termValue == "":
        for subject, terms in grades.items():
            for term, categories in terms.items():
                for category, grades in categories.items():
                    if category == "answer" or category == "quiz" or category == "test":
                        for grade in grades:
                            sumGrades += grade
                            length += 1
    elif termValue == "":
        for subject, terms in grades.items():
            if subject == subjectValue:
                for term, categories in terms.items():
                    for category, grades in categories.items():
                        if category == "answer" or category == "quiz" or category == "test":
                            for grade in grades:
                                sumGrades += grade
                                length += 1
    else:
        for subject, terms in grades.items():
            if subject == subjectValue:
                for term, categories in terms.items():
                    if term == termValue:
                        for category, grades in categories.items():
                            if category == "answer" or category == "quiz" or category == "test":
                                for grade in grades:
                                    sumGrades += grade
                                    length += 1
    if length != 0:
        return round(sumGrades/length, 2)
    else:
        return 0

def getEndangered():
    with open('data/grades.json') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
    subjectsString = ""
    for subject, terms in grades.items():
        if countAverage(subject, "") < 2:
            if subjectsString == "":
                subjectsString = subject
            else:
                subjectsString = subjectsString + ", " + subject
    if subjectsString == "":
        subjectsString = "brak zagrożeń"
    return subjectsString

def getHighest():
    with open('data/grades.json') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
    subjectsArray = []
    for subject, terms in grades.items():
        avg = countAverage(subject, "")
        subjectsArray.append({"subject": subject, "average": avg})
    subjectsArray.sort(key=sortArray)
    while len(subjectsArray) > 2:
        subjectsArray.pop()
    return subjectsArray

def getInterim(selectedSubject, selectedTerm):
    with open('data/grades.json') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
    sumGrades = 0
    length = 0
    for subject, terms in grades.items():
        if subject == selectedSubject:
            for term, categories in terms.items():
                if term == selectedTerm:
                    for category, grades in categories.items():
                        if category == "answer" or category == "quiz" or category == "test":
                            for grade in grades:
                                sumGrades += grade
                                length += 1
    if length == 0:
        return 0
    avg = sumGrades / length
    if avg >= 5.4:
        return 6
    if avg >= 4.6:
        return 5
    if avg >= 3.6:
        return 4
    if avg >= 2.6:
        return 3
    if avg >= 2.0:
        return 2
    return 1


def sortArray(k):
    return -k['average']

lstObj = [{'value' : -1},{'value' : 200},{'value' : 1},{'value' : 100},{'value' : 50}]



@app.route('/')
def index():
    return render_template('index.html', title='Strona główna')

@app.route('/login', methods=['POST', 'GET'])
def login():
    login = LoginForm()
    if login.validate_on_submit():
        userLogin = login.userLogin.data
        userPass = login.userPass.data
        if userLogin == users[1]['userLogin'] and userPass == users[1]['userPass']:
            session['userLogin'] = userLogin
            return redirect('dashboard')
    return render_template('login.html', title='Logowanie', login=login, userLogin=session.get('userLogin'))

@app.route('/logout')
def logout():
    session.pop('userLogin')
    return redirect('login  ')

@app.route('/dashboard')
def dashboard():
    with open('data/grades.json') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
    return render_template('dashboard.html', title='Dashboard', userLogin=session.get('userLogin'), date=date, grades=grades, categories=grades, countAverage=countAverage, getEndangered=getEndangered, getHighest=getHighest, getInterim=getInterim)

@app.route('/addSubject', methods=['POST', 'GET'])
def addSubject():
    addSubject = AddSubject()
    if addSubject.validate_on_submit():
        with open('data/grades.json', encoding='utf-8') as gradesFile:
            grades = json.load(gradesFile)
            gradesFile.close()
            subject = addSubject.subject.data
            grades[subject] = {
                'term1': {'answer': [], 'quiz': [], 'test': [], 'interim': 0},
                'term2': {'answer': [], 'quiz': [], 'test': [], 'interim': 0, 'yearly': 0}
            }
            with open('data/grades.json', 'w', encoding='utf-8') as gradesFile:
                json.dump(grades, gradesFile)
                gradesFile.close()
                flash('Dane zapisane poprawnie')
                return redirect('addSubject')
    return render_template('addSubject.html', title="Dodaj przedmiot", userLogin=session.get('userLogin'), date=date, addSubject=addSubject)

@app.route('/addGrade', methods=['POST', 'GET'])
def addGrade():
    addGradeForm = AddGrade()
    with open('data/grades.json') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
        addGradeForm.subject.choices = [subject for subject in grades]
        if addGradeForm.validate_on_submit():
            subject = addGradeForm.subject.data
            term = addGradeForm.term.data
            category = addGradeForm.category.data
            grades[subject][term][category].append(int(addGradeForm.grade.data))
            with open('data/grades.json', 'w', encoding='utf-8') as gradesFile:
                json.dump(grades, gradesFile)
                gradesFile.close()
                flash('Dane zapisane poprawnie')
                return redirect('addGrade')
    return render_template('addGrade.html', title="Dodaj ocenę", userLogin=session.get('userLogin'), date=date, addGradeForm=addGradeForm)

if __name__ == '__main__':
    app.run(debug=True)

