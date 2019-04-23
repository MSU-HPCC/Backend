import pyslurm
from datetime import datetime, timedelta


class user_access(): #Basic Data Access Class
    def __init__(self, user, time=31): #Inputs Username, Time in days for which data will be available
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

        self.all_jobs = pyslurm.slurmdb_jobs().get(starttime=start.encode('utf-8'), endtime=end.encode('utf-8'))#Initial Call to Pyslurm

        for i in self.all_jobs:#Search for User information matching supplied username
            if self.all_jobs[i]['user'] == self.user:
                self.user_id = self.all_jobs[i]['gid']
                self.group_id = self.all_jobs[i]['account']
                break

        for j in self.all_jobs:#Assemble table of user in the supplied username's group and assemble an organized version of all the available data
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

        for k in self.all_jobs:#Add group data to seperate table
            if self.all_jobs[k]['user'] in self.group_table:
                if self.all_jobs[k]['user'] != self.user:
                    self.group_job_table[self.all_jobs[k]['user']].update({k: self.all_jobs[k]})

    def user_jobs(self, user=None, time=31):#Input Username, time in days for which jobs will be returned
        if user == None:#Default to calling object's username
            user = self.user
        unix_time = datetime.now() - timedelta(days=time)
        unix_time = int(unix_time.strftime("%s"))

        temp = {user: {}}
        for i in self.all_jobs:#Sort out the eligible jobs from calling object's complete job table
            if self.all_jobs[i]['user'] == user and self.all_jobs[i]['submit'] >= unix_time:
                if self.all_jobs[i]['submit'] < 10000:#Catch uninitialized times
                  temp_submit = "0000-00-00 00:00:00"
                else:
                  temp_submit = datetime.fromtimestamp(self.all_jobs[i]['submit']).strftime('%Y-%m-%d %H:%M:%S')

                if self.all_jobs[i]['end'] < 10000:#Catch uninitialized times
                  temp_end = "0000-00-00 00:00:00"
                else:
                  temp_end = datetime.fromtimestamp(self.all_jobs[i]['end']).strftime('%Y-%m-%d %H:%M:%S')

                if self.all_jobs[i]['start'] < 10000:#Catch uninitialized times
                  temp_start = "0000-00-00 00:00:00"
                else:
                  temp_start = datetime.fromtimestamp(self.all_jobs[i]['start']).strftime('%Y-%m-%d %H:%M:%S')

                self.all_jobs[i].update(
                       {'submit_time': temp_submit,
                     'end_time': temp_end,
                     'start_time': temp_start})

                temp[user].update({i: self.all_jobs[i]})
        if temp == {user: {}}:#Check empty condition
            return None
        else:
            return temp

    def my_jobs(self, time=31):#Same as user_jobs except only for calling object's user
        return self.user_jobs(self.user, time)

    def user_stats(self, user=None, time=31):#Input Username, time in days for which stats will be returned
        if user == None:#Default to calling object's username
            user = self.user

        holder = self.user_jobs(user, time)

        if holder[user] == {}:#Check for empty job table
            stats_list = None
        else:
            total = len(holder[user].keys())
            tot_comp = 0
            tot_error = 0
            tot_run = 0
            tot_pending = 0
            for i in holder[user]:#Sum number of various types of jobs
                if holder[user][i]['end'] == 0:
                    if holder[user][i]['start'] == 0:
                        tot_pending += 1
                    else:
                        tot_run += 1
                elif holder[user][i]['exit_code'] == 0:
                    tot_comp += 1
                else:
                    tot_error += 1
            stats_list = {
                user: {'complete': (tot_comp / total), 'error': (tot_error / total), 'running': (tot_run / total),
                       'pending': (tot_pending / total), 'total': total, 'complete_raw': tot_comp,
                       'error_raw': tot_error, 'run_raw': tot_run,
                       'pending_raw': tot_pending}}

        return stats_list

    def my_stats(self, time=31):
        return self.user_stats(self.user, time)


