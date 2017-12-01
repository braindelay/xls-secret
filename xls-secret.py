from openpyxl import load_workbook
import argparse
import hashlib
import yaml

def parse_args():
    parser = argparse.ArgumentParser(description='Files to parse.')
    parser.add_argument('files', metavar='N', nargs='+',  help='files to parse')
    parser.add_argument('-c', dest = 'hide_config', help='Config file to use',required=True)

    return parser.parse_args()

#
# This handles the actual hiding
#
class Hide:
    #
    # What sheet and column to hide, the from_row indicates from which row to _start_ the hiding (so as to
    # not hide column names - the first row is 0)
    #
    # args.salt, sheet_name,key_name, columns_names, args.from_row
    def __init__(self, salt, sheet_name, column_names, clear_columns, from_row, is_strict):
        self.salt = salt
        self.sheet_name = sheet_name
        self.column_names = column_names
        self.clear_columns= clear_columns
        self.from_row=from_row
        self.is_strict = is_strict

    # Apply this rule to the given workbook
    def hide(self, workbook):

        if self.sheet_name in workbook:
            sheet = workbook[self.sheet_name]

            # open the given sheet and find the column
            # into which the hashed value will be written
            root_col_name=self.column_names[0]
            root_col=sheet[root_col_name]

            # now, root through this column
            # and replace it with a hash pf all the working columns
            row = 1
            for r in root_col:
                if not self.from_row or row >= self.from_row:
                    hash = hashlib.sha512()
                    for c in self.column_names:
                        cell = sheet['%s%s' %(c, row)]

                        cell_value = cell.value
                        if not cell_value:
                            if self.is_strict:
                                exit("File cannot be secured: missing field for %s:%s:%s" % (self.sheet_name, c, row))
                            else:
                                cell_value = ''

                        hash.update(cell_value)

                        if c in self.clear_columns:
                            cell.value = None
                    r.value = hash.hexdigest()
                row = row + 1


def load_configs(args):
    with open(args.hide_config) as f:
        # use safe_load instead load
        return yaml.safe_load(f)

# Parse the args and build the hides
def build_hides(config):
    hides = []
    for h in default(config, 'translations'):
        # SheetA:A.B.C
        hides.append(
            Hide(
                default(config, 'salt'),
                default(h, 'sheet'),
                default(h, 'key'),
                default(h, 'hide'),
                default(h, 'from_row'),
                default(config, 'is_strict')
            )
        )
    if not hides:
        exit("No secrets specified")
    return hides

def default(dict, name, default_val=None):
    return default_val if name not in dict else dict[name]
# Secure the files, and dump a secret version in the same directory
def make_secret(files, hides):
    for f in files:
        wb = load_workbook(filename=f)
        for h in hides:
            h.hide(wb)

        wb.save(filename='secret.%s' % (f))

# Parse the args and then "secretify" the files
args = parse_args()

config = load_configs(args)
hides=build_hides(config)
make_secret(args.files,hides)



