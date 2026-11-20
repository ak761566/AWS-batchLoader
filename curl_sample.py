''' Request
curl -X 'POST' \
  'http://awe1ptstpeps01.aws.portico.org:9500/loader/job/multistepjob/v1/submitwithjson/LoaderJob' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{"configSourceType":"GIT", "propertyFileName":"AMD-CARIBNEWS_I-LoaderConfig.properties", "loaderProfileFileName":"AMD-CARIBNEWS_I-LoaderProfile.xml"}'

'''
''' Response
{
  "jobId": "6138",
  "jobName": "LoaderJob",
  "jobOutputIds": null,
  "jobInputIds": null,
  "jobResult": null,
  "jobStatus": "JOB_SUBMITTED",
  "jobInputParameters": null,
  "jobStartTime": null,
  "jobEndTime": null,
  "errors": null,
  "jobsLibError": null,
  "steps": [],
  "className": "org.ithaka.portico.jobslib.utils.webservice.JobWebserviceResponse"
}
'''

#Status
'''
curl -X 'GET' \
  'http://awe1ptstpeps01.aws.portico.org:9500/loader/job/v1/status/6138' \
  -H 'accept: */*'


'''
'''
Response:
{
  "jobId": "6138",
  "jobName": "LoaderJob",
  "jobOutputIds": null,
  "jobInputIds": [
    "24f73902-72e9-4863-af97-2fda7a083073"
  ],
  "jobResult": "EXECUTING",
  "jobStatus": "STARTED",
  "jobInputParameters": {
    "job_name_param": "LoaderJob",
    "json": "file:/portico/workarea/loader/workarea/jobs-cache/4f995025-e88e-4a50-bd57-62b3c825f343.json",
    "jobkey": "ab82bd15-3179-42e3-9198-cbfdb27e95e2"
  },
  "jobStartTime": "2026-11-12T05:01:06.129-0500",
  "jobEndTime": null,
  "errors": [],
  "jobsLibError": null,
  "steps": [
    {
      "stepName": "LoaderJob_Initialize",
      "extCode": "COMPLETED",
      "exitDescription": "Workflow step completed successfully."
    },
    {
      "stepName": "LoaderJob_ConfigurationProcessor",
      "extCode": "COMPLETED",
      "exitDescription": "Workflow step completed successfully."
    },
    {
      "stepName": "LoaderJob_FetchBaseDataUnitsOntoWorkarea",
      "extCode": "COMPLETED",
      "exitDescription": "Workflow step completed successfully."
    },
    {
      "stepName": "LoaderJob_RuleProcessor",
      "extCode": "COMPLETED",
      "exitDescription": "Workflow step completed successfully."
    },
    {
      "stepName": "LoaderJob_BatchNameCreator",
      "extCode": "COMPLETED",
      "exitDescription": "Workflow step completed successfully."
    },
    {
      "stepName": "LoaderJob_BatchGroupValidator",
      "extCode": "EXECUTING",
      "exitDescription": ""
    }
  ],
  "className": "org.ithaka.portico.jobslib.utils.webservice.JobWebserviceResponse"
}
'''