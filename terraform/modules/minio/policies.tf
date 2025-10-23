resource "minio_canned_policy" "etl_policy" {
    name = "etl_policy"
    policy = <<EOT
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::raw-data/*",
                    "arn:aws:s3:::processed-data/*",
                    "arn:aws:s3:::logs/*"
                ]
            }
        ]
    }
    EOT
}

resource "minio_canned_policy" "analytics_policy" {
    name = "analytics_policy"
    policy = <<EOT
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::processed-data/*",
                    "arn:aws:s3:::logs/*"
                ]
            }
        ]
    }
    EOT
}