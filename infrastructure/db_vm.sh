#!/bin/bash

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

RESOURCE_GROUP="TEST"
LOCATION="norwayeast"
VM_NAME="db-vm-1" # Change this if you want to create multiple DB VMs (e.g., db-vm-2 for replicas)
VM_SIZE="Standard_B2als_v2"
IMAGE="Ubuntu2404"
ADMIN_USER="azureuser"
SSH_KEY="$HOME/.ssh/id_rsa.pub"
VNET_NAME="project-vnet"
SUBNET_NAME="backend-subnet"
NSG_NAME="backend-nsg"

# ---------------------------------------------------------
# Create Resource Group
# ---------------------------------------------------------

az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# ---------------------------------------------------------
# Create VNet + Subnet
# ---------------------------------------------------------

az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name $VNET_NAME \
  --address-prefix 10.0.0.0/16 \
  --subnet-name $SUBNET_NAME \
  --subnet-prefix 10.0.1.0/24

# ---------------------------------------------------------
# Create NSG
# ---------------------------------------------------------

az network nsg create \
  --resource-group $RESOURCE_GROUP \
  --name $NSG_NAME

# Allow Patroni API
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name $NSG_NAME \
  --name AllowPatroniAPI \
  --protocol tcp \
  --priority 1000 \
  --destination-port-range 8008 \
  --access allow

# Allow PostgreSQL
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name $NSG_NAME \
  --name AllowPostgres \
  --protocol tcp \
  --priority 1001 \
  --destination-port-range 5432 \
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
# Install PostgreSQL + Patroni (cloud-init)
# ---------------------------------------------------------

az vm extension set \
  --resource-group $RESOURCE_GROUP \
  --vm-name $VM_NAME \
  --publisher Microsoft.Azure.Extensions \
  --name CustomScript \
  --settings "{
    \"commandToExecute\": \"
      apt update &&
      apt install -y postgresql-16 postgresql-client-16 python3-pip &&
      pip install patroni[etcd] &&
      mkdir -p /etc/patroni &&
      PRIVATE_IP=$(hostname -I | awk '{print \$1}') &&
      cat <<EOF > /etc/patroni/patroni.yml
scope: recipe-cluster
name: $VM_NAME

restapi:
  listen: \$PRIVATE_IP:8008
  connect_address: \$PRIVATE_IP:8008

etcd:
  host: 10.0.0.4:2379

postgresql:
  listen: \$PRIVATE_IP:5432
  connect_address: \$PRIVATE_IP:5432
  data_dir: /var/lib/postgresql/16/main
  bin_dir: /usr/lib/postgresql/16/bin
  authentication:
    superuser:
      username: postgres
      password: admin123
    replication:
      username: replicator
      password: admin123
  parameters:
    wal_level: replica
    hot_standby: on

EOF

      systemctl stop postgresql &&
      systemctl disable postgresql &&
      pip install patroni &&
      cat <<EOF > /etc/systemd/system/patroni.service
[Unit]
Description=Patroni PostgreSQL
After=network.target

[Service]
User=postgres
ExecStart=/usr/local/bin/patroni /etc/patroni/patroni.yml
Restart=always

[Install]
WantedBy=multi-user.target
EOF

      systemctl daemon-reload &&
      systemctl enable patroni &&
      systemctl start patroni
    \"
  }"

echo "VM + Patroni bootstrap completed."
