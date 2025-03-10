locals {
  counter                        = var.counter != "" ? var.counter : random_id.counter.hex
  default_dataset_bucket         = "${var.project}-${var.environment}-rs-fwd-${var.venue}"
  dataset_bucket                 = var.dataset_bucket != "" ? var.dataset_bucket : local.default_dataset_bucket
  default_code_bucket            = "${var.project}-${var.environment}-cc-fwd-${var.venue}"
  code_bucket                    = var.code_bucket != "" ? var.code_bucket : local.default_code_bucket
  default_isl_bucket             = "${var.project}-${var.environment}-isl-fwd-${var.venue}"
  isl_bucket                     = var.isl_bucket != "" ? var.isl_bucket : local.default_isl_bucket
  default_osl_bucket             = "${var.project}-${var.environment}-osl-fwd-${var.venue}"
  osl_bucket                     = var.osl_bucket != "" ? var.osl_bucket : local.default_osl_bucket
  default_triage_bucket          = "${var.project}-${var.environment}-triage-fwd-${var.venue}"
  triage_bucket                  = var.triage_bucket != "" ? var.triage_bucket : local.default_triage_bucket
  default_lts_bucket             = "${var.project}-${var.environment}-lts-fwd-${var.venue}"
  lts_bucket                     = var.lts_bucket != "" ? var.lts_bucket : local.default_lts_bucket
  clear_s3_aws_es                = var.clear_s3_aws_es
  key_name                       = var.keypair_name != "" ? var.keypair_name : split(".", basename(var.private_key_file))[0]
  sns_count                      = var.po_daac_cnm_r_event_trigger == "sns" ? 1 : 0
  sqs_count                      = var.asf_daac_cnm_r_event_trigger == "sqs" ? 1 : 0
  cnm_r_kinesis_count            = 0
  lambda_repo                    = "${var.artifactory_base_url}/${var.artifactory_repo}/gov/nasa/jpl/${var.project}/sds/pcm/lambda"
  po_daac_delivery_event_type    = split(":", var.po_daac_delivery_proxy)[2]
  po_daac_delivery_region        = split(":", var.po_daac_delivery_proxy)[3]
  po_daac_delivery_account       = split(":", var.po_daac_delivery_proxy)[4]
  po_daac_delivery_resource_name = split(":", var.po_daac_delivery_proxy)[5]

  asf_daac_delivery_event_type     = split(":", var.asf_daac_delivery_proxy)[2]
  asf_daac_delivery_region         = split(":", var.asf_daac_delivery_proxy)[3]
  asf_daac_delivery_account        = split(":", var.asf_daac_delivery_proxy)[4]
  asf_daac_delivery_resource_name  = split(":", var.asf_daac_delivery_proxy)[5]
  asf_daac_proxy_cnm_r_sns_count   = var.environment == "dev" && var.venue != "int" && local.sqs_count == 1 ? 1 : 0
  asf_daac_delivery_proxy_maturity = split("-", var.asf_daac_delivery_proxy)[4]

  pge_artifactory_dev_url     = "${var.artifactory_base_url}/general-develop/gov/nasa/jpl/${var.project}/sds/pge"
  pge_artifactory_release_url = "${var.artifactory_base_url}/general/gov/nasa/jpl/${var.project}/sds/pge"

  # refer to job spec file extension
  #  accountability_report_job_type    = "accountability_report"
  hlsl30_query_job_type            = "hlsl30_query"
  hlss30_query_job_type            = "hlss30_query"
  batch_query_job_type             = "batch_query"
  slcs1a_query_job_type            = "slcs1a_query"
  slc_ionosphere_download_job_type = "slc_download_ionosphere"

  use_s3_uri_structure = var.use_s3_uri_structure
  grq_es_url           = "${var.grq_aws_es ? "https" : "http"}://${var.grq_aws_es ? var.grq_aws_es_host : aws_instance.grq.private_ip}:${var.grq_aws_es ? var.grq_aws_es_port : 9200}"

  cnm_response_queue_name = {
    "dev"  = "${var.project}-dev-daac-cnm-response"
    "int"  = "${var.project}-int-daac-cnm-response"
    "test" = "${var.project}-test-daac-cnm-response"
  }
  cnm_response_dl_queue_name = {
    "dev"  = "${var.project}-dev-daac-cnm-response-dead-letter-queue"
    "int"  = "${var.project}-int-daac-cnm-response-dead-letter-queue"
    "test" = "${var.project}-test-daac-cnm-response-dead-letter-queue"
  }

  e_misfire_metric_alarm_name = "${var.project}-${var.venue}-${local.counter}-event-misfire"
  enable_query_timer          = var.cluster_type == "reprocessing" ? false : true
  enable_download_timer       = false

  delete_old_job_catalog = true
}
resource "null_resource" "download_lambdas" {
  provisioner "local-exec" {
    #curl -H "X-JFrog-Art-Api:${var.artifactory_fn_api_key}" -O https://artifactory-fn.jpl.nasa.gov/artifactory/general-develop/gov/nasa/jpl/opera/sds/pcm/lambda/develop/lambda-cnm-r-handler-develop.zip
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_cnm_r_handler_package_name}-${var.lambda_package_release}.zip"
  }
  provisioner "local-exec" {
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_harikiri_handler_package_name}-${var.lambda_package_release}.zip"
  }
  provisioner "local-exec" {
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_isl_handler_package_name}-${var.lambda_package_release}.zip"
  }
  provisioner "local-exec" {
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_e-misfire_handler_package_name}-${var.lambda_package_release}.zip"
  }
  provisioner "local-exec" {
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_timer_handler_package_name}-${var.lambda_package_release}.zip"
  }
  provisioner "local-exec" {
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_report_handler_package_name}-${var.lambda_package_release}.zip"
  }
  provisioner "local-exec" {
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_data-subscriber-download_handler_package_name}-${var.lambda_package_release}.zip"
  }
  provisioner "local-exec" {
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_data-subscriber-query_handler_package_name}-${var.lambda_package_release}.zip"
  }
  provisioner "local-exec" {
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_data-subscriber-download-slc-ionosphere_handler_package_name}-${var.lambda_package_release}.zip"
  }
  provisioner "local-exec" {
    command = "curl -H \"X-JFrog-Art-Api:${var.artifactory_fn_api_key}\" -O ${local.lambda_repo}/${var.lambda_package_release}/${var.lambda_batch-query_handler_package_name}-${var.lambda_package_release}.zip"
  }
}

