import pyslurm
from datetime import datetime, timedelta
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
                self.user_id = self.all_jobs[i]['gid']
                self.group_id = self.all_jobs[i]['account']
                break

        for j in self.all_jobs:
            if self.all_jobs[j]['account'] == self.group_id:
                self.group_table.add(self.all_jobs[j]['user'])
            if self.all_jobs[j]['user'] == self.user:
                self.job_table.update({j: self.all_jobs[j]})
            if self.all_jobs[j]['account'] not in self.full_table.keys():
              self.full_table.update({self.all_jobs[j]['account']: {self.all_jobs[j]['user']: {j: self.all_jobs[j]}}})
            elif self.all_jobs[j]['user'] not in self.full_table[self.all_jobs[j]['account']].keys():
              self.full_table[self.all_jobs[j]['account']].update({self.all_jobs[j]['user']: {j: self.all_jobs[j]}})
            else:
              self.full_table[self.all_jobs[j]['account']][self.all_jobs[j]['user']].update({j: self.all_jobs[j]})

        self.group_table = list(self.group_table)

        for i in self.group_table:
            self.group_job_table[i] = {}

        self.group_job_table.update({self.user: self.job_table})

        for k in self.all_jobs:
            if self.all_jobs[k]['user'] in self.group_table:
                if self.all_jobs[k]['user'] != self.user:
                    self.group_job_table[self.all_jobs[k]['user']].update({k: self.all_jobs[k]})

    def user_jobs(self, user = None,time = 31): #General purpose information gatherer
        if user == None:
            user = self.user
        unix_time = datetime.now() - timedelta(days=time)
        unix_time = int(unix_time.strftime("%s"))

        if user == self.user:
            #return {user:self.job_table}
            temp = {user: {}}
            for i in self.job_table:
                if self.job_table[i]['user'] == user and self.job_table[i]['submit'] >= unix_time:
                    temp[user].update({i: self.all_jobs[i]})
            if temp == {user: {}}:
                return None
            else:
                return temp
        else:
            temp = {user:{}}
            for i in self.all_jobs:
                if self.all_jobs[i]['user'] == user and self.all_jobs[i]['submit'] >= unix_time:
                    temp[user].update({i:self.all_jobs[i]})
            if temp =={user:{}}:
                return None
            else:
                return temp

    def my_jobs(self,time=31): #Publically callable method
        return self.user_jobs(self.user,time)

    def user_stats(self, user = None,time = 31):
        if user == None:
            user = self.user

        holder = self.user_jobs(user,time)

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
            stats_list = {user: {'complete': (tot_comp / total), 'error': (tot_error / total), 'running': (tot_run / total),
                'pending': (tot_pending / total),'total': total, 'complete_raw': tot_comp, 'error_raw': tot_error, 'run_raw': tot_run,
                                 'pending_raw': tot_pending}}

        return stats_list

    def my_stats(self,time=31):
        return self.user_stats(self.user,time)


class group_access(user_access):
    def group_jobs(self, user_list=[],time = 31):
        group_name = self.group_id
        unix_time = datetime.now() - timedelta(days=time)
        unix_time = int(unix_time.strftime("%s"))

        if group_name == None:  # Check User is in a Group
            return self.my_jobs()
        else:
            if user_list == []:
                user_list = self.group_table
            else:
                user_list = list(set(user_list) & set(self.group_table))

            temp = {}

            for i in user_list:
                temp.update({i:{}})
                for j in self.group_job_table[i]:
                    if self.group_job_table[i][j]['submit'] >= unix_time:
                        temp[i].update({j:self.group_job_table[i][j]})

            return temp

    def group_stats(self, user_list=[],time = 31):

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
                if temp != None:
                    temp_stats.update(temp)

            if temp_stats == {}:
                return None
            else:
                total = 0
                total_comp = 0
                tot_error = 0
                total_run = 0
                tot_pending = 0
                for i in temp_stats.keys():
                    total += temp_stats[i]['total']
                    total_comp += temp_stats[i]['complete_raw']
                    tot_error += temp_stats[i]['error_raw']
                    total_run += temp_stats[i]['run_raw']
                    tot_pending += temp_stats[i]['pending_raw']
                # if total == 0:
                #     total = 1
                # if total_comp == 0:
                #     total_comp = 1
                # if tot_error == 0:
                #     tot_error = 1
                # if total_run == 0:
                #     total_run = 1
                holder = {group_name:{'summary':{'complete': (total_comp / total), 'error': (tot_error / total),
                                'running': (total_run / total), 'pending': (tot_pending / total),
                                'total': total, 'complete_raw': total_comp, 'error_raw': tot_error,
                                'run_raw': total_run, 'pending_raw': tot_pending}}}

                for i in temp_stats.keys():
                    holder[group_name].update({i:temp_stats[i]})
                return holder


