#!/bin/bash

USAGE="
`basename $0` [-e] -- This script creates local user account and installs apps.
    Where:
        -h shows this help text
        -e Install Xcode
"

# script must run as root. need a check here.

# Ask if current accout should be hidden? Add logic to check for currently logged in user, if it's "Admin" hide the account.
#CURRENT_USERNAME = $(whoami)
sudo dscl . create /Users/Admin IsHidden 1

# Test if current user is root
#if [ $EUID != 0 ]
#    then
#        echo "This script must be run as root (or using sudo). Exiting!"
#        exit 1
#fi

# Takes one option to initiate the install of xcode. Xcode is usually installed on dev machines.
while getopts "eh?" opts; do
    case $opts in
      e) ENGINEER=$OPTARG
          echo "installing xcode!"
          installer -pkg /Volumes/ACCOUNTS/xcode.pkg -target /
          echo "Done installing!"
          ;;
      h|\?) echo "$USAGE"
      exit 1 ;;
    esac
done
shift $((OPTIND - 1))


# Pre-flight configurations to do before creating an account.

# Install package to local hard dirve. Change pkg location to google drive
installer -pkg /Volumes/ACCOUNTS/MerakiSM-Agent-sqor-systems.pkg -target /

# Install slack to /Applications
installer -pkg /Volumes/ACCOUNTS/Slack_2.0.3.pkg -target /

# Install chrome browser to /Applications
installer -pkg /Volumes/ACCOUNTS/Google_Chrome.pkg -target /

# Install google drive to /Applications
installer -pkg /Volumes/ACCOUNTS/Google_Drive.pkg -target /

# Setup customized Dock
cp /Volumes/ACCOUNTS/com.apple.dock.plist /System/Library/User\ Template/English.lproj/Library/Preferences/

# Copy Chrome preferences
if [ ! -d "/Library/Google" ]
    then
        mkdir "/Library/Google"
fi
cp /Volumes/ACCOUNTS/Google\ Chrome\ Master\ Preferences /Library/Google/


# Create local admin account
echo "Enter a username for this account: "
read USERNAME

echo "Enter a full name for this account: "
read FULLNAME

echo "Enter a password for this user: "
read -s PASSWORD

# Give user admin privileges
echo "Is this an administrative user? (y/n)"
read GROUP_ADD

if [ "$GROUP_ADD" = n ]
    then
        SECONDARY_GROUPS="staff"  # for a non-admin user
elif [ "$GROUP_ADD" = y ]
    then
        SECONDARY_GROUPS="admin _lpadmin _appserveradm _appserverusr" # for an admin user
else
    echo "You did not make a valid selection!"
fi

# Find out the next available user ID
MAXID=$(dscl . -list /Users UniqueID | awk '{print $2}' | sort -ug | tail -1)
USERID=$((MAXID+1))

#Check OS version. if osx 10.11 or 10.10 then create user . Could probably remove this if statement?
OSXVERSION=$(sw_vers -productVersion | awk -F '.' '{print $1 "." $2}')
if [ "$OSXVERSION" == "10.11" ] || [ "$OSXVERSION" == "10.10" ]
    then
        # printf "$OSXVERSION $USERNAME $FULLNAME $USERID $PASSWORD"
        sysadminctl -addUser $USERNAME -fullName "$FULLNAME" -UID=$USERID -password $PASSWORD
fi

# Add user to the Admin group
for GROUP in $SECONDARY_GROUPS ; do
    dseditgroup -o edit -t user -a $USERNAME $GROUP
done
echo "Created user $USERID: $USERNAME ($FULLNAME)"

# Generate hostname from username ie. "User Name" to "user-name"
COMPNAME=$(echo $FULLNAME | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')
printf " Setting computer name to  $FULLNAME \n"

# Set hostname, bonjour name, and computer name using scutil
#printf "$COMPNAME"
printf "\n Setting hostname to $COMPNAME \n"

sudo scutil --set ComputerName $COMPNAME
sudo scutil --set HostName $COMPNAME
sudo scutil --set LocalHostName $COMPNAME
#scutil --get ComputerName

