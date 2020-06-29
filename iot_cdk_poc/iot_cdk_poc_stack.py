from aws_cdk import core
from aws_cdk import aws_iam as iam
from aws_cdk import aws_iot as iot

class IotCdkPocStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.provisioning_role = iam.Role(
            self, "AwsIotProvisioningRole", 
            assumed_by=iam.ServicePrincipal("iot.amazonaws.com"), 
            inline_policies={
                "AwsIotProvisioningPolicy":
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(
                            actions=[
                                "iot:AddThingToThingGroup",
                                "iot:AttachPrincipalPolicy",
                                "iot:AttachThingPrincipal",
                                "iot:CreateCertificateFromCsr",
                                "iot:CreatePolicy",
                                "iot:CreateThing",
                                "iot:DescribeCertificate",
                                "iot:DescribeThing",
                                "iot:DescribeThingGroup",
                                "iot:DescribeThingType",
                                "iot:DetachThingPrincipal",
                                "iot:GetPolicy",
                                "iot:ListPolicyPrincipals",
                                "iot:ListPrincipalPolicies",
                                "iot:ListPrincipalThings",
                                "iot:ListThingGroupsForThing",
                                "iot:ListThingPrincipals",
                                "iot:RegisterCertificate",
                                "iot:RegisterThing",
                                "iot:RemoveThingFromThingGroup",
                                "iot:UpdateCertificate",
                                "iot:UpdateThing",
                                "iot:UpdateThingGroupsForThing",
                                "iot:AddThingToBillingGroup",
                                "iot:DescribeBillingGroup",
                                "iot:RemoveThingFromBillingGroup"
                            ],
                            resources=["*"],
                            effect=iam.Effect.ALLOW,
                        )
                    ])
            })

        policy_name = "AwsIotProvisioningDataPolictyTest1"
        iot.CfnPolicy(scope=self, 
                      id='AWSIotProvisioningDataPlanePolicy',
                      policy_document=get_data_policy_doc(),
                      policy_name=policy_name)

        template_body = get_template_body(device_type='YoYoMaDeviceType', policy_name=policy_name)
        self.provisioning_template = \
            iot.CfnProvisioningTemplate(scope=self, 
                                        id='AWSIoTProvisioningTemplate',
                                        provisioning_role_arn=self.provisioning_role.role_arn,
                                        template_body=template_body,
                                        enabled=True,
                                        template_name='IotProvisioningTemplateTest1',
                                        pre_provisioning_hook=None)


def get_data_policy_doc():
    return {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish",
        "iot:Receive"
      ],
      "Resource": [
        "arn:aws:iot:eu-west-1:195361640859:topic/12345678/audit",
        "arn:aws:iot:eu-west-1:195361640859:topic/sdk/test/java",
        "arn:aws:iot:eu-west-1:195361640859:topic/sdk/test/Python",
        "arn:aws:iot:eu-west-1:195361640859:topic/topic_1",
        "arn:aws:iot:eu-west-1:195361640859:topic/topic_2"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Subscribe"
      ],
      "Resource": [
        "arn:aws:iot:eu-west-1:195361640859:topicfilter/12345678/audit",
        "arn:aws:iot:eu-west-1:195361640859:topicfilter/sdk/test/java",
        "arn:aws:iot:eu-west-1:195361640859:topicfilter/sdk/test/Python",
        "arn:aws:iot:eu-west-1:195361640859:topicfilter/topic_1",
        "arn:aws:iot:eu-west-1:195361640859:topicfilter/topic_2"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect"
      ],
      "Resource": [
        "arn:aws:iot:eu-west-1:195361640859:client/sdk-java",
        "arn:aws:iot:eu-west-1:195361640859:client/basicPubSub",
        "arn:aws:iot:eu-west-1:195361640859:client/sdk-nodejs-*"
      ]
    }
  ]
}


def get_template_body(device_type: str, policy_name: str) -> str:
    return f'''{{
    "Parameters": {{
        "SerialNumber": {{
        "Type": "String"
        }},
        "AWS::IoT::Certificate::Id": {{
        "Type": "String"
        }}
    }},
    "Resources": {{
        "certificate": {{
        "Properties": {{
            "CertificateId": {{
            "Ref": "AWS::IoT::Certificate::Id"
            }},
            "Status": "Active"
        }},
        "Type": "AWS::IoT::Certificate"
        }},
        "policy": {{
        "Properties": {{
            "PolicyName": "{policy_name}"
        }},
        "Type": "AWS::IoT::Policy"
        }},
        "thing": {{
        "OverrideSettings": {{
            "AttributePayload": "MERGE",
            "ThingGroups": "DO_NOTHING",
            "ThingTypeName": "REPLACE"
        }},
        "Properties": {{
            "AttributePayload": {{}},
            "ThingGroups": [],
            "ThingName": {{
            "Ref": "SerialNumber"
            }},
            "ThingTypeName": "{device_type}"
        }},
        "Type": "AWS::IoT::Thing"
        }}
    }}
    }}'''