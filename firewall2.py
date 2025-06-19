# Coursera:
# - Software Defined Networking (SDN) course
# -- Programming Assignment: Layer-2 Firewall Application 
# Professor: Nick Feamster
# Teaching Assistant: Arpit Gupta

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr, IPAddr
from collections import namedtuple
import os
import json

log = core.getLogger()

class Firewall(EventMixin):
    def __init__(self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")
        self._set_rules('../rules.json')
    
    def _handle_ConnectionUp(self, event):
        self._load_rules(event.connection)
    
    def _load_rules(self, connection):
        for rule in self.rules:
            print("Adding rule:", rule)
            self._add_rule(rule, connection)
    
    def _add_rule(self, rule, connection):
        rule_msg = of.ofp_flow_mod()
        
        # Configurar prioridad (reglas específicas tienen mayor prioridad)
        rule_msg.priority = rule.get('priority', 100)
        
        # Configurar campos de match con los prerequisitos correctos
        if 'dl_type' in rule:
            rule_msg.match.dl_type = rule['dl_type']
        
        # Para campos IP, necesitamos dl_type = 0x0800 (IPv4)
        if any(field in rule for field in ['src_ip', 'dst_ip', 'tr_proto']):
            rule_msg.match.dl_type = 0x0800  # IPv4
            
            if 'src_ip' in rule:
                rule_msg.match.nw_src = IPAddr(rule['src_ip'])
            if 'dst_ip' in rule:
                rule_msg.match.nw_dst = IPAddr(rule['dst_ip'])
            if 'tr_proto' in rule:
                rule_msg.match.nw_proto = rule['tr_proto']
        
        # Para puertos TCP/UDP, necesitamos el protocolo especificado
        if any(field in rule for field in ['src_port', 'dst_port']):
            rule_msg.match.dl_type = 0x0800  # IPv4
            
            # Si no está especificado el protocolo, asumir TCP
            if 'tr_proto' not in rule:
                rule_msg.match.nw_proto = 6  # TCP
            else:
                rule_msg.match.nw_proto = rule['tr_proto']
            
            if 'src_port' in rule:
                rule_msg.match.tp_src = rule['src_port']
            if 'dst_port' in rule:
                rule_msg.match.tp_dst = rule['dst_port']
        
        # Configurar acción según el tipo de regla
        action = rule.get('action', 'drop').lower()
        if action == 'allow':
            # Reenviar al controlador para que l2_learning maneje el forwarding
            rule_msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
        elif action == 'drop':
            # No action = drop (por defecto)
            pass
        
        connection.send(rule_msg)
        return rule_msg
    
    def _set_rules(self, f_name):
        try:
            with open(f_name, "r") as file:
                self.rules = json.load(file)
                log.info(f"Loaded {len(self.rules)} firewall rules")
        except FileNotFoundError:
            log.error(f"Rules file {f_name} not found")
            self.rules = []
        except json.JSONDecodeError:
            log.error(f"Invalid JSON in rules file {f_name}")
            self.rules = []

def launch():
    # Starting the Firewall module
    core.registerNew(Firewall)