import re
import datetime
import pytz

# from product import TextProduct, TextProductException
# from ugc import ugcs_to_text

_re = "(/([A-Z])\.([A-Z]+)\.([A-Z]+)\.([A-Z]+)\.([A-Z])\.([0-9]+)\.([0-9,T,Z]+)-([0-9,T,Z]+)/)"

_classDict = {'O': 'Operational',
              'T': 'Test',
              'E': 'Experimental',
              'X': 'Experimental VTEC'}

_actionDict = {'NEW': 'issues',
               'CON': 'continues',
               'EXA': 'extends area of',
               'EXT': 'extends time of',
               'EXB': 'extends area+time of',
               'UPG': 'issues upgrade to',
               'CAN': 'cancels',
               'EXP': 'expires',
               'ROU': 'routine',
               'COR': 'corrects'}

_sigDict = {'W': 'Warning',
            'Y': 'Advisory',
            'A': 'Watch',
            'S': 'Statement',
            'O': 'Outlook',
            'N': 'Synopsis',
            'F': 'Forecast'}

_phenDict = {
    'AF': 'Ashfall',
    'AS': 'Air Stagnation',
    'BH': 'Beach Hazard',
    'BS': 'Blowing Snow',
    'BW': 'Brisk Wind',
    'BZ': 'Blizzard',
    'CF': 'Coastal Flood',
    'DS': 'Dust Storm',
    'DU': 'Blowing Dust',
    'EC': 'Extreme Cold',
    'EH': 'Excessive Heat',
    'EW': 'Extreme Wind',
    'FA': 'Areal Flood',
    'FF': 'Flash Flood',
    'FG': 'Dense Fog',
    'FL': 'Flood',
    'FR': 'Frost',
    'FW': 'Red Flag',
    'FZ': 'Freeze',
    'GL': 'Gale',
    'HF': 'Hurricane Force Wind',
    'HI': 'Inland Hurricane',
    'HS': 'Heavy Snow',
    'HT': 'Heat',
    'HU': 'Hurricane',
    'HW': 'High Wind',
    'HY': 'Hydrologic',
    'HZ': 'Hard Freeze',
    'IP': 'Sleet',
    'IS': 'Ice Storm',
    'LB': 'Lake Effect Snow and Blowing Snow',
    'LE': 'Lake Effect Snow',
    'LO': 'Low Water',
    'LS': 'Lakeshore Flood',
    'LW': 'Lake Wind',
    'MA': 'Marine',
    'MF': 'Marine Dense Fog',
    'MS': 'Marine Dense Smoke',
    'MH': 'Marine Ashfall',
    'RB': 'Small Craft for Rough',
    'RP': 'Rip Currents',
    'SB': 'Snow and Blowing',
    'SC': 'Small Craft',
    'SE': 'Hazardous Seas',
    'SI': 'Small Craft for Winds',
    'SM': 'Dense Smoke',
    'SN': 'Snow',
    'SR': 'Storm',
    'SU': 'High Surf',
    'SV': 'Severe Thunderstorm',
    'SW': 'Small Craft for Hazardous',
    'TI': 'Inland Tropical Storm',
    'TO': 'Tornado',
    'TR': 'Tropical Storm',
    'TS': 'Tsunami',
    'TY': 'Typhoon',
    'UP': 'Ice Accretion',
    'WC': 'Wind Chill',
    'WI': 'Wind',
    'WS': 'Winter Storm',
    'WW': 'Winter Weather',
    'ZF': 'Freezing Fog',
    'ZR': 'Freezing Rain',
}

