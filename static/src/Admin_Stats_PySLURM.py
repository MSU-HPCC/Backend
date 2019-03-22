import pyslurm
from datetime import datetime, timedelta
#TIME UNIMPLEMENTED
class user_access():
    def __init__(self, user, time=31):
        self.user = user
        self.user_id = None
        self.group_id = None
        self.job_table = {}
        self.group_table = set()
        self.group_job_table = {}
        self.all_jobs = None
        self.full_table = {}
        
        end = datetime.now() + timedelta(days=31)
        end = end.strftime("%m%d%y")
        t_delta = timedelta(days=time)
        start = datetime.now() - t_delta
        start = start.strftime("%m%d%y")

        self.all_jobs = pyslurm.slurmdb_jobs().get(starttime=start.encode('utf-8'),endtime=end.encode('utf-8'))

        for i in self.all_jobs:
            if self.all_jobs[i]['user'] == self.user:
                print(user," : ",self.all_jobs[i])
                self.user_id = self.all_jobs[i]['gid']
                self.group_id = self.all_jobs[i]['account']
                break

        for j in self.all_jobs:
            if self.all_jobs[j]['account'] == self.group_id:
                self.group_table.add(self.all_jobs[j]['user'])
            if self.all_jobs[j]['user'] == self.user:
                self.job_table.update({j: self.all_jobs[j]})
            self.full_table.update({self.all_jobs[j]['account']: {self.all_jobs[j]['user']: {j: self.all_jobs[j]}}})

        self.group_table = list(self.group_table)

        for i in self.group_table:
            self.group_job_table[i] = {}

        self.group_job_table.update({self.user: self.job_table})

        for k in self.all_jobs:
            if self.all_jobs[k]['user'] in self.group_table:
                if self.all_jobs[k]['user'] != self.user:
                    self.group_job_table[self.all_jobs[k]['user']].update({k: self.all_jobs[k]})



    def user_jobs(self, user = None,time = 7): #General purpose information gatherer
        #ADD NONE RETURNS
        if user == None:
            user = self.user

        if user == self.user:
            return {user:self.job_table}
        else:
            temp = {user:{}}
            for i in self.all_jobs:
                if self.all_jobs[i]['user'] == user:
                    temp[user].update({i:self.all_jobs[i]})
            return temp

    def my_jobs(self,time=7): #Publically callable method
        if self.job_table == {}:
            return None
        else:
            return self.job_table

    def user_stats(self, user,time = 7):
        if user == None:
            user = self.user

        holder = self.user_jobs(user)

        if holder[user] == {}:
            stats_list = None
        else:
            total = len(holder[user].keys())
            tot_comp = 0
            tot_error = 0
            tot_run = 0
            tot_pending = 0
            for i in holder[user]:
                #(user, " : ", holder[user][i])
                if holder[user][i]['end'] == 0:
                    if holder[user][i]['start']==0:
                        tot_pending += 1
                    else:
                        tot_run += 1
                elif holder[user][i]['exit_code'] == 0:
                    tot_comp += 1
                else:
                    tot_error += 1

            stats_list = [[(tot_comp/total),(tot_error/total),(tot_run/total)],total,tot_comp,tot_error,tot_run]

        return {user:stats_list}

    def my_stats(self,time=7):
        return self.user_stats(self.user,time)


