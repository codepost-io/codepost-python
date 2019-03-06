# codePost CLI

## Command Line Syntax

```
$ push-to-codePost2 --help
usage: push-to-codePost2 [-h] [-a A] [-s S [S ...]] [--netid] [--groupname]
                         [--extend] [--overwrite] [--verbose]
                         [--without-tests] [--use-cache] [--skip-notdone]

optional arguments:
  -h, --help       show this help message and exit
  -a A             The name of the assignment to upload to (e.g. Loops)
  -s S [S ...]     The list of folders, one folder per submission to upload.
  --netid          Assume each folder name is a different NetID instead of
                   submission hashes, and resolve partners. [NOT RECOMMENDED]
  --groupname      Assume each folder name contains all NetIDs of a group, of
                   submission hashes.
  --extend         If submission already exists, add new files to it and
                   replace old files if the code has changed.
  --overwrite      If submission already exists, overwrite it.
  --verbose        Display informational messages.
  --without-tests  Allow upload assignments that do not have compiled tests.
  --use-cache      Allow for caching mechanism (i.e., for groups).
  --skip-notdone   Skip submissions that are not done.
```