# Taken from http://www.weather.gov/help-map
NWS_COLORS = {
    'AS.Y': '#808080',
    'AF.Y': '#696969',
    'AF.W': '#A9A9A9',
    'BH.S': '#40E0D0',
    'BZ.W': '#FF4500',
    'BZ.A': '#ADFF2F',
    'DU.Y': '#BDB76B',
    'BW.Y': '#D8BFD8',
    'CF.Y': '#7CFC00',
    'CF.S': '#6B8E23',
    'CF.W': '#228B22',
    'CF.A': '#66CDAA',
    'FG.Y': '#708090',
    'SM.Y': '#F0E68C',
    'DU.W': '#FFE4C4',
    'EH.W': '#C71585',
    'EH.Y': '#800000',
    'EC.W': '#0000FF',
    'EC.A': '#0000FF',
    'EW.W': '#FF8C00',
    'FW.A': '#FFDEAD',
    'FF.S': '#8B0000',
    'FF.W': '#8B0000',
    'FF.A': '#2E8B57',
    'FL.Y': '#00FF7F',
    'FL.S': '#00FF00',
    'FL.W': '#00FF00',
    'FL.A': '#2E8B57',
    'FZ.W': '#483D8B',
    'FZ.A': '#00FFFF',
    'ZF.Y': '#008080',
    'ZR.Y': '#DA70D6',
    'FR.Y': '#6495ED',
    'GL.W': '#DDA0DD',
    'GL.A': '#FFC0CB',
    'HZ.W': '#9400D3',
    'HZ.A': '#4169E1',
    'SE.W': '#D8BFD8',
    'SE.A': '#483D8B',
    'HT.Y': '#FF7F50',
    'SU.Y': '#BA55D3',
    'SU.W': '#228B22',
    'HW.W': '#DAA520',
    'HW.A': '#B8860B',
    'HF.W': '#CD5C5C',
    'HF.A': '#9932CC',
    'HU.W': '#DC143C',
    'HU.A': '#FF00FF',
    'HY.Y': '#00FF7F',
    'IS.W': '#8B008B',
    'LE.Y': '#48D1CC',
    'LE.W': '#008B8B',
    'LE.A': '#87CEFA',
    'LW.Y': '#D2B48C',
    'LS.Y': '#7CFC00',
    'LS.S': '#6B8E23',
    'LS.W': '#228B22',
    'LS.A': '#66CDAA',
    'LO.Y': '#A52A2A',
    'MA.S': '#FFDAB9',
    'FW.W': '#FF1493',
    'RP.S': '#40E0D0',
    'SV.W': '#FFA500',
    'SV.A': '#DB7093',
    'SC.Y': '#D8BFD8',
    'SW.Y': '#D8BFD8',
    'RB.Y': '#D8BFD8',
    'SI.Y': '#D8BFD8',
    'MA.W': '#FFA500',
    'TO.W': '#FF0000',
    'TO.A': '#FFFF00',
    'TR.S': '#FFE4B5',
    'TR.W': '#B22222',
    'TR.A': '#F08080',
    'TS.Y': '#D2691E',
    'TS.W': '#FD6347',
    'TS.A': '#FF00FF',
    'TY.W': '#DC143C',
    'TY.A': '#FF00FF',
    'WI.Y': '#D2B48C',
    'WC.Y': '#AFEEEE',
    'WC.W': '#B0C4DE',
    'WC.A': '#5F9EA0',
    'WS.W': '#FF69B4',
    'WS.A': '#4682B4',
    'WW.Y': '#7B68EE',
}


def parse(text):
    """ I look for and return vtec objects as I find them """
    vtec = []
    tokens = re.findall(_re, text)
    for t in tokens:
        vtec.append(VTEC(t))
    return vtec


def contime(s):
    if (len(re.findall("0000*T", s)) > 0):
        return None
    try:
        ts = datetime.datetime.strptime(s, '%y%m%dT%H%MZ')
        return ts.replace(tzinfo=pytz.timezone('UTC'))
    except Exception, err:
        print err
        return None


def do_sql_hvtec(txn, segment):
    ''' Process the HVTEC in this product '''
    nwsli = segment.hvtec[0].nwsli.id
    if len(segment.bullets) < 4:
        return
    stage_text = ""
    flood_text = ""
    forecast_text = ""
    for qqq in range(len(segment.bullets)):
        if segment.bullets[qqq].strip().find("FLOOD STAGE") == 0:
            flood_text = segment.bullets[qqq]
        if segment.bullets[qqq].strip().find("FORECAST") == 0:
            forecast_text = segment.bullets[qqq]
        if (segment.bullets[qqq].strip().find("AT ") == 0 and
                    stage_text == ""):
            stage_text = segment.bullets[qqq]

    txn.execute("""INSERT into riverpro(nwsli, stage_text,
      flood_text, forecast_text, severity) VALUES
      (%s,%s,%s,%s,%s) """, (nwsli, stage_text, flood_text,
                             forecast_text,
                             segment.hvtec[0].severity))


class VTEC:
    def __init__(self, tokens):
        self.line = tokens[0]
        self.status = tokens[1]
        self.action = tokens[2]
        self.office = tokens[3][1:]
        self.office4 = tokens[3]
        self.phenomena = tokens[4]
        self.significance = tokens[5]
        self.ETN = int(tokens[6])
        self.begints = contime(tokens[7])
        self.endts = contime(tokens[8])

    def get_end_string(self, prod):
        """ Return an appropriate end string for this VTEC """
        if self.action == 'CAN':
            return ''
        if self.endts is None:
            return 'until further notice'
        fmt = "%b %-d, %-I:%M %p %Z"
        if self.endts < (prod.valid + datetime.timedelta(hours=1)):
            fmt = '%-I:%M %p %Z'
        localts = self.endts.astimezone(prod.tz)
        return "till %s" % (localts.strftime(fmt),)

    def get_begin_string(self, prod):
        ''' Return an appropriate beginning string for this VTEC '''
        if self.begints is None:
            return ''
        fmt = "%b %-d, %-I:%M %p %Z"
        if self.begints < (prod.valid + datetime.timedelta(hours=1)):
            fmt = '%-I:%M %p %Z'
        localts = self.begints.astimezone(prod.tz)
        return "valid at %s" % (localts.strftime(fmt),)

    def url(self, year):
        """ Generate a VTEC url string needed """
        return "%s-%s-%s-%s-%s-%s-%04i" % (year, self.status, self.action,
                                           self.office4, self.phenomena, self.significance, self.ETN)

    def getID(self, year):
        ''' Return a custom string identifier for this VTEC product 
        This is used by the Live client '''
        return '%s-%s-%s-%s-%04i' % (year, self.office4,
                                     self.phenomena, self.significance,
                                     self.ETN)

    def __str__(self):
        return self.line

    def get_ps_string(self):
        ''' Return the combination of Phenomena + Significance as string '''
        p = _phenDict.get(self.phenomena, "Unknown %s" % (self.phenomena,))
        a = _sigDict.get(self.significance, "Unknown %s" % (self.significance,))
        # Hack for special FW case
        if self.significance == 'A' and self.phenomena == 'FW':
            p = "Fire Weather"
        return "%s %s" % (p, a)

    def get_action_string(self):
        return _actionDict.get(self.action, "unknown %s" % (self.action,))

    def product_string(self):
        return "%s %s" % (self.get_action_string(), self.get_ps_string())


