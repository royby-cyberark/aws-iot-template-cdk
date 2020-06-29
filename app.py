#!/usr/bin/env python3

from aws_cdk import core

from iot_cdk_poc.iot_cdk_poc_stack import IotCdkPocStack


app = core.App()
IotCdkPocStack(app, "iot-cdk-poc")

app.synth()
