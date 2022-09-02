#!/bin/bash

echo "Injectig AWS keys"

sed -i "s/AWS_ACCESS_KEY_ID/$1/g" config.yaml
sed -i "s/AWS_SECRET_ACCESS_KEY/$2/g" config.yaml

echo "Injection complete"
