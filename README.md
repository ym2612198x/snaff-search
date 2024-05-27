usage: snaff-search.py [-h] -i INPUT [-d] [-e EXCLUDE] [-w INCLUDE] [-n] [-yellow] [-green] [-red] [-black] [-shares] [-all] [-v]

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Filename of Snaffler log

  -e EXCLUDE, --exclude EXCLUDE
                        List of words to exclude from results (comma separated eg. ".inc,example,etc")
  -w INCLUDE, --include INCLUDE
                        List of words to include in results (comma separated eg. "password,username,.ps1")
  -d, --duplicate       Include duplicate entries
  -n, --names           Only print filenames of found items
  -yellow, --yellow     Only print yellow items
  -green, --green       Only print green items
  -red, --red           Only print red items
  -black, --black       Only print black items
  -shares, --shares     Print share info
  -all, --all           Print all items
  -v, --verbose         Show verbose messages
