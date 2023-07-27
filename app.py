#!/usr/bin/env python3
import os
import aws_cdk as   cdk

from dotenv import load_dotenv
from codewhisperer.codewhisperer_stack import CodewhispererStack

load_dotenv()

app = cdk.App()

AWS_ACCOUNT_ID = os.getenv('account')
AWS_REGION = os.getenv('region')

CodewhispererStack(app, "codewhisperer-cats",
                   env=cdk.Environment(account=AWS_ACCOUNT_ID, region=AWS_REGION),
                   )

app.synth()
