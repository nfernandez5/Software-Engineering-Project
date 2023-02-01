import os

from jobs.models import User, Account, Job

def addStudentAccountsFromFile(filePath):
    if os.path.isfile(filePath): # Student Accounts file provided
        studentAccountsFile = open(filePath, "r") # Will be reading from file
        newStudentAccounts = [] # List to hold the Student Account Data that will be added to the DB upon startup (if possible and not at capacity)
        lines = studentAccountsFile.readlines()
        newStudentAccount = {} # Dictionary that will hold the username, first name, last name, and password for account

        for line in lines:
            splitLine = line.split(" ")
            if len(splitLine) == 3: # First line of new student data that contains username, first name, and last name separated by a space
                newStudentAccount["username"] = splitLine[0]
                newStudentAccount["firstName"] = splitLine[1]
                newStudentAccount["lastName"] = splitLine[2].split("\n")[0] # Remove new line character
            elif line == "=====\n" or line == "=====": # Student Account data separator
                newStudentAccounts.append(newStudentAccount)
                newStudentAccount = {} # Reset it to empty dictionary for next student account data, if any
            else: # Would have to be password if not the other two
                newStudentAccount["password"] = line.split("\n")[0] # Remove new line character
        
        # If the number of new student accounts in the file will cause the account table to exceed capacity (10 accounts), do not add any new students
        currentNumAccounts = len(Account.objects.all())
        newTotalNumAccounts = currentNumAccounts + len(newStudentAccounts)
        
        if newTotalNumAccounts > 10:
            print("Error: Adding the students in the file will cause the max number of accounts (10) to be exceeded")
            return

        createdAccounts = [] # List to store accounts successfully added
    
        # If the capacity will not be exceeded, then insert into Users and Accounts table
        for acc in newStudentAccounts:
            usernameInUse = User.objects.filter(username=acc["username"]).exists() # Check if username (which must be unique) is being used 

            if not usernameInUse:
                User.objects.create_user(username=acc["username"], first_name=acc["firstName"], last_name=acc["lastName"], password=acc["password"])
                # Verify User and Account objects were created, and if not, output error message for User/Account that was not created
                try:
                    userObj = User.objects.get(username=acc["username"])
                    userCreated = True
                except User.DoesNotExist:
                    userCreated = False

            if userCreated:
                Account.objects.create(user=userObj, first_name=acc["firstName"], last_name=acc["lastName"])
                try:
                    accountObj = Account.objects.get(user=userObj)
                    accountCreated = True
                except Account.DoesNotExist:
                    accountCreated = False

            if accountCreated:
                createdAccounts.append(accountObj)

            if not userCreated or usernameInUse or not accountCreated:
                username = acc["username"]
                print(f"Error: Account with username {username} could not be created")

        print(f"Successfully added {len(createdAccounts)} student accounts to InCollege")
        print("These accounts were added: ")
        print(createdAccounts)

def addNewJobsFromFile(filePath):
    if os.path.isfile(filePath): # New Jobs file provided
        newJobsFile = open(filePath, "r") # Will be reading from file
        newJobs = []
        lines = newJobsFile.readlines()
        newJob = {}
        
        # First, scan the file to see when a multi-line description appears (end marked by '&&&' line)
        jobsWithMultilineDesc = [] # Will hold job number that corresponds to job being inserted (ex: if two jobs are in file, job 1 will be first)
        jobNumber = 1
        for line in lines:
            if line == "=====\n" or line == "=====":
                jobNumber += 1
            elif line == "&&&\n":
                jobsWithMultilineDesc.append(jobNumber)

        description = "" # Used in case there are multiline descriptions

        # Then, scan lines normally
        jobNumber = 1
        lineNumber = 1
        for line in lines:
            if line == "=====\n" or line == "=====":
                jobNumber += 1
                newJobs.append(newJob)
                newJob = {}
                description = "" # Reset multipart description
                lineNumber = 0 # Next iteration would be a new job
            elif lineNumber == 1:
                newJob["title"] = line.split("\n")[0] # Remove new line character
            elif not jobNumber in jobsWithMultilineDesc: # Job does not have a multiline description
                if lineNumber == 2:
                    newJob["description"] = line.split("\n")[0]
                if lineNumber == 3:
                    newJob["poster"] = line.split("\n")[0]
                if lineNumber == 4:
                    newJob["employer"] = line.split("\n")[0]
                if lineNumber == 5:
                    newJob["location"] = line.split("\n")[0]
                if lineNumber == 6:
                    newJob["salary"] = line.split("\n")[0]
            else: # Job does have a multiline description
                if line != "&&&\n":
                    description += (line.split("\n")[0] + " ")
                else:
                    newJob["description"] = description[:-1] # Remove last extra space
                    jobsWithMultilineDesc.remove(jobNumber)
                    lineNumber = 2 # So, next loop iteration will get poster
            lineNumber += 1

        # If the number of new jobs in the file will cause the jobs table to exceed capacity (10 jobs), do not add any new jobs
        currentNumJobs = len(Job.objects.all())
        newTotalNumJobs = currentNumJobs + len(newJobs)

        if newTotalNumJobs > 10:
            print("Error: Adding the jobs in the file will cause the max number of jobs (10) to be exceeded")
            return

        createdJobs = [] # List to store jobs successfully added

        # If the capacity will not be exceeded, then insert into Jobs table
        for job in newJobs:
            jobTitleExists = Job.objects.filter(title=job["title"]).exists()

            # Only accept new jobs via the API if they have a different title than the jobs that are already in the system
            if not jobTitleExists:
                posterFirstName = job["poster"].split(" ")[0]
                posterLastName = job["poster"].split(" ")[1]
                try:
                    posterUserObj = User.objects.get(first_name=posterFirstName, last_name=posterLastName)
                    posterIsUser = True
                except User.DoesNotExist:
                    posterIsUser = False

                if posterIsUser:
                    Job.objects.create(title=job["title"], description=job["description"], postedBy=posterUserObj, employer=job["employer"], location=job["location"], salary=int(job["salary"]))

                    # Verify Job was created
                    try:
                        jobObj = Job.objects.get(title=job["title"], description=job["description"], postedBy=posterUserObj, employer=job["employer"], location=job["location"], salary=int(job["salary"]))
                        jobCreated = True
                    except Job.DoesNotExist:
                        jobCreated = False

                if jobCreated:
                    createdJobs.append(jobObj)

                if not jobCreated or not posterIsUser:
                    jobTitle = job["title"]
                    print(f"Error: Job with title '{jobTitle}' could not be created")
            
            if jobTitleExists:
                jobTitle = job["title"]
                print(f"Error: Job with title '{jobTitle}' could not be created")

        print(f"Successfully added {len(createdJobs)} jobs to InCollege")
        print("These jobs were added: ")
        print(createdJobs)
    