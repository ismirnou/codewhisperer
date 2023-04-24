#!/usr/bin/env python3
import os

import aws_cdk as cdk

from codewhisperer.codewhisperer_stack import CodewhispererStack


app = cdk.App()
CodewhispererStack(app, "CodewhispererStack",
    env=cdk.Environment(account='359260672493', region='us-east-1'),
    )

app.synth()
