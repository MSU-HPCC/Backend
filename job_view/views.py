from django.shortcuts import render
#from . import dbcreds
from django.http import HttpResponse
#from .contrib import Admin_Stats_SQL
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def jobs(request):
    import mysql.connector
    cnx = mysql.connector.connect(user=dbcreds.user, password=dbcreds.pwd, host=dbcreds.host,
                                 database=dbcreds.db)

    cursor = cnx.cursor()
    query = "SELECT id_user, job_name, nodelist, nodes_alloc, time_submit, time_start, time_end, exit_code, cpus_req FROM hpcc_job_table WHERE id_user='"+ str(request.user) + "';"
    cursor.execute(query)
    result = "<html><body>"
    #jobs =['one', 'five', 'ten']
    jobs = []
    for (id_user, job_name, nodelist, nodes_alloc, time_submit, time_start, time_end, exit_code, cpus_req) in cursor:
        jobs.append((id_user, job_name, nodelist, nodes_alloc, time_submit, time_start, time_end, exit_code, cpus_req))

    result += "</body></html>"
    cnx.close()
    cols = ['id_user', 'job_name', 'nodelist', 'nodes_alloc', 'time_submit', 'time_start', 'time_end', 'exit_code', 'cpus_req']
    itr = 0
    for col in cols:
        cols[itr] = (col, itr)
        itr += 1
    return render(request, 'job_view/jobs.html', {'jobs': jobs, 'user': request.user, 'cols': cols, })
    return HttpResponse("This is the jobs page")

def adminJobs(request, user):
    import mysql.connector
    cnx = mysql.connector.connect(user=dbcreds.user, password=dbcreds.pwd, host=dbcreds.host,
                                 database=dbcreds.db)
    if (request.user.id == 1):
        cursor = cnx.cursor()
        query = "SELECT id_user, job_name, nodelist, nodes_alloc, time_submit, time_start, time_end, exit_code, cpus_req FROM hpcc_job_table WHERE id_user='" + user + "';"
        cursor.execute(query)
        result = "<html><body>"
        jobs = []
        idx = 0
        for (id_user, job_name, nodelist, nodes_alloc, time_submit, time_start, time_end, exit_code, cpus_req) in cursor:
            jobs.append([id_user, job_name, nodelist, nodes_alloc, time_submit, time_start, time_end, exit_code, cpus_req])

        result += "</body></html>"
        cnx.close()
        cols = ['id_user', 'job_name', 'nodelist', 'nodes_alloc', 'time_submit', 'time_start', 'time_end', 'exit_code', 'cpus_req']
        itr = 0
        for col in cols:
            cols[itr] = (col, itr)
            itr += 1
        return render(request, 'job_view/adminJobs.html', {'jobs': jobs, 'urlUser': user, 'cols': cols, })
    else:
        return render(request, '../templates/error_pages/403.html')
    # return HttpResponse("this is the admin jobs")

@login_required
def groupJobs(request):
    u = "user05"
    x = Admin_Stats_SQL.group_access(u)
    y = x.group_jobs()

    cols = ['job_db_inx', 'mod_time', 'job_name', 'id_job', 'id_user', 'id_group', 'nodelist', 'nodes_alloc', 'time_submit', 'time_start', 'time_end', 'exit_code']
    itr = 0
    for col in cols:
        cols[itr] = (col,itr)
        itr += 1
    return render(request, 'job_view/groupJobs.html', {'jobs': y, 'urlUser': u, 'cols': cols, })
    # return  HttpResponse("this is the group jobs")

def filterColumns(request, id_user=1, job_db_idx=1, job_name=1, cpus_req=1):
    if (id_user == 1):
        id_user = 'id_user'

    # return render(request, 'job_view/adminJobs.html', {'jobs': jobs, 'urlUser': user, 'cols': cols, })
    return HttpResponse("This is filtering the columns")
