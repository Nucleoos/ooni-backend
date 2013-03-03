__all__ = ['Report', 'TestHelperTMP']
from storm.twisted.transact import transact
from storm.locals import *

from oonib import randomStr
from oonib import transactor

def generateReportID():
    """
    Generates a report ID for usage in the database backed oonib collector.

    XXX note how this function is different from the one in report/api.py
    """
    report_id = randomStr(100)
    return report_id

class OModel(object):

    transactor = transactor

    def getStore(self):
        return Store(database)

    @transact
    def create(self, query):
        store = Store(database)
        store.execute(query)
        store.commit()

    @transact
    def save(self):
        store = getStore()
        store.add(self)
        store.commit()

class Report(OModel):
    """
    This represents an OONI Report as stored in the database.

    report_id: this is generated by the backend and is used by the client to
               reference a previous report and append to it. It should be
               treated as a shared secret between the probe and backend.

    software_name: this indicates the name of the software performing the test
                   (this will default to ooniprobe)

    software_version: this is the version number of the software running the
                      test.

    test_name: the name of the test on which the report is being created.

    test_version: indicates the version of the test

    progress: what is the current progress of the report. This allows clients
              to report event partial reports up to a certain percentage of
              progress. Once the report is complete progress will be 100.

    content: what is the content of the report. If the current progress is less
             than 100 we should append to the YAML data structure that is
             currently stored in such field.

    XXX this is currently not used.
    """
    __storm_table__ = 'reports'

    createQuery = "CREATE TABLE " + __storm_table__ +\
                  "(id INTEGER PRIMARY KEY, report_id VARCHAR, software_name VARCHAR,"\
                  "software_version VARCHAR, test_name VARCHAR, test_version VARCHAR,"\
                  "progress VARCHAR, content VARCHAR)"


    id = Int(primary=True)

    report_id = Unicode()

    software_name = Unicode()
    software_version = Unicode()
    test_name = Unicode()
    test_version = Unicode()
    progress = Int()

    content = Unicode()

    @transact
    def new(report):
        store = self.getStore()

        print "Creating new report %s" % report

        report_id = generateReportID()
        new_report = models.Report()
        new_report.report_id = unicode(report_id)

        new_report.software_name = report['software_name']
        new_report.software_version = report['software_version']
        new_report.test_name = report['test_name']
        new_report.test_version = report['test_version']
        new_report.progress = report['progress']

        if 'content' in report:
            new_report.content = report['content']

        print "Report: %s" % report

        store.add(new_report)
        try:
            store.commit()
        except:
            store.close()

        defer.returnValue({'backend_version': backend_version, 'report_id':
                            report_id})


class TestHelperTMP(OModel):
    __storm_table__ = 'testhelpertmp'

    createQuery = "CREATE TABLE " + __storm_table__ +\
                  "(id INTEGER PRIMARY KEY, report_id VARCHAR, test_helper VARCHAR,"\
                  " client_ip VARCHAR, creation_time VARCHAR)"

    id = Int(primary=True)

    report_id = Unicode()

    test_helper = Unicode()
    client_ip = Unicode()

    creation_time = Date()