resource "null_resource" "is_po_daac_cnm_r_event_trigger_value_valid" {
  count = contains(var.cnm_r_event_trigger_values_list, var.po_daac_cnm_r_event_trigger) ? 0 : "ERROR: Invalid po_daac_cnm_r_event_trigger value"
}

resource "null_resource" "is_asf_daac_cnm_r_event_trigger_value_valid" {
  count = contains(var.cnm_r_event_trigger_values_list, var.asf_daac_cnm_r_event_trigger) ? 0 : "ERROR: Invalid asf_daac_cnm_r_event_trigger value"
}

resource "null_resource" "is_cluster_type_valid" {
  count = contains(var.valid_cluster_type_values, var.cluster_type) ? 0 : "ERROR: cluster_type must be one of the following: ${var.valid_cluster_type_values}"
}

resource "random_id" "counter" {
  byte_length = 2
}


######################
# sns
######################

# SNS Topic that the operator will subscribe to. All failed event messages
# should be sent here
resource "aws_sns_topic" "operator_notify" {
  name = "${var.project}-${var.venue}-${local.counter}-operator-notify"
}

resource "aws_sns_topic_policy" "operator_notify" {
  depends_on = [aws_sns_topic.operator_notify, data.aws_iam_policy_document.operator_notify]
  arn        = aws_sns_topic.operator_notify.arn
  policy     = data.aws_iam_policy_document.operator_notify.json
}

