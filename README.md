# xls-secret

A simple enough script to apply the `sha512` hash against
all the values in a given set of columns.

So, given a sheet with data like this:

```
Who am I        What did I do 	school name score
Arch Stantom	test4	        Degrassi    15
Bob Dobalina	test1	        Degrassi    91
Frank Sinatry	test5	        Schooly     3

```
And assuming you wanted to hide the pupil and school
names, but in a way that meant when new files came along
you'd be able to compare them.

You can do this:

```
python xls-secret.py  sample.xlsx -s SheetA:A,B,C --from-row=2 --salt "this is a secret"

```

Where:
- `-s` is used top define a column to make secret. 
    The format is `<sheet name>:<column names>`. 
    You can have as many of these as you like.
- `--from-row` from which row (starting at 1) should the hashes
   be applied - use this to skip over headers - optional
- `--salt' an optional salt - see below for more details
- A list of files to process.

This will apply a `SHA512` hash over each value in these 
columns, wipe the values that are there, and insert this hash
as the value for the _first_ column. 

It is _astronomically_ unlikely that two different
values would collide.

The resulting hashed file is written into the same folder
as `secret.<original file name>`

### Salting

By default, the hash is applied _without_ a salt. If you
wish to use a salt to make it harder to use a rainbow table
to reverse engineer the hidden data, you can use a the `--salt`
parameter to apply one.

**NOTE:** however, this will mean that you **MUST** remember
to apply the _same_ salt to every file, every
time you use this.

## Requirements

- This is a `python 2.7 `script
- The `pip` requirements can be installed using 
```sudo  python -m pip install -r requirements.txt```