class admin_access(group_access):
    def view_jobs(self, group_list = [],user_list = [],time = 31):
        holder = {'Admin':{}}

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
            holder['Admin'].update(self.admin_group_jobs(i,user_list,time))
            # for j in user_list:
            #     if j in self.full_table[i].keys():
            #         holder.append(self.full_table[i][j])

        if holder == {'Admin':{}}:
            return None
        else:
            return holder

    def view_stats(self,group_list = [],user_list = [],time = 31):
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
        list_temp = []
        for i in group_list:
            temp = self.admin_group_stats(i,user_list,time)
            if temp is not None:
                temp_stats.update(temp)
                list_temp.append(i)
        group_list = list_temp

        if temp_stats == {}:
            return None
        else:
            total = 0
            total_comp = 0
            tot_error = 0
            total_run = 0
            tot_pending = 0

            for i in temp_stats.keys():
                total += temp_stats[i]['summary']['total']
                total_comp += temp_stats[i]['summary']['complete_raw']
                tot_error += temp_stats[i]['summary']['error_raw']
                total_run += temp_stats[i]['summary']['run_raw']
                tot_pending += temp_stats[i]['summary']['pending_raw']
            # if total == 0:
            #     total = 1
            # if total_comp == 0:
            #     total_comp = 1
            # if tot_error == 0:
            #     tot_error = 1
            # if total_run == 0:
            #     total_run = 1

            holder = {}

            holder.update({'Admin':{
                "summary":{'complete':(total_comp / total), 'error':(tot_error / total), 'running':(total_run / total), 'pending':(tot_pending / total),
                           'total':total, 'complete_raw':total_comp, 'error_raw':tot_error, 'run_raw':total_run, 'pending_raw':tot_pending }}})

            for i in group_list:
                holder['Admin'].update({i:temp_stats[i]})

            return holder

    def admin_group_jobs(self, group_name=None, user_list = [],time = 31):
        if group_name == None:
            if self.group_id == None:
                return None
            else:
                return self.group_jobs(user_list,time)
        else:
            group_table = self.full_table[group_name].keys()
            group_job_table = {group_name:{}}
            # for j in self.all_jobs:
            #     if self.all_jobs[j]['account'] == group_name:
            #         group_table.add(self.all_jobs[j]['user'])
            #
            # group_table = list(group_table)

            if user_list == []:
                user_list = group_table
            else:
                user_list = list(set(user_list) & set(group_table))

            for i in user_list:
                temp = self.user_jobs(i,time)
                group_job_table[group_name].update(temp)

            # for k in self.all_jobs:
            #     if self.all_jobs[k]['user'] in user_list:
            #         group_job_table[self.all_jobs[k]['user']].update({k: self.all_jobs[k]})

            return group_job_table


    def admin_group_stats(self, group_name=None, user_list=[],time = 31):
        if group_name == None:
            if self.group_id == None:
                return None
            else:
                return self.group_stats(user_list,time)
        else:
            group_table = self.full_table[group_name].keys()

            # for j in self.all_jobs:
            #     if self.all_jobs[j]['account'] == group_name:
            #         group_table.add(self.all_jobs[j]['user'])
            #
            # group_table = list(group_table)

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
                tot_pending = 0
                for i in temp_stats.keys():
                    total += temp_stats[i]['total']
                    total_comp += temp_stats[i]['complete_raw']
                    tot_error += temp_stats[i]['error_raw']
                    total_run += temp_stats[i]['run_raw']
                    tot_pending += temp_stats[i]['pending_raw']
                # if total == 0:
                #     total = 1
                # if total_comp == 0:
                #     total_comp = 1
                # if tot_error == 0:
                #     tot_error = 1
                # if total_run == 0:
                #     total_run = 1
                holder = {group_name:
                    {'summary':{'complete':(total_comp / total), 'error':(tot_error / total), 'running':(total_run / total), 'pending': (tot_pending / total),
                                'total':total, 'complete_raw':total_comp, 'error_raw':tot_error, 'run_raw':total_run, 'pending_raw': tot_pending}}}

                for i in temp_stats.keys():
                    holder[group_name].update({i:temp_stats[i]})

                return holder

#________________TESTS_____________________________