# class VTECProductException(TextProductException):
#     ''' Something we can raise when bad things happen! '''
#     pass
#
#
# class VTECProduct(TextProduct):
#     ''' Represents a text product of the LSR variety '''
#
#     def __init__(self, text, utcnow=None, ugc_provider=None,
#                  nwsli_provider=None):
#         ''' constructor '''
#         # Make sure we are CRLF above all else
#         if text.find("\r\r\n") == -1:
#             text = text.replace("\n", "\r\r\n")
#         # Get rid of extraneous whitespace on right hand side only
#         text = "\r\r\n".join([a.rstrip() for a in text.split("\r\r\n")])
#
#         TextProduct.__init__(self, text, utcnow, ugc_provider, nwsli_provider)
#         self.nwsli_provider = nwsli_provider
#         self.skip_con = self.get_skip_con()
#
#     def debug_warning(self, txn, warning_table, ugcstring, vtec, segment,
#                       ets):
#         """ Get a more useful warning message for this failure """
#         cnt = txn.rowcount
#         txn.execute("""SELECT ugc,
#                     issue at time zone 'UTC' as utc_issue,
#                     expire at time zone 'UTC' as utc_expire,
#                     updated at time zone 'UTC' as utc_updated,
#                     status from """ + warning_table + """
#                     WHERE wfo = %s and eventid = %s
#                     and ugc in """ + ugcstring + """ and significance = %s
#                     and phenomena = %s ORDER by ugc ASC, issue ASC""",
#                     (vtec.office, vtec.ETN, vtec.significance,
#                      vtec.phenomena))
#         debugmsg = "UGC    STA ISSUE            EXPIRE           UPDATED\n"
#
#         def myfmt(val):
#             """ Be more careful """
#             if val is None:
#                 return '%-16s' % ('((NULL))',)
#             return val.strftime("%Y-%m-%d %H:%M")
#
#         for row in txn:
#             debugmsg += "%s %s %s %s %s\n" % (row['ugc'], row['status'],
#                                               myfmt(row['utc_issue']),
#                                               myfmt(row['utc_expire']),
#                                               myfmt(row['utc_updated']))
#         return ('Warning: %s.%s.%s do_sql_vtec %s '
#                 + 'updated %s row, should %s rows\nUGCS: %s\n'
#                 + 'valid: %s expire: %s\n%s') % (
#                    vtec.phenomena, vtec.significance, vtec.ETN, vtec.action,
#                    cnt, len(segment.ugcs), segment.ugcs, self.valid,
#                    ets, debugmsg)
#
#     def sql(self, txn):
#         """Persist to the database
#
#         Args:
#           txn (psycopg2.transaction): A database transaction object that we can
#             exec() database calls against.
#
#         """
#         for segment in self.segments:
#             if len(segment.ugcs) == 0:
#                 continue
#             if len(segment.vtec) == 0:
#                 continue
#             for vtec in segment.vtec:
#                 if vtec.status == 'T' or vtec.action == 'ROU':
#                     continue
#                 if segment.sbw:
#                     self.do_sbw_geometry(txn, segment, vtec)
#                 # Check for Hydro-VTEC stuff
#                 if (len(segment.hvtec) > 0 and
#                             segment.hvtec[0].nwsli != "00000"):
#                     do_sql_hvtec(txn, segment)
#
#                 self.do_sql_vtec(txn, segment, vtec)
#
#     def which_warning_table(self, txn, vtec):
#         """ Figure out which table we should work against """
#         if vtec.action in ["NEW", ]:
#             return "warnings_%s" % (self.valid.year,)
#         # Look this year
#         txn.execute("""SELECT
#         min(product_issue at time zone 'UTC') from warnings
#         WHERE wfo = %s and eventid = %s and significance = %s and
#         phenomena = %s and (expire + '1 hour'::interval) > %s""", (
#             vtec.office, vtec.ETN, vtec.significance, vtec.phenomena,
#             self.valid))
#         row = txn.fetchone()
#         if row['min'] is None:
#             self.warnings.append(("Failed to find active year:\n"
#                                   + "  VTEC:%s\n  PRODUCT: %s") % (
#                                      str(vtec), self.get_product_id()))
#             return "warnings_%s" % (self.valid.year,)
#         year = row['min'].year
#         if abs(year - self.valid.year) > 1:
#             self.warnings.append("Thought this warning was %s" % (year,))
#             return "warnings_%s" % (self.valid.year,)
#         return "warnings_%s" % (year,)
#
#     def do_sql_vtec(self, txn, segment, vtec):
#         """ Persist the non-SBW stuff to the database
#
#         Arguments:
#         txn -- A pyscopg2 transaction
#         segment -- A TextProductSegment instance
#         vtec -- A vtec instance
#         """
#         warning_table = self.which_warning_table(txn, vtec)
#         ugcstring = str(tuple([str(u) for u in segment.ugcs]))
#         if len(segment.ugcs) == 1:
#             ugcstring = "('%s')" % (segment.ugcs[0],)
#         fcster = self.get_signature()
#         if fcster is not None:
#             fcster = fcster[:24]
#
#         # If this product is ...RESENT, lets check to make sure we did not
#         # already get it
#         if self.is_resent():
#             txn.execute("""SELECT max(updated) as maxtime
#             from """ + warning_table + """
#             WHERE eventid = %s and significance = %s and wfo = %s and
#             phenomena = %s
#             """, (vtec.ETN, vtec.significance, vtec.office, vtec.phenomena))
#             maxtime = txn.fetchone()['maxtime']
#             if maxtime is not None:
#                 if maxtime == self.valid:
#                     print("RESENT Match, skipping SQL for %s!" % (
#                         self.get_product_id(),))
#                     return
#
#         if vtec.action in ['NEW', 'EXB', 'EXA']:
#             # New Event Types!
#             bts = vtec.begints
#             if bts is None or vtec.action in ["EXB", ]:
#                 bts = self.valid
#             # If this product has no expiration time, just set it ahead
#             # 24 hours in time...
#             ets = vtec.endts
#             if vtec.endts is None:
#                 ets = bts + datetime.timedelta(hours=72)
#
#             # For each UGC code in this segment, we create a database entry
#             for ugc in segment.ugcs:
#                 # Check to see if we have entries already for this UGC
#                 # Some previous entries may not be in a terminated state, so
#                 # also check the expiration time
#                 txn.execute("""
#                 SELECT issue, expire, updated from """ + warning_table + """
#                 WHERE ugc = %s and eventid = %s and significance = %s and
#                 wfo = %s and phenomena = %s
#                 and status not in ('CAN', 'UPG') and expire > %s
#                 """, (str(ugc), vtec.ETN, vtec.significance, vtec.office,
#                       vtec.phenomena, self.valid))
#                 if txn.rowcount > 0:
#                     if self.is_correction():
#                         # We'll delete old entries, gulp
#                         txn.execute("""
#                         DELETE from """ + warning_table + """ WHERE ugc = %s
#                         and eventid = %s and significance = %s and
#                         wfo = %s and phenomena = %s and
#                         status in ('NEW', 'EXB', 'EXA')
#                         """, (str(ugc), vtec.ETN, vtec.significance,
#                               vtec.office, vtec.phenomena))
#                         if txn.rowcount != 1:
#                             self.warnings.append(("%s.%s.%s %s duplicated via "
#                                                   + "product correction, deleted %s old rows instead "
#                                                   + "of 1") % (
#                                                      vtec.phenomena, vtec.significance,
#                                                      vtec.ETN, str(ugc), txn.rowcount))
#
#                     else:
#                         self.warnings.append(("Duplicate(s) WWA found, "
#                                               + "rowcount: %s for UGC: %s") % (txn.rowcount, ugc))
#
#                 txn.execute("""
#                 INSERT into """ + warning_table + """ (issue, expire, updated,
#                 wfo, eventid, status, fcster, report, ugc, phenomena,
#                 significance, gid, init_expire, product_issue, hvtec_nwsli)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#                 get_gid(%s, %s), %s, %s, %s)
#                 RETURNING issue
#                 """, (bts, ets, self.valid, vtec.office,
#                       vtec.ETN, vtec.action, fcster, self.unixtext, str(ugc),
#                       vtec.phenomena, vtec.significance, str(ugc),
#                       self.valid, vtec.endts, self.valid,
#                       segment.get_hvtec_nwsli()))
#                 if txn.rowcount != 1:
#                     self.warnings.append(('Failed to add entry for UGC: %s, '
#                                           + 'rowcount was: %s') % (str(ugc),
#                                                                    txn.rowcount))
#
#         elif vtec.action in ['COR', ]:
#             # A previous issued product is being corrected
#             txn.execute("""
#             UPDATE """ + warning_table + """
#             SET expire = coalesce(%s, expire), status = %s,
#             svs = (CASE WHEN (svs IS NULL) THEN '__' ELSE svs END)
#                    || %s || '__',
#             issue = coalesce(%s, issue),
#             init_expire = coalesce(%s, init_expire) WHERE
#             wfo = %s and eventid = %s and ugc in """ + ugcstring + """
#             and significance = %s and phenomena = %s and
#             (expire + '1 hour'::interval) >= %s
#             """, (vtec.endts, vtec.action, self.unixtext, vtec.begints,
#                   vtec.endts, vtec.office, vtec.ETN,
#                   vtec.significance, vtec.phenomena, self.valid))
#             if txn.rowcount != len(segment.ugcs):
#                 self.warnings.append(
#                     self.debug_warning(txn, warning_table, ugcstring,
#                                        vtec, segment, vtec.endts)
#                 )
#
#         elif vtec.action in ['CAN', 'UPG', 'EXT']:
#             ets = vtec.endts
#             # These are terminate actions, so we act accordingly
#             if vtec.action in ['CAN', 'UPG']:
#                 ets = self.valid
#             # If we are extending into infinity, lets call this +72 HRS
#             if vtec.action == 'EXT' and vtec.endts is None:
#                 ets = self.valid + datetime.timedelta(hours=72)
#
#             txn.execute("""
#                 UPDATE """ + warning_table + """ SET
#                 expire = %s,
#                 status = %s,
#                 updated = %s,
#                 svs = (CASE WHEN (svs IS NULL) THEN '__' ELSE svs END)
#                    || %s || '__'
#                 WHERE wfo = %s and eventid = %s and ugc in """ + ugcstring + """
#                 and significance = %s and phenomena = %s
#                 and status not in ('CAN', 'UPG') and
#                 (expire + '1 hour'::interval) >= %s
#                 """, (ets, vtec.action, self.valid, self.unixtext,
#                       vtec.office, vtec.ETN,
#                       vtec.significance, vtec.phenomena, self.valid))
#             if txn.rowcount != len(segment.ugcs):
#                 if not self.is_correction():
#                     self.warnings.append(
#                         self.debug_warning(txn, warning_table, ugcstring,
#                                            vtec, segment, ets)
#                     )
#
#
#         elif vtec.action in ['CON', 'EXP', 'ROU']:
#             # These are no-ops, just updates
#             ets = vtec.endts
#             if vtec.endts is None:
#                 ets = self.valid + datetime.timedelta(hours=72)
#
#             # Offices have 1 hour to expire something :), actually 30 minutes
#             txn.execute("""
#                 UPDATE """ + warning_table + """ SET status = %s,
#                 svs = (CASE WHEN (svs IS NULL) THEN '__' ELSE svs END)
#                    || %s || '__' , expire = %s WHERE
#                 wfo = %s and eventid = %s and ugc in """ + ugcstring + """
#                 and significance = %s and phenomena = %s
#                 and status not in ('CAN', 'UPG') and
#                 (expire + '1 hour'::interval) >= %s
#                 """, (vtec.action, self.unixtext, ets, vtec.office, vtec.ETN,
#                       vtec.significance, vtec.phenomena, self.valid))
#             if txn.rowcount != len(segment.ugcs):
#                 self.warnings.append(
#                     self.debug_warning(txn, warning_table, ugcstring,
#                                        vtec, segment, ets)
#                 )
#
#         else:
#             self.warnings.append(('Warning: do_sql_vtec() encountered %s '
#                                   + 'VTEC status') % (
#                                      vtec.action,))
#
#     def do_sbw_geometry(self, txn, segment, vtec):
#         ''' Storm Based Warnings are stored in seperate tables as we need
#         to track geometry changes, etc '''
#
#         # Technically, this is a bug as the it would be based on VTEC issuance
#         sbw_table = self.which_warning_table(txn, vtec).replace("warnings",
#                                                                 "sbw")
#
#         # The following time columns are set in the database
#         # issue         - VTEC encoded issuance time, can be null
#         # init_expire   - VTEC encoded expiration
#         # expire        - VTEC encoded expiration
#         # polygon_begin - Time domain this polygon is valid for inclusive
#         # polygon_end   - Time domain this polygon is valid for exclusive
#         # updated       - Product time of this product
#
#         # Figure out when this polygon begins and ends
#         polygon_begin = self.valid
#         if vtec.action == 'NEW' and vtec.begints is not None:
#             polygon_begin = vtec.begints
#         polygon_end = self.valid
#         if vtec.action not in ['CAN', 'UPG']:
#             if vtec.endts is not None:
#                 polygon_end = vtec.endts
#             else:
#                 polygon_end = self.valid + datetime.timedelta(hours=24)
#
#         if self.is_correction() and vtec.action == 'NEW':
#             # Go delete the previous NEW polygon
#             txn.execute("""
#             DELETE from """ + sbw_table + """ WHERE status = 'NEW' and
#             eventid = %s and wfo = %s and phenomena = %s and significance = %s
#             """, (vtec.ETN, vtec.office, vtec.phenomena, vtec.significance))
#             if txn.rowcount != 1:
#                 self.warnings.append(("%s.%s.%s product is a correction"
#                                       + ", but SBW delete removed %s rows instead of 1" % (
#                                           vtec.phenomena, vtec.significance, vtec.ETN, txn.rowcount)))
#
#         # Lets go find the initial warning (status == NEW)
#         txn.execute("""
#         SELECT issue, expire from """ + sbw_table + """ WHERE status = 'NEW' and
#         eventid = %s and wfo = %s and phenomena = %s and significance = %s
#         """, (vtec.ETN, vtec.office, vtec.phenomena, vtec.significance))
#         if txn.rowcount > 0:
#             if vtec.action == 'NEW':  # Uh-oh, we have a duplicate
#                 self.warnings.append(("%s.%s.%s is a SBW duplicate! %s other "
#                                       + "row(s) found.") % (vtec.phenomena, vtec.significance, vtec.ETN,
#                                                             txn.rowcount))
#
#         # Lets go find our current active polygon
#         txn.execute("""
#         SELECT polygon_end from """ + sbw_table + """ WHERE
#         eventid = %s and wfo = %s and phenomena = %s and significance = %s
#         and polygon_begin != polygon_end ORDER by updated DESC LIMIT 1
#         """, (vtec.ETN, vtec.office, vtec.phenomena, vtec.significance))
#         current = None
#         if txn.rowcount == 0 and vtec.action != 'NEW':
#             self.warnings.append(("%s.%s.%s Failed to find currently "
#                                   + "active SBW") % (vtec.phenomena,
#                                                      vtec.significance, vtec.ETN))
#         if txn.rowcount > 0:
#             current = txn.fetchone()
#
#         # If ncessary, lets find the current active polygon and truncate it
#         # to when our new polygon starts
#         if vtec.action != 'NEW' and current is not None:
#             txn.execute("""
#             UPDATE """ + sbw_table + """ SET polygon_end = %s WHERE
#             eventid = %s and wfo = %s and phenomena = %s and significance = %s
#             and polygon_end != polygon_begin
#             and polygon_end = %s and status != 'CAN'
#             """, (polygon_begin,
#                   vtec.ETN, vtec.office, vtec.phenomena, vtec.significance,
#                   current['polygon_end']))
#             if txn.rowcount != 1:
#                 self.warnings.append(("%s.%s.%s SBW prev polygon update "
#                                       + "resulted in update of %s rows, should be 1") % (
#                                          vtec.phenomena, vtec.significance, vtec.ETN,
#                                          txn.rowcount))
#
#         # Prepare the TIME...MOT...LOC information
#         tml_valid = None
#         tml_column = 'tml_geom'
#         if segment.tml_giswkt and segment.tml_giswkt.find("LINE") > 0:
#             tml_column = 'tml_geom_line'
#         if segment.tml_valid:
#             tml_valid = segment.tml_valid
#
#
#         # OK, ready to insert away!
#         sql = """INSERT into """ + sbw_table + """(wfo, eventid,
#             significance, phenomena, issue, expire, init_expire,
#             polygon_begin, polygon_end, geom, status, report, windtag,
#             hailtag, tornadotag, tornadodamagetag, tml_valid,
#             tml_direction, tml_sknt, """ + tml_column + """, updated)
#             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
#             %s,%s,%s,%s,%s,%s,%s,%s,%s)"""
#         myargs = (
#             vtec.office,
#             vtec.ETN,
#             vtec.significance,
#             vtec.phenomena,
#             vtec.begints,
#             vtec.endts,
#             vtec.endts,
#             polygon_begin,  # polygon_begin
#             polygon_end,  # polygon_end
#             segment.giswkt, vtec.action, self.unixtext, segment.windtag,
#             segment.hailtag, segment.tornadotag, segment.tornadodamagetag,
#             tml_valid, segment.tml_dir, segment.tml_sknt, segment.tml_giswkt,
#             self.valid)
#         txn.execute(sql, myargs)
#         if txn.rowcount != 1:
#             self.warnings.append(("%s.%s.%s sbw table insert "
#                                   + "resulted in %s rows, should be 1") % (
#                                      vtec.phenomena, vtec.significance, vtec.ETN,
#                                      txn.rowcount))
#
#     def get_action(self):
#         """ How to describe the action of this product """
#         keys = []
#         for segment in self.segments:
#             for vtec in segment.vtec:
#                 if vtec.action not in keys:
#                     keys.append(vtec.action)
#         if len(keys) == 1:
#             return self.segments[0].vtec[0].get_action_string()
#         return "updates"
#
#     def is_homogeneous(self):
#         ''' Test to see if this product contains just one VTEC event '''
#         keys = []
#         for segment in self.segments:
#             for vtec in segment.vtec:
#                 key = "%s.%s.%s" % (vtec.phenomena, vtec.ETN,
#                                     vtec.significance)
#                 if key not in keys:
#                     keys.append(key)
#
#         return len(keys) == 1
#
#     def get_first_non_cancel_vtec(self):
#         """ Return the first non-CANcel VTEC """
#         for segment in self.segments:
#             for vtec in segment.vtec:
#                 if vtec.action != 'CAN':
#                     return vtec
#         return None
#
#     def get_first_non_cancel_segment(self):
#         """ Return the first segment that is a non-CAN """
#         for segment in self.segments:
#             if len(segment.vtec) > 0 and segment.vtec[0].action != 'CAN':
#                 return segment
#         return None
#
#     def get_jabbers(self, uri, river_uri=None):
#         """Return a list of triples representing how this goes to social
#         Arguments:
#         uri -- The URL for the VTEC Browser
#         river_uri -- The URL of the River App
#
#         Returns:
#         [[plain, html, xtra]] -- A list of triples of plain text, html, xtra
#         """
#         wfo = self.source[1:]
#         if self.skip_con:
#             xtra = {'product_id': self.get_product_id(),
#                     'channels': ",".join(self.get_affected_wfos()) + ",FLS" + wfo,
#                     'twitter': '%s issues updated FLS product %s?wfo=%s' % (
#                         wfo, river_uri, wfo)}
#             text = ("%s has sent an updated FLS product (continued products "
#                     + "were not reported here).  Consult this website for more "
#                     + "details. %s?wfo=%s") % (wfo, river_uri, wfo)
#             html = ("<p>%s has sent an updated FLS product (continued products "
#                     + "were not reported here).  Consult "
#                     + "<a href=\"%s?wfo=%s\">this website</a> for more "
#                     + "details.</p>") % (wfo, river_uri, wfo)
#             return [(text, html, xtra)]
#         msgs = []
#
#         actions = []
#         long_actions = []
#         html_long_actions = []
#
#         for segment in self.segments:
#             for vtec in segment.vtec:
#                 if vtec.action == 'ROU':
#                     continue
#                 # CRITICAL: redefine this for each loop as it gets passed by
#                 # reference below and is subsequently overwritten otherwise!
#                 if self.afos[:3] in ['MWW', 'RFW']:
#                     channels = ["%s%s" % (self.afos[:3], s) for s in
#                                 self.get_affected_wfos()]
#                 else:
#                     channels = self.get_affected_wfos()
#                 channels.append('%s.%s' % (vtec.phenomena, vtec.significance))
#                 channels.append(self.afos)
#                 channels.append('%s.%s.%s' % (vtec.phenomena,
#                                               vtec.significance, vtec.office))
#                 for ugc in segment.ugcs:
#                     channels.append('%s.%s.%s' % (vtec.phenomena,
#                                                   vtec.significance, str(ugc)))
#                     channels.append(str(ugc))
#                 xtra = {'product_id': self.get_product_id(),
#                         'channels': ",".join(channels),
#                         'status': vtec.status,
#                         'vtec': vtec.getID(self.valid.year),
#                         'ptype': vtec.phenomena,
#                         'twitter': ''}
#
#                 long_actions.append("%s %s" % (vtec.get_action_string(),
#                                                ugcs_to_text(segment.ugcs)))
#                 html_long_actions.append(("<span style='font-weight: bold;'>"
#                                           + "%s</span> %s") % (vtec.get_action_string(),
#                                                                ugcs_to_text(segment.ugcs)))
#                 actions.append("%s %s area%s" % (vtec.get_action_string(),
#                                                  len(segment.ugcs),
#                                                  "s" if len(segment.ugcs) > 1 else ""))
#
#                 if segment.giswkt is not None:
#                     xtra['category'] = 'SBW'
#                     xtra['geometry'] = segment.giswkt.replace("SRID=4326;", "")
#                 if vtec.endts is not None:
#                     xtra['expire'] = vtec.endts.strftime("%Y%m%dT%H:%M:00")
#                 # Set up Jabber Dict for stuff to fill in
#                 jmsg_dict = {'wfo': vtec.office,
#                              'product': vtec.product_string(),
#                              'county': ugcs_to_text(segment.ugcs),
#                              'sts': ' ', 'ets': ' ',
#                              'svr_special': segment.special_tags_to_text(),
#                              'svs_special': '',
#                              'svs_special_html': '',
#                              'year': self.valid.year,
#                              'phenomena': vtec.phenomena,
#                              'eventid': vtec.ETN,
#                              'significance': vtec.significance,
#                              'url': "%s#%s" % (uri,
#                                                vtec.url(self.valid.year))}
#                 if (len(segment.hvtec) > 0 and
#                             segment.hvtec[0].nwsli.id != '00000'):
#                     jmsg_dict['county'] = segment.hvtec[0].nwsli.get_name()
#                 if (vtec.begints is not None and
#                             vtec.begints > (self.utcnow + datetime.timedelta(
#                             hours=1))):
#                     jmsg_dict['sts'] = ' %s ' % (vtec.get_begin_string(self),)
#                 jmsg_dict['ets'] = vtec.get_end_string(self)
#
#                 # Include the special bulletin for Tornado Warnings
#                 if vtec.phenomena == 'TO' and vtec.significance == 'W':
#                     jmsg_dict['svs_special'] = segment.svs_search()
#                     jmsg_dict['svs_special_html'] = segment.svs_search()
#
#                 # Emergencies
#                 if vtec.phenomena in ['TO', 'FF'] and vtec.significance == 'W':
#                     _btext = segment.svs_search()
#                     if (_btext == "" and vtec.phenomena == 'TO' and
#                                 vtec.action not in ['CAN', 'EXP']):
#                         self.warnings.append(("Could not find bullet text in "
#                                               + "segment!"), self.raw)
#                     elif (_btext != "" and vtec.phenomena == 'FF' and
#                                   _btext.find("FLASH FLOOD EMERGENCY") > 0):
#                         jmsg_dict['svs_special'] = _btext
#                         jmsg_dict['svs_special_html'] = _btext.replace("FLASH FLOOD EMERGENCY",
#                                                                        '<span style="color: #FF0000;">FLASH FLOOD EMERGENCY</span>')
#                     elif _btext != "" and vtec.phenomena == 'TO':
#                         jmsg_dict['svs_special_html'] = _btext.replace("TORNADO EMERGENCY",
#                                                                        '<span style="color: #FF0000;">TORNADO EMERGENCY</span>')
#
#                 plain = ("%(wfo)s %(product)s %(svr_special)s%(sts)s for "
#                          + "%(county)s %(ets)s %(svs_special)s "
#                          + "%(url)s") % jmsg_dict
#                 html = ("<p>%(wfo)s <a href=\"%(url)s\">%(product)s</a> "
#                         + "%(svr_special)s%(sts)s for %(county)s "
#                         + "%(ets)s %(svs_special_html)s</p>") % jmsg_dict
#                 xtra['twitter'] = ("%(wfo)s %(product)s%(sts)sfor %(county)s "
#                                    + "%(ets)s %(url)s") % jmsg_dict
#                 # brute force removal of duplicate spaces
#                 xtra['twitter'] = ' '.join(xtra['twitter'].split())
#                 msgs.append([" ".join(plain.split()),
#                              " ".join(html.split()), xtra])
#
#         # If we have a homogeneous product and we have more than one
#         # message, lets try to condense it down, some of the xtra settings
#         # from above will be used here, this is probably bad design
#         if self.is_homogeneous() and len(msgs) > 1:
#             vtec = self.get_first_non_cancel_vtec()
#             if vtec is None:
#                 vtec = self.segments[0].vtec[0]
#             segment = self.get_first_non_cancel_segment()
#             if segment is None:
#                 segment = self.segments[0]
#             if self.afos[:3] in ['MWW', 'RFW']:
#                 channels = ["%s%s" % (self.afos[:3], s) for s in
#                             self.get_affected_wfos()]
#             else:
#                 channels = self.get_affected_wfos()
#             channels.append('%s.%s' % (vtec.phenomena, vtec.significance))
#             channels.append(self.afos)
#             channels.append('%s.%s.%s' % (vtec.phenomena,
#                                           vtec.significance, vtec.office))
#             for seg in self.segments:
#                 for ugc in seg.ugcs:
#                     channels.append('%s.%s.%s' % (vtec.phenomena,
#                                                   vtec.significance, str(ugc)))
#                     channels.append(str(ugc))
#             xtra['channels'] = ",".join(channels)
#             jdict = {
#                 'as': ", ".join(actions),
#                 'asl': ", ".join(long_actions),
#                 'hasl': ", ".join(html_long_actions),
#                 'wfo': vtec.office,
#                 'ets': vtec.get_end_string(self),
#                 'svr_special': segment.special_tags_to_text(),
#                 'svs_special': '',
#                 'sts': '',
#                 'action': self.get_action(),
#                 'product': vtec.get_ps_string(),
#                 'url': "%s#%s" % (uri, vtec.url(self.valid.year)),
#             }
#             # Include the special bulletin for Tornado Warnings
#             if vtec.phenomena in ['TO', ] and vtec.significance == 'W':
#                 jdict['svs_special'] = segment.svs_search()
#             if (vtec.begints is not None and
#                         vtec.begints > (self.utcnow + datetime.timedelta(
#                         hours=1))):
#                 jdict['sts'] = ' %s ' % (vtec.get_begin_string(self),)
#
#             plain = ("%(wfo)s %(action)s %(product)s%(svr_special)s%(sts)s (%(asl)s) "
#                      + "%(ets)s. %(svs_special)s %(url)s") % jdict
#             xtra['twitter'] = ("%(wfo)s %(action)s %(product)s%(svr_special)s%(sts)s (%(asl)s) "
#                                + "%(ets)s") % jdict
#             if len(xtra['twitter']) > (140 - 25):
#                 xtra['twitter'] = ("%(wfo)s %(action)s %(product)s%(sts)s "
#                                    + "(%(as)s) %(ets)s") % jdict
#                 if len(xtra['twitter']) > (140 - 25):
#                     xtra['twitter'] = ("%(wfo)s %(action)s %(product)s%(sts)s %(ets)s") % jdict
#             xtra['twitter'] += " %(url)s" % jdict
#             html = ("<p>%(wfo)s <a href=\"%(url)s\">%(action)s %(product)s</a>%(svr_special)s%(sts)s "
#                     + "(%(hasl)s) %(ets)s. %(svs_special)s</p>") % jdict
#             return [(" ".join(plain.split()),
#                      " ".join(html.split()),
#                      xtra)]
#
#         return msgs
#
#     def get_skip_con(self):
#         ''' Should this product be skipped from generating jabber messages'''
#         if self.afos[:3] == 'FLS' and len(self.segments) > 4:
#             return True
#         return False
#
#
# def parser(text, utcnow=None, ugc_provider=None, nwsli_provider=None):
#     ''' Helper function that actually converts the raw text and emits an
#     VTECProduct instance or returns an exception'''
#     prod = VTECProduct(text, utcnow=utcnow, ugc_provider=ugc_provider,
#                        nwsli_provider=nwsli_provider)
#
#     return prod
