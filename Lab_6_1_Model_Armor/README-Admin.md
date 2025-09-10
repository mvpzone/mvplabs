## 1. Admin - Setup
1.  Enable ModelArmor API in the project (one-time)
2.  Assign "modelarmor.admin" role to all the students

## 2. Admin  - Cleanup 

To clean up your environment and remove any resources created during this lab, run the provided reset script:

run for the prod and for all the locations

```bash
gcloud auth application-default login
python lab6.1-cleanup-templates.py --project ts-labs-npp-ai-sec-prd --location us-central1
```
