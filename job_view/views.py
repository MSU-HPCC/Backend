from django.shortcuts import render
from . import dbcreds
from django.http import HttpResponse
from .contrib import Admin_Stats_SQL

# Create your views here.

def jobs(request):
    import mysql.connector
    cnx = mysql.connector.connect(user=dbcreds.user, password=dbcreds.pwd, host=dbcreds.host,
                                 database=dbcreds.db)

    cursor = cnx.cursor()
    query = "SELECT id_user, job_db_inx, job_name, cpus_req  FROM hpcc_job_table WHERE id_user='"+ str(request.user) + "';"
    cursor.execute(query)
    result = "<html><body>"
    #jobs =['one', 'five', 'ten']
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
    return render(request, 'job_view/jobs.html', {'jobs': jobs, 'user': request.user,})


def adminJobs(request, user):
    import mysql.connector
    cnx = mysql.connector.connect(user=dbcreds.user, password=dbcreds.pwd, host=dbcreds.host,
                                 database=dbcreds.db)
    if (request.user.id == 1):
        cursor = cnx.cursor()
        query = "SELECT id_user, job_db_inx, job_name, cpus_req  FROM hpcc_job_table WHERE id_user='"+ user + "';"
        cursor.execute(query)
        result = "<html><body>"
        #jobs =['one', 'five', 'ten']
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
        return render(request, 'job_view/adminJobs.html', {'jobs': jobs, 'urlUser':user,})
    else:
        return render(request, '../templates/error_pages/403.html')


def groupJobs(request):
    u = "user01"
    x = Admin_Stats_SQL.group_access(u)
    y = x.group_jobs()
    return render(request, 'job_view/groupJobs.html', {'jobs': y, 'urlUser': u})