data "aws_iam_policy_document" "operator_notify" {
  depends_on = [aws_sns_topic.operator_notify]
  policy_id  = "__default_policy_ID"
  statement {
    actions = [
      "SNS:Publish",
      "SNS:RemovePermission",
      "SNS:SetTopicAttributes",
      "SNS:DeleteTopic",
      "SNS:ListSubscriptionsByTopic",
      "SNS:GetTopicAttributes",
      "SNS:Receive",
      "SNS:AddPermission",
      "SNS:Subscribe"
    ]

    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    resources = [
      aws_sns_topic.operator_notify.arn
    ]
    sid = "__default_statement_ID"
  }
}

######################
# sqs
######################
resource "aws_sqs_queue" "harikiri_queue" {
  name                      = "${var.project}-${var.venue}-${local.counter}-queue"
  delay_seconds             = 0
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 0
  #sqs_managed_sse_enabled    = true
  visibility_timeout_seconds = 600
}

resource "aws_sqs_queue_policy" "queue_policy" {
  queue_url = aws_sqs_queue.harikiri_queue.id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "harikirisqspolicy",
  "Statement": [
    {
      "Sid": "First",
      "Effect": "Allow",
      "Principal": {
          "AWS": "arn:aws:iam::${var.aws_account_id}:role/${var.asg_role}"
      },
      "Action": [
          "SQS:SendMessage",
          "SQS:GetQueueUrl"
      ],
      "Resource": "${aws_sqs_queue.harikiri_queue.arn}"
    }
  ]
}
POLICY
}

resource "aws_sqs_queue" "cnm_response_dead_letter_queue" {
  name = "${var.project}-${var.venue}-${local.counter}-daac-cnm-response-dead-letter-queue"
  #  name                      = "${var.project}-dev-daac-cnm-response-dead-letter-queue"
  message_retention_seconds = 1209600
  #sqs_managed_sse_enabled   = true
}

resource "aws_sqs_queue" "cnm_response" {
  name                       = var.use_daac_cnm_r == true ? "${var.project}-${var.cnm_r_venue}-daac-cnm-response" : "${var.project}-${var.venue}-${local.counter}-daac-cnm-response"
  redrive_policy             = "{\"deadLetterTargetArn\":\"${aws_sqs_queue.cnm_response_dead_letter_queue.arn}\", \"maxReceiveCount\": 2}"
  visibility_timeout_seconds = 300
  receive_wait_time_seconds  = 10
  #sqs_managed_sse_enabled    = true
}

data "aws_sqs_queue" "cnm_response" {
  depends_on = [aws_sqs_queue.cnm_response]
  name       = aws_sqs_queue.cnm_response.name
}

resource "aws_lambda_event_source_mapping" "sqs_cnm_response" {
  depends_on       = [aws_sqs_queue.cnm_response, aws_lambda_function.sqs_cnm_response_handler]
  count            = local.sqs_count
  event_source_arn = var.use_daac_cnm_r == true ? var.cnm_r_sqs_arn[local.asf_daac_delivery_proxy_maturity] : aws_sqs_queue.cnm_response.arn
  #event_source_arn = var.use_daac_cnm_r == true ? "${var.project}-${var.cnm_r_venue}-daac-cnm-response" : aws_sqs_queue.cnm_response.arn
  function_name = aws_lambda_function.sqs_cnm_response_handler.arn
}

data "aws_iam_policy_document" "cnm_response" {
  policy_id = "SQSDefaultPolicy"
  statement {
    actions = [
      "SQS:SendMessage"
    ]
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${var.aws_account_id}:root",
        "arn:aws:iam::871271927522:root",
        "arn:aws:iam::156214815904:root",
        "arn:aws:iam::097260566921:root"
      ]
    }
    resources = [
      data.aws_sqs_queue.cnm_response.arn
    ]
    sid = "Sid1571258347580"
  }
}

resource "aws_sqs_queue_policy" "cnm_response" {
  queue_url = data.aws_sqs_queue.cnm_response.url
  policy    = data.aws_iam_policy_document.cnm_response.json
}

