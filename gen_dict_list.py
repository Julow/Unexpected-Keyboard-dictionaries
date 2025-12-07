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

def gen_dict_list_for_dir(dicts, output):
    def gen_dict_enum(d):
        dict_name, size = d
        sn = dict_name # Short name
        return "%s(\"%s\", R.string.dict_name_%s, %d)" % (
                sn.upper(), sn, sn.lower(), size)
    print("""package juloo.keyboard2.dict;

import juloo.keyboard2.R;

public enum SupportedDictionaries
{
  /** Enumeration of the supported dictionaries. */

  %s;

  /** Associated information. */

  public final String locale; /** Locale that matches this dictionary. */
  public final int name_resource; /** Display name. */
  public final int size; /** Size in bytes of the dictionary file. */

  SupportedDictionaries(String l, int r, int s)
  { locale = l; name_resource = r; size = s; }

  /** Name used in preferences, URLs and file names. */
  public String internal_name() { return locale; }
}""" % ",\n  ".join(map(gen_dict_enum, dicts)), file=output)

def gen_dict_names_for_dir(dicts, output):
    def gen_string(d):
        dict_name, _s = d
        loc = dict_name.replace("_", "-")
        return "<string name=\"dict_name_%s\">%s</string>" % (
                dict_name.lower(), locales.get(loc, loc))
    print("""<?xml version="1.0" encoding="utf-8"?>
<resources>
  %s
</resources>""" % "\n  ".join(map(gen_string, dicts)), file=output)

for v_dir in sys.argv[1:]:
    dicts = list(scan_dicts(v_dir))
    v_name = os.path.basename(v_dir)
    with open("gen/%s/SupportedDictionaries.java" % v_name, "w") as output:
        gen_dict_list_for_dir(dicts, output)
    with open("gen/%s/dict_names.xml" % v_name, "w") as output:
        gen_dict_names_for_dir(dicts, output)
