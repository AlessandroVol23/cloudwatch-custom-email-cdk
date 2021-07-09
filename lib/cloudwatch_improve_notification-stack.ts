import * as lambda from "@aws-cdk/aws-lambda";
import * as path from "path";
import * as cdk from "@aws-cdk/core";
import * as cloudwatch from "@aws-cdk/aws-cloudwatch";
import * as sns from "@aws-cdk/aws-sns";
import * as snsSubscription from "@aws-cdk/aws-sns-subscriptions";
import * as iam from "@aws-cdk/aws-iam";
import { AlarmActionConfig } from "@aws-cdk/aws-cloudwatch";

export class CloudwatchImproveNotificationStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Lambda function to track something
    const fn = new lambda.Function(
      this,
      "lambda_cloudwatch_customize_notification",
      {
        runtime: lambda.Runtime.PYTHON_3_8,
        handler: "index.handler",
        code: new lambda.InlineCode(
          "def handler(event, context):\n\tprint(event)\n\treturn {'statusCode': 200, 'body': 'Hello, World'}"
        ),
      }
    );

    // SNS Topic for notifiying the lambda function
    const snsTopic = new sns.Topic(this, "cloudwatchAlarm");

    // Metric for the alarm
    const metric = fn.metric("Invocations");

    // Lambda which should be notified when the alarm kicks in
    const lambdaCustomizeMail = new lambda.Function(
      this,
      "customize_cloudwatch_alarm",
      {
        runtime: lambda.Runtime.PYTHON_3_8,
        handler: "index.handler",
        code: lambda.Code.fromAsset(`${path.resolve(__dirname)}/lambda`),
        environment: {
          SOURCE_EMAIL: process.env.SOURCE_EMAIL!,
          DESTINATION_EMAIL: process.env.DESTINATION_EMAIL!,
        },
      }
    );

    lambdaCustomizeMail.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["ses:SendEmail"],
        resources: ["*"],
        effect: iam.Effect.ALLOW,
      })
    );

    snsTopic.addSubscription(
      new snsSubscription.LambdaSubscription(lambdaCustomizeMail)
    );

    const alarm = new cloudwatch.Alarm(this, "testCustomizeAlarm", {
      metric: metric,
      threshold: 5,
      evaluationPeriods: 1,
    });

    alarm.addAlarmAction({
      bind(): AlarmActionConfig {
        return { alarmActionArn: snsTopic.topicArn };
      },
    });

    new cdk.CfnOutput(this, "AlarmToTrigger", { value: alarm.alarmName });
  }
}
