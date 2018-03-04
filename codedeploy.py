from troposphere import GetAtt, Join, Output, Parameter, Ref, Template, Tags
from troposphere import codedeploy, route53
from troposphere import elasticloadbalancingv2 as elb
from troposphere.ec2 import SecurityGroup, SecurityGroupRule, Instance
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration
from troposphere.codedeploy import AutoRollbackConfiguration, \
    DeploymentStyle, DeploymentGroup, ElbInfoList, LoadBalancerInfo, TargetGroupInfoList, Application

VpcSubnets = ["subnet-c78a4fae", "subnet-c64b4e8c"]
myvpc = "vpc-f8d62a91"

template = Template()

template.add_version('2010-09-09')

template.add_description(
    "AWS CloudFormation Template Demo"
)

lbsg = template.add_resource(SecurityGroup(
    "lbsg",
    VpcId='vpc-f8d62a91',
    GroupDescription='SG For ALB',
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='80',
            ToPort='80',
            CidrIp='52.56.182.198/32',
        ),
    ]
))

instancesg = template.add_resource(SecurityGroup(
    "instancesg",
    VpcId='vpc-f8d62a91',
    GroupDescription='SG For ASG instances',
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='80',
            ToPort='80',
            SourceSecurityGroupId=Ref(lbsg),
        ),
    ]

))

FrontendAlb = template.add_resource(elb.LoadBalancer(
    "FrontendAlb",
    Scheme="internet-facing",
    Subnets=VpcSubnets,
))

WebTargets = template.add_resource(elb.TargetGroup(
    "WebTargets",
    HealthCheckIntervalSeconds="30",
    HealthCheckProtocol="HTTP",
    HealthCheckTimeoutSeconds="10",
    HealthyThresholdCount="4",
    Matcher=elb.Matcher(
        HttpCode="200"),
    Name="WebTarget",
    Port="80",
    Protocol="HTTP",
    UnhealthyThresholdCount="3",
    VpcId=myvpc,
))

Listener = template.add_resource(elb.Listener(
    "Listener",
    Port="80",
    Protocol="HTTP",
    LoadBalancerArn=Ref(FrontendAlb),
    DefaultActions=[elb.Action(
        Type="forward",
        TargetGroupArn=Ref(WebTargets)
    )]
))

template.add_resource(elb.ListenerRule(
    "ListenerRule",
    ListenerArn=Ref(Listener),
    Conditions=[elb.Condition(
        Field="path-pattern",
        Values=["/*"])],
    Actions=[elb.Action(
        Type="forward",
        TargetGroupArn=Ref(WebTargets)
    )],
    Priority="1"
))

lcf = template.add_resource(LaunchConfiguration(
    "lcf",
    AssociatePublicIpAddress=False,
    ImageId='ami-4faa4d28',
    InstanceType='t2.micro',
    KeyName='Demo',
    SecurityGroups=[Ref(instancesg)],
))

asg = template.add_resource(AutoScalingGroup(
    "asg",
    DesiredCapacity="0",
    HealthCheckGracePeriod="10",
    HealthCheckType='EC2',
    LaunchConfigurationName=Ref(lcf),
    MaxSize="1",
    MinSize="0",
    TargetGroupARNs=[Ref(WebTargets)],
    VPCZoneIdentifier=VpcSubnets,
))

################### create deploy ######################

auto_rollback_configuration = AutoRollbackConfiguration(
    Enabled=True,
    Events=['DEPLOYMENT_FAILURE']
)

deployment_style = DeploymentStyle(
    DeploymentOption='WITH_TRAFFIC_CONTROL'
)

tg_info_list = TargetGroupInfoList(
    Name=GetAtt(WebTargets, "TargetGroupName")
)

load_balancer_info = LoadBalancerInfo(
    TargetGroupInfoList=[tg_info_list]
)

cdapp = template.add_resource(Application(
    "cdapp",
    ApplicationName="demoapp",
    ComputePlatform="Server"
))

deployment_group = DeploymentGroup(
    "DemoDeploymentGroup",
    ApplicationName=Ref(cdapp),
    AutoScalingGroups=[Ref(asg)],
    AutoRollbackConfiguration=auto_rollback_configuration,
    DeploymentStyle=deployment_style,
    LoadBalancerInfo=load_balancer_info,
    ServiceRoleArn='arn:aws:iam::364564756213:role/Admin'
)
template.add_resource(deployment_group)

print(template.to_yaml())