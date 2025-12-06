import sys, os, glob

# Generates Unexpected Keyboard's class at:
#   srcs/juloo.keyboard2/dict/SupportedDictionaries.java

def gen_dict_enum(d):
    dict_name, size = d
    sn = dict_name # Short name
    return "%s(\"%s\", R.string.dict_name_%s, %d)" % (sn.upper(), sn, sn.lower(), size)

def scan_dicts(d):
    for ent in sorted(os.scandir(d), key=lambda ent: ent.name):
        if ent.is_file():
            dict_name, ext = os.path.splitext(os.path.basename(ent.path))
            if ext == ".dict":
                yield (dict_name, ent.stat().st_size)

def gen_dict_list_for_dir(d):
    files = list(scan_dicts(d))
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
}""" % ",\n  ".join(map(gen_dict_enum, files)))

gen_dict_list_for_dir(sys.argv[1])
