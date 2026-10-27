# AWS progress

Chapters: [aws/](../aws/). Account rules: [docs/aws/aws-safety-rules.md](../docs/aws/aws-safety-rules.md). How this file is used, including re-teaching: [docs/progress-tracking-rules.md](../docs/progress-tracking-rules.md).

**How the author is learning AWS:** through the console so far, alongside a Udemy course, *AWS Glue: The Complete Masterclass*, in this same AWS account. The code chapters in [aws/](../aws/) were written and run by Claude and have not been studied yet, so their topics are **Mentioned**; they start when the author moves to code. Topics covered only in the Udemy course are **Unknown** until the author says how deep they went. The course files, adapted to this account, are in [Glue-MasterClass/](../Glue-MasterClass/README.md).

## Topics

### Foundations

| Topic | Status | Where | First covered |
|---|---|---|---|
| boto3 clients and sessions | Mentioned | [aws/chapter1.py](../aws/chapter1.py) | 2026-10-25 |
| The credential chain | Mentioned | [aws/chapter1.py](../aws/chapter1.py) | 2026-10-25 |
| Reading boto3 errors | Mentioned | [aws/chapter1.py](../aws/chapter1.py) | 2026-10-25 |
| `sts:GetCallerIdentity` | Mentioned | [aws/chapter1.py](../aws/chapter1.py) | 2026-10-25 |
| IAM user, access keys and `aws configure` | Practised | console + terminal | 2026-10-26 |
| Credential hygiene: key ID vs secret, rotating a leaked key | Practised | console | 2026-10-26 |
| IAM users vs roles vs policies | Walked through | console | 2026-10-27 |
| Explicit deny: SCP vs bucket policy vs identity policy | Practised | console | 2026-10-27 |
| Bucket policy: deny everyone except a list | Walked through | console | 2026-10-27 |
| Recovering a locked bucket: Root access management | Practised | console | 2026-10-27 |
| AWS Organizations and SCPs: the region guardrail | Mentioned | - | 2026-10-27 |
| S3 bucket encryption: SSE-KMS, Bucket Key, customer managed key | Walked through | Udemy + console | 2026-10-24 |
| S3 buckets vs prefixes: one bucket instead of the course's four | Walked through | [Glue-MasterClass/](../Glue-MasterClass/README.md) | 2026-10-27 |
| S3 with boto3: objects, paginators, presigned URLs | Not started | chapter 2 | - |
| IAM in depth: writing policies, `AssumeRole` | Not started | chapter 3 | - |
| CloudWatch Logs | Not started | - | - |

### Compute

| Topic | Status | Where | First covered |
|---|---|---|---|
| Lambda: `invoke()`, payloads, cold starts | Not started | - | - |
| API Gateway + Lambda | Not started | - | - |
| EC2: launch, tags, lifecycle, teardown | Not started | - | - |
| ECR: pushing a container image | Not started | - | - |
| ECS / Fargate | Not started | - | - |

### Data

| Topic | Status | Where | First covered |
|---|---|---|---|
| DynamoDB | Not started | - | - |
| Glue Data Catalog: crawlers, databases, tables | Unknown | Udemy; [crawler labs](../Glue-MasterClass/README.md) | - |
| Glue ETL jobs: PySpark on AWS | Unknown | Udemy (at the GlueJob2 assignment); [jobs 1, 2, 6](../Glue-MasterClass/README.md) | - |
| Glue workflows and triggers | Not started | [cfnworkflow2.json](../Glue-MasterClass/README.md) | - |
| Glue Data Quality | Not started | [gluejob6.py](../Glue-MasterClass/README.md) | - |
| Glue DataBrew | Not started | [gluejob345.yaml](../Glue-MasterClass/README.md) | - |
| Glue streaming with Kinesis | Not started | blocked: Kinesis is denied by the SCP | - |
| Athena: SQL over S3 | Not started | - | - |

### Integration

| Topic | Status | Where | First covered |
|---|---|---|---|
| SQS / SNS | Not started | - | - |
| Step Functions | Not started | - | - |
| VPC basics | Not started | - | - |
| Infrastructure as code: CloudFormation or CDK | Not started | - | - |

## Re-teach notes