resource "aws_sqs_queue" "isl_queue" {
  name                      = "${var.project}-${var.venue}-${local.counter}-isl-queue"
  delay_seconds             = 0
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  #sqs_managed_sse_enabled    = true
  visibility_timeout_seconds = 60
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.isl_dead_letter_queue.arn
    maxReceiveCount     = 2
  })
}
resource "aws_sqs_queue_policy" "isl_queue_policy" {
  queue_url = aws_sqs_queue.isl_queue.id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "islsqspolicy",
  "Statement": [
    {
      "Sid": "First",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "SQS:SendMessage",
      "Resource": "${aws_sqs_queue.isl_queue.arn}",
      "Condition": {
        "ArnLike": { "aws:SourceArn": "arn:aws:s3:*:*:${local.isl_bucket}" }
      }
    }
  ]
}
POLICY
}

# resource "aws_s3_bucket_object" "folder" {
#  bucket = local.isl_bucket
#  acl    = "private"
#  key    = "met_required/"
#  source = "/dev/null"
#}

# resource "aws_s3_bucket_notification" "sqs_isl_notification" {
#  bucket = local.isl_bucket
#
#  queue {
#    id        = "sqs_event"
#    queue_arn = aws_sqs_queue.isl_queue.arn
#    events    = ["s3:ObjectCreated:*"]
#  }

#}

resource "aws_sqs_queue" "isl_dead_letter_queue" {
  name                      = "${var.project}-${var.venue}-${local.counter}-isl-dead-letter-queue"
  delay_seconds             = 0
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 0
  #sqs_managed_sse_enabled    = true
  visibility_timeout_seconds = 500
}

######################
# lambda
######################
resource "aws_lambda_function" "harikiri_lambda" {
  depends_on    = [null_resource.download_lambdas]
  filename      = "${var.lambda_harikiri_handler_package_name}-${var.lambda_package_release}.zip"
  description   = "Lambda function to terminate & decrement instances from their ASG"
  function_name = "${var.project}-${var.venue}-${local.counter}-harikiri-autoscaling"
  role          = var.lambda_role_arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.7"
  timeout       = 600
}

resource "aws_cloudwatch_log_group" "harikiri_lambda" {
  name              = "/aws/lambda/${var.project}-${var.venue}-${local.counter}-harikiri-autoscaling"
  retention_in_days = var.lambda_log_retention_in_days
}


resource "aws_lambda_event_source_mapping" "harikiri_queue_event_source_mapping" {
  batch_size       = 1
  enabled          = true
  event_source_arn = aws_sqs_queue.harikiri_queue.arn
  function_name    = aws_lambda_function.harikiri_lambda.arn
}

data "aws_subnet_ids" "lambda_vpc" {
  vpc_id = var.lambda_vpc
}

resource "aws_lambda_function" "isl_lambda" {
  depends_on    = [null_resource.download_lambdas, aws_sns_topic.operator_notify]
  filename      = "${var.lambda_isl_handler_package_name}-${var.lambda_package_release}.zip"
  description   = "Lambda function to process data from ISL bucket"
  function_name = "${var.project}-${var.venue}-${local.counter}-isl-lambda"
  handler       = "lambda_function.lambda_handler"
  role          = var.lambda_role_arn
  runtime       = "python3.8"
  timeout       = 60
  vpc_config {
    security_group_ids = [var.cluster_security_group_id]
    subnet_ids         = data.aws_subnet_ids.lambda_vpc.ids
  }
  environment {
    variables = {
      "JOB_TYPE"            = var.lambda_job_type
      "JOB_RELEASE"         = var.pcm_branch
      "JOB_QUEUE"           = var.lambda_job_queue
      "MOZART_URL"          = "https://${aws_instance.mozart.private_ip}/mozart"
      "DATASET_S3_ENDPOINT" = "s3-us-west-2.amazonaws.com"
      "SIGNAL_FILE_SUFFIX"  = "{\"met_required\":{\"ext\":\".signal\"}}"
      "ISL_SNS_TOPIC"       = aws_sns_topic.operator_notify.arn
      "MET_REQUIRED"        = "met_required"
    }
  }
}

resource "aws_cloudwatch_log_group" "isl_lambda" {
  name              = "/aws/lambda/${var.project}-${var.venue}-${local.counter}-isl-lambda"
  retention_in_days = var.lambda_log_retention_in_days
}

