def test_metadata_csv_csv_generator():
    from igvfd.metadata.csv import CSVGenerator
    csv = CSVGenerator()
    row = csv.writerow(['a', 'b', '123'])
    assert row == b'a\tb\t123\r\n'


def test_metadata_csv_strips_special_chars_without_quoting():
    from igvfd.metadata.csv import CSVGenerator
    csv = CSVGenerator()
    row = csv.writerow(['col with\ttab', 'line1\nline2'])
    assert row == b'col with tab\tline1 line2\r\n'
