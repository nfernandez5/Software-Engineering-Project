import sys
import os # Needed to stop code from executing twice
from django.apps import AppConfig

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

studentAccountFilePath = "{}/../api/studentAccounts.txt".format(BASE_DIR)
newJobsFilePath = "{}/../api/newJobs.txt".format(BASE_DIR)

class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'
    
    def ready(self):
        # signals are imported, so that they are defined and can be used
        from jobs.api import addStudentAccountsFromFile, addNewJobsFromFile

        # The import data from input files API should only be used when running the server or tests
        if "runserver" not in sys.argv and "test" not in sys.argv:
            return True

        if os.environ.get("RUN_MAIN"):
            addStudentAccountsFromFile(studentAccountFilePath)
            addNewJobsFromFile(newJobsFilePath)

        import jobs.signals