class group_access(user_access):#Group Data Access Class (limited to object's username's group)
    def group_jobs(self, user_list=[], time=31):#Input list of requested usernames, time in days jobs will be returned for
        group_name = self.group_id
        unix_time = datetime.now() - timedelta(days=time)
        unix_time = int(unix_time.strftime("%s"))

        if group_name == None:  # Check User is in a Group
            return self.my_jobs()
        else:
            if user_list == []:#Defaults to all users in group and all jobs
                user_list = self.group_table
            else:
                user_list = list(set(user_list) & set(self.group_table))#Remove usernames not in group

            temp = {}

            for i in user_list:
                temp.update({i: {}})
                for j in self.group_job_table[i]:#Sort out the eligible jobs from calling object's group job table
                    if self.group_job_table[i][j]['submit'] >= unix_time:

                        if self.group_job_table[i][j]['submit'] < 10000:#Catch uninitialized times
                          temp_submit = "0000-00-00 00:00:00"
                        else:
                          temp_submit = datetime.fromtimestamp(self.group_job_table[i][j]['submit']).strftime('%Y-%m-%d %H:%M:%S')

                        if self.group_job_table[i][j]['end'] < 10000:#Catch uninitialized times
                          temp_end = "0000-00-00 00:00:00"
                        else:
                          temp_end = datetime.fromtimestamp(self.group_job_table[i][j]['end']).strftime('%Y-%m-%d %H:%M:%S')

                        if self.group_job_table[i][j]['start'] < 10000:#Catch uninitialized times
                          temp_start = "0000-00-00 00:00:00"
                        else:
                          temp_start = datetime.fromtimestamp(self.group_job_table[i][j]['start']).strftime('%Y-%m-%d %H:%M:%S')

                        self.group_job_table[i][j].update({'submit_time': temp_submit,'end_time': temp_end,'start_time': temp_start})
                        temp[i].update({j: self.group_job_table[i][j]})

            flag = False
            for i in temp:#Check Empty Condition
                if temp[i] != {}:
                    flag = True
                    break
            if flag:
                return temp
            else:
                return None

    def group_stats(self, user_list=[], time=31):#Input list of requested usernames, time in days stats will be returned for

        group_name = self.group_id

        temp_stats = {}

        if group_name == None:  # Check User is in a Group
            return self.my_stats()
        else:
            if user_list == []:#Defaults to all users in group and all jobs
                user_list = self.group_table
            else:
                user_list = list(set(user_list) & set(self.group_table))#Remove usernames not in the group

            for i in user_list:#Calls Lower level user_stats function for each username
                temp = self.user_stats(i, time)
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
                for i in temp_stats.keys():#Sum different types of jobs and total number of jobs
                    total += temp_stats[i]['total']
                    total_comp += temp_stats[i]['complete_raw']
                    tot_error += temp_stats[i]['error_raw']
                    total_run += temp_stats[i]['run_raw']
                    tot_pending += temp_stats[i]['pending_raw']

                holder = {group_name: {'summary': {'complete': (total_comp / total), 'error': (tot_error / total),
                                                   'running': (total_run / total), 'pending': (tot_pending / total),
                                                   'total': total, 'complete_raw': total_comp, 'error_raw': tot_error,
                                                   'run_raw': total_run, 'pending_raw': tot_pending}}}

                for i in temp_stats.keys():#Add Individual stats for each username to table containing group summary stats
                    holder[group_name].update({i: temp_stats[i]})
                return holder


