# PRTG-to-Nagios
Con esta integración es posible enviar notificaciones de PRTG a NAGIOS XI

En PRTG:
          Ir a Setup/Account Settings/Notification Templates/Add Notification Template


          Completar el formulario y como canal de envío seleccionar Send SNMP Trap.


          Host/IP Address:    IP_NAGIOS
          SNMP Port:          162
          Community String:   COMUNIDAD_SNMP
          Custom Trap Code:   0310 (Este codigo es variable)
          Message ID:         0
          Message:            {"device":"%device","name":"%shortname","message":"%message"}
          Agent IP:           IP_LOCALHOST

                      __SAVE__


En NAGIOS:
          Desde la web importar el MIB del PRTG:
            - PRTG-MIB.mib
            - La opción: _Check this box if this server uses the SNMP Trap Interface._ debe de estar desmarcada.
            - Click en Procesar todos los Traps
            
          Desde el servidor Nagios ir a /etc/snmp/
            - Realizar un Backup del archivo de configuración: 
                cp snmptt.conf bk_202304141200_snmptt.conf
            - Buscar la siguiente linea:
            
                EVENT paesslerPrtgTrap .1.3.6.1.4.1.32446.0.10 "Status Events" Normal
                FORMAT $*
                EXEC /usr/local/bin/snmptraphandling.py "$aR" "SNMP Traps" "$s" "$@" "$-*" "$*"
                SDESC
                Variables:
                  1: paesslerPrtgTrapID
                  2: paesslerPrtgTrapEvent
                  3: paesslerPrtgTrapSensorstate
                  4: paesslerPrtgTrapMessage
                EDESC
             - Agregar justo despues:
                EVENT paesslerPrtgTrap .1.3.6.1.4.1.32446.0.0310 "Status Events" Normal
                FORMAT $*
                EXEC /usr/local/bin/prtg_snmptraphandling.py "$r" "SNMP Traps" "$3" "$@" "" "$4"
                SDESC
                Variables:
                  1: paesslerPrtgTrapID
                  2: paesslerPrtgTrapEvent
                  3: paesslerPrtgTrapSensorstate
                  4: paesslerPrtgTrapMessage
                EDESC
                
              - IMPORTANTE MANTENER EL MISMO "Custom Trap Code"

              - Crear el archivo /usr/local/bin/prtg_snmptraphandling.py
              - Reiniciar el proceso de SNMPTT para que cargue la nueva configuración:
                 systemctl restart snmptt.service


Listo ya las alarmas se pueden visualizar en objetos desconocidos dentro de Nagios.

