#!/usr/bin/env node
import * as cdk from '@aws-cdk/core';
import { CloudwatchImproveNotificationStack } from '../lib/cloudwatch_improve_notification-stack';

const app = new cdk.App();
new CloudwatchImproveNotificationStack(app, 'CloudwatchImproveNotificationStack');
