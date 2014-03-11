"""
A simple Cython-based wrapper for the excellent MDBTools package to read data
from MS Access MDB files. Currently, it supports a few basic operations like
listing tables and table columns, iterating through rows, or exporting a table
to a pandas DataFrame. It does not support SQL or inserts.

Prerequisites
=============

The prerequisites are:

- pkg-config
- glib-2.0
- mdbtools

On Ubuntu this can be satisfied by:

.. code-block:: bash

    sudo apt-get install -y mdbtools-dev

On Arch Linux:

.. code-block:: bash

    yaourt -S mdbtools

On OSX:

.. code-block:: bash

    brew install mdbtools

mdbtools is also available under Cygwin. However, I haven't tested this package
on Windows and there are much easier ways to use Access files under Windows,
such as ODBC or the Python Windows API.

Usage
=====

.. code-block:: python

    >>> from BioTK.io import MDB
    >>> db = MDB.Database("MyDB.mdb")
    >>> print db.tables
    ["tbl1", "tbl2", "tbl3"]

    >>> tbl = db["tbl1"]
    >>> print tbl.columns
    ["foo","bar","baz"]

To get the data in a table, you have three options:

- **MDB.Table.records()** returns a generator of dictionaries, where the keys are column names and the values are the data.
- **iter(MDB.Table)** will return a namedtuple for each row. You can also use this form with **for row in tbl:**
- **MDB.Table.to_data_frame()** will return a pandas DataFrame containing all the data for the entire table (possibly requiring lots of memory) .

Limitations
===========

The biggest current limitation is that not all MS Access datatypes are coerced
to Python objects. So, if you are iterating through rows in an MDB and the
column has an unusual type, the program may fail with a KeyError. You can file
an issue or e-mail me and I can add your favorite datatype. Or, you can simply
add your own coercion to the "transformers" dictionary within BioTK/io/MDB.pyx.
"""

import time
from collections import namedtuple

import pandas

# TODO: confirm this is the correct encoding for table names, 
#  column names, and text fields
MDB_ENCODING = "ISO-8859-1"

cdef extern from "glib.h":
    void* g_malloc(int)
    void* g_malloc0(int)
    void g_free(void*)
    void* g_ptr_array_index(GPtrArray*, int)
    ctypedef struct GPtrArray:
        pass

cdef extern from "mdbsql.h":
    void mdb_init()
    ctypedef struct MdbHandle:
        int num_catalog
        GPtrArray* catalog

    MdbHandle* mdb_open(char*,int)
    enum MdbFileFlags:
        MDB_NOFLAGS
    int MDB_TABLE
    int MDB_BIND_SIZE
    int MDB_ANY

    int mdb_read_catalog(MdbHandle*, int) 
    ctypedef struct MdbCatalogEntry:
        char* object_name
        int object_type

    ctypedef struct MdbTableDef:
        GPtrArray* columns
        int num_cols

    ctypedef struct MdbColumn:
        int col_type
        char* name

    MdbTableDef* mdb_read_table_by_name(MdbHandle*,char*,int)
    void mdb_read_columns(MdbTableDef*)
    void mdb_rewind_table(MdbTableDef*)
    
    char* mdb_get_colbacktype_string(MdbColumn*)

    void mdb_bind_column(MdbTableDef*,int,char*,int*)
    int mdb_fetch_row(MdbTableDef*)
    void mdb_close(MdbHandle*)
    void mdb_exit()

transformers = {
    b"Long Integer": int,
    b"Single": float,
    b"Boolean": lambda x: bool(int(x)),
    b"Text": lambda x: x.decode(MDB_ENCODING),
    b"DateTime": lambda dt: time.strptime(dt, "%m/%d/%y %H:%M:%S")
}

cdef class Database(object):
    cdef MdbHandle* _handle

    def __init__(self, str path):
        mdb_init()
        cpath = path.encode("ascii")
        self._handle = mdb_open(cpath, MDB_NOFLAGS)
        if not mdb_read_catalog(self._handle, MDB_ANY):
            raise Exception("File is not a valid Access database!")

    @property
    def tables(self):
        cdef MdbCatalogEntry* entry

        tables = []
        for i in xrange(self._handle.num_catalog):
            entry = <MdbCatalogEntry*> \
                    g_ptr_array_index(self._handle.catalog, i)
            name = entry.object_name
            if entry.object_type == MDB_TABLE:
                if not "MSys" in name:
                    tables.append(name)
        return tables

    def __iter__(self):
        for tbl in self.tables:
            yield Table(self, tbl)

    def __getitem__(self, key):
        return Table(self, key)

    def __del__(self):
        mdb_close(self._handle)
        mdb_exit()

cdef class Table(object):
    cdef MdbTableDef* tbl
    cdef int ncol
    cdef char* name
    cdef char** bound_values
    cdef int* bound_lens

    def __init__(self, Database mdb, str name):
        cname = name.encode(MDB_ENCODING)
        self.name = cname
        self.tbl = mdb_read_table_by_name(mdb._handle,
                                          self.name,MDB_TABLE)
        self.ncol = self.tbl.num_cols
        self.bound_values = \
            <char**> g_malloc(<int>(self.ncol * sizeof(char*)))
        self.bound_lens = \
            <int*> g_malloc(<int> (self.ncol * sizeof(int)))

        for j in xrange(self.ncol):
            self.bound_values[j] = <char*> g_malloc0(MDB_BIND_SIZE)

        mdb_read_columns(self.tbl)

    def _column_names(self):
        names = []
        cdef MdbColumn* col
        for j in xrange(self.ncol):
            col = <MdbColumn*> g_ptr_array_index(self.tbl.columns, j)
            names.append(col.name)
        return names

    @property
    def columns(self):
        return [c.decode(MDB_ENCODING) for c in self._column_names()]

    def records(self):
        Row = namedtuple("Row",self.columns)
        for row in self:
            yield Row(*row)

    def __iter__(self):
        mdb_rewind_table(self.tbl)

        cdef unsigned int j
        cdef MdbColumn* col
        cdef char* col_type
        col_types = []

        for j in xrange(self.ncol):
            col = <MdbColumn*> g_ptr_array_index(self.tbl.columns, j)
            col_type = mdb_get_colbacktype_string(col)
            col_types.append(col_type)

            mdb_bind_column(self.tbl,j+1,
                            self.bound_values[j],
                            &self.bound_lens[j])

        _transformers = [transformers[t] for t in col_types]
        while mdb_fetch_row(self.tbl):
            row = [_transformers[j](self.bound_values[j]) 
                   for j in xrange(self.ncol)]
            yield row

    def __del__(self):
        for i in xrange(self.ncol):
            g_free(self.bound_values[i])

        g_free(self.bound_values)
        g_free(self.bound_lens)
 
    def to_data_frame(self):
        rows = []
        for row in self:
            rows.append(row)
        names = self.columns
        return pandas.DataFrame(rows, columns=names)
