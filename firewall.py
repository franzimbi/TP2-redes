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

class Firewall (EventMixin) :
    def init (self) :
        self.listenTo( core . openflow )
        log.debug( " Enabling ␣ Firewall ␣ Module " )
        self._set_rules('../rules.json')

    def _handle_ConnectionUp (self, event) :
        self._load_rules(event.connection)

    def _load_rules(self, connection):
        for rule in self.rules:
            self._add_rule(rule, connection)


    def _add_rule(self, rule, connection):
        rule_msg = of.ofp_flow_mod()
        self._set_match_field(rule, rule_msg.match, 'dl_type', 'dl_type')
        self._set_match_field(rule, rule_msg.match, 'tr_proto', 'nw_proto')
        self._set_match_field(rule, rule_msg.match, 'src_ip', 'nw_src')
        self._set_match_field(rule, rule_msg.match, 'dst_ip', 'nw_dst')
        self._set_match_field(rule, rule_msg.match, 'src_port', 'tp_src')
        self._set_match_field(rule, rule_msg.match, 'dst_port', 'tp_dst')
        connection.send(rule_msg)
        return rule_msg

    def _set_match_field(self, rule, rule_msg, key, field):
        value = rule.get(key)
        if value is not None:
            setattr(rule_msg, field, value)

    def _set_rules(self, f_name):
        with open(f_name, "r") as file:
            self.rules = json.load(file)

def launch () :
    # Starting the Firewall module
    core.registerNew(Firewall)