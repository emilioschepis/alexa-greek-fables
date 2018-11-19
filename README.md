# Greek Fables
**Greek Fables** tells you fables written in the Ancient Greece by the famous storyteller Aesop. Enter a world of anthropomorphic creatures and timeless lessons.
## Alexa Skill Availability
*Coming soon*
## Technical details
### Scraper
The scraper is written in Python3 and utilizes [BeautifulSoup 4](https://pypi.org/project/beautifulsoup4/) to parse the HTML coming from the source (see credits).
Once organized, the stories are converted in JSON language and uploaded to AWS's DynamoDB through [boto3](https://pypi.org/project/boto3/).
### Skill
The skill is written in Python3 and utilizes the [AWS Skill SDK (ASK)](https://pypi.org/project/ask-sdk-core/) to create the structure and organize the interaction with the user.
When the user asks for a story, this script queries the AWS's DynamoDB for a random one, parses it and adds [SSML](https://developer.amazon.com/docs/custom-skills/speech-synthesis-markup-language-ssml-reference.html) tags.
## Credits
* [Stories](http://read.gov/aesop/001.html)
* [Icon source](https://www.flaticon.com/free-icon/story_306127)
