#!/usr/local/bin/bash

### set -e exits the script immediately if any command exits with a non-zero status.
set -e
### Command line parser
USAGE="
`basename $0` [-t] <tag color> [-s] <path> -- This script will rsync tagged directories from src to dest.

  Where:
    -h Shows this help text
    -t tag color to search for
    -s source path
    -l emails report
    -n dry run of copy
    -d deletes directories

"
### Color variables to print text in color
red=$(tput setaf 1)
yellow=$(tput setaf 3)
green=$(tput setaf 2)
reset=$(tput sgr0)
dest_path="/Volumes/Department Archive 2/Archives"
IFS=$'\n\t'
while getopts "t:s:lndh?" opt; do
    case $opt in
      t) tag_color=$OPTARG ;;
      s) src_path=$OPTARG ;;
#      a) dest_path=$OPTARG ;; #archive path
#      l) email_log ;;
      n) dry_run=1 ;;
      d) delete_dirs=1;;
      h|\?) echo "$USAGE"
      exit 1 ;;
    esac
done
shift $((OPTIND -1))

printf "\nSearching for all directories tagged with the color ${tag_color^^}\n\n"
#printf "$dest_path"

###Test conditions. Will test if paths are valid
if [[ -d "${src_path}" ]]
  then
  printf "Path is valid: ${src_path}\n"
else
  printf "Error: ${src_path} does not exist!\n"
  exit 1
fi
if [[ -d "${dest_path}" ]] # Test if directory exist
    then
    printf "Path is valid: ${dest_path}\n"
else
  print "Error: ${dest_path} does not exist!\n"
fi

### Associates name to number. The number is mac specific and corresponds to a tag color
color_code=$(case ${tag_color,,} in
  (none) echo '0' ;;
  (gray) echo '1' ;;
  (green) echo '2' ;;
  (purple) echo '3' ;;
  (blue) echo '4' ;;
  (yellow) echo '5' ;;
  (red) echo '6' ;;
  (orange) echo '7' ;;
esac)
#printf "Color code number ${color_code}\n"

### Generate a list off all directories and its tag color. maxdepth can be set to 2 if running from parent level
listings=$(find "$src_path" -maxdepth 2 -type d | while read line; do
  mdls -name kMDItemFSLabel -raw "$line" ; echo ",$line"
done)

### Find all directories with specified tag color
dir_list=$(printf "${listings}\n" | grep -e "^$color_code" | cut -d',' -f2)

###Get number of directories
dir_count=$(printf "$dir_list\n" | wc -l)
printf "$dir_count\n"

### Create a directory with date.
date=`date +%d%m%Y`
cur_date=$(date +"%F")
hour=`date +%H`
printf "$cur_date\n"
mkdir $dest_path/"$cur_date"

### Size of each directory and a grand total
function src_size {
  #printf "\nGathering a list of directories and their sizes\n"
  dir_report=$(du -ch -xd0 $dir_list)
  printf "$dir_report\n"
}

### Trap interrupts and exit instead of continuing the loop
function trap_clean {
  echo -e "Caught an error trying to rsync $(basename $0) $(date +"%F")"
  echo "Encountered error! stopping rsync!" | mail -s "Error archiving" <email address>
}
trap trap_clean ERR SIGHUP SIGINT SIGTERM

### remove_dirs deletes directories in the list
function remove_dirs {
  IFS=$(echo -en "\n\b")
  for dir in $dir_list; do
    (du -sh "$dir")
    dirname=$(basename "$dir")
    get_dest="$dest_path/${dirname}"
    (du -sh "$get_dest") # Spawning a subprocess
  printf "Directory to Delete: $dir\n" ; read -t 24 -p "Hit enter or wait 24 seconds to exit"; rm -rfv "$dir"
  done
}

### get size of archived directories and compare with source directories.
function file_count {
  IFS=$(echo -en "\n\b")
  for dir in $dir_list; do
  dirname=$(basename "$dir")
  #printf "$dirname\n"
  get_dest="$dest_path/${dirname}"
  (du -sh "$get_dest") # Spawning a subprocess
#  (du -sh "$get_dest"; du -sh "$dir") # This formatting isn't right.
  done
}

### if Dry run else run rsync and send an email when finished.
if [[ $dry_run -eq 1 ]]; then
  printf "${yellow}Dry run report, inculudes sizes:${reset}\n"
  src_size
  #$dir_report\n"
elif [[ $delete_dirs -eq 1 ]]; then
  printf "${red}About to delete a lot of files!${reset}\n"  ## add a wait time of 5 seconds
  #file_count
  remove_dirs
else
  printf "${green}The following list of directories will be archived, sizes included:${reset}\n
$dir_report\n"
  NORMIFS=$IFS
  IFS=$(echo -en "\n\b")
    for dir in $dir_list
    do
       rsync -auvWP "$dir" "$dest_path"
  done

### email report
  dir_report=$(src_size)
  archive_dir_report=$(file_count)
IFS=$NORMIFS
  mail -s "Archive Successful!" <email address here><<EOF
  Hello all,
  Here is a report of what has been archived. Please do not reply
  to this email.
  Source report:
  ${dir_report}

  Archive report:
  ${archive_dir_report}


EOF
fi
