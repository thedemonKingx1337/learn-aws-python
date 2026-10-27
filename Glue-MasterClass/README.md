# Glue MasterClass (Udemy course files, adapted)

Files from the Udemy course *AWS Glue: The Complete Masterclass*, changed to run in this AWS account. Every change is listed below. Inside `.py` and `.yaml` files the changes are also marked `OURS:` in comments; JSON can't hold comments, so template changes are recorded here only.

Progress on the Glue topics is tracked in [progress/aws.md](../progress/aws.md).

## Course names vs ours

| Course | Ours |
|---|---|
| bucket `awsglueudemycourse-datasoup-etl-artifacts` | `bucket101pb/etl-artifacts/` |
| bucket `awsglueudemycourse-datasoup-etl-targets` | `bucket101pb/etl-targets/` |
| bucket `awsglueudemycourse-datasoup-gluejob2-source` | `bucket101pb/gluejob2-source/` |
| bucket `crawlerdatasoup2022101` | `bucket101pb/crawler/` |
| Glue role `gluejobrole1` | `role101` (already exists) |
| region `us-east-1` | `ap-southeast-2` |
| Glue database `database101` | `database101` (same name; create it first) |

One bucket with four prefixes instead of four buckets. `bucket101pb` already exists, is encrypted with the KMS key `alias/s3101-KMS`, and its bucket policy already lets `role101` in.

`cfniamrole1.json` is kept for reference only: it creates `gluejobrole1`, and `role101` already does that job.

## Where to upload each folder

| Local folder | Upload to |
|---|---|
| `Glue-MasterClass/gluejob-artifacts/` | `s3://bucket101pb/etl-artifacts/gluejob-artifacts/` |
| `Glue-MasterClass/crawlerfiles/` | `s3://bucket101pb/crawler/crawlerfiles/` |
| `Glue-MasterClass/city_temperature.csv` | `s3://bucket101pb/gluejob2-source/` |

Upload through the console, signed in with your usual login. `learning-cli` can't: writing to an SSE-KMS bucket needs `kms:GenerateDataKey`, and it doesn't have that.

## Before running any job or crawler

1. **Let `role101` use the KMS key.** Without this, every job fails before it starts, because it can't even read its own script from `bucket101pb`. In IAM, open Roles, then `role101`, then Add permissions, then Create inline policy, and paste this JSON:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "UseS3101KmsKey",
         "Effect": "Allow",
         "Action": ["kms:Decrypt", "kms:GenerateDataKey"],
         "Resource": "PASTE-THE-KEY-ARN-HERE"
       }
     ]
   }
   ```

   Copy the key's ARN from KMS, Customer managed keys, the key with alias `s3101-KMS`. An IAM policy is enough here because the key policy's first statement, *Enable IAM User Permissions*, lets IAM policies in this account grant use of the key.

2. **Create the Glue database `database101`.** Glue, Data Catalog, Databases, Add database.

3. **Deploy the templates through CloudFormation**, Create stack, Upload a template file. Deploy `cfngluejob2.json` and `cfncrawler2.json` before `cfnworkflow2.json`, because the workflow's triggers name that job and that crawler.

Jobs 1 and 6 read the table `csv` in `database101`. The lab 1 crawler creates it when it crawls `s3://bucket101pb/crawler/crawlerfiles/lab1/csv/`.

## Which labs can run here

| Lab | Files | Runs here? |
|---|---|---|
| Crawlers, labs 1 to 4 | `crawlerfiles/` | yes, after step 1 |
| Glue job 1 | `gluejob1script.py`, `cfngluejob1.json` | yes, after steps 1 and 2 |
| Glue job 2 with crawler and workflow | `gluejob2script.py`, `cfngluejob2.json`, `cfncrawler2.json`, `cfnworkflow2.json` | yes, after steps 1 and 2 |
| Glue job 6, Data Quality | `code/gluejob6.py` | yes, after steps 1 and 2 |
| Glue jobs 3 to 5, streaming and DataBrew | `gluejob345.yaml`, `code/gluejob-streaming-*.py` | **no**: Kinesis is denied by the organisation's service control policy in every region checked |

DataBrew itself is allowed. The roles `gluejob345.yaml` would create, though, are not on `bucket101pb`'s exemption list, so they could not read the bucket.

The templates use Glue version 3.0. On 2026-10-27, AWS's version support policy listed only 0.9, 1.0 and 2.0 as end of life, so 3.0 can still be used for new jobs. The newest version is 6.0.

## Changes made to the course files

**Names, region and role** as in the first table, in every file.

**Bugs fixed:**

- `cfngluejob2.json` pointed at `gluejob2scripts.py`, but the file is `gluejob2script.py`. The job would have failed with "script not found".
- `cfngluejob2.json` passed `--s3_Destination_bucket`, with a capital D, but the script reads `s3_destination_bucket`. Argument names are case-sensitive, so the job would have stopped with a missing-argument error.
- `cfngluejob1.json` misspelled its target bucket (`wsglue...`). The script never reads that argument, so it did no harm, but it is corrected.
- `gluejob1script.py` and `gluejob6.py` defined the country lookup table at the bottom of the file, after the UDF had already been applied. The lookup then failed, the bare `except:` hid the error, and `country_code_2` came out NULL for every row. The table is now at the top. To check after a run: the Australia rows should show `AU`.
- `gluejob6.py` wrote to job 1's folder with `mode('overwrite')`, which would have deleted job 1's output. It now writes to `etl-targets/gluejob6`.

**Cost changes:**

- Jobs 1 and 2 used 15 `G.2X` workers, which is 30 DPUs. They now use 2 `G.1X` workers, 2 DPUs: about 15 times cheaper per minute, and plenty for files this size.
- `MaxRetries` went from 2 to 0, so a failing job runs once instead of three times, and you see the real error straight away.

## Cost and cleaning up

Glue charges per DPU-hour while a job or crawler is running. Nothing in these labs costs money while idle, apart from the KMS key itself, which is about $1 a month.

**`cfnworkflow2.json` schedules job 2 for every Saturday** (`cron(15 12 ? * 7/7 *)`, starting as soon as the stack is created), and the crawler runs after each successful job. Delete that stack when the lab is done, or it keeps running every week.

To clean up: delete the CloudFormation stacks, which removes the jobs, crawler, workflow and triggers. Then empty the four prefixes in `bucket101pb`.

## The large file

`city_temperature.csv` is 140 MB. GitHub rejects files over 100 MB in an ordinary push, so it is stored with Git LFS. The repo holds a small pointer file, and the content lives in GitHub's LFS storage.
