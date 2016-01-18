"""Select text and some data from Perseus TEI XML files and put into CLTK's
JSON format.
"""

import json
import os
import re
import sys

from lxml import etree

AMPERSAND_MAP = [('&Aacute;', 'Á', 'Latin: Capital Letter A Acute'),
                 ('&aacute;', 'á', 'Latin: Small Letter A Acute'),
                 ('&Acirc;', 'Â', 'Latin: Capital Letter A Circumflex'),
                 ('&acirc;', 'â', 'Latin: Small Letter A Circumflex'),
                 ('&AElig;', 'Æ', 'Latin: Capital Letter AE'),
                 ('&aelig;', 'æ', 'Latin: Small Letter AE'),
                 ('&Agrave;', 'À', 'Latin: Capital Letter A Grave'),
                 ('&agrave;', 'à', 'Latin: Small Letter A Grave'),
                 ('&aleph;', 'ℵ', 'mathmisc:'),
                 ('&Alpha;', 'Α', 'Greek: Capital Letter Alpha'),
                 ('&alpha;', 'α', 'Greek: Small Letter Alpha'),
                 ('&and;', '∧', 'mathmisc:'),
                 ('&ap;', '≈', 'mathmisc:'),
                 ('&apostrophe;', '&apostrophe;', 'miscell:'),
                 ('&archive;', '&archive;', 'icons:'),
                 ('&Aring;', 'Å', 'Latin: Capital Letter A Ring'),
                 ('&aring;', 'å', 'Latin: Small Letter A Ring'),
                 ('&asterisk;', '&asterisk;', 'miscell:'),
                 ('&Atilde;', 'Ã', 'Latin: Capital Letter A Tilde'),
                 ('&atilde;', 'ã', 'Latin: Small Letter A Tilde'),
                 ('&audio;', '&audio;', 'icons:'),
                 ('&Auml;', 'Ä', 'Latin: Capital Letter A Unlaut'),
                 ('&auml;', 'ä', 'Latin: Small Letter A Umlaut'),
                 ('&Beta;', 'Β', 'Greek: Capital Letter Beta'),
                 ('&beta;', 'β', 'Greek: Small Letter Beta'),
                 ('&binary.document;', '&binary.document;', 'icons:'),
                 ('&binhex.document;', '&binhex.document;', 'icons:'),
                 ('&bottom;', '⊥', 'mathmisc:'),
                 ('&brvbar;', '¦', 'miscell: Broken Vertical Bar', 'Letter Pipe'),
                 ('&calculator;', '&calculator;', 'icons:'),
                 ('&cap;', '∩', 'mathsets:'),
                 ('&caution;', '&caution;', 'icons:'),
                 ('&Ccedil;', 'Ç', 'Latin: Capital Letter C Cedilla'),
                 ('&ccedil;', 'ç', 'Latin: Small Letter C Cedilla'),
                 ('&cent;', '¢', 'miscell: Cent'),
                 ('&Chi;', 'Χ', 'Greek: Capital Letter Chi'),
                 ('&chi;', 'χ', 'Greek: Small Letter Chi'),
                 ('&cir;', '○', 'mathmisc:'),
                 ('&clock;', '&clock;', 'icons:'),
                 ('&colon;', ':', 'miscell:'),
                 ('&comma;', ',', 'miscell:'),
                 ('&compressed.document;', '&compressed.document;', 'icons:'),
                 ('&congr;', '&congr;', 'mathmisc:'),
                 ('&cup;', '∪', 'mathsets:'),
                 ('&dArr;', '⇓', 'mathmisc:'),
                 ('&darr;', '↓', 'mathmisc:'),
                 ('&deg;', '°', 'miscell: Degree'),
                 ('&Delta;', 'δ', 'Greek: Capital Letter Delta'),
                 ('&delta;', 'δ', 'Greek: Small Letter Delta'),
                 ('&disk.drive;', '&disk.drive;', 'icons:'),
                 ('&diskette;', '&diskette;', 'icons:'),
                 ('&display;', '&display;', 'icons:'),
                 ('&document;', '&document;', 'icons:'),
                 ('&dollar;', '$', 'miscell:'),
                 ('&dot;', '˙', 'mathmisc:'),
                 ('&Eacute;', 'É', 'Latin: Capital Letter E Acute'),
                 ('&eacute;', 'é', 'Latin: Small Letter E Acute'),
                 ('&Ecirc;', 'Ê', 'Latin: Capital Letter E Circumflex'),
                 ('&ecirc;', 'ê', 'Latin: Small Letter E Circumflex'),
                 ('&Egrave;', 'È', 'Latin: Capital Letter E Grave'),
                 ('&egrave;', 'è', 'Latin: Small Letter E Grave'),
                 ('&empty;', '∅', 'mathmisc:'),
                 ('&Epsilon;', 'Ε', 'Greek: Capital Letter Epsilon'),
                 ('&epsilon;', 'ε', 'Greek: Small Letter Epsilon'),
                 ('&eq;', '&eq;', 'mathmisc:'),
                 ('&equals;', '=', 'miscell:'),
                 ('&equiv;', '≡', 'mathmisc:'),
                 ('&Eta;', 'Η', 'Greek: Capital Letter Eta'),
                 ('&eta;', 'η', 'Greek: Small Letter Eta'),
                 ('&ETH;', 'Ð', 'Latin: Capital Letter Eth'),
                 ('&eth;', 'ð', 'Latin: Small Letter Eth'),
                 ('&Euml;', 'Ë', 'Latin: Capital Letter E Umlaut'),
                 ('&euml;', 'ë', 'Latin: Small Letter E Umlaut'),
                 ('&excl;', '!', 'miscell:'),
                 ('&exist;', '∃', 'mathmisc:'),
                 ('&fax;', '&fax;', 'icons:'),
                 ('&filing.cabinet;', '&filing.cabinet;', 'icons:'),
                 ('&film;', '&film;', 'icons:'),
                 ('&fixed.disk;', '&fixed.disk;', 'icons:'),
                 ('&folder;', '&folder;', 'icons:'),
                 ('&forall;', '∀', 'mathmisc:'),
                 ('&form;', '&form;', 'icons:'),
                 ('&frac18;', '⅛', 'miscell: One eighth'),
                 ('&frac14;', '¼', 'miscell: One quarter'),
                 ('&frac38;', '⅜', 'miscell: Three eighths'),
                 ('&frac12;', '½', 'miscell: One half'),
                 ('&frac58;', '⅝', 'miscell: Five eighths'),
                 ('&frac34;', '¾', 'miscell: Three quarters'),
                 ('&frac78;', '⅞', 'miscell: Seven eighths'),
                 ('&ftp;', '&ftp;', 'icons:'),
                 ('&Gamma;', 'Γ', 'Greek: Capital Letter Gamma'),
                 ('&gamma;', 'γ', 'Greek: Small Letter Gamma'),
                 ('&ge;', '≥', 'mathmisc:'),
                 ('&glossary;', '&glossary;', 'icons:'),
                 ('&gopher;', '&gopher;', 'icons:'),
                 # ('&gt;', '>', 'mathmisc: Greater than'),
                 ('&half;', '½', 'miscell:'),
                 ('&hArr;', '⇔', 'mathmisc:'),
                 ('&harr;', '↔', 'mathmisc:'),
                 ('&home;', '&home;', 'icons:'),
                 ('&hyphen;', '‐', 'miscell:'),
                 ('&Iacute;', 'Í', 'Latin: Capital Letter I Acute'),
                 ('&iacute;', 'í', 'Latin: Small Letter I Acute'),
                 ('&Icirc;', 'Î', 'Latin: Capital Letter I Circumflex'),
                 ('&icirc;', 'î', 'Latin: Small Letter I Circumflex'),
                 ('&iexcl;', '¡', 'miscell:'),
                 ('&Igrave;', 'Ì', 'Latin: Capital Letter I Grave'),
                 ('&igrave;', 'ì', 'Latin: Small Letter I Grave'),
                 ('&image;', 'ℑ', 'icons:'),
                 ('&index;', '&index;', 'icons:'),
                 ('&inf;', '&inf;', 'mathmisc:'),
                 ('&Iota;', 'Ι', 'Greek: Capital Letter Iota'),
                 ('&iota;', 'ι', 'Greek: Small Letter Iota'),
                 ('&iquest;', '¿', 'miscell: Inverted Question Mark'),
                 ('&isin;', '∈', 'mathsets:'),
                 ('&Iuml;', 'Ï', 'Latin: Capital Letter I Umlaut'),
                 ('&iuml;', 'ï', 'Latin: Small Letter I Umlaut'),
                 ('&Kappa;', 'Κ', 'Greek: Capital Letter Kappa'),
                 ('&kappa;', 'κ', 'Greek: Small Letter Kappa'),
                 ('&Lambda;', 'Λ', 'Greek: Capital Letter Lamda'),
                 ('&lambda;', 'λ', 'Greek: Small Letter Lamda'),
                 ('&lang;', '〈', 'mathmisc:'),
                 ('&laquo;', '«', 'miscell: Left Double Arrow Quotation Mark'),
                 ('&lArr;', '⇐', 'mathmisc:'),
                 ('&larr;', '←', 'mathmisc:'),
                 ('&le;', '≤', 'mathmisc:'),
                 ('&lpar;', '(', 'miscell:'),
                 ('&lsqb;', '[', 'miscell:'),
                 # ('&lt;', '<', 'mathmisc: Less than'),
                 ('&mail.in;', '&mail.in;', 'icons:'),
                 ('&mail.out;', '&mail.out;', 'icons:'),
                 ('&mail;', '&mail;', 'icons:'),
                 ('&map;', '↦', 'icons:'),
                 ('&mdash;', '—', 'M-dash'),
                 ('&micro;', 'µ', 'miscell: Mu'),
                 ('&mid;', '∣', 'mathmisc:'),
                 ('&middot;', '·', 'miscell: Middle Dot'),
                 ('&mouse;', '&mouse;', 'icons:'),
                 ('&Mu;', 'Μ', 'Greek: Capital Letter Mu'),
                 ('&mu;', 'μ', 'Greek: Small Letter Mu'),
                 ('&ndash;', '–', 'N-dash'),
                 ('&ne;', '≠', 'mathmisc:'),
                 ('&nequiv;', '≢', 'mathmisc:'),
                 ('&next;', '&next;', 'icons:'),
                 ('&not;', '¬', 'mathsets: NOT'),
                 ('&Ntilde;', 'Ñ', 'Latin: Capital Letter N Tilde'),
                 ('&ntilde;', 'ñ', 'Latin: Small Letter N Tilde'),
                 ('&Nu;', 'Ν', 'Greek: Capital Letter Nu'),
                 ('&nu;', 'ν', 'Greek: Small Letter Nu'),
                 ('&nvDash;', '⊭', 'mathmisc:'),
                 ('&nvdash;', '⊬', 'mathmisc:'),
                 ('&Oacute;', 'Ó', 'Latin: Capital Letter O Acute'),
                 ('&oacute;', 'ó', 'Latin: Small Letter O Acute'),
                 ('&Ocirc;', 'Ô', 'Latin: Capital Letter O Circumflex'),
                 ('&ocirc;', 'ô', 'Latin: Small Letter O Circumflex'),
                 ('&Ograve;', 'Ò', 'Latin: Capital Letter O Grave'),
                 ('&ograve;', 'ò', 'Latin: Small Letter O Grave'),
                 ('&Omega;', 'Ω', 'Greek: Capital Letter Omega'),
                 ('&omega;', 'ω', 'Greek: Small Letter Omega'),
                 ('&Omicron;', 'Ο', 'Greek: Capital Letter Omicron'),
                 ('&omicron;', 'ο', 'Greek: Small Letter Omicron'),
                 ('&oplus;', '⊕', 'mathmisc:'),
                 ('&or;', '∨', 'mathmisc:'),
                 ('&Oslash;', 'Ø', 'Latin: Capital Letter O Slash'),
                 ('&oslash;', 'ø', 'Latin: Small Letter O Slash'),
                 ('&Otilde;', 'Õ', 'Latin: Capital Letter O Tilde'),
                 ('&otilde;', 'õ', 'Latin: Small Letter O Tilde'),
                 ('&otimes;', '⊗', 'mathmisc:'),
                 ('&Ouml;', 'Ö', 'Latin: Capital Letter O Umlaut'),
                 ('&ouml;', 'ö', 'Latin: Small Letter O Umlaut'),
                 ('&para;', '¶', 'miscell: Paragraph'),
                 ('&parent;', '&parent;', 'icons:'),
                 ('&part;', '∂', 'mathmisc:'),
                 ('&pd;', '&pd;', 'mathmisc:'),
                 ('&percent;', '&percent;', 'miscell:'),
                 ('&period;', '.', 'miscell:'),
                 ('&Phi;', 'Φ', 'Greek: Capital Letter Phi'),
                 ('&phi;', 'φ', 'Greek: Small Letter Phi'),
                 ('&Pi;', 'Π', 'Greek: Capital Letter Pi'),
                 ('&pi;', 'π', 'Greek: Small Letter Pi'),
                 ('&plus;', '+', 'miscell:'),
                 ('&plusmn;', '±', 'mathmisc: Plus-minus'),
                 ('&pound;', '£', 'miscell: Pound Sterling'),
                 ('&previous;', '&previous;', 'icons:'),
                 ('&Prime;', ' ', 'mathmisc:'),
                 ('&prime;', ' ', 'mathmisc:'),
                 ('&printer;', '&printer;', 'icons:'),
                 ('&Prod;', '&Prod;', 'mathmisc:'),
                 ('&prop;', '∝', 'mathmisc:'),
                 ('&Psi;', 'Ψ', 'Greek: Capital Letter Psi'),
                 ('&psi;', 'ψ', 'Greek: Small Letter Psi'),
                 ('&quest;', '?', 'miscell:'),
                 ('&quot;', '"', 'miscell: Double Quotation Mark'),
                 ('&rang;', '〉', 'mathmisc:'),
                 ('&raquo;', '»', 'miscell: Right Double Arrow Quotation Mark'),
                 ('&rarr;', '→', 'mathmisc:'),
                 ('&rArr;', '⇒', 'mathmisc:'),
                 ('&real;', 'ℜ', 'mathmisc:'),
                 ('&Rho;', 'Ρ', 'Greek: Capital Letter Rho'),
                 ('&rho;', 'ρ', 'Greek: Small Letter Rho'),
                 ('&rpar;', ')', 'miscell:'),
                 ('&rsqb;', ']', 'miscell:'),
                 ('&sect;', '§', 'miscell: Section'),
                 ('&semi;', ';', 'miscell:'),
                 ('&setmn;', '∖', 'mathmisc:'),
                 ('&Sigma;', 'Σ', 'Greek: Capital Letter Sigma'),
                 ('&sigma;', 'σ', 'Greek: Small Letter Sigma'),
                 ('&square;', '□', 'mathmisc:'),
                 ('&sub;', '⊂', 'mathsets:'),
                 ('&Sum;', '∑', 'mathmisc:'),
                 ('&summary;', '&summary;', 'icons:'),
                 ('&sup1;', '¹', 'miscell: Superscript Numeral 1'),
                 ('&sup2;', '²', 'miscell: Superscript Numeral 2'),
                 ('&sup3;', '³', 'miscell: Superscript Numeral 3'),
                 ('&sup;', '⊃', 'mathsets:'),
                 ('&SZlig;', '&SZlig;', 'Latin: Latin Capital Letter Ess-Zed'),
                 ('&szlig;', 'ß', 'Latin: Latin Small Letter Ess-Zed'),
                 ('&Tau;', 'Τ', 'Greek: Capital Letter Tau'),
                 ('&tau;', 'τ', 'Greek: Small Letter Tau'),
                 ('&telnet;', '&telnet;', 'icons:'),
                 ('&text.document;', '&text.document;', 'icons:'),
                 ('&Theta;', 'Θ', 'Greek: Capital Letter Theta'),
                 ('&theta;', 'θ', 'Greek: Small Letter Theta'),
                 ('&Thorn;', '&Thorn;', 'Latin: Capital Letter Thorn'),
                 ('&thorn;', 'þ', 'Latin: Small Letter Thorn'),
                 ('&three.quarters;', '&three.quarters;', 'miscell:'),
                 ('&tilde;', '˜', 'miscell: Tilde Accent'),
                 ('&tn3270;', '&tn3270;', 'icons:'),
                 ('&toc;', '&toc;', 'icons:'),
                 ('&trash;', '&trash;', 'icons:'),
                 ('&Uacute;', 'Ú', 'Latin: Capital Letter U Acute'),
                 ('&uacute;', 'ú', 'Latin: Small Letter U Acute'),
                 ('&uArr;', '⇑', 'mathmisc:'),
                 ('&uarr;', '↑', 'mathmisc:'),
                 ('&Ucirc;', 'Û', 'Latin: Capital Letter U Circumflex'),
                 ('&ucirc;', 'û', 'Latin: Small Letter U Circumflex'),
                 ('&Ugrave;', 'Ù', 'Latin: Capital Letter U Grave'),
                 ('&ugrave;', 'ù', 'Latin: Small Letter U Grave'),
                 ('&unknown.document;', '&unknown.document;', 'icons:'),
                 ('&Upsilon;', 'Υ', 'Greek: Capital Letter Upsilon'),
                 ('&upsilon;', 'υ', 'Greek: Small Letter Upsilon'),
                 ('&uuencoded.document;', '&uuencoded.document;', 'icons:'),
                 ('&Uuml;', 'Ü', 'Latin: Capital Letter U Umlaut'),
                 ('&uuml;', 'ü', 'Latin: Small Letter U Umlaut'),
                 ('&vDash;', '⊨', 'mathmisc:'),
                 ('&vdash;', '⊢', 'mathmisc:'),
                 ('&verbar;', '|', 'miscell:'),
                 ('&Xi;', 'Ξ', 'Greek: Capital Letter Xi'),
                 ('&xi;', 'ξ', 'Greek: Small Letter Xi'),
                 ('&Yacute;', 'Ý', 'Latin: Capital Letter Y Acute'),
                 ('&yacute;', 'ý', 'Latin: Small Letter Y Acute'),
                 ('&yen;', '¥', 'miscell: Yen'),
                 ('&Yuml;', 'Ÿ', 'Latin: Capital Letter Y Umlaut'),
                 ('&yuml;', 'ÿ', 'Latin: Small Letter Y Umlaut'),
                 ('&Zeta;', 'Ζ', 'Greek: Capital Letter Zeta'),
                 ('&zeta;', 'ζ', 'Greek: Small Letter Zeta'),
                 ('&fund.Mellon;', ''),
                 ('&Perseus.publish;', ''),
                 ('&responsibility;', ''),
                 ('&fund.AnnCPB;', ''),
                 ('&fund.NEH;', ''),
                 ('efund.Tufts;', ''),
                 ('ePerseus.publist;', ''),
                 ('fund.FIPSE;', ''),
                 # ?('fund.Tufts;', ''),
                 ('&fund.Tufts;', ''),
                 ('&fund.FIPSE;', ''),
                 ('&amacr;', 'ā'),
                 ('&emacr;', 'ē'),
                 ('&imacr;', 'ī'),
                 ('&omacr;', 'ō'),
                 ('&umacr;', 'ū'),
                 ('&dagger;', '†'),
                 ('&lsquo;', "'"),
                 ('&nbsp;', ' '),
                 ('&c;', 'Ↄ'),
                 ('&racute;', 'ŕ'),
                 ('&ldquo;', '"'),
                 ('&itilde;', 'ĩ'),
                 ('&oelig;', 'œ'),
                 ('&divide;', '÷'),
                 ('&rdquo;', '"'),
                 ('&rsquo;', "'"),
                 ('&Perseus.OCR', ''),
                 ('&ast;', '*'),
                 ('&infin;', '∞'),
                 ('&Imacr;', 'Ī'),
                 ('&utilde;', 'ũ'),
                 ('&ubreve;', 'ŭ'),
                 ('&circ;', 'ˆ'),
                 ('&uring;', 'ů'),
                 ('&cdot;', 'ċ'),
                 ('&rect;', '▭'),
                 ('&Emacr;', 'Ē'),
                 ('&ecaron;', 'ě'),
                 ('&macr;', '¯'),
                 ('&grave;', '`'),
                 ('&ccirc;', 'ĉ'),
                 ('&times;', '×'),
                 ('&fund.DLI2;', ''),
                 ('&Perseus.DE;', ''),
                 # ('&;', ''),
                 ]