class admin_access(group_access):#Global Data Access Class
    def view_jobs(self, group_list=[], user_list=[], time=31):#Input list of requested groups to search, list of requested usernames, time in days jobs will be returned for
        holder = {'Admin': {}}

        if group_list == []:  # Default to all groups
            group_list = self.full_table.keys()
        if user_list == []:  # Default to all users
            for i in group_list:
                temp = self.full_table[i].keys()
                for j in temp:
                    if j not in user_list:
                        user_list.append(j)

        for i in group_list:#Call lower level group _jobs function for each group and all users
            temp = self.admin_group_jobs(i, user_list, time)
            if temp is not None:
                holder['Admin'].update(temp)

        if holder == {'Admin': {}}:#Check Empty Condition
            return None
        else:
            return holder

    def view_stats(self, group_list=[], user_list=[], time=31):#Input list of requested groups to search, list of requested usernames, time in days stats will be returned for
        temp_stats = {}
        if group_list == []:  # Default to all groups
            group_list = self.full_table.keys()
        if user_list == []:  # Default to all users
            for i in group_list:
                temp = self.full_table[i].keys()
                for j in temp:
                    if j not in user_list:
                        user_list.append(j)

        list_temp = []
        for i in group_list:#Call lower level group _stats function for each group and all users
            temp = self.admin_group_stats(i, user_list, time)
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

            for i in temp_stats.keys():#Sum different types of jobs and total number of jobs
                total += temp_stats[i]['summary']['total']
                total_comp += temp_stats[i]['summary']['complete_raw']
                tot_error += temp_stats[i]['summary']['error_raw']
                total_run += temp_stats[i]['summary']['run_raw']
                tot_pending += temp_stats[i]['summary']['pending_raw']

            holder = {}

            holder.update({'Admin': {
                "summary": {'complete': (total_comp / total), 'error': (tot_error / total),
                            'running': (total_run / total), 'pending': (tot_pending / total),
                            'total': total, 'complete_raw': total_comp, 'error_raw': tot_error, 'run_raw': total_run,
                            'pending_raw': tot_pending}}})

            for i in group_list:#Add Group stats for each username to table containing global summary stats
                holder['Admin'].update({i: temp_stats[i]})

            return holder

    #Following Implementations of group_jobs and group_stats allow for selecting groups other then the calling object's own group, otherwise they function as the previous implementations
    def admin_group_jobs(self, group_name=None, user_list=[], time=31):#Input requested group, list of requested usernames, time in days jobs will be returned for
        if group_name == None:#Default to calling object's group
            if self.group_id == None:#Check No Group Condition
                return None
            else:
                return self.group_jobs(user_list, time)
        else:
            group_table = self.full_table[group_name].keys()
            group_job_table = {group_name: {}}

            if user_list == []:#Default to all users
                user_list = group_table
            else:
                user_list = list(set(user_list) & set(group_table))#Remove usernames not in requested group
            for i in user_list:#Call lower level user_jobs function for each username
                temp = self.user_jobs(i, time)
                if temp is not None:
                    group_job_table[group_name].update(temp)

            if group_job_table == {group_name: {}}:#Check Empty Condition
                return None
            else:
                return group_job_table

    def admin_group_stats(self, group_name=None, user_list=[], time=31):#Input requested group, list of requested usernames, time in days stats will be returned for
        if group_name == None:#Default to calling object's group
            if self.group_id == None:#Check No Group Condition
                return None
            else:
                return self.group_stats(user_list, time)
        else:
            group_table = self.full_table[group_name].keys()

            if user_list == []:#Default to all users
                user_list = group_table
            else:
                user_list = list(set(user_list) & set(group_table))#Remove usernames not in requested group

            temp_stats = {}

            for i in user_list:#Call lower level user_stats function for each username
                temp = self.user_stats(i, time)
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
                for i in temp_stats.keys():#Sum different types of jobs and total number of jobs
                    total += temp_stats[i]['total']
                    total_comp += temp_stats[i]['complete_raw']
                    tot_error += temp_stats[i]['error_raw']
                    total_run += temp_stats[i]['run_raw']
                    tot_pending += temp_stats[i]['pending_raw']

                holder = {group_name:
                              {'summary': {'complete': (total_comp / total), 'error': (tot_error / total),
                                           'running': (total_run / total), 'pending': (tot_pending / total),
                                           'total': total, 'complete_raw': total_comp, 'error_raw': tot_error,
                                           'run_raw': total_run, 'pending_raw': tot_pending}}}

                for i in temp_stats.keys():#Add Individual stats for each username to table containing group summary stats
                    holder[group_name].update({i: temp_stats[i]})

                return holder