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
    cols = ['id_user', 'job_db_inx', 'job_name', 'cpus_req']
    itr = 0
    for col in cols:
        cols[itr] = (col, itr)
        itr += 1
    return render(request, 'job_view/jobs.html', {'jobs': jobs, 'user': request.user, 'cols': cols, })


def adminJobs(request, user):
    import mysql.connector
    cnx = mysql.connector.connect(user=dbcreds.user, password=dbcreds.pwd, host=dbcreds.host,
                                 database=dbcreds.db)
    if (request.user.id == 1):
        cursor = cnx.cursor()
        query = "SELECT id_user, job_db_inx, job_name, cpus_req  FROM hpcc_job_table WHERE id_user='" + user + "';"
        cursor.execute(query)
        result = "<html><body>"
        jobs = []
        idx = 0
        for (userid, jobidx, jobname, cpusreq) in cursor:
            jobObj = {'userid': userid,
                      'jobidx': jobidx,
                      'jobname': jobname,
                      'cpusreq': cpusreq,
                     }
            jobs.append([userid, jobidx, jobname, cpusreq])

        result += "</body></html>"
        cnx.close()
        cols = ['id_user', 'job_db_inx', 'job_name', 'cpus_req']
        itr = 0
        for col in cols:
            cols[itr] = (col, itr)
            itr += 1
        return render(request, 'job_view/adminJobs.html', {'jobs': jobs, 'urlUser': user, 'cols': cols, })
    else:
        return render(request, '../templates/error_pages/403.html')


def groupJobs(request):
    u = "user05"
    x = Admin_Stats_SQL.group_access(u)
    y = x.group_jobs()
    cols = ['job_db_inx', 'mod_time', 'job_name', 'id_job', 'id_user', 'id_group', 'kill_requid', 'mem_req', 'nodelist', 'nodes_alloc', 'node_inx', 'state', 'timelimit', 'time_submit', 'time_eligible', 'time_start', 'time_end', 'time_suspended', 'work_dir']
    itr = 0
    for col in cols:
        cols[itr] = (col,itr)
        itr += 1
    return render(request, 'job_view/groupJobs.html', {'jobs': y, 'urlUser': u, 'cols': cols, })

def filterColumns(request, id_user=1, job_db_idx=1, job_name=1, cpus_req=1):
    if (id_user == 1):
        id_user = 'id_user'

    return render(request, 'job_view/adminJobs.html', {'jobs': jobs, 'urlUser': user, 'cols': cols, })
