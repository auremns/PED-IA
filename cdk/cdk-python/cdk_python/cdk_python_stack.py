#!/usr/bin/env python3
from aws_cdk import Duration, Stack
from aws_cdk import aws_dynamodb as ddb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_python_alpha as _lambda_python
from aws_cdk.aws_apigateway import LambdaIntegration, RestApi
from constructs import Construct


class CdkPythonStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api = RestApi(self, "flask-api", rest_api_name="flask-api")

        flask_lambda = _lambda_python.PythonFunction(
            self,
            "lambda_handler",
            function_name="pedia-flask-lambda",
            entry="lambdas",
            index="back.py",
            handler="handler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            timeout=Duration.seconds(300),
        )

        ddbTable = ddb.Table(
            scope=self,
            id="Sessions",
            table_name="Sessions",
            partition_key=ddb.Attribute(name="id", type=ddb.AttributeType.STRING),
            time_to_live_attribute="expiration",
        )

        ddbTable.grant_full_access(flask_lambda.grant_principal)

        root_resource = api.root

        any_method = root_resource.add_proxy(any_method=True, default_integration=LambdaIntegration(flask_lambda))
