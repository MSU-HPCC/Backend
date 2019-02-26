from django.shortcuts import render
import os
# Create your views here.
from django.http import HttpResponse
import matplotlib.pyplot as plt, mpld3
import mysql.connector

import matplotlib.dates as mdates
from . import dbcreds
from datetime import datetime
from . import  dbcreds
def index(request):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:

    cnx = mysql.connector.connect(user=dbcreds.user,password= dbcreds.pwd,host=dbcreds.host,database=dbcreds.db)
    cursor = cnx.cursor()
    query = 'select id_user from hpcc_big.msuhpcc_job_table limit 100000;'
    cursor.execute(query)
    user_dict={}
    for user in cursor:
        user = user[0]
        if user in user_dict:
            user_dict[user] +=1
        else:
            user_dict[user]=1
    total = sum(user_dict.values())
    labels=[user for user in user_dict if user_dict[user] > total/100]
    sizes= [user_dict[user] for user in user_dict if user_dict[user] > total/100]
    fig,ax = plt.subplots()
    ax.pie(sizes,labels=labels,startangle=90)
    ax.axis('equal')



    cnx.close()
    g = mpld3.fig_to_html(fig)


    return render(request, 'stats/graphic.html', {'graph':g})



def JobSubStats(request):
    '''
    cnx = mysql.connector.connect(user=dbcreds.user, password=dbcreds.pwd, host=dbcreds.host, database=dbcreds.db)
    cursor = cnx.cursor()

    query = 'select time_submit from hpcc_big.msuhpcc_job_table;'
    cursor.execute(query)
    date_dict = {}


    for line in cursor:
        secs = int(line[0])

        FullTime = datetime.utcfromtimestamp(secs).strftime('%Y-%m-%d %H:%M:%S')
        date = FullTime.split()[0]
        if date in date_dict:
            date_dict[date] += 1
        else:
            date_dict[date] = 1

    cursor.close()
    cnx.close()

    dates = [date for date in date_dict]

    x = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]
    y = [date_dict[date] for date in date_dict]
    fig, ax = plt.subplots()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

    ax.plot(x,y)

    plt.xlabel("Dates")
    plt.ylabel("Jobs Submitted")
    plt.title("Jobs Submitted In 2018")
    plt.gcf().autofmt_xdate()
    g = mpld3.fig_to_html(fig)
    '''
    #return render(request, 'stats/graphic.html', {'graph': g})
    return render(request, 'stats/SubmissionGraphic.html')


def JobFailure(request):
    '''
    cnx = mysql.connector.connect(user=dbcreds.user, password=dbcreds.pwd, host=dbcreds.host, database=dbcreds.db)
    cursor = cnx.cursor()
    query = 'select id_user,exit_code from hpcc_big.msuhpcc_job_table where id_group=2000 ;'
    cursor.execute(query)
    errorDict = {}
    for line in cursor:
        user = int(line[0])
        code = int(line[1])
        # if we have an error
        if code != 0:
            # increment users errors if theyre already in the dictionary
            if user in errorDict:
                errorDict[user] += 1
            # if they arent in the dictionary the user=1
            else:
                errorDict[user] = 1

    i = 0

    total = sum(errorDict.values())
    labels = [user for user in errorDict]
    sizes = [errorDict[user] for user in errorDict if errorDict[user] > total / 100]
    fig, ax = plt.subplots()
    ax.pie(sizes,autopct='%1.0f%%', startangle=90)
    ax.axis('equal')
    plt.title("Failed Jobs by user id in group 2000")
    plt.legend(labels)
    cnx.close()
    cursor.close()
    g = mpld3.fig_to_html(fig)
    '''

    return render(request, 'stats/FailedJobs.html')

def MajorUsers(request):
    path = STATIC_ROOT = os.path.join(os.getcwd(), 'static\\images\\user-jobs-submitted.png')
    #pngPath = image_data = open(path, "rb").read()

    return render(request, 'stats/MajorUserJobs.html',{'graph': path})
