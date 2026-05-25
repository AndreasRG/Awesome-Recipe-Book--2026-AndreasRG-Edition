#!/bin/bash









# NOTE! I set up VM's manually in Azure Portal UI (ClickOps) so this is just a demonstration and documentation 
# for my VM's. Both are the same, ports are different but I will not be doing those here since they 
# already exist in Azure! They are both the same config apart from names and ports so I only did one file aswell.














# ---------------------------------------------------------
# Configuration (edit these if needed)
# ---------------------------------------------------------

RESOURCE_GROUP="TEST"
LOCATION="norwayeast"
VM_NAME="backend-vm"
VM_SIZE="Standard_B2als_v2"
IMAGE="Ubuntu2404"
ADMIN_USER="azureuser"
SSH_KEY="$HOME/.ssh/id_rsa.pub"
VNET_NAME="project-vnet"
SUBNET_NAME="backend-subnet"
NSG_NAME="backend-nsg"

# ---------------------------------------------------------
# Resource Group
# ---------------------------------------------------------

az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# ---------------------------------------------------------
# Virtual Network + Subnet
# ---------------------------------------------------------

az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name $VNET_NAME \
  --address-prefix 10.0.0.0/16 \
  --subnet-name $SUBNET_NAME \
  --subnet-prefix 10.0.1.0/24

# ---------------------------------------------------------
# Network Security Group
# ---------------------------------------------------------

az network nsg create \
  --resource-group $RESOURCE_GROUP \
  --name $NSG_NAME

# Open ports for Nginx or backend
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name $NSG_NAME \
  --name AllowHTTP \
  --protocol tcp \
  --priority 1000 \
  --destination-port-range 80 \
  --access allow

az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name $NSG_NAME \
  --name AllowHTTPS \
  --protocol tcp \
  --priority 1001 \
  --destination-port-range 443 \
  --access allow

# ---------------------------------------------------------
# Create VM
# ---------------------------------------------------------

az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image $IMAGE \
  --size $VM_SIZE \
  --admin-username $ADMIN_USER \
  --ssh-key-values $SSH_KEY \
  --vnet-name $VNET_NAME \
  --subnet $SUBNET_NAME \
  --nsg $NSG_NAME \
  --public-ip-sku Standard \
  --zone 1

# ---------------------------------------------------------
# Install Docker + Compose (cloud-init)
# ---------------------------------------------------------

az vm extension set \
  --resource-group $RESOURCE_GROUP \
  --vm-name $VM_NAME \
  --publisher Microsoft.Azure.Extensions \
  --name CustomScript \
  --settings '{
    "fileUris": [],
    "commandToExecute": "apt update && apt install -y docker.io docker-compose"
  }'

echo "VM creation script completed (not executed)."