class group_access(user_access):
    def group_jobs(self, user_list=[],time = 7):
        group_name = self.group_id

        self.job_table = []
        if group_name == None:  # Check User is in a Group
            return self.my_jobs()
        else:
            if user_list == []:
                user_list = self.group_table
            else:
                user_list = list(set(user_list) & set(self.group_table))

            temp = {}

            for i in user_list:
                temp[i] = self.group_job_table[i]

            return temp

    def group_stats(self, user_list=[],time = 7):

        group_name = self.group_id

        temp_stats = {}

        if group_name == None:  # Check User is in a Group
            return self.my_stats()
        else:
            if user_list == []:
                user_list = self.group_table
            else:
                user_list = list(set(user_list) & set(self.group_table))

                for i in user_list:
                    temp = self.user_stats(i,time)
                    if temp[i] != None:
                        temp_stats[i] = temp[i]

            if temp_stats == {}:
                return None
            else:
                total = 0
                total_comp = 0
                tot_error = 0
                total_run = 0
                for i in temp_stats.keys():
                    total += temp_stats[i][1]
                    total_comp += temp_stats[i][2]
                    tot_error += temp_stats[i][3]
                    total_run += temp_stats[i][4]
                if total == 0:
                    total = 1
                if total_comp == 0:
                    total_comp = 1
                if tot_error == 0:
                    tot_error = 1
                if total_run == 0:
                    total_run = 1
                holder = {group_name:[[(total_comp / total), (tot_error / total), (total_run / total)], total, total_comp, tot_error,
                          total_run]}

                for i in temp_stats.keys():
                    holder.update({i:[(temp_stats[i][2] / total), (temp_stats[i][3] / total), (temp_stats[i][4] / total)]})

                return holder


class admin_access(group_access):
    def view_jobs(self, user_list = [],group_list = [],time = 7):#UNCHANGED
        self.job_table = []

        if group_list == []: #Default to all groups
            group_list = self.full_table.keys()
        if user_list == []:  # Default to all users
            for i in group_list:
                temp = self.full_table[i].keys()
                for j in temp:
                    if j not in user_list:
                        user_list.append(j)
                #user_list.append(self.full_table[i].keys())
                #user_list = list(set(user_list))

        for i in group_list:
            for j in user_list:
                if j in self.full_table[i].keys():
                    self.job_table.append(self.full_table[i][j])

        if self.job_table == []:
            return None
        else:
            return self.job_table

    def view_stats(self,user_list = [],group_list = [],time = 7): #UNCHANGED
        temp_stats = {}
        if group_list == []: #Default to all groups
            group_list = self.full_table.keys()
        if user_list == []:  # Default to all users
            for i in group_list:
                temp = self.full_table[i].keys()
                for j in temp:
                    if j not in user_list:
                        user_list.append(j)
                #user_list.append(self.full_table[i].keys())
                #user_list = list(set(user_list))


        if temp_stats == {}:
            return None
        else:
            total = 0
            total_comp = 0
            tot_error = 0
            total_run = 0

            for i in group_list:
                temp_stats.update({i:self.admin_group_stats(i,user_list,time)})

            for i in temp_stats.keys():
                total += temp_stats[i]['summary']['total']
                total_comp += temp_stats[i]['summary']['complete_raw']
                tot_error += temp_stats[i]['summary']['error_raw']
                total_run += temp_stats[i]['summary']['run_raw']
            if total == 0:
                total = 1
            if total_comp == 0:
                total_comp = 1
            if tot_error == 0:
                tot_error = 1
            if total_run == 0:
                total_run = 1

            holder = {}

            holder.update({'Admin':{"summary":{'complete':(total_comp / total), 'error':(tot_error / total), 'running':(total_run / total), 'total':total, 'complete_raw':total_comp, 'error_raw':tot_error, 'run_raw':total_run }}})

            for i in group_list:
                holder['Admin'].update(temp_stats[i])

            return holder

    def admin_group_jobs(self, group_name=None, user_list = [],time = 7):
        if group_name == None:
            if self.group_id == None:
                return None
            else:
                return self.group_jobs(user_list,time)
        else:
            group_table = set()
            group_job_table = {}
            for j in self.all_jobs:
                if self.all_jobs[j]['account'] == group_name:
                    group_table.add(self.all_jobs[j]['user'])

            group_table = list(group_table)

            if user_list == []:
                user_list = group_table
            else:
                user_list = list(set(user_list) & set(group_table))

            for i in user_list:
                group_job_table[i] = {}

            for k in self.all_jobs:
                if self.all_jobs[k]['user'] in user_list:
                    group_job_table[self.all_jobs[k]['user']].update({k: self.all_jobs[k]})

            return group_job_table


    def admin_group_stats(self, group_name=None, user_list=[],time = 7):
        if group_name == None:
            if self.group_id == None:
                return None
            else:
                return self.group_stats(user_list,time)
        else:
            group_table = set()

            for j in self.all_jobs:
                if self.all_jobs[j]['account'] == group_name:
                    group_table.add(self.all_jobs[j]['user'])

            group_table = list(group_table)

            if user_list == []:
                user_list = group_table
            else:
                user_list = list(set(user_list) & set(group_table))

            temp_stats = {}

            for i in user_list:
                temp = self.user_stats(i,time)
                if temp[i] != None:
                    temp_stats[i] = temp[i]

            if temp_stats == {}:
                return None
            else:
                total = 0
                total_comp = 0
                tot_error = 0
                total_run = 0
                for i in temp_stats.keys():
                    total += temp_stats[i][1]
                    total_comp += temp_stats[i][2]
                    tot_error += temp_stats[i][3]
                    total_run += temp_stats[i][4]
                if total == 0:
                    total = 1
                if total_comp == 0:
                    total_comp = 1
                if tot_error == 0:
                    tot_error = 1
                if total_run == 0:
                    total_run = 1
                holder = {group_name:{'summary':{'complete':(total_comp / total), 'error':(tot_error / total), 'running':(total_run / total), 'total':total, 'complete_raw':total_comp, 'error_raw':tot_error, 'run_raw':total_run}}}

                for i in temp_stats.keys():
                    holder[group_name].update({i:{'complete':(temp_stats[i][2] / total), 'error':(temp_stats[i][3] / total), 'running':(temp_stats[i][4] / total), 'total':temp_stats[i][1], 'complete_raw':temp_stats[i][2], 'error_raw':temp_stats[i][3], 'run_raw':temp_stats[i][4]}})

                return holder