def extract_xml(filepath):
    """Open file, return LXML etree."""
    return etree.parse(filepath)


def extract_xml_str(xml_string):
    """Parse XML string, return LXML etree."""
    # return etree.parse(filepath)
    '''
    try:
        return etree.fromstring(xml_string)
    except etree.XMLSyntaxError as lxml_err:
        print(lxml_err)
    '''
    return etree.fromstring(xml_string)


def dir_scan(filepath, suffix='.xml'):
    """Recursively scan dir with os.scandir() (new to Python 3.5)"""
    for author in os.scandir('.'):
        if author.is_dir():
            name = author.name
            opensource = os.path.join(name, 'opensource')
            if os.path.isdir(opensource):
                text_files = os.scandir(opensource)
                for text_file in text_files:
                    if text_file.is_file() and not text_file.name.startswith('.') and text_file.name.endswith(suffix):
                        yield text_file.path


def write_json(json_obj, filepath):
    """Take dict and write JSON and filepath, write JSON to file."""
    dirs, name = os.path.split(filepath)

    # Remove .xml and add .json to filename
    name_json = name[:-len('.xml')] + '.json'

    fp_json = os.path.join(dirs, name_json)
    with open(fp_json, 'w') as file_open:
        json.dump(json_obj, file_open)


def parse_chapter(lxml_etree, filepath):
    """Take etree and parse the XML type of Sallust's BC.

    /Users/kyle/latin_text_perseus/Sallust/opensource/sallust.catil_lat.xml
    /Users/kyle/latin_text_perseus/Sallust/opensource/sallust.jugur_lat.xml
    """

    dict_object = {}
    dict_object['meta'] = 'chapter'

    # Parse header
    tei_header = lxml_etree.find('teiHeader')
    file_desc = tei_header.find('fileDesc')
    title_statement = file_desc.find('titleStmt')
    title = title_statement.find('title')
    author = title_statement.find('author')
    # print(title.text)
    # print(author.text)
    dict_object['title'] = title.text
    try:
        dict_object['author'] = author.text
    except AttributeError:
        dict_object['author'] = filepath.split('/')[0]

    # Parse body
    dict_text = {}
    text = lxml_etree.find('text')
    body = text.find('body')
    div1s = body.findall('div1')
    for div1 in div1s:
        type = div1.get('type')
        # print(type)
        if type != 'chapter':  # 'Not a "chapter" type, try another XML parsing function.'
            return AssertionError
        number = str(div1.get('n'))
        p = div1.find('p')
        dict_text[number] = p.text

    dict_object['text'] = dict_text

    return dict_object


