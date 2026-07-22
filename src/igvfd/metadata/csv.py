from igvfd.report import format_row


class CSVGenerator:

    def writerow(self, row):
        return format_row([str(c) if c is not None else '' for c in row])