#________________TESTS_____________________________

x1 = user_access("matt")
x2 = group_access("christian")
x3 = admin_access("luedtke2")
#
print("FINISHED")
#
# print(x1)
# print(x2)
# print(x3)
#
z1 = x1.my_stats()
z2 = x2.my_stats()
z3 = x3.my_stats(120)
#
print("User mystats: ",z1)
print("Group mystats: ",z2)
print("Admin mystats: ",z3)

#
z1 = x1.my_jobs()
z2 = x2.my_jobs()
z3 = x3.my_jobs()

print("User my_jobs: ",z1)
print("Group my_jobs: ",z2)
print("Amin my_jobs: ",z3)
#
y2 = x2.group_stats(["matt"],120)
y3 = x3.admin_group_stats(None,["matt"],120)
#
print("Group group_stats: ",y2)
print("Admin group_stats: ",y3)
#
y2 = x2.group_jobs(["christian"],120)
y3 = x3.admin_group_jobs(None,["christian"],120)
#
print("Group group_jobs: ",y2)
print("Admin group_jobs: ",y3)
#
y2 = x2.group_stats([],120)
y3 = x3.admin_group_stats(None,[],120)
#
print("Group group_stats: ",y2)
print("Admin group_stats: ",y3)
#
y2 = x2.group_jobs([],120)
y3 = x3.admin_group_jobs(None,[],120)
#
print("Group group_jobs: ",y2)
print("Admin group_jobs: ",y3)
#
y2 = x3.view_jobs(["matt"],[],120)
y3 = x3.view_stats(["matt"],[],120)
#
print("Admin view_jobs: ",y2)
print("Admin view_stats: ",y3)
#
y2 = x3.view_jobs([],[],120)
y3 = x3.view_stats([],[],120)
#
print("Admin view_jobs: ",y2)
print("Admin view_stats: ",y3)
#
print(x1.user)
print(x1.user_id)
print(x1.group_id)
