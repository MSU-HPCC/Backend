import matplotlib
matplotlib.use('Agg')
from django.shortcuts import render
import os
# using this solution to avoid windows vs unix slashes
from pathlib import Path
# Create your views here.
from django.http import HttpResponse
import matplotlib.pyplot as plt, mpld3


import matplotlib.dates as mdates

from datetime import datetime

import pyslurm
import numpy as np

from django.views.generic import TemplateView
def index(request):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    '''
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
    '''
    return HttpResponse("This is the index page")



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


    AllJobs= pyslurm.slurmdb_jobs().get()
    DateDict={}
    for jobid in AllJobs:
        startTime = AllJobs[jobid]['start']
        date = datetime.utcfromtimestamp(startTime).strftime('%Y-%m-%d')

        if int(startTime) > 0:
            if date in DateDict:
                DateDict[date]+=1
            else:
                DateDict[date]=1

    dates = [(date,DateDict[date]) for date in DateDict]
    x= sorted(dates)

    xDates= [pair[0] for pair in x ]
    y = [pair[1] for pair in x ]
    fig, ax = plt.subplots()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))


    ax.plot(xDates, y)

    plt.xlabel("Dates")
    plt.ylabel("Jobs Submitted")
    plt.title("Jobs Submitted In 2018")
    plt.gcf().autofmt_xdate()
    g = mpld3.fig_to_html(fig)




    data_folder = Path("/static/images/")
    path = data_folder / "submission-stats.png"
    path = "/static/images/submission-stats.png"
    return render(request, 'stats/graphic.html', {'graph': g})
    #return render(request, 'stats/SubmissionGraphic.html')


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

    AllJobs= pyslurm.slurmdb_jobs().get()
    ErrorDict= {}
    for jobid in AllJobs:
        user = AllJobs[jobid]['user']
        errorCode= AllJobs[jobid]['exit_code']
        if int(errorCode) != 0:
            if user in ErrorDict:
                ErrorDict[user]+=1
            else:
                ErrorDict[user]=1
    TotalErrors= sum(ErrorDict.values())
    labels= [ user for user in ErrorDict]
    sizes=[ErrorDict[user] for user in ErrorDict]
    fig, ax = plt.subplots()
    ax.pie(sizes, autopct='%1.0f%%', startangle=90)
    ax.axis('equal')
    plt.title("Failed Jobs by user id in group 2000")
    plt.legend(labels)

    g = mpld3.fig_to_html(fig)


    data_folder = Path("/static/images/")
    path = data_folder / "failed-jobs.png"
    return render(request, 'stats/graphic.html', {'graph': g})
    #return render(request, 'stats/FailedJobs.html')

def MajorUsers(request):
    #path = STATIC_ROOT = os.path.join(os.getcwd(), '\\static\\images\\user-jobs-submitted.png')
    #pngPath = image_data = open(path, "rb").read()

    AllJobs = pyslurm.slurmdb_jobs().get()
    userSubDict={}
    for jobid in AllJobs:
        user= AllJobs[jobid]['user']
        if user in userSubDict:
            userSubDict[user]+=1
        else:
            userSubDict[user]=1


    labels = [user for user in userSubDict]

    sizes = [userSubDict[user] for user in userSubDict]
    fig, ax = plt.subplots()
    ax.pie(sizes, autopct='%1.0f%%', startangle=90)
    ax.axis('equal')
    plt.title("Failed Jobs by user id in group 2000")
    plt.legend(labels)

    g = mpld3.fig_to_html(fig)
    data_folder = Path("/static/images/")
    path = data_folder / "user-jobs-submitted.png"

    return render(request, 'stats/graphic.html',{'graph': g})

def AvgWait(request):

    AllJobs= pyslurm.job().get()
    WaitTimes=[]
    startTimes=[]
    for jobid in AllJobs:
        submitTime = AllJobs[jobid]['submit_time']
        startTime= AllJobs[jobid]['start_time']
        waitTime = startTime-submitTime
        startTimes.append(startTime)

        if waitTime <= 0:
            pass
        else:
            WaitTimes.append(waitTime)
    if len(WaitTimes)!=0:
        avgWait= sum(WaitTimes)/len(WaitTimes)
    else:
        avgWait=0
    totalJobs = len(AllJobs)
    ### get dict of all jobs submitted by date

    SubDays={}


    for start in startTimes:
        startDate = datetime.utcfromtimestamp(start).strftime('%Y-%m-%d')
        if startDate in SubDays:
            SubDays[startDate]+=1
        else:
            SubDays[startDate]=1

    now = datetime.now()
    currentMonth=int(now.month)
    print(currentMonth)
    JobsThisMonth=0
    for date in SubDays:
        month = int(date.split('-')[1])
        print(month)
        if month==currentMonth:
            JobsThisMonth+= SubDays[date]
    print("jobs this month = "+str(JobsThisMonth))
    print(SubDays)
    weeks = int(now.isocalendar()[1])
    avgJobsPerWeek= len(AllJobs)/weeks

    info =[avgWait,totalJobs,JobsThisMonth,avgJobsPerWeek]
    categories=['Average Wait Time','Total Jobs Submitted','Jobs Submitted this Month','Average Jobs Submitted Per Week']
    Table= zip(categories,info)
    return render(request, 'stats/table.html',{'info':Table, 'range': range(len(info))})




'''
def plot1d():
    x_data = np.arange(0, 120, 0.1)
    trace1 = go.Scatter(
        x=x_data,
        y=np.sin(x_data)
    )

    data = [trace1]
    layout = go.Layout(
        # autosize=False,
        # width=900,
        # height=500,

        xaxis=dict(
            autorange=True
        ),
        yaxis=dict(
            autorange=True
        )
    )
    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return plot_div

class Plot1DView(TemplateView):
    template_name = "stats/plot.html"

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(Plot1DView, self).get_context_data(**kwargs)
        context['plot'] = plot1d()
        return context

class Graph(TemplateView):
    template_name = 'stats/plot.html'

    def get_context_data(self, **kwargs):
        context = super(Graph, self).get_context_data(**kwargs)

        x = [-2,0,4,6,7]
        y = [q**2-q+3 for q in x]
        trace1 = go.Scatter(x=x, y=y, marker={'color': 'red', 'symbol': 104, 'size': 10},
                            mode="lines",  name='1st Trace')

        data=go.Data([trace1])
        layout=go.Layout(title="Meine Daten", xaxis={'title':'x1'}, yaxis={'title':'x2'})
        figure=go.Figure(data=data,layout=layout)
        div = opy.plot(figure, auto_open=False, output_type='div')

        context['plot'] = div

        return context
'''
