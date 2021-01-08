# CSLR Canopy Forum Scraper

Used to gather [Canopy Forum](https://canopyforum.org/) Authors and Articles for the CSLR Team.

## Usage:
	
  1. Download/Clone this repository by clicking on the "Code" green button. 
  1. Install Python 3: Visit the [python webpage](https://www.python.org/downloads/) and use the installer
  1. Install the neccessary python-3 packages: `python3 -m pip install requests beautifulsoup4 tqdm`
  1. Run the scraper from your terminal - ensure you are in the appropriate directory: `python3 CFScraper.py`

## Script Flags:

Inside the `CFScraper.py` script, you will find a couple of flags at the top of the script:

  - `logging = False` Setting this to `True` will print warnings and progress information to the console
  - `save_to_pdf = False # Has not been fully implemented` Setting this to `True` will save each script as a pdf
  - `debugging = False` Setting this to `True` will only export 1 contact
  - `auto_email = False`  Setting this to `True` will email the csv file to a target email you provide

## Script Parameters:

If you have set the `auto_email` script flag to `True`, then you must use the following parameters when running the script:

  - `--email` - The from sender (gmail account - CSLR team, see login info for scraper email)
  - `--password` - The password for the from sender
  - `--to` - The to email address (can be any email address)


Example: `python3 CFScraper.py --email "MY EMAIL" --password "MY PASSWORD", --to "TO EMAIL"`

## Bugs

If you run into a `Bad Credentials Error`, note that the from email you are using must be a gmail account.
Furthermore, the gmail account must have "Less Secure Apps Authentication" enabled.

For any other issues, feel free to contact me or file a new issue.
