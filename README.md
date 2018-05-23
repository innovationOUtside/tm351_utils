# `tm351_utils`


Some utilities to support notebook activities in TM351


`!pip3 install --upgrade git+https://github.com/innovationOUtside/tm351_utils.git`

## Usage

`from tm351_utils.utils import *`
`from tm351_utils.db import showDatabases, showTables, showColumns, showUsers, showConnections, clearConnections`

## Functions available:

- `table_def(table,db='tm351test', retval=False, noprint=False)`: run `pg_dump` command from Python to obtain `CREATE TABLE` statement for identified table from specified database. Set `retval=True` to return the value as a text string that can be used as an input to `show_diff()`; set `noprint=True` to suppress printing of the table statement
- `show_diff(string1, string2)`: display a diff between two strings
- `merged_notebooks_in_dir(dirpath,filenames=None)`:
    Merge all notebooks in a directory into a single notebook
- `merged_notebooks_down_path(path, typ='docx', execute=False)`: Walk a path, creating an output file in each directory that merges all notebooks in the directory

- `showUsers()`:
- `showConnections(DBNAME)`:
- `showTables(DBNAME)`:
- `showColumns(DBNAME, TABLENAME)`:
- `clearConnections(DBNAME)`:

## See Also
Relavent to TM351 but not installed directly as part of the `tm351_utils` package:

- [`innovationOUtside/ipython_magic_sqlalchemy_schemadisplay`](https://github.com/innovationOUtside/ipython_magic_sqlalchemy_schemadisplay)