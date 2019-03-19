from django.shortcuts import render
from django.http import HttpResponse
from static.src import Admin_Stats_PySLURM as api
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def jobs(request):
    #query = "SELECT id_user, job_name, nodelist, nodes_alloc, time_submit, time_start, time_end, exit_code, cpus_req FROM hpcc_job_table WHERE id_user='"+ str(request.user) + "';"
    cols = ['id_user', 'job_name', 'nodelist', 'nodes_alloc', 'time_submit', 'time_start', 'time_end', 'exit_code', 'cpus_req']
    itr = 0
    for col in cols:
        cols[itr] = (col, itr)
        itr += 1
    return render(request, 'job_view/jobs.html', {'jobs': jobs, 'user': request.user, 'cols': cols, })

def adminJobs(request, user):
    if (request.user.id == 1):
        query = "SELECT id_user, job_name, nodelist, nodes_alloc, time_submit, time_start, time_end, exit_code, cpus_req FROM hpcc_job_table WHERE id_user='" + user + "';"
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
    #u = "user05"
    #x = Admin_Stats_SQL.group_access(u)
    #y = x.group_jobs()
    y = []
    u = request.user
    cols = ['job_db_inx', 'mod_time', 'job_name', 'id_job', 'id_user', 'id_group', 'nodelist', 'nodes_alloc', 'time_submit', 'time_start', 'time_end', 'exit_code']
    itr = 0
    for col in cols:
        cols[itr] = (col,itr)
        itr += 1
    return render(request, 'job_view/groupJobs.html', {'jobs': y, 'urlUser': u, 'cols': cols, })
