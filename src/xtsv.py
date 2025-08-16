#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class XtsvCell:
    """
    The container class holding a cell in a table of XTSV file.
    """
    def __init__(self, value: object, unit: str = None):
        """
        Initialize an XtsvCell object.

        Parameters
        ----------
        value : object
            An object of type "str", "int" or "float".
        unit : str, optional
            The unit of the value when **value** is of type "int" or "float".
            The default is None, i.e. no unit.

        Returns
        -------
        None.
        """
        self.value = value
        self.unit = unit
    
    def __repr__(self) -> str:
        """
        Get a string representation of the cell.

        Returns
        -------
        str
            A string representing the value of the cell.
        """
        return '{} {}'.format(self.value, self.unit)

class XtsvTable:
    """
    The container class holding a table of XTSV file.
    """
    def __init__(self, name: str, columnNames: list[str] = None):
        """
        Initialize an XtsvTable object.

        Parameters
        ----------
        name : str
            The name of the XtsvTable.

        Returns
        -------
        None.
        """
        self.name = name
        self.columnNames = columnNames
        self.rowNames: list[str] = []
        self.values: list[list[XtsvCell]] = []
    
    def columnCount(self) -> int:
        """
        Get the number of columns in the table.

        Returns
        -------
        int
            The number of columns.
        """
        return max(len(X) for X in self.values)
    
    def rowCount(self) -> int:
        """
        Get the number of rows in the table.

        Returns
        -------
        int
            The number of rows.
        """
        return len(self.values)
    
    def appendRow(self, values: list[XtsvCell], rowName: str = None):
        """
        Append a row to the table.

        Parameters
        ----------
        values : list[XtsvCell]
            A list of XtsvCell objects representing a row of data.
        rowName : str, optional
            The name of the row. 
            The default is None, i.e. no row name.

        Returns
        -------
        None.
        """
        self.values.append(values)
        self.rowNames.append(rowName)
    
    def item(self, row: int, column: int) -> XtsvCell:
        """
        Get an item in the table by row and column index.

        Parameters
        ----------
        row : int
            The row index of a cell.
        column : int
            The column index of a cell.

        Returns
        -------
        XtsvCell
            A XtsvCell object representing a cell.
        """
        if row < len(self.values) and column < len(self.values[row]):
            return self.values[row][column]
        raise IndexError('invalid table index ({}, {})'.format(row, column))

class XtsvSection:
    """
    The container class holding a section of XTSV file.
    """
    def __init__(self, name: str, value: object = None):
        """
        Initialize an XtsvSection object.

        Parameters
        ----------
        name : str
            The name of the section.
        value : object, optional
            An object of type "str", "int" or "float" representing the value 
            attached to the section.
            The default is None.

        Returns
        -------
        None.
        """
        self.name = name
        self.value = value
        self.tables: list[XtsvTable] = []
    
    def appendTable(self, table: XtsvTable):
        """
        Append a table to the section.

        Parameters
        ----------
        table : XtsvTable
            A XtsvTable object representing a table of XTSV File.

        Returns
        -------
        None.
        """
        self.tables.append(table)

class XtsvFile:
    """
    The class for parsing eXtended Tab Separated Value (XTSV) files.
    """
    def __init__(self, filename: str, delimiter: str = '\t'):
        """
        Initialize an XtsvFile object.

        Parameters
        ----------
        filename : str
            The name of the tabular file.
        delimiter : str, optional
            The delimiter of values in a row. The default is TAB.

        Returns
        -------
        None.
        """
        self.filename = filename
        self.delimiter = delimiter
    
    @staticmethod
    def detectNumeral(value: str) -> object:
        """
        Detect numeric value in a string.

        Parameters
        ----------
        value : str
            A string potentially representing a potential numeric value.

        Returns
        -------
        object
            An object of type "str", "int" or "float".
        """
        if '.' in value:
            try:
                return float(value)
            except ValueError:
                return value
        try:
            return int(value)
        except ValueError:
            return value
    
    @staticmethod
    def parseCell(value: str, detectNumeral: bool = True) -> XtsvCell:
        """
        Parse a string as a cell in a table of XTSV file.

        Parameters
        ----------
        value : str
            A string representing the value of a cell.
        detectNumerals : bool, optional
            Whether to convert cell values to numerals whenever possible.
            The default is True.

        Returns
        -------
        XtsvCell
            A XtsvCell object holding the parse value.
        """
        if not detectNumeral:
            return XtsvCell(value.strip())
        
        nonNumericPosition = next(iter(i for i, X in enumerate(value) 
                                       if not X.isnumeric() and \
                                          X not in ('.', 'e', 'E', '+', '-')), 
                                  None)
        if nonNumericPosition is None:
            return XtsvCell(XtsvFile.detectNumeral(value.strip()))
        return XtsvCell(XtsvFile.detectNumeral(value[:nonNumericPosition]), 
                        value[nonNumericPosition:].strip())
    
    def parse(self, detectNumerals: bool = True, rowNames: bool = True) \
             -> list[XtsvSection]:
        """
        Parse the specified XTSV file.

        Parameters
        ----------
        detectNumerals : bool, optional
            Whether to convert cell values to numerals whenever possible.
            The default is True.
        rowNames : bool, optional
            Whether to treat the first cell in each row in a table as 
            the row name.
            The default is True.
        
        Returns
        -------
        list[XtsvSection]
            A list of sections in the XTSV file.
        """
        sections = {}
        
        with open(self.filename, 'r') as file:
            inSection = False
            section = None
            table = None
            while True:
                line = file.readline()
                if len(line) == 0:
                    break
                
                # Get values in non-empty cells
                cells = [X.strip() for X in line.split('\t')]
                cells = [X for X in cells if len(X) > 0]
                if len(cells) == 0:
                    continue
                if len(cells) == 1:
                    # The beginning of a section containing tables
                    inSection = True
                    sectionName = cells[0]
                    section = sections.get(sectionName, 
                                           XtsvSection(sectionName))
                    sections[sectionName] = section
                    table = None
                else:
                    if inSection:
                        if table is None:
                            # The beginning of a table
                            table = XtsvTable(cells[0], cells[1:])
                            section.appendTable(table)
                        else:
                            if len(cells) == 2 and \
                               (len(table.values) == 0 or \
                                len(table.values[-1]) != 2):
                                # A new section with no table but a value
                                inSection = False
                                table = None
                                sectionName = cells[0]
                                sections[sectionName] = \
                                    XtsvSection(sectionName, cells[1])
                            else:
                                # Table content
                                if rowNames:
                                    table.appendRow(
                                        [self.parseCell(X, detectNumerals) 
                                         for X in cells[1:]], 
                                        cells[0])
                                else:
                                    table.appendRow(
                                        [self.parseCell(X, detectNumerals) 
                                         for X in cells])
                    else:
                        if len(cells) > 2:
                            # Invalid number of cells outside a table
                            raise ValueError('{} cells found in the section '
                                             '{} but without a table'.
                                             format(len(cells), section.name))
                        # A section with no table but a value
                        sectionName = cells[0]
                        sections[sectionName] = XtsvSection(sectionName, 
                                                            cells[1])
        
        # Remove empty sections
        sections = {name: section for name, section in sections.items() 
                    if len(section.tables) > 0 or section.value is not None}
        
        return list(sections.values())
