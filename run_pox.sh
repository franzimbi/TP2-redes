
POX_MODULE="ext.firewall"

POX_ARGS="--verbose"

./pox/pox.py samples.pretty_log  $POX_ARGS forwarding.l2_learning $POX_MODULE