# x1 = user_access("christian")
# x2 = group_access("matt")
# x3 = admin_access("luedtke2")
# x4 = admin_access("luedtke2",1)

# for i in x2.full_table.keys():
#     print("Group: ",i)
#     for j in x2.full_table[i].keys():
#         print("----User: ", j)
#         print("--------Jobs: ", len(x2.full_table[i][j].keys()))

# print("FINISHED")
#
# print(x1)
# print(x2)
# print(x3)
#
# z1 = x1.my_stats()
# z2 = x2.my_stats()
# z3 = x3.my_stats()
# z4 = x4.my_stats(7)
# print("z1 = x1.my_stats()")
# print("User mystats: ",z1)
# print("")
# print("z2 = x2.my_stats()")
# print("Group mystats: ",z2)
# print("")
# print("z3 = x3.my_stats()")
# print("Admin mystats: ",z3)
# print("")
# print("z4 = x3.my_stats(7)")
# print("Admin Week mystats: ",z4)
# print("")
# #
#
# z1 = x1.my_jobs()
# z2 = x2.my_jobs()
# z3 = x3.my_jobs()
# z4 = x4.my_jobs(7)
# #
# print("z1 = x1.my_jobs()")
# print("User my_jobs: ",z1)
# print("")
# print("z2 = x2.my_jobs()")
# print("Group my_jobs: ",z2)
# print("")
# print("z3 = x3.my_jobs()")
# print("Admin my_jobs: ",len(z3["luedtke2"].keys()))
# print("")
# print("z4 = x3.my_jobs(7)")
# print("Admin my_jobs: ",len(z4["luedtke2"].keys()))
# print("")
#
# y2 = x2.group_stats(["matt","user07","christian"],120)
# y3 = x3.admin_group_stats(None,["matt","user07","christian"],120)
#
# print("y2 = x2.group_stats([matt,user07,christian],120)")
# print("Group group_stats: ",y2)
# print("")
# print("y3 = x3.admin_group_stats(None,[matt,user07,christian],120)")
# print("Admin group_stats: ",y3)
# print("")
#
# y2 = x2.group_jobs(["matt","user07","christian"],120)
# y3 = x3.admin_group_jobs(None,["matt","user07","christian"],120)
#
# print("y2 = x2.group_jobs(['matt','user07','christian'],120)")
# print("Group group_jobs: ",y2)
# print("")
# print("y3 = x3.admin_group_jobs(None,['matt','user07','christian'],120)")
# print("Admin group_jobs: ",y3)
# print("")
#
# y2 = x2.group_stats([],120)
# y3 = x3.admin_group_stats(None,[],120)
#
# print("y2 = x2.group_stats([],120)")
# print("Group group_stats: ",y2)
# print("")
# print("y3 = x3.admin_group_stats(None,[],120)")
# print("Admin group_stats: ",y3)
# print("")
#
y2 = x2.group_jobs([],120)
y3 = x3.admin_group_jobs(None,[],120)
#
# print("y2 = #x2.group_jobs([],120)")
# print("Group group_jobs: ",y2.keys())
# print("")
# print("y3 = x3.admin_group_jobs(None,[],120)")
# print("Admin group_jobs: ",y3.keys())
# print("")
#
# y2 = x3.view_jobs([],['matt'],120)
# y3 = x3.view_stats([],['matt'],120)
#
# print("y2 = x3.view_jobs([],['matt'],120)")
# print("Admin view_jobs: ",y2['Admin'].keys())
# for i in y2:
#     print("Admin: ",i)
#     for j in y2[i]:
#         print("----Group: ",j)
#         for k in y2[i][j]:
#             print("--------User: ",k)
# print("")
# print("y3 = x3.view_stats([],['matt'],120)")
# print("Admin view_stats: ",y3)
# print("")
#
# y2 = x3.view_jobs(['buyin-07','buyin-04'],[],120)
# y3 = x3.view_stats(['buyin-07','buyin-04'],[],120)
# #
# print("y2 = x3.view_jobs(['buyin-07','buyin-04'],[],120")
# print("Admin view_jobs: ",y2['Admin'].keys())
# for i in y2:
#     print("Admin: ",i)
#     for j in y2[i]:
#         print("----Group: ",j)
#         for k in y2[i][j]:
#             print("--------User: ",k)
# print("")
#
# print("y3 = x3.view_stats(['buyin-07','main'],[],120)")
# print("Admin view_stats: ",y3)
# print("")
# #
# print(x1.user)
# print(x1.user_id)
# print(x1.group_id)



