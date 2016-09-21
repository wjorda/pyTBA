# pyTBA
Python 3 Blue Alliance API Layer for parsing FIRST Robotics Competition event data.

## Adding it to your code:
To add PyTBA to your project, all you have to do is import the `pytba.api`
module, and set an app id:

```python
from pytba import api as tba

tba.set_api_key("<Your Name>", "<App Name>", "<App Version>")
```
## Usage:
The most basic usage is to make a query to an arbitrary URL in the TBA API.
 This is done by:
 ```python
 tba.tba_get('relative/url/goes/here')
 ```
 PyTBA makes a request to the TBA API (https://www.thebluealliance.com/api/v2/)
  and returns the response, stored as a `dict`. (See [https://www.thebluealliance.com/apidocs](TBA api docs) for more information)

