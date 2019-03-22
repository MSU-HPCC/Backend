from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_protect
#import mysql.connector
#from job_view.dbcreds import *
@csrf_protect
@login_required
def index(request):
    cnx = mysql.connector.connect(user=user, password=pwd, host=host,
                                  database=db)

    cursor = cnx.cursor()
    query = "SELECT id_user, job_db_inx, job_name, cpus_req  FROM hpcc_job_table WHERE id_user='" + str(request.user) + "';"
    cursor.execute(query)
    result = "<html><body>"
    # jobs =['one', 'five', 'ten']
    jobs = []
    for (userid, jobidx, jobname, cpusreq) in cursor:
        jobObj = {'userid': userid,
                  'jobidx': jobidx,
                  'jobname': jobname,
                  'cpusreq': cpusreq,
                  }
        jobs.append((userid, jobidx, jobname, cpusreq))

    result += "</body></html>"
    cnx.close()
    return render_to_response('index.html', {'jobs': jobs, 'urlUser': request.user})
    return render_to_response('index.html')