'''
jobs: view uses pyslurm to get job data specific to the currently logged in user.
adminJobs: View used pyslurm to get **all** users job data -- Restricted to users specified in admins.txt
groupJobs: View uses pyslurm to get job data for all users in the same group as the logged in user.
adminSearch: View verifys that logged in user is an admin. Returns job data specific to the netID obtained from the url slug
    Param: user = the url slug str representing a netID to search
'''
from django.shortcuts import render
from django.http import HttpResponse
from static.src import Admin_Stats_PySLURM as api
from django.contrib.auth.decorators import login_required

@login_required
def jobs(request):
    user = request.user.username
    access = api.user_access(user,2)
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
    # make cols variable into list of tuples with index so the template can render the data properly
    itr = 0
    for col in cols:
        cols[itr] = (col, itr)
        itr += 1
    return render(request, 'job_view/jobs.html', {'jobs': jobs, 'user': user, 'cols': cols, })

@login_required
def adminJobs(request):
    admin_list_file = open("admins.txt")
    allowed_users = []
    for line in admin_list_file:
        allowed_users.append(line.strip())
    if (request.user.username in allowed_users):
        user = request.user.username
        access = api.admin_access(user,2)
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
        # make cols variable into list of tuples with index so the template can render the data properly
        itr = 0
        for col in cols:
            cols[itr] = (col, itr)
            itr += 1
        return render(request, 'job_view/adminJobs.html', {'jobs': jobs, 'urlUser': user, 'cols': cols, })
    else:
        return render(request, '../templates/error_pages/403.html')

@login_required
def groupJobs(request):
    user = request.user.username
    access = api.group_access(user,2)
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
    # make cols variable into list of tuples with index so the template can render the data properly
    itr = 0
    for col in cols:
        cols[itr] = (col,itr)
        itr += 1
    return render(request, 'job_view/groupJobs.html', {'jobs': jobs, 'urlUser': user, 'cols': cols, })

@login_required
def adminSearch(request, user):
    admin_list_file = open("admins.txt")
    allowed_users = []
    for line in admin_list_file:
        allowed_users.append(line.strip())
    if (request.user.username in allowed_users):
        # user is a parameter.
        access = api.user_access(user,2)
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
        # make cols variable into list of tuples with index so the template can render the data properly
        itr = 0
        for col in cols:
            cols[itr] = (col, itr)
            itr += 1
        return render(request, 'job_view/jobSearch.html', {'jobs': jobs, 'urlUser': user, 'cols': cols, })
    else:
        return render(request, '../templates/error_pages/403.html')