resource "aws_lambda_event_source_mapping" "isl_queue_event_source_mapping" {
  batch_size       = 10
  enabled          = true
  event_source_arn = aws_sqs_queue.isl_queue.arn
  function_name    = aws_lambda_function.isl_lambda.arn
}

#####################################
# sds config  QUEUE block generation
#####################################
resource "null_resource" "destroy_es_snapshots" {
  triggers = {
    private_key_file   = var.private_key_file
    mozart_pvt_ip      = aws_instance.mozart.private_ip
    grq_aws_es         = var.grq_aws_es
    purge_es_snapshot  = var.purge_es_snapshot
    project            = var.project
    venue              = var.venue
    counter            = var.counter
    es_snapshot_bucket = var.es_snapshot_bucket
    grq_es_url         = "${var.grq_aws_es ? "https" : "http"}://${var.grq_aws_es ? var.grq_aws_es_host : aws_instance.grq.private_ip}:${var.grq_aws_es ? var.grq_aws_es_port : 9200}"
    clear_s3_aws_es    = var.clear_s3_aws_es
  }

  connection {
    type        = "ssh"
    host        = self.triggers.mozart_pvt_ip
    user        = "hysdsops"
    private_key = file(self.triggers.private_key_file)
  }

  provisioner "remote-exec" {
    when = destroy
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 5; done",
      "set -ex",
      "source ~/.bash_profile",
      "if [ \"${self.triggers.purge_es_snapshot}\" = true ]; then",
      "  aws s3 rm --recursive s3://${self.triggers.es_snapshot_bucket}/${self.triggers.project}-${self.triggers.venue}-${self.triggers.counter}",
      "  if [ \"${self.triggers.grq_aws_es}\" = true ]; then",
      "    ~/mozart/bin/snapshot_es_data.py --es-url ${self.triggers.grq_es_url} delete-lifecycle --policy-id hourly-snapshot",
      "    ~/mozart/bin/snapshot_es_data.py --es-url ${self.triggers.grq_es_url} delete-all-snapshots --repository snapshot-repository",
      "    ~/mozart/bin/snapshot_es_data.py --es-url ${self.triggers.grq_es_url} delete-repository --repository snapshot-repository",
      "  fi",
      "fi"
    ]
  }
}

locals {
  rs_fwd_lifecycle_configuration_json = jsonencode(
    {
      "Rules" : [
        {
          "Expiration" : {
            "Days" : var.venue == "pst" ? 1095 : var.rs_fwd_bucket_ingested_expiration
          },
          "ID" : "RS Bucket Products Deletion",
          "Prefix" : "products/",
          "Status" : "Enabled"
        },
        {
          "Expiration" : {
            "Days" : var.venue == "pst" ? 1095 : var.rs_fwd_bucket_ingested_expiration
          },
          "ID" : "RS Bucket Inputs Deletion",
          "Prefix" : "inputs/",
          "Status" : "Enabled"
        }
      ]
    }
  )
}

resource "null_resource" "rs_fwd_add_lifecycle_rule" {
  depends_on = [local.rs_fwd_lifecycle_configuration_json, aws_instance.mozart]

  connection {
    type        = "ssh"
    host        = aws_instance.mozart.private_ip
    user        = "hysdsops"
    private_key = file(var.private_key_file)
  }

  # this makes it re-run every time
  triggers = {
    always_run = timestamp()
  }

  provisioner "remote-exec" {
    inline = ["aws s3api put-bucket-lifecycle-configuration --bucket ${local.dataset_bucket} --lifecycle-configuration '${local.rs_fwd_lifecycle_configuration_json}'"]
  }

}

