# TP2-redes

terminal 1:

cd ~/pox
./pox.py forwarding.l2_learning firewall


terminal 2:

sudo mn -c (limpia mininet)

sudo python3 topologia.py 3



Regla 1: Puerto 80 bloqueado (HTTP)
    # Crear servidor web en h3
    mininet> h3 python3 -m http.server 80 &

    # Intentar acceder desde h1 (debería fallar)
    mininet> h1 curl -m 5 10.0.0.3:80

Regla 2: UDP puerto 5001 desde h1 bloqueado
    # Crear servidor UDP en h2
    mininet> h2 nc -u -l 5001 &

    # Intentar enviar desde h1 (debería fallar)
    mininet> h1 echo "test" | nc -u -w 5 10.0.0.2 5001

    # Intentar enviar desde h3 (debería funcionar)
    mininet> h3 echo "test" | nc -u -w 5 10.0.0.2 5001

Verificar reglas en los switches:
    mininet> sh ovs-ofctl dump-flows s1
    mininet> sh ovs-ofctl dump-flows s2
    mininet> sh ovs-ofctl dump-flows s3

