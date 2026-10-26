"""
Chapter 1 - boto3 Clients, Sessions and the Credential Chain

Run:  python chapter1.py

What you will learn:
  - what boto3.client() actually creates, and what it does NOT create
  - where boto3 looks for your credentials, in order, and which link won
  - how to read a botocore error instead of guessing at it

This chapter is safe to run with no AWS account configured. It makes
exactly one real API call (sts:GetCallerIdentity), which is free, reads
nothing and changes nothing. If you have no credentials yet it will say
so in plain English instead of crashing.

Long-form material is in the NOTES section at the bottom of this file.
"""

import boto3
import botocore.exceptions

# The region this account's console and project live in.
# Keep this aligned with what `aws configure` was given - an explicit
# region_name= argument OVERRIDES the one in ~/.aws/config, so a
# mismatch here silently wins and you get "does not exist" errors for
# resources you just created in the other region.
REGION = "ap-southeast-2"


def a_client_is_just_a_local_object() -> None:
    s3 = boto3.client("s3", region_name=REGION)

    print("python type   :", type(s3).__name__)
    print("service       :", s3.meta.service_model.service_name)
    print("endpoint      :", s3.meta.endpoint_url)
    print("api version   :", s3.meta.service_model.api_version)

    # ------------------------------------------------------------------
    # Nothing above touched the network. boto3.client() builds a plain
    # Python object that holds your credentials, a region and a URL -
    # that is all. It is closer to writing down a phone number than to
    # making a phone call.
    #
    # Notice the type name is "S3", a class that did not exist until the
    # line ran. boto3 reads a JSON description of the service shipped
    # inside botocore and generates the class and all its methods at
    # runtime. That is why your editor cannot autocomplete them, and why
    # a misspelled method only fails when you call it.
    #
    # Practical consequence: a wrong region or a typo'd service name
    # does NOT fail here. It fails later, on the first real call, which
    # is the single most confusing thing for beginners.
    # ------------------------------------------------------------------


def where_do_the_credentials_come_from() -> None:
    session = boto3.Session()
    credentials = session.get_credentials()

    if credentials is None:
        print("credential source : NONE FOUND")
        print("region resolved   :", session.region_name)
        return

    frozen = credentials.get_frozen_credentials()
    print("credential source :", credentials.method)
    print("access key id     : ...%s" % frozen.access_key[-4:])
    print("region resolved   :", session.region_name)

    # ------------------------------------------------------------------
    # A Session is the thing that actually owns your identity; a client
    # is created from one. Call boto3.client() directly, as above, and
    # boto3 quietly builds a default Session for you - so the two styles
    # are the same thing, one just hides the Session.
    #
    # credentials.method is the useful part: it names which link of the
    # chain supplied the keys ("env", "shared-credentials-file",
    # "iam-role", ...). When a script works on your laptop but fails on
    # an EC2 box, print this first - it answers the question instantly.
    # ------------------------------------------------------------------


def who_am_i() -> None:
    sts = boto3.client("sts", region_name=REGION)

    try:
        identity = sts.get_caller_identity()
    except botocore.exceptions.NoCredentialsError:
        print("No credentials found - the chain ran out before step 5.")
        print("Fix it by running:  aws configure")
        return
    except botocore.exceptions.ClientError as exc:
        # The server answered, and the answer was "no".
        code = exc.response["Error"]["Code"]
        print("AWS rejected the call. Error code:", code)
        if code in ("InvalidClientTokenId", "SignatureDoesNotMatch"):
            print("The keys exist but are wrong, revoked, or mistyped.")
        return

    print("account           :", identity["Account"])
    print("user/role arn     :", identity["Arn"])

    # ------------------------------------------------------------------
    # Two different failures, caught separately, because they mean
    # opposite things:
    #
    #   NoCredentialsError - boto3 never found keys to sign with, so no
    #                        request was ever sent. A LOCAL problem.
    #   ClientError        - the request was sent, signed, and AWS said
    #                        no. A REMOTE problem: wrong keys, expired
    #                        token, or missing IAM permission.
    #
    # Catching bare Exception here would merge the two and cost you the
    # distinction that tells you where to look.
    #
    # get_caller_identity is the "whoami" of AWS. Every caller is
    # allowed to run it - it needs no IAM permission at all - which
    # makes it the right first call to prove a setup works.
    # ------------------------------------------------------------------


if __name__ == "__main__":
    print("=" * 62)
    print("1. a client is just a local object")
    print("=" * 62)
    a_client_is_just_a_local_object()

    print()
    print("=" * 62)
    print("2. where do the credentials come from")
    print("=" * 62)
    where_do_the_credentials_come_from()

    print()
    print("=" * 62)
    print("3. who am i")
    print("=" * 62)
    who_am_i()


# ======================================================================
# NOTES - read these once the code above makes sense
# ======================================================================
#
# 1. The credential chain
#
#    boto3 never asks you where your keys are. It walks a fixed list of
#    places and stops at the first one that has them:
#
#    ┌────────────────────────────────────────────────────┐
#    │ 1. Keys passed straight into boto3.client(...)     │
#    ├────────────────────────────────────────────────────┤
#    │ 2. Environment variables (AWS_ACCESS_KEY_ID)       │
#    ├────────────────────────────────────────────────────┤
#    │ 3. Shared credentials file  ~/.aws/credentials     │
#    ├────────────────────────────────────────────────────┤
#    │ 4. Shared config file       ~/.aws/config          │
#    ├────────────────────────────────────────────────────┤
#    │ 5. IAM role - EC2 / ECS / Lambda metadata          │
#    └────────────────────────────────────────────────────┘
#                            │
#                            ▼
#              first one with keys wins, rest ignored
#
#    Now the same five steps, in words:
#
#    1. Hard-coded keys in the call itself. This works, and you must
#       never do it - it is how keys end up in git history forever.
#    2. Environment variables. Wins over the files, which is why an old
#       AWS_ACCESS_KEY_ID left in a shell silently overrides the profile
#       you just configured. First thing to check when "aws configure
#       worked but my script still fails".
#    3. ~/.aws/credentials - what `aws configure` writes. The normal
#       place for a laptop.
#    4. ~/.aws/config - region and profile settings, and SSO.
#    5. Instance metadata. On EC2, ECS or Lambda the machine itself
#       carries a role, so there are no keys on disk at all. This is the
#       correct way to do it in production, and the reason steps 1-4
#       should stay empty on a server.
#
#    "First one wins" is the whole rule. Every confusing credential bug
#    is really a higher step winning that you forgot was set.
#
#
# 2. Client vs resource
#
#    boto3 offers two interfaces to the same services:
#
#      boto3.client("s3")    - thin wrapper over the raw HTTP API.
#                              Every AWS action exists here. Returns
#                              plain dicts straight from the JSON.
#      boto3.resource("s3")  - object-oriented layer on top. Nicer to
#                              read, but it is frozen: AWS stopped
#                              adding to it, and newer services have
#                              no resource interface at all.
#
#    Learn the client. It covers everything, every tutorial and every
#    StackOverflow answer uses it, and the dicts it returns match the
#    AWS API documentation field for field.
#
#
# 3. Why the dicts look like that
#
#    get_caller_identity() returned a dict with "Account", "Arn" and
#    also a "ResponseMetadata" key you did not ask for. That metadata -
#    request id, HTTP status, retry count - is attached to every single
#    boto3 response. Ignore it while learning; reach for the request id
#    when you need AWS support to find your call in their logs.