resource "aws_lambda_function" "sns_cnm_response_handler" {
  depends_on    = [null_resource.download_lambdas, aws_instance.mozart]
  filename      = "${var.lambda_cnm_r_handler_package_name}-${var.lambda_package_release}.zip"
  description   = "Lambda function to process CNM Response messages"
  function_name = "${var.project}-${var.venue}-${local.counter}-daac-sns-cnm_response-handler"
  handler       = "lambda_function.lambda_handler"
  timeout       = 300
  role          = var.lambda_role_arn
  runtime       = "python3.8"
  vpc_config {
    security_group_ids = [var.cluster_security_group_id]
    subnet_ids         = data.aws_subnet_ids.lambda_vpc.ids
  }
  environment {
    variables = {
      "EVENT_TRIGGER" = "sns"
      "JOB_TYPE"      = var.cnm_r_handler_job_type
      "JOB_RELEASE"   = var.product_delivery_branch
      "JOB_QUEUE"     = var.cnm_r_job_queue
      "MOZART_URL"    = "https://${aws_instance.mozart.private_ip}/mozart"
      "PRODUCT_TAG"   = "true"
    }
  }
}

resource "aws_lambda_function" "sqs_cnm_response_handler" {
  depends_on    = [null_resource.download_lambdas, aws_instance.mozart]
  filename      = "${var.lambda_cnm_r_handler_package_name}-${var.lambda_package_release}.zip"
  description   = "Lambda function to process CNM Response messages"
  function_name = "${var.project}-${var.venue}-${local.counter}-daac-sqs-cnm_response-handler"
  handler       = "lambda_function.lambda_handler"
  timeout       = 300
  role          = var.lambda_role_arn
  runtime       = "python3.8"
  vpc_config {
    security_group_ids = [var.cluster_security_group_id]
    subnet_ids         = data.aws_subnet_ids.lambda_vpc.ids
  }
  environment {
    variables = {
      "EVENT_TRIGGER" = "sqs"
      "JOB_TYPE"      = var.cnm_r_handler_job_type
      "JOB_RELEASE"   = var.product_delivery_branch
      "JOB_QUEUE"     = var.cnm_r_job_queue
      "MOZART_URL"    = "https://${aws_instance.mozart.private_ip}/mozart"
      "PRODUCT_TAG"   = "true"
    }
  }
}

resource "aws_cloudwatch_log_group" "sns_cnm_response_handler" {
  name              = "/aws/lambda/${var.project}-${var.venue}-${local.counter}-daac-sns-cnm_response-handler"
  retention_in_days = var.lambda_log_retention_in_days
}

resource "aws_cloudwatch_log_group" "sqs_cnm_response_handler" {
  name              = "/aws/lambda/${var.project}-${var.venue}-${local.counter}-daac-sqs-cnm_response-handler"
  retention_in_days = var.lambda_log_retention_in_days
}

resource "aws_sns_topic" "cnm_response" {
  name = var.use_daac_cnm_r == true ? "${var.project}-${var.cnm_r_venue}-daac-cnm-response" : "${var.project}-${var.venue}-${local.counter}-daac-cnm-response"
}

data "aws_sns_topic" "cnm_response" {
  depends_on = [aws_sns_topic.cnm_response]
  name       = aws_sns_topic.cnm_response.name
}

resource "aws_sns_topic_policy" "cnm_response" {
  depends_on = [aws_sns_topic.cnm_response, data.aws_iam_policy_document.sns_topic_policy]
  arn        = aws_sns_topic.cnm_response.arn
  policy     = data.aws_iam_policy_document.sns_topic_policy.json
}

data "aws_iam_policy_document" "sns_topic_policy" {
  depends_on = [aws_sns_topic.cnm_response]
  policy_id  = "__default_policy_ID"
  statement {
    actions = [
      "SNS:Publish",
      "SNS:SetTopicAttributes",
      "SNS:ListSubscriptionsByTopic",
      "SNS:GetTopicAttributes",
      "SNS:Receive",
      "SNS:Subscribe"
    ]
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${var.aws_account_id}:root",
        "arn:aws:iam::638310961674:root",
        "arn:aws:iam::234498297282:root"
      ]
    }
    resources = [
      aws_sns_topic.cnm_response.arn
    ]
    sid = "__default_statement_ID"
  }
}

