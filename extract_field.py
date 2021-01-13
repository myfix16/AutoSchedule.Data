from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
import os
import re
import csv


class FieldExtractor():
    def __init__(self, class_name: str, source: Optional[str] = None) -> None:
        self.class_name = class_name
        if source is None:
            source = f"./pages/{class_name}.html"
        self.doc = BeautifulSoup(open(source, encoding='utf-8'))
        self.subject_table: Tag = self.doc.select('#ACE_\$ICField102\$0')[0]
        self._names: List[str] = None
        self._codes: List[List[str]] = None
        self._instructors: List[List[str]] = None
        self._times: List[List[str]] = None
        self._locations: List[List[str]] = None
        self._contents: list = None

    @property
    def names(self) -> List[str]:
        """Get the name of every sessions.
        """
        if self._names is None:
            names_span: ResultSet = self.subject_table.find_all(
                'span', id=re.compile('DERIVED_CLSRCH_DESCR200\$\d'))
            self._names = [span.string.replace(" ", "", 3) for span in names_span]
        return self._names

    @property
    def codes(self) -> List[List[str]]:
        """Get the code of every sessions.
        """
        if self._codes is None:
            code_container: ResultSet = self.subject_table.find_all(
                'a', id=re.compile('DERIVED_CLSRCH_SSR_CLASSNAME_LONG\$\d'))
            self._codes = [a.string for a in code_container]
        return self._codes

    @property
    def instructors(self) -> List[List[str]]:
        if self._instructors is None:
            self._read_details()
        return self._instructors

    @property
    def times(self) -> List[List[str]]:
        if self._times is None:
            self._read_details()
        return self._times

    @property
    def locations(self) -> List[List[str]]:
        if self._locations is None:
            self._read_details()
        return self._locations

    @property
    def contents(self) -> list:
        """Get the content of every session, return all div's.
        """
        if self._contents is None:
            self._contents: ResultSet = self.subject_table.select("a[id^='win0div$ICField106$']")
        return self._contents







    # TODO: The function doesn't parse the html correctly. In specific, the name and details are not matched in some courses like ERG3020.
    def _read_details(self) -> None:
        self._instructors = []
        self._times = []
        self._locations = []
        # Loop through all sessions and gather session information.
        for div in self.contents:
            instructors = []
            times = []
            locations = []
            details_table: ResultSet = div.findAll('table', id=re.compile('SSR_CLSRCH_MTG1\$scroll\$\d+'))
            # Deal with sessions that have multiple session time.
            for detail in details_table:
                rows = detail.find_all(
                    'tr', id=re.compile('trSSR_CLSRCH_MTG1\$\d+_row\d'))
                if len(rows) == 1:
                    row: Tag = rows[0]
                    times.append(
                        row.find('span', id=re.compile('MTG_DAYTIME\$\d')).string)
                    locations.append(
                        row.find('span', id=re.compile('MTG_ROOM\$\d')).string)
                    instructors.append(
                        row.find('span', id=re.compile('MTG_INSTR\$\d')).string)
                elif len(rows) > 1:
                    locations.append(
                        rows[0].find('span', id=re.compile('MTG_ROOM\$\d')).string)
                    instructors.append(
                        rows[0].find('span', id=re.compile('MTG_INSTR\$\d')).string)
                    time: List[str] = [
                        row.find('span', id=re.compile('MTG_DAYTIME\$\d')).string for row in rows]
                    times.append(";".join(time))
                else:
                    raise ValueError(
                        f"The number of detail rows is incorrect. Expect an integer larger than 1, actual value: {len(rows)}")
            self._instructors.append(instructors)
            self._times.append(times)
            self._locations.append(locations)

    def write_to_csv(self, path: str) -> None:
        headers: List[str] = ["Name", "Code", "Time", "Instructor", "Location"]
        # contents: List[Tuple[str]] = zip(
        #     self.names, self.codes, self.times, self.instructors, self.locations)
        
        contents: List[List[str]]=[]
        for i in range(len(self._names)):
            for j in range(len(self._codes[i])):
                contents.append([self._names[i], self.codes[i][j], self.times[i][j], self.instructors[i][j], self.locations[i]])
        with open(path, 'w+', encoding='utf-8', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)
            f_csv.writerows(contents)


subjects: List[str] [name[:-5] for name in os.listdir(r"C:\Users\MyFix\Documents\Projects\AutoSchedule.Data\pages")]
subject = ["Accounting"]
for subject in subjects:
    fe = FieldExtractor(subject)
    fe.write_to_csv(f"./output/{subject}.csv")
