# TP2-redes

terminal 1:
./run_pox.sh


terminal 2:

./run_mininet.sh

Regla 1: Bloqueo puerto destino 80

h2 iperf -u -s -p 80 &
h1 iperf -u -c h2 -p 80

Regla 2: Bloqueo UDP desde h1 hacia puerto 5001

h4 iperf -u -s -p 5001 &
h1 iperf -u -c h4 -p 5001

Regla 3: Bloqueo bidireccional entre h2 y h4

h4 iperf -u -s -p 1000 &
h2 iperf -u -c h4 -p 1000


Verificar reglas en los switches:
    mininet> sh ovs-ofctl dump-flows s1
    mininet> sh ovs-ofctl dump-flows s2
    mininet> sh ovs-ofctl dump-flows s3

