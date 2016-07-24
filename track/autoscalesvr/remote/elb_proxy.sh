
#!/usr/bin/env sh
lbname=$1
aws elb create-load-balancer-policy --load-balancer-name $lbname --policy-name EnableProxyProtocol  --policy-type-name ProxyProtocolPolicyType --policy-attributes AttributeName=ProxyProtocol,AttributeValue=True
aws elb set-load-balancer-policies-for-backend-server --load-balancer-name $lbname --instance-port 80 --policy-names EnableProxyProtocol
aws elb describe-load-balancers --load-balancer-name $lbname


