from mysql.connector import MySQLConnection, Error
from job_view import dbcreds

class user_access():
    def __init__(self, user_id):
        self.job_table = []
        self.node_table = []
        self.group_table = []
        self.user_table = []
        self.user = user_id
        self.user_id = None
        self.group_id = None
        self.conn = MySQLConnection(user = dbcreds.user, password = dbcreds.pwd, database = dbcreds.db, host = dbcreds.host)
        self.cursor = self.conn.cursor()
        self.offset = None

        self.cursor.execute("SELECT acct FROM hpcc.hpcc_assoc_table WHERE user = %(user)s;",{'user':self.user})

        self.group_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT min(id_assoc) FROM hpcc.hpcc_assoc_table where user!= '' AND user != 'root';")

        self.offset = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT min(id_user) FROM hpcc.hpcc_job_table;")

        self.offset = self.cursor.fetchone()[0] - self.offset

        self.cursor.execute("SELECT id_assoc FROM hpcc.hpcc_assoc_table WHERE user = %(user)s;", {'user':self.user})

        self.user_id = self.offset + self.cursor.fetchone()[0]

        self.cursor.execute("SELECT id_assoc FROM hpcc.hpcc_assoc_table WHERE acct = %(id)s;",{'id':self.group_id})

        row = self.cursor.fetchone()[0]

        while row != None:
            self.group_table.append(row)
            row = self.cursor.fetchone()
            if row != None:
                row = row[0]

    def __user_jobs(self, user = None): #General purpose information gatherer

        if user == None:
            user = self.user

        self.cursor.execute("SELECT id_assoc FROM hpcc.hpcc_assoc_table WHERE user = %(user)s;", {'user':user})

        user_id = self.offset + self.cursor.fetchone()[0]

        self.cursor.execute("SELECT job_db_inx, mod_time, job_name, id_job, id_user, id_group, kill_requid, mem_req, nodelist, nodes_alloc, node_inx, state, timelimit, time_submit, time_eligible, time_start, time_end, time_suspended, work_dir FROM hpcc.hpcc_job_table WHERE id_user = %(id)s AND (UNIX_TIMESTAMP()-time_submit) < 21*86400;",{'id':user_id})
        row = self.cursor.fetchone()
        temp_table = []
        while row != None:
            temp_table.append(row)
            row = self.cursor.fetchone()
        return temp_table

    def my_jobs(self): #Publically callable method
        self.job_table.append(self.__user_jobs(self.user))
        return self.job_table

    def user_stats(self, user):
        stats_list = []

        self.cursor.execute("SELECT id_assoc FROM hpcc.hpcc_assoc_table WHERE user = %(user)s;", {'user':user})

        id_user = self.offset + self.cursor.fetchone()[0]

        self.cursor.execute("SELECT count(job_name) FROM hpcc.hpcc_job_table WHERE id_user = %(id)s and UNIX_TIMESTAMP()-time_end < (21*86400)",{'id':id_user})
        total = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT count(job_name) FROM hpcc.hpcc_job_table WHERE id_user = %(id)s and (UNIX_TIMESTAMP()-time_end)<(21*86400) and exit_code = 0;",{'id':id_user})
        tot_comp = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT count(job_name) FROM hpcc.hpcc_job_table WHERE id_user = %(id)s and (UNIX_TIMESTAMP()-time_end)<(21*86400) and exit_code != 0",{'id':id_user})
        tot_error = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT count(job_name) FROM hpcc.hpcc_job_table WHERE id_user = %(id)s and time_end = 0;",{'id':id_user})
        tot_run = self.cursor.fetchone()[0]

        stats_list = [user,[(tot_comp/total),(tot_error/total),(tot_run/total)],total,tot_comp,tot_error,tot_run]

        return stats_list

    def my_stats(self):
        return self.user_stats(self.user)


class group_access(user_access):
    def group_jobs(self,user_list = []):
        temp_list = []
        self.job_table = []
        if self.group_id == None: #Check User is in a Group
            print("----------")
            return self.my_jobs()
        else:
            if user_list == []: #Default to all users
<<<<<<< HEAD

                self.cursor.execute("SELECT job_db_inx, mod_time, job_name, id_job, id_user, id_group, kill_requid, mem_req, nodelist, nodes_alloc, node_inx, state, timelimit, time_submit, time_eligible, time_start, time_end, time_suspended, work_dir FROM hpcc.hpcc_job_table WHERE UNIX_TIMESTAMP()-time_submit < 21*86400;")
=======
                print("****************")
                self.cursor.execute("SELECT job_db_inx, mod_time, job_name, id_job, id_user, id_group, kill_requid, mem_req, nodelist, nodes_alloc, node_inx, state, timelimit, time_submit, time_eligible, time_start, time_end, time_suspended, work_dir FROM hpcc.hpcc_job_table;")
