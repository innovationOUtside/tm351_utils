# `tm351_utils`


Some utilities to support notebook activities in TM351


`!pip3 install --upgrade git+https://github.com/innovationOUtside/tm351_utils.git`

## Usage

`from tm351_utils.utils import *`

## Functions available:

- `table_def(table,db='tm351test', retval=False, noprint=False)`: run `pg_dump` command from Python to obtain `CREATE TABLE` statement for identified table from specified database. Set `retval=True` to return the value as a text string that can be used as an input to `show_diff()`; set `noprint=True` to suppress printing of the table statement
- `show_diff(string1, string2)`: display a diff between two strings


## See Also
Relavent to TM351 but not installed directly as part of the `tm351_utils` package:

- [`ipython_magic_eralchemy`](https://github.com/innovationOUtside/ipython_magic_eralchemy)
- [`eralchemy (updated)`](https://github.com/psychemedia/eralchemy)
