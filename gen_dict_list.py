import xml.etree.ElementTree as ET
import sys, os, glob, re

# This script generates into gen/vN:
# - SupportedDictionaries.java: List of dictionaries available in the app.
# - dict_names.xml: Dictionaries names from android-sdk's
#   'core/res/res/values/locale_config.xml'.

def parse_locales():
    r = re.compile("^ *<item>(([^-]+)[^<]+)</item> *<!--( *([^(]+)[^-]+)-->$")
    with open("locale_config.xml", "r") as inp:
        for line in inp:
            m = r.match(line)
            if m is not None:
                yield (m.group(2), m.group(4).strip())
                yield (m.group(1), m.group(3).strip())

locales = dict(parse_locales())

def scan_dicts(d):
    for ent in sorted(os.scandir(d), key=lambda ent: ent.name):
        if ent.is_file():
            dict_name, ext = os.path.splitext(os.path.basename(ent.path))
            if ext == ".dict":
                yield (dict_name, ent.stat().st_size)

def gen_array(root, name, array, array_kind="string-array"):
    array_elt = ET.SubElement(root, array_kind, attrib={ "name": name })
    for elt in array:
        item = ET.SubElement(array_elt, "item")
        item.text = elt

def dict_name_res(d):
    return "dict_name_" + d[0].lower()

def dict_name_res_ref(d):
    return "@string/" + dict_name_res(d)

def dict_name_text(d):
    loc = d[0].replace("_", "-")
    return locales.get(loc, loc)

def gen_dict_list_xml(dicts, output):
    root = ET.Element("resources")
    for d in dicts:
        elt = ET.SubElement(root, "string")
        elt.attrib["name"] = dict_name_res(d)
        elt.text = dict_name_text(d)
    gen_array(root, "dictionaries_locale", ( n for n, _ in dicts ))
    gen_array(root, "dictionaries_name", map(dict_name_res_ref, dicts))
    gen_array(root, "dictionaries_size", ( str(s) for _, s in dicts ),
              array_kind="integer-array")
    ET.indent(root)
    output.write(ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("UTF-8"))

for v_dir in sys.argv[1:]:
    dicts = list(scan_dicts(v_dir))
    v_name = os.path.basename(v_dir)
    with open("gen/%s/dictionaries.xml" % v_name, "w") as output:
        gen_dict_list_xml(dicts, output)