>>>>>>> 8010e6fdb4fd93b031051dbe2944ed8b4ca4f919
                row = self.cursor.fetchone()
                print(row)
                while row != None:
                    if row[4]-self.offset in self.group_table:
                        temp_list.append(row)
                    #else:
                    #    print("User ID: ", row[4], " is not part of your Research Group.")
                    row = self.cursor.fetchone()
                self.job_table = temp_list
            else:
                print(user_list)
                for i in user_list: #Search Specified User List
                    self.cursor.execute("SELECT id_assoc FROM hpcc.hpcc_assoc_table where user = %s;",i)
                    temp = self.cursor.fetchone()
                    print(temp)
                    temp_list.append(self.__user_jobs(temp+self.offset))
                for i in temp_list: #Filter for users in group
                    if i[4] == self.group_table:
                        print(i)
                        self.job_table.append(i)
                    else:
                        print("User ID: ", i[21], " is not part of your Research Group.")

        return self.job_table

    def group_stats(self, user_list = []):
        temp_stats = []
        group_name = self.group_id
        if user_list == []:
            self.cursor.execute("SELECT user FROM hpcc.hpcc_assoc_table WHERE acct = %(group)s AND user != '';", {'group':group_name})
            user_list.append(self.cursor.fetchone()[0])

        for i in user_list: #Search Specified User List
            temp_stats.append(self.user_stats(i))

        total = 0
        total_comp = 0
        tot_error = 0
        total_run = 0
        for i in temp_stats:
            total += i[2]
            total_comp += i[3]
            tot_error += i[4]
            total_run += i[5]

        holder = [group_name,[(total_comp / total), (tot_error / total), (total_run / total)], total, total_comp, tot_error,
                total_run]

        for i in temp_stats:
            holder.append([i[0],(i[3] / total), (i[4] / total), (i[5] / total)])

        return holder


class admin_access(group_access):
    def view_jobs(self, user_list = []):
        self.job_table = []
        if user_list == []: #Default to all users
            self.cursor.execute("SELECT job_db_inx, mod_time, job_name, id_job, id_user, id_group, kill_requid, mem_req, nodelist, nodes_alloc, node_inx, state, timelimit, time_submit, time_eligible, time_start, time_end, time_suspended, work_dir FROM hpcc.hpcc_job_table WHERE UNIX_TIMESTAMP()-time_submi2 < 21*86400;")
            row = self.cursor.fetchone()
            while row != None:
                self.job_table.append(row)
                row = self.cursor.fetchone()
        else:
            for i in user_list: #Search Specified User List
                self.job_table.append(self.__user_jobs(i))
        return self.job_table

    def view_stats(self,user_list = []):
        temp_stats = []
        if user_list == []: #Default to all users
            self.cursor.execute("SELECT name FROM hpcc.user_table WHERE name != 'root';")
            row = self.cursor.fetchone()
            while row != None:
                user_list.append(row)
                row = self.cursor.fetchone()

        for i in user_list: #Search Specified User List
            temp_stats.append(self.user_stats(i))

        total = 0
        total_comp = 0
        tot_error = 0
        total_run = 0
        for i in temp_stats:
            total += i[2]
            total_comp += i[3]
            tot_error += i[4]
            total_run += i[5]

        return [[(total_comp / total), (tot_error / total), (total_run / total)], total, total_comp, tot_error, total_run]

    def group_jobs(self, group_name=None, user_list = []):
        if group_name == None:
            group_name = self.group_id
        temp_list = []
        group_list = []
        self.job_table = []
        if group_name == None: #Check User is in a Group
            return self.my_jobs()
        else:
            self.cursor.execute("SELECT user FROM hpcc.hpcc_assoc_table WHERE acct = %s AND user != '';", group_name)
            row = self.cursor.fetchone()
            while row != None:
                group_list.append(row)
                row = self.cursor.fetchone()

            if user_list == []:
                user_list = group_list

            for i in user_list: #Search Specified User List
                if i in group_list:
                    temp_list.append(self.__user_jobs(i))
                else:
                    print("User ID: ", i, " is not part of your Research Group.")

        return self.job_table

    def group_stats(self, group_name=None, user_list=[]):
        temp_stats = []
        if group_name == None:  # Check User is in a Group
            return self.my_jobs()
        if user_list == []:
            self.cursor.execute("SELECT user FROM hpcc.hpcc_assoc_table WHERE acct = %s AND user != '';", group_name)
            row = self.cursor.fetchone()
            while row != None:
                user_list.append(row)
                row = self.cursor.fetchone()

        for i in user_list:  # Search Specified User List
            temp_stats.append(self.user_stats(i))

        total = 0
        total_comp = 0
        tot_error = 0
        total_run = 0
        for i in temp_stats:
            total += i[2]
            total_comp += i[3]
            tot_error += i[4]
            total_run += i[5]

        holder = [[(total_comp / total), (tot_error / total), (total_run / total)], total, total_comp, tot_error,
                  total_run]

        for i in temp_stats:
            holder.append([i[0], (i[3] / total), (i[4] / total), (i[5] / total)])

        return holder
