# pyTBA
Python 3 Blue Alliance API Layer for parsing FIRST Robotics Competition event data.
https://www.thebluealliance.com/

## Features:
* Simple and lightweight API for downloading and parsing BlueAlliance data
* Data caching faster performance
* OPR / Individual Stats calculation

## Adding it to your code:
To install with `pip`:
```bash
pip install pyTBA
```

To add PyTBA to your project, import the `pytba.api` module, and set an app id:

```python
from pytba import api as tba

tba.set_api_key("<Your Name>", "<App Name>", "<App Version>")
```
## Basic Usage:
The most basic usage is to make a query to an arbitrary URL in the TBA API.
 This is done by:
 ```python
 tba.tba_get('relative/url/goes/here')
 ```
 PyTBA makes a request to the TBA API (https://www.thebluealliance.com/api/v2/)
  and returns the response, stored as a `dict`. (See [TBA API docs](https://www.thebluealliance.com/apidocs) for more information about keys)
 
 PyTBA can also retrieve data for entire events:
 ```python
    tba.event_get('<Event Code>')
 ```
 This returns an `Event` object, which groups together location, team, match, awards, and rankings data.
 For example, to retrieve a list of `match` models from an `Event`:
 ```python
    event = tba.event_get('2016chcmp')
    matches = event.matches
 ```
 
 More advanced usage can be found in the documentation in the source code.
  
##Modules required:
* `requests`
* `cachecontrol`
* `dpath`
* `numpy` - for OPR calculation
  
###Note about older versions:
If you are updating from an older version (with the single blualliance.py file), be aware that the package structure has become more modularized. The core API code is now in the `pytba.api` module. The `Event` class is now under `pytba.models`. The decorators and utility methods are now under `pytba.util`, and OPR calcuation is now under `pytba.stat`. Check out [the init release](https://github.com/Thing342/pyTBA/releases/tag/init) if you need to clone the older code.