### boto3 clients and sessions
- **Idea:** `boto3.client("s3")` builds a local object holding a region, an endpoint and your keys, and sends nothing. Its class is generated at runtime from botocore's JSON service model, which is why the editor can't autocomplete it. A typo'd region fails later, on the first real call. A `boto3.Session()` owns the identity; clients are made from it.
- **Came up:** Claude wrote and ran `aws/chapter1.py` on 2026-10-25; the author has not opened it yet.
- **Start with:** read `aws/chapter1.py` top to bottom, run it, then re-type it without looking.
- **Check:** a wrong region didn't fail on the `boto3.client()` line. Why, and where does it fail?

### The credential chain
- **Idea:** boto3 looks for keys in a fixed order and the first match wins: keys passed in code, environment variables, `~/.aws/credentials`, `~/.aws/config`, then instance metadata (a role on EC2, ECS or Lambda). `session.get_credentials()` and `credentials.method` show which link supplied the keys.
- **Came up:** the author ran `aws configure`, which fills step 3. Claude then ran `aws/chapter1.py` to show the source change from `NONE FOUND` to `shared-credentials-file`.
- **Start with:** `where_do_the_credentials_come_from()` and the NOTES section at the bottom of `aws/chapter1.py`.
- **Check:** an old `AWS_ACCESS_KEY_ID` is still set in your shell after `aws configure`. Which keys win?

### Reading boto3 errors
- **Idea:** `NoCredentialsError` means no keys were found and nothing was sent (a local problem). `ClientError` means AWS answered and refused (a remote problem). Catch them separately, because they need opposite fixes. Inside `ClientError`, `InvalidClientTokenId` means AWS doesn't recognise the key ID, and `SignatureDoesNotMatch` means the secret is wrong.
- **Came up:** when Claude explained `AccessDenied` errors during the console work.
- **Start with:** `who_am_i()` in `aws/chapter1.py`.
- **Check:** your keys exist, but every call fails with `SignatureDoesNotMatch`. Which half of the key pair is wrong?

### `sts:GetCallerIdentity`
- **Idea:** the "whoami" of AWS: it returns the account and the user or role ARN. It is free and needs no permission, so it is the first call to prove a setup works.
- **Came up:** Claude ran `aws sts get-caller-identity` to confirm the author's `aws configure` worked; the ARN ended in `:user/learning-cli`.
- **Start with:** run `aws sts get-caller-identity` yourself.
- **Check:** it returns an ARN ending in `:root`. What is wrong?

### IAM user, access keys and `aws configure`
- **Idea:** the CLI needs an IAM **user** with an access key. A role has no keys, because something has to assume it. The author first opened the Roles wizard by mistake, which is how the difference was learned.
- **Did:** created `learning-cli` with `ReadOnlyAccess` + `AmazonS3FullAccess`, made a CLI access key, and ran `aws configure`. Claude showed the `LOCATION` column of `aws configure list`, which says which file supplied each value.
- **Check:** why not give a key that lives on your laptop `AdministratorAccess`?

### Credential hygiene: key ID vs secret, rotating a leaked key
- **Idea:** the Access Key ID (`AKIA...`) is an identifier and safe to show. The Secret Access Key is typed only at the `aws configure` prompt. A leaked secret is rotated (a new key, and the old one deleted), because copies of the leak may exist.
- **Did:** rotated the key after the leak; the local credentials file now holds the new one (`...COHR`).
- **Shaky:** pasted the secret into chat on 2026-10-26. To show a setup, send `aws sts get-caller-identity` output instead.
- **Check:** you pasted a secret key into a chat. Is deleting the message enough?

### IAM users vs roles vs policies
- **Idea:** a user is a permanent employee with an ID card (a long-lived key). A role is a temporary badge someone puts on: Glue wears `role101`, and the console login wears `AccountFullAccessRole`. A policy is the rule paper (Allow or Deny), attached to an identity or to a resource such as a bucket. Humans sign in through roles; IAM users are for programs and the CLI.
- **What worked:** that office analogy, in Malayalam: സ്ഥിരം ജോലിക്കാരൻ, താൽക്കാലിക badge, നിയമ പേപ്പർ.
- **Check:** why does the IAM console say users should only be used for programmatic access?

