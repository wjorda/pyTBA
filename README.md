# pyTBA
Python 3 Blue Alliance API Layer for parsing FIRST Robotics Competition event data.

## Adding it to your code:
To add PyTBA to your project, all you have to do is import the `pytba.api`
module, and set an app id:

`
from pytba import api as tba

tba.set_api_key("<Your Name>", "<App Name>", "<App Version>")
`
## Usage:
The most basic usage is to make a query to a known URL in the TBA API.
 This is done by:
 '
 tba.tba_get('relative/url/goes/here')
 '
 PyTBA makes a request to the TBA API and returns the JSON response stored
 as a `dict`.
