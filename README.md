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


-- informe --

¿Cuál es la diferencia entre un Switch y un router? ¿Qué tienen en común?

son dispositivos de red que operan en distintas capas segun el modelo OSI.
Un switch opera en la capa de enlace, conecta dispositivos dentro de una misma red LAN. Usa direcciones MAC para direccionar los datos. 
Un router opera en la capa de red conecta diferentes redes entre si (LANs, WANs, internet). Usa direcciones IP para el enrutamiento, donde se encarga de encontrar el mejor camino para enviar informacion entre distintas redes.
Ambos dispositivos tienen la funcion de recibir, procesar y reenviar informacion en la red, utilizando tablas internas que les ayudan a determinar donde enviar los datos. Lo que los diferencia es el alcance de estas funciones.

¿Cuál es la diferencia entre un Switch convencional y un Switch OpenFlow?

Un switch convencional opera autonomamente distribuido sobre los switches. los cuales tomas sus propias decisiones sobre el manejo del trafico que pasa por ellos. construyen sus tablas automaticamente e independientemente por medio de politicas y algoritmos preconfigurados.
En cambio, un switch openflow depende de un controlador externo que se configura por medio de software. Solo recibe las isntrucciones del controlador y las aplica. Cuando le llega un paquete desconocido no toma sus propias decisiones, si no que se las delega al controlador.
Los Switches con openFlow permiten mayor flexibilidad para la gestion de red, por ser configurable a traves de programacion en un punto central, pero ofrece menor autonomia ya que tiene un unico punto de fallo, dandole ,mas vulnerabilidad en comparacion a un switch tradicional.


¿Se pueden reemplazar todos los routers de la Intenet por Switches OpenFlow? Piense en el escenario interASes para
elaborar su respuesta

No, un controlador que maneje los millones de flujos de toda la internet en tiempo real introduciria problemas de vulnerabilidad muy grandes. ademas de que los calculos computacionales en un solo punto serian imposibles con la tecnololgia actual. Ademas las politicas de enrutamiento especificas para empresas grandes, gobiernos y demas no podria ser controlado en una sola entidad sin bulnerar la seguridad y soberania de cada red.
La continuidad de internet depende de que no existan puntos unicos de fallos.

