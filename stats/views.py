from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import matplotlib.pyplot as plt, mpld3
import mysql.connector
from . import dbcreds

def index(request):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    '''
    labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
    sizes = [15, 30, 45, 10]
    explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    g = mpld3.fig_to_html(fig1)'''
    cnx = mysql.connector.connect(user=dbcreds.user,password= dbcreds.pwd,host=dbcreds.host,database=dbcreds.db)
    cursor = cnx.cursor()
    query = 'select id_user from hpcc_job_table'
    cursor.execute(query)
    user_dict={}
    for user in cursor:
        user = user[0]
        if user in user_dict:
            user_dict[user] +=1
        else:
            user_dict[user]=1

    labels=[user for user in user_dict]
    sizes= [user_dict[user] for user in user_dict]
    fig,ax = plt.subplots()
    ax.pie(sizes,labels=labels,startangle=90)
    ax.axis('equal')



    cnx.close()
    g = mpld3.fig_to_html(fig)
    return render(request, 'stats/graphic.html', {'graph':g})