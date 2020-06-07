provider "aws" {
    region = "us-east-1"
}

resource "aws_s3_bucket" "main" {
    bucket = "alferpir-flack-project"
    acl = "public-read"
    policy = file("./policy.json")
}