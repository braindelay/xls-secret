from openpyxl import load_workbook
import argparse
import hashlib

def parse_args():
    parser = argparse.ArgumentParser(description='Files to parse.')
    parser.add_argument('files', metavar='N', nargs='+',  help='files to parse')
    parser.add_argument('-s', dest = 'hides', action = 'append', help="Set of entries to hide, see readme for more details")
    parser.add_argument('--salt', default=None)
    parser.add_argument('--from-row', dest='from_row', default=None, type=int)

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
    def __init__(self, salt, sheet_name, column_names, from_row):
        self.salt = salt
        self.sheet_name = sheet_name
        self.column_names = column_names
        self.from_row=from_row

    # Apply this rule to the given workbook
    def hide(self, workbook):
        sheet = workbook[self.sheet_name]
        # open the given sheet and find the column
        root_col=sheet[self.column_names[0]]

        # hash the keys
        row = 1
        for r in root_col:
            if not self.from_row or row >= self.from_row:
                hash = hashlib.sha512()
                for c in self.column_names:
                    cell = sheet['%s%s' %(c, row)]
                    hash.update(cell.value)
                    cell.value = None
                r.value = hash.hexdigest()
            row = row + 1

        # now deleyte the non-root cols
        if len(self.column_names) > 1:
            for c in self.column_names[1:]:
                print c
# Parse the args and build the hides
def build_hides(args):
    hides = []
    for h in args.hides:
        # SheetA:A.B.C
        (sheet_name, cell_args) = h.split(':')
        columns_names = cell_args.split(',')
        hides.append(Hide(args.salt, sheet_name, columns_names, args.from_row))
    if not hides:
        exit("No secrets specified")
    return hides

# Secure the files, and dump a secret version in the same directory
def make_secret(files, hides):
    for f in files:
        wb = load_workbook(filename=f)
        for h in hides:
            h.hide(wb)

        wb.save(filename='secret.%s' % (f))

# Parse the args and then "secretify" the files
args = parse_args()

hides=build_hides(args)
make_secret(args.files,hides)



