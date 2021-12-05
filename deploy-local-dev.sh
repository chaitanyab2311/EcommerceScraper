kubectl apply -f cassandra/cassandra-deployment.yaml
kubectl apply -f cassandra/cassandra-service.yaml

kubectl port-forward --address 0.0.0.0 service/cassandra 9042:9042 