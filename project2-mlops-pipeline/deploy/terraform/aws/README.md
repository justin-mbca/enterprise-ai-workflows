# Terraform: AWS one-command deployment (Project 2)

This Terraform config provisions a small Ubuntu VM in the default VPC, opens the required ports, and bootstraps the MLOps stack automatically using the repository's `cloud-deploy.sh`.

## Prereqs
- Terraform >= 1.3
- AWS CLI configured with creds (or environment variables)
- Existing EC2 Key Pair name (to SSH if needed)

## Usage

```bash
cd project2-mlops-pipeline/deploy/terraform/aws

# Initialize
terraform init

# Plan (choose your key name and optionally region/instance type)
terraform plan -var "key_name=<YOUR_KEYPAIR_NAME>"

# Apply
terraform apply -auto-approve -var "key_name=<YOUR_KEYPAIR_NAME>"
```

After ~2-3 minutes, Terraform will output the public IP and endpoints, e.g.:

```
endpoints = {
  api_docs     = "http://<ip>:8000/docs"
  jupyter      = "http://<ip>:8888"
  mlflow       = "http://<ip>:5000"
  mlflow_proxy = "http://<ip>:5001"
}
public_dns = "ec2-xx-xx-xx-xx.compute-1.amazonaws.com"
public_ip = "xx.xx.xx.xx"
```

## Cleanup

```bash
terraform destroy -auto-approve -var "key_name=<YOUR_KEYPAIR_NAME>"
```

## Notes
- Security group allows 22, 5000, 5001, 8000, 8888 from `allowed_cidr` (default 0.0.0.0/0). Restrict it as needed using `-var "allowed_cidr=YOUR_IP/32"`.
- Instance type defaults to `t3.small`. Adjust via `-var "instance_type=t3.medium"` if needed.
- The instance uses cloud-init to fetch and run the project deploy script from GitHub.
