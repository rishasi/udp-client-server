## Simple UDP Client-Server Deployment on AKS

The purpose of this document is to deploy a simple Client-Server model using UDP on AKS Cluster. The test was performed to `verify` the "Session Affinity" using "Client IP".

The Server is deployed as Pod(s) on AKS Cluster, while the Clients are deployed as simple Python apps on Azure VMs.

The idea is to have 1 client send request to one Pod, through the Azure Load Balancer.

Part of the code has been taken from [here](https://pythontic.com/modules/socket/udp-client-server-example).

### How to use the Application.

#### Deploying the Server

The Docker Image is available at `rishasi/udp-server:v1`.

> Dockerfile for reference:
>
> ```dockerfile
> FROM python:3
> WORKDIR /usr/src/app
> COPY . .
> ENV UDPPORT 20001
> CMD [ "python3", "./server.py" ]
> EXPOSE ${UDPPORT}/udp
> ```
>
>
> The Dockerfile was written and built into an image from a location containing the `server.py` file.

**Deployment YAML:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: udp-server
  labels:
    app: udp-server
spec:
  replicas: 4
  selector:
    matchLabels:
      app: udp-server
  template:
    metadata:
      labels:
        app: udp-server
    spec:
      containers:
      - name: udp-server
        image: "rishasi/udp-server:v1"
        imagePullPolicy: Always
        ports:
        - containerPort: 20001

```

After the Deployment is up and running, expose the Deployment using a Service. For test purposes, the Deployment was exposed using an Internal Azure Load balancer.

**Service YAML:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: udp-server
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
spec:
  type: LoadBalancer
  ports:
  - name: udp-server
    port: 20001
    protocol: UDP
  selector:
    app: udp-server
  sessionAffinity: ClientIP
  externalTrafficPolicy: Local

```

Notice the last 2 lines, these are the ones that allow preserving the Client IP and to have session affinity based on Client's IP.

Reference links:

- https://kubernetes.io/docs/concepts/services-networking/service/#proxy-mode-ipvs
- https://kubernetes.io/docs/tutorials/services/source-ip/#source-ip-for-services-with-type-loadbalancer
- https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip



Once the `Deployment` and `Service` is created, you can use the endpoint of the Application to send UDP packets.

```bash
$ k get svc,deploy
NAME                         TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)           AGE
service/udp-server           LoadBalancer   10.0.191.31   10.240.0.7      20001:31698/UDP   7d22h

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/udp-server   4/4     4            4           35s
```



The Service can now be accessed on `External-IP` of the Load balancer Service.

---

#### Deploying the Client

Now to consume the Service, deploy the Client. The Client sends 150 requests to the Server, with 1 second interval between each message.

On a VM, where you have Python2 installed, run the following:

```bash
$ git clone https://github.com/rishasi/udp-client-server.git
$ cd client
$ python3 client.py <lb-external-ip>

  Do Ctrl+c to exit the program !!

 1. Client Sent :  Message number 0 from: 172.16.0.4
 2. Client received :  Hello UDP Client

 1. Client Sent :  Message number 1 from: 172.16.0.4
 2. Client received :  Hello UDP Client
....

```

To test the Session Affinity, and the Client IP Preservation, run the client on 2-3 different VMs, so that it is easier to verify.

After the requests have been sent from multiple clients, check the logs for each Pod. You will notice each Client being connected to a unique Pod.



