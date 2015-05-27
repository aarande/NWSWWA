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
# def parser(text, utcnow=None, ugc_provider=None, nwsli_provider=None):
#     ''' Helper function that actually converts the raw text and emits an
#     VTECProduct instance or returns an exception'''
#     prod = VTECProduct(text, utcnow=utcnow, ugc_provider=ugc_provider,
#                        nwsli_provider=nwsli_provider)
#
#     return prod
