# snaff-search

Search Snaffler (https://github.com/SnaffCon/Snaffler) log files
Include/Exclude colours words etc.
Usage: `snaff-search.py [-h] -i INPUT [-d] [-e EXCLUDE] [-w INCLUDE] [-n] [-yellow] [-green] [-red] [-black] [-shares] [-all] [-v]`

Options:
```

  -i INPUT, --input INPUT         Filename of Snaffler log
  -e EXCLUDE, --exclude EXCLUDE   List of words to exclude from results (comma separated eg. ".inc,example,etc")
  -w INCLUDE, --include INCLUDE   List of words to include in results (comma separated eg. "password,username,.ps1")
  -n, --names                     Only print filenames of found items
  -d, --duplicate                 Include duplicate entries
  -yellow, --yellow               Only print yellow items
  -green, --green                 Only print green items
  -red, --red                     Only print red items
  -black, --black                 Only print black items
  -shares, --shares               Print share info
  -all, --all                     Print all items
  -v, --verbose                   Show verbose messages

```
