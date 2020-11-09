provider "aws" {
  region = "us-east-1"
}

locals {
  resource_name = "ella-admin"
  s3 = "dabble-of-devops-ella-admin-docs"
  s3_origin_id = "dabble-of-devops-ella-admin-docs"
  name = "Ella Admin Docs"
}

variable "cloudfront_aliases" {
  description = "Aliases for cloudfront"
  default = [
    "ella-admin.dabbleofdevopsonaws.com"]
}

resource "aws_s3_bucket" "ella-admin-logs" {
  bucket = "${local.s3}-logs"
  acl = "private"

  lifecycle_rule {
    id = "log"
    enabled = true

    //    prefix = "/"

    tags = {
      "rule" = "log"
      "autoclean" = "true"
    }

    expiration {
      days = 30
    }
  }

  tags = merge({
    Name = "${local.s3}-logs"
  })
}

resource "aws_cloudfront_origin_access_identity" "origin_access_identity" {
  comment = "Cloudfront ${local.name}"
}

resource "aws_s3_bucket" "ella-admin" {
  bucket = local.s3

  acl = "public-read"

  website {
    index_document = "index.html"
  }

  tags = merge({
    Name = "Ella Admin Docs"
  })
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name = aws_s3_bucket.ella-admin.bucket_regional_domain_name
    origin_id = local.s3_origin_id

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.origin_access_identity.cloudfront_access_identity_path
    }
  }

  custom_error_response {
    error_code = 403
    response_code = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code = 404
    response_code = 200
    response_page_path = "/index.html"
  }

  enabled = true
  is_ipv6_enabled = true
  comment = "Cloudfront distro for ${local.resource_name}"
  default_root_object = "index.html"

  logging_config {
    include_cookies = false
    bucket = "${aws_s3_bucket.ella-admin-logs.bucket}.s3.amazonaws.com"
    prefix = "logs"
  }

  aliases = var.cloudfront_aliases

  default_cache_behavior {
    allowed_methods = [
      "DELETE",
      "GET",
      "HEAD",
      "OPTIONS",
      "PATCH",
      "POST",
      "PUT"]
    cached_methods = [
      "GET",
      "HEAD"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl = 0
    default_ttl = 3600
    max_ttl = 86400
  }

  # Cache behavior with precedence 0
  ordered_cache_behavior {
    path_pattern = "/_static/*"
    allowed_methods = [
      "GET",
      "HEAD",
      "OPTIONS"]
    cached_methods = [
      "GET",
      "HEAD"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl = 0
    default_ttl = 3600
    max_ttl = 86400
    compress = true
    viewer_protocol_policy = "redirect-to-https"
  }

  price_class = "PriceClass_200"

  tags = merge({
    Name = "${local.resource_name}-cloudfront"
    Description = "${local.resource_name}-cloudfront"
  })

  viewer_certificate {
    acm_certificate_arn = "	arn:aws:acm:us-east-1:018835827632:certificate/ef7aba2f-c03a-47da-8d02-49a73f828553"
    ssl_support_method = "sni-only"
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations = [
        "US",
        "CA",
        "GB",
        "DE"]
    }
  }
}

output "cloudfront" {
  description = "Cloudfront Info"
  value = {
    id = aws_cloudfront_distribution.s3_distribution.id
    domain = aws_cloudfront_distribution.s3_distribution.domain_name
    etag = aws_cloudfront_distribution.s3_distribution.etag
    s3_bucket_regional_domain_name = aws_s3_bucket.ella-admin.bucket_regional_domain_name
    s3_bucket_domain_name = aws_s3_bucket.ella-admin.bucket_regional_domain_name
  }
}
