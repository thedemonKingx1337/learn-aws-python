# AWS Safety and Unsettled Decisions

## Confirm before spending money

EC2 instances, Glue jobs, Glue crawlers, NAT gateways and provisioned databases cost real money even on a learning account, and a `.py` file is easier to run accidentally than a notebook.

- **Confirm with the author before running anything that provisions billable infrastructure.** Reading, listing and describing are fine; creating is not.
- **Write the teardown steps into the chapter alongside the setup steps**, so the chapter cannot teach how to create something without also teaching how to delete it.
- Prefer the free-tier or free-call option when one exists (for example `sts:GetCallerIdentity`, which costs nothing and needs no IAM permission).

## Never commit secrets

Never write access keys into a chapter, a README or a commit. The existing [.gitignore](../../.gitignore) already covers `__pycache__/`, `*.py[cod]`, `.venv/`, `.vscode/`, `data/`, `.aws/`, `credentials` and `*.pem`. Extend it **before** writing any file that could hold a secret.

Hard-coding keys into `boto3.client(...)` is step 1 of the credential chain and it does work — which is exactly why it must be shown as a thing never to do, not as a convenience.

## Decisions still open — ask rather than assume

- **Credentials** — whether chapters use a named profile, environment variables, or AWS SSO. Not yet decided; `aws configure` has never been run on this machine.
- **Target environment** — whether a chapter runs against real AWS, against LocalStack/`moto`, or in Glue's local container. This changes the code, so state it at the top of each chapter.
- **Region** — settled on `ap-southeast-2`, matching the account's console and the `REGION` constant in `chapter1.py`. Do not switch regions: the account sits under an AWS Organizations *service control policy* that returned an explicit deny for `kms:ListAliases` in 14 of the 17 enabled regions. Only `ap-southeast-2`, `us-east-1` and `us-west-2` answered. Only KMS was tested, so the full scope of the restriction is inferred, not confirmed.
- **Kinesis** — denied by the same service control policy in every region tested (ap-southeast-2, us-east-1, us-west-2). Anything that needs a Kinesis stream can't run in this account, including the Udemy course's streaming lab.