def parse_poems(lxml_etree, filepath):
    """Take etree and parse the XML type of Catullus."""

    dict_object = {}
    dict_object['meta'] = 'poem-line'

    # Parse header
    tei_header = lxml_etree.find('teiHeader')
    file_desc = tei_header.find('fileDesc')
    title_statement = file_desc.find('titleStmt')
    title = title_statement.find('title')
    author = title_statement.find('author')
    # print('Title:', title.text)
    # print('Author:', author.text)
    dict_object['title'] = title.text
    try:
        dict_object['author'] = author.text
    except AttributeError:
        dict_object['author'] = filepath.split('/')[0]
        # print('Author not found in XML, got from dir name.')

    # Parse body
    dict_text = {}
    text = lxml_etree.find('text')
    body = text.find('body')
    filename = os.path.split(filepath)[1]
    if filename in ['persius.sat_lat.xml']:
        div1s = body.findall('div1')
        for div1 in div1s:
            type = div1.get('type')
            # print(type)
            poem_number = div1.get('n')
            # print(poem_number)
            if type not in ['satire']:
                return AssertionError
            p = div1.find('p')
            print(p)
            return {}

    else:  # works for Catullus
        div1s = body.findall('div1')
        for div1 in div1s:
            type = div1.get('type')
            # print(type)
            # assert type in ['Lyrics', 'Long Poems', 'Elegies'], 'Not a "poems" type, try another XML parsing function.'
            if type not in ['Lyrics', 'Long Poems', 'Elegies']:
                return AssertionError

            div2s = div1.findall('div2')
            for div2 in div2s:
                number_str = div2.get('n')
                try:
                    number = int(number_str)
                except ValueError as val_err:
                    number = int(number_str[:-1])
                # print(number)
                xml_lines = div2.findall('l')
                lines_list = []
                for xml_line in xml_lines:
                    lines_list.append(xml_line.text)
                dict_poem = {}
                for count, line in enumerate(lines_list, 1):
                    dict_poem[count] = line
                dict_text[number] = dict_poem

        dict_object['text'] = dict_text

        return dict_object


