# Coursera :
# - Software Defined Networking ( SDN ) course
# -- Programming Assignment : Layer -2 Firewall Application Professor : Nick Feamster
# Teaching Assistant : Arpit Gupta
from pox.core import core
import pox. openflow .libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
import json
log = core . getLogger ()

NORMALIZE_MAP = {
    'tcp': 6,
    'udp': 17,
    'ipv4': 0x0800,
    'ipv6': 0x86DD
}


class Firewall (EventMixin) :
    def __init__(self):
        self.listenTo( core . openflow )
        self._set_rules('rules.json')

    def _handle_ConnectionUp (self, event) :
        self._load_rules(event.connection)

    def _load_rules(self, connection):
        for rule in self.rules:
            normalized_rule = self._normalize_rule(rule)
            self._add_rule(normalized_rule, connection)


    def _normalize_rule(self, rule):

        if 'tr_proto' in rule and isinstance(rule['tr_proto'], str):
            rule['tr_proto'] = NORMALIZE_MAP.get(rule['tr_proto'].lower(), rule['tr_proto'])

        if 'nw_proto' in rule and isinstance(rule['nw_proto'], str):
            rule['nw_proto'] = NORMALIZE_MAP.get(rule['nw_proto'].lower(), rule['nw_proto'])

        return rule



    def _add_rule(self, rule, connection):
        rule_msg = of.ofp_flow_mod()

        if ('src_port' in rule or 'dst_port' in rule) and 'tr_proto' not in rule and 'nw_proto' not in rule:
            for proto_name in ['tcp', 'udp']:
                rule_copy = dict(rule)
                rule_copy['tr_proto'] = NORMALIZE_MAP[proto_name]
                comment_original = rule_copy.get('comment', '')
                suffix = f" version {proto_name.upper()}"
                rule_copy['comment'] = comment_original + suffix
                self._add_rule(rule_copy, connection)
            return rule_msg


        if 'nw_proto' in rule:
            rule_msg.match.dl_type = rule['nw_proto']
        elif any(k in rule for k in ['src_ip', 'dst_ip', 'src_port', 'dst_port', 'tr_proto']):
            rule_msg.match.dl_type = NORMALIZE_MAP.get('ipv4')

        if rule_msg.match.dl_type != NORMALIZE_MAP.get('ipv6'):
            self._set_match_field(rule, rule_msg.match, 'tr_proto', 'nw_proto')
            self._set_match_field(rule, rule_msg.match, 'src_ip', 'nw_src')
            self._set_match_field(rule, rule_msg.match, 'dst_ip', 'nw_dst')
            self._set_match_field(rule, rule_msg.match, 'src_port', 'tp_src')
            self._set_match_field(rule, rule_msg.match, 'dst_port', 'tp_dst')

        self._set_match_field(rule, rule_msg.match, 'src_mac', 'dl_src')
        self._set_match_field(rule, rule_msg.match, 'dst_mac', 'dl_dst')


        rule_msg.priority = rule.get('priority', 1)

        action = rule.get('action', 'drop').lower()

        comment = rule.get('comment', 'Sin comentario')
        log.info(f"Cargando regla: {comment}")

        if action == 'allow':
            rule_msg.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
        else:
            #rule_msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
            pass

        connection.send(rule_msg)
        return rule_msg


    def _handle_PacketIn(self, event):
        pkt = event.parsed
        ip_pkt = pkt.find('ipv4')
        tcp_pkt = pkt.find('tcp')
        udp_pkt = pkt.find('udp')

        src_ip = str(ip_pkt.srcip) if ip_pkt else None
        dst_ip = str(ip_pkt.dstip) if ip_pkt else None
        proto = ip_pkt.protocol if ip_pkt else None
        src_port = tcp_pkt.srcport if tcp_pkt else (udp_pkt.srcport if udp_pkt else None)
        dst_port = tcp_pkt.dstport if tcp_pkt else (udp_pkt.dstport if udp_pkt else None)

        for rule in self.rules:
            if rule.get('action') == 'allow':
                continue

            if rule.get('src_ip') and rule['src_ip'] != src_ip:
                continue
            if rule.get('dst_ip') and rule['dst_ip'] != dst_ip:
                continue
            if rule.get('tr_proto') and rule['tr_proto'] != proto:
                continue
            if rule.get('src_port') and rule['src_port'] != src_port:
                continue
            if rule.get('dst_port') and rule['dst_port'] != dst_port:
                continue

            comment = rule.get('comment', 'Sin comentario')
            log.info(f"[DROP] Por la regla: {comment} Se bloqueo un paquete: desde {src_ip}:{src_port} hacia {dst_ip}:{dst_port}")
            return

        return


    def _set_match_field(self, rule, rule_msg, key, field):
        value = rule.get(key)
        if value is not None:
            if key in ['src_mac', 'dst_mac']:
                value = EthAddr(value)
            setattr(rule_msg, field, value)

    def _set_rules(self, f_name):
        with open(f_name, "r") as file:
            self.rules = json.load(file)

def launch () :
    # Starting the Firewall module
    core.registerNew(Firewall)