resource "aws_sns_topic_subscription" "lambda_cnm_r_handler_subscription" {
  depends_on = [aws_sns_topic.cnm_response, aws_lambda_function.sns_cnm_response_handler]
  topic_arn  = aws_sns_topic.cnm_response.arn
  protocol   = "lambda"
  endpoint   = aws_lambda_function.sns_cnm_response_handler.arn
}

resource "aws_lambda_permission" "allow_sns_cnm_r" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sns_cnm_response_handler.function_name
  principal     = "sns.amazonaws.com"
  statement_id  = "ID-1"
  source_arn    = aws_sns_topic.cnm_response.arn
}

resource "aws_kinesis_stream" "cnm_response" {
  count       = local.cnm_r_kinesis_count
  name        = "${var.project}-${var.venue}-${local.counter}-daac-cnm-response"
  shard_count = 1
}

resource "aws_lambda_event_source_mapping" "kinesis_event_source_mapping" {
  depends_on        = [aws_kinesis_stream.cnm_response, aws_lambda_function.sns_cnm_response_handler]
  count             = local.cnm_r_kinesis_count
  event_source_arn  = aws_kinesis_stream.cnm_response[count.index].arn
  function_name     = aws_lambda_function.sns_cnm_response_handler.arn
  starting_position = "TRIM_HORIZON"
}

data "aws_ebs_snapshot" "docker_verdi_registry" {
  most_recent = true

  filter {
    name   = "tag:Verdi"
    values = [var.hysds_release]
  }
  filter {
    name   = "tag:Registry"
    values = ["2"]
  }
  filter {
    name   = "tag:Logstash"
    values = ["7.9.3"]
  }
}

resource "aws_lambda_function" "event-misfire_lambda" {
  depends_on    = [null_resource.download_lambdas, aws_instance.mozart]
  filename      = "${var.lambda_e-misfire_handler_package_name}-${var.lambda_package_release}.zip"
  description   = "Lambda function to process data from EVENT-MISFIRE bucket"
  function_name = "${var.project}-${var.venue}-${local.counter}-event-misfire-lambda"
  handler       = "lambda_function.lambda_handler"
  role          = var.lambda_role_arn
  runtime       = "python3.8"
  timeout       = 500
  vpc_config {
    security_group_ids = [var.cluster_security_group_id]
    subnet_ids         = data.aws_subnet_ids.lambda_vpc.ids
  }
  environment {
    variables = {
      "JOB_TYPE"                    = var.lambda_job_type
      "JOB_RELEASE"                 = var.pcm_branch
      "JOB_QUEUE"                   = var.lambda_job_queue
      "MOZART_ES_URL"               = "http://${aws_instance.mozart.private_ip}:9200"
      "DATASET_S3_ENDPOINT"         = "s3-us-west-2.amazonaws.com"
      "SIGNAL_FILE_BUCKET"          = local.isl_bucket
      "DELAY_THRESHOLD"             = var.event_misfire_delay_threshold_seconds
      "E_MISFIRE_METRIC_ALARM_NAME" = local.e_misfire_metric_alarm_name
    }
  }
}

resource "aws_cloudwatch_log_group" "event-misfire_lambda" {
  name              = "/aws/lambda/${var.project}-${var.venue}-${local.counter}-event-misfire-lambda"
  retention_in_days = var.lambda_log_retention_in_days
}

resource "aws_cloudwatch_event_rule" "event-misfire_lambda" {
  name                = "${aws_lambda_function.event-misfire_lambda.function_name}-Trigger"
  description         = "Cloudwatch event to trigger event misfire monitoring lambda"
  schedule_expression = var.event_misfire_trigger_frequency
}

resource "aws_cloudwatch_event_target" "event-misfire_lambda" {
  rule      = aws_cloudwatch_event_rule.event-misfire_lambda.name
  target_id = "Lambda"
  arn       = aws_lambda_function.event-misfire_lambda.arn
}

resource "aws_lambda_permission" "event-misfire_lambda" {
  statement_id  = aws_cloudwatch_event_rule.event-misfire_lambda.name
  action        = "lambda:InvokeFunction"
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.event-misfire_lambda.arn
  function_name = aws_lambda_function.event-misfire_lambda.function_name
}
