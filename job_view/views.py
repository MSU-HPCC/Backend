from django.shortcuts import render
from django.http import HttpResponse
from static.src import Admin_Stats_PySLURM as api
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def jobs(request):
    user = request.user.username
    access = api.user_access(user)
    temp = access.my_jobs()
    jobs = []
    cols = ['id_user', 'job_name', 'nodelist', 'nodes_alloc', 'time_submit', 'time_start', 'time_end', 'exit_code',
            'cpus_req']
    keys = ['user', 'jobname', 'nodes', 'allocated_nodes', 'submit_time', 'start_time', 'end_time', 'exit_code', 'req_cpus']
    if temp is None:
        jobs = [""]*len(keys)
    else:
        temp = temp[user]
        for key, value in temp.items():
            temp = []
            for i in keys:
                if i == 'exit_code':
                    meaning = ""
                    val = value[i]
                    if val == 0:
                        meaning = "Run Successful"
                    elif val == 1:
                        meaning = "General Error"
                    elif val == 2:
                        meaning = "Misuse of Shell Builtins"
                    elif val == 126:
                        meaning = "Cannot invoke Command"
                    elif val == 127:
                        meaning = "Command not found"
                    elif val == 128:
                        meaning = "Invalid Exit Code"
                    elif val == 130:
                        meaning = "Program Terminated"
                    elif val == 255:
                        meaning = "Exit Status Out of Range"
                    elif val >= 129 and val <= 165 and val != 130:
                        val_str = str(val-128)
                        meaning = "Fatal error: " + val_str
                    else:
                        val_str = str(val)
                        meaning = "Unrecognized or Custom Error Code: " + val_str
                    temp.append(meaning)
                else:
                    temp.append(value[i])
            jobs.append(temp)
    itr = 0
    for col in cols:
        cols[itr] = (col, itr)
        itr += 1
    return render(request, 'job_view/jobs.html', {'jobs': jobs, 'user': user, 'cols': cols, })

def adminJobs(request, user):
    if (request.user.id == 1):
        user = request.user.username
        access = api.admin_access(user)
        temp = access.view_jobs()
        jobs = []
        cols = ['id_user', 'job_name', 'nodelist', 'nodes_alloc', 'time_submit', 'time_start', 'time_end', 'exit_code', 'cpus_req']
        keys = ['user', 'jobname', 'nodes', 'allocated_nodes', 'submit_time', 'start_time', 'end_time', 'exit_code', 'req_cpus']
        if temp is None:
            jobs = [""] * len(keys)
        else:
            temp=temp['Admin']
            for key, value in temp.items():
                for key2, value2 in value.items():
                    for key3, value3 in value2.items():
                        temp = []
                        for i in keys:
                            if i == 'exit_code':
                                meaning = ""
                                val = value3[i]
                                if val == 0:
                                    meaning = "Run Successful"
                                elif val == 1:
                                    meaning = "General Error"
                                elif val == 2:
                                    meaning = "Misuse of Shell Builtins"
                                elif val == 126:
                                    meaning = "Cannot invoke Command"
                                elif val == 127:
                                    meaning = "Command not found"
                                elif val == 128:
                                    meaning = "Invalid Exit Code"
                                elif val == 130:
                                    meaning = "Program Terminated"
                                elif val == 255:
                                    meaning = "Exit Status Out of Range"
                                elif val >= 129 and val <= 165 and val != 130:
                                    val_str = str(val - 128)
                                    meaning = "Fatal error: " + val_str
                                else:
                                    val_str = str(val)
                                    meaning = "Unrecognized or Custom Error Code: " + val_str
                                temp.append(meaning)
                            else:
                                temp.append(value3[i])
                        jobs.append(temp)
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
    user = request.user.username
    access = api.group_access(user)
    temp = access.group_jobs()
    jobs = []
    cols = ['job_db_inx', 'group_name', 'job_name', 'id_job', 'id_user', 'id_group', 'nodelist', 'nodes_alloc',
            'time_submit', 'time_start', 'time_end', 'exit_code']
    keys = ['jobid','account','jobname','jobid','user','gid','nodes', 'allocated_nodes', 'submit_time', 'start_time', 'end_time', 'exit_code', 'req_cpus']
    if temp is None:
        jobs = [""]*len(keys)
    else:
        for key,value in temp.items():
            for key2, value2 in value.items():
                temp = []
                for i in keys:
                    if i == 'exit_code':
                        meaning = ""
                        val = value2[i]
                        if val == 0:
                            meaning = "Run Successful"
                        elif val == 1:
                            meaning = "General Error"
                        elif val == 2:
                            meaning = "Misuse of Shell Builtins"
                        elif val == 126:
                            meaning = "Cannot invoke Command"
                        elif val == 127:
                            meaning = "Command not found"
                        elif val == 128:
                            meaning = "Invalid Exit Code"
                        elif val == 130:
                            meaning = "Program Terminated"
                        elif val == 255:
                            meaning = "Exit Status Out of Range"
                        elif val >= 129 and val <= 165 and val != 130:
                            val_str = str(val - 128)
                            meaning = "Fatal error: " + val_str
                        else:
                            val_str = str(val)
                            meaning = "Unrecognized or Custom Error Code: " + val_str
                        temp.append(meaning)
                    else:
                        temp.append(value2[i])
                jobs.append(temp)
    itr = 0
    for col in cols:
        cols[itr] = (col,itr)
        itr += 1
    return render(request, 'job_view/groupJobs.html', {'jobs': jobs, 'urlUser': user, 'cols': cols, })