### Explicit deny: SCP vs bucket policy vs identity policy
- **Idea:** an explicit Deny beats every Allow. The error says where the deny came from: `explicit deny in a service control policy` (the organisation's guardrail), `in a resource-based policy` (a bucket policy), `in an identity-based policy` (the user's or role's own policy).
- **Did:** met the bucket-policy deny in the console, where it blocked even the full-access console role. The SCP deny showed up only in Claude's KMS checks.
- **Check:** `learning-cli` has `AmazonS3FullAccess` but gets `explicit deny in a resource-based policy`. Is the fix in IAM or on the bucket?

### Bucket policy: deny everyone except a list
- **Idea:** `"Effect": "Deny"`, `"Principal": "*"` and a `Condition` of `ArnNotLike` on `aws:PrincipalArn` together mean "deny anyone not on this list". `Resource` needs both `arn:aws:s3:::bucket` and `arn:aws:s3:::bucket/*`.
- **Did:** pasted Claude's policy into the bucket's console page, saved it, and hit the lock-out that followed.
- **Shaky:** Claude's first version copied the console role's ARN from an error message and locked the console out. Errors print the session ARN, `assumed-role/AccountFullAccessRole/<session>`, which drops the role's path; the real role ARN is `role/managed/AccountFullAccessRole`. Copy ARNs from the IAM role page or `aws iam get-role`, never from an error, and re-check access straight after saving a Deny.
- **Check:** why must `role101` be on the list for the GlueJob2 bucket?

### Recovering a locked bucket: Root access management
- **Idea:** IAM, then Root access management, then *Delete S3 bucket policy* starts a short-lived root session for that one action. Root can delete a bucket policy even when the policy denies everyone.
- **Did:** found the page and used it to remove the locking policy, then applied a corrected one.
- **Check:** why couldn't the console role delete the policy from the bucket's own Permissions tab?

### AWS Organizations and SCPs: the region guardrail
- **Idea:** this account belongs to an AWS Organization whose service control policy denies KMS in every enabled region except `ap-southeast-2`, `us-east-1` and `us-west-2`. Only KMS was tested. No IAM policy can override an SCP.
- **Came up:** in Claude's KMS checks during the GlueJob2 assignment; the author has not met this error themselves.
- **Check:** why can't the chapters move to `ap-south-1` (Mumbai)?

### S3 bucket encryption: SSE-KMS, Bucket Key, customer managed key
- **Idea:** SSE-KMS encrypts every object with a KMS key. Bucket Key cuts the number of KMS calls, so it costs less. A customer managed key costs about $1 a month while it exists. Reading or writing objects also needs `kms:Decrypt` and `kms:GenerateDataKey` on the key.
- **Did:** created `bucket101pb` (2026-10-24) and the key `alias/s3101-KMS` by following the Udemy lectures. Claude checked on 2026-10-27: SSE-KMS with that key, Bucket Key on, all public access blocked.
- **Check:** `learning-cli` can list the bucket, but an upload fails with an error that mentions KMS. Why?

### S3 buckets vs prefixes: one bucket instead of the course's four
- **Idea:** a bucket is flat, with no real folders. A key is the object's whole name, such as `etl-targets/gluejob1/part-00000.parquet`; the console draws a folder for each shared prefix up to a `/`, and `aws s3 ls` prints it as `PRE`. Glue jobs and crawlers take an S3 path, not just a bucket, so `s3://bucket101pb/etl-targets/` does the job of a whole course bucket, and the bucket's SSE-KMS, Block Public Access and policy setup is reused instead of repeated.
- **What worked:** not confirmed yet. Analogy given: one almirah (അലമാര) with four labelled shelves instead of four almirahs; then the twist that there are no shelves either, only the label written into each item's name.
- **Shaky:** asked twice whether one bucket is enough: first proposed reusing it, then asked how many to create. Check that the reason (prefixes) landed, not just the decision.
- **Check:** what does `PRE` stand for in `aws s3 ls`, and why doesn't `etl-targets/` need creating before job 1 writes to it? A crawler is pointed at `s3://bucket101pb/` instead of one lab folder: what goes wrong?
