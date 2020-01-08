from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

"""
Build strava-compatible gpx file.

:param time: activity start time 
:type time: str (ISO 8061-extended)

:param name: name of activity
:type name: str

:param timestamps: list of gps timestamps
:type timestamps: [str]

:param lat: list of latitude values
:type lat: [str]

:param lon: list of gps timestamps
:type lon: [str]

:return: xml string
:rtype: str

"""

def gpx_gen(time, name, timestamps, lat, lon):
  # Configure one attribute with set()
  Gpx = Element('gpx',{'creator':'StravaGPX','xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:schemaLocation':'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd','version':'1.1','xmlns':'http://www.topografix.com/GPX/1/1'})

  Metadata = SubElement(Gpx,'metadata')
  Time = SubElement(Metadata,'time')
  Time.text = str(time)
  Trk = SubElement(Gpx,'trk')
  Name = SubElement(Trk,'name')
  Name.text = str(name)
  Type = SubElement(Trk,'type')
  Type.text = '9'
  Trkseg = SubElement(Trk,'trkseg')

  for i in range(len(timestamps)):
    Trkpt = SubElement(Trkseg,'trkpt',{'lat':str(lat[i]),'lon':str(lon[i])})
    time = SubElement(Trkpt,'time')
    time.text = str(timestamps[i])

  ugly_xml = tostring(Gpx, 'utf-8')
  pretty_xml = minidom.parseString(ugly_xml)
  return pretty_xml.toprettyxml(indent="  ")