def isAdmin(user):
    admin_list_file = open("admins.txt")
    allowed_users = []
    for line in admin_list_file:
        allowed_users.append(line.strip())
    admin_access = user in allowed_users
    return admin_access
