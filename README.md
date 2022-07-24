# File Filter

Filter files with python expressions.

## Examples

Output all lines that contain "abc":
```
file_filter.py input.txt -f '"abc" in l'
```

Output all rows from a CSV file where "column1" has the value "abc":
```
file_filter.py input.csv -f 'r["column1"] == "abc"'
```