def cleanup_file_perseus_xml(filepath_xml):
    """Cleanup input xml file, return string."""
    with open(filepath_xml) as file_open:
        file_text = file_open.read()

    for mapping in AMPERSAND_MAP:
        asc = mapping[0]
        unicode = mapping[1]
        file_text = re.sub(r'%s' % asc, unicode, file_text)

    return file_text


def main():
    """Main"""

    file_type_parsers = [parse_chapter, parse_poems]

    for filepath_xml in dir_scan('.', suffix='lat.xml'):
        xml_str = cleanup_file_perseus_xml(filepath_xml)
        print(filepath_xml)
        tei = extract_xml_str(xml_str)
        for file_parser in file_type_parsers:
            try:
                dict_object = file_parser(tei, filepath_xml)

                if str(dict_object) == "<class 'AssertionError'>":
                    continue
                #if dict_object['text'] == {}:
                if dict_object.get('text') == {}:
                    continue

                print("Parser '{}' worked! Moving to next file …".format(file_parser))
                write_json(dict_object, filepath_xml)
                break

            except AttributeError as attrib_err:
                pass
            '''
            try:
                dict_object = file_parser(tei, filepath_xml)
                if str(dict_object) == "<class 'AssertionError'>":
                    continue
                #if dict_object['text'] == {}:
                #    print("Didn't find any text, try again")
                #    continue
                print('Success:', filepath_xml)
                write_json(dict_object, filepath_xml)
                break
            except AttributeError as attrib_err:
                pass
            '''
        print()


if __name__ == '__main__':
    